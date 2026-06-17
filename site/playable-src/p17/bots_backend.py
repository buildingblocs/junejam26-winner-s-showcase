"""In-process backend for the browser build of BREACH.

The original game is real-time multiplayer (an authoritative websockets server
plus 3 connected clients). The browser build can't host a server or match up
players, so this module runs the SAME server logic (server.py) locally, in the
same process, and fills the other two seats with bots. The human plays exactly
as before; the "network" is just direct calls into the server module.

LocalBackend exposes the same surface the client used from NetworkClient:
  - .incoming : a queue the client drains with get_nowait()
  - .send(message) : client -> server
  - .start() : boot the server loop + bots
"""
import asyncio
import json
import math
import queue
import random
import uuid

import server
from config import TERMINALS, INTERACTION_RANGE

SPECIALTIES = ["Python Engineer", "Cryptographer", "Network Analyst"]


def _new_player(player_id):
    """The exact lobby player record server.connection_handler creates."""
    spawn_index = len(server.players)
    return {
        "id": player_id,
        "name": "Player",
        "x": 100 + (spawn_index % 6) * 45,
        "y": 600,
        "role": "",
        "specialty": "",
        "social_role": "",
        "life_state": "lobby",
        "alive": False,
        "color": (220, 220, 220),
        "ready": False,
        "joined": False,
        "difficulty_vote": "",
        "attack_points": 0,
        "attack_bonus": 0,
        "ability_cooldowns": {},
        "learning_profile": {},
        "answer_history": [],
        "active_challenge": None,
        "challenge_cache": {},
        "challenge_cache_epoch": 0,
        "activity": "",
    }


async def register_player(sock):
    player_id = uuid.uuid4().hex[:8]
    server.players[player_id] = _new_player(player_id)
    server.clients[player_id] = sock
    await server.send(sock, {"type": "welcome", "player_id": player_id})
    return player_id


class HumanSock:
    """Server -> human client. Pushes decoded messages onto the client queue."""

    def __init__(self, incoming):
        self.incoming = incoming

    async def send(self, data):
        self.incoming.put(json.loads(data))


class BotSock:
    """Server -> bot. Just remembers the latest broadcast state."""

    def __init__(self):
        self.state = None

    async def send(self, data):
        message = json.loads(data)
        if message.get("type") == "state_update":
            self.state = message["state"]


class BotBrain:
    """A very small AI: joins, picks a free specialty, readies up, votes, then
    walks to terminals and solves their challenges (it can read the correct
    answer straight from the in-process game state)."""

    def __init__(self, player_id, sock, name, human_id, order=0):
        self.pid = player_id
        self.sock = sock
        self.name = name
        self.human_id = human_id
        self.order = order
        self._target = None
        self._retarget_at = 0.0

    async def _send(self, message):
        try:
            await server.handle_message(self.sock, self.pid, message)
        except Exception:
            pass

    def _available_specialty(self):
        taken = {
            p.get("specialty")
            for pid, p in server.players.items()
            if pid != self.pid and p.get("specialty")
        }
        for spec in SPECIALTIES:
            if spec not in taken:
                return spec
        return random.choice(SPECIALTIES)

    async def run(self):
        await asyncio.sleep(1.0)
        await self._send({"type": "join", "name": self.name})
        # The human ALWAYS picks their specialty first. There is no time
        # pressure here: the lobby cannot start until everyone is ready, and the
        # human can't ready without a specialty (MIN_PLAYERS = 3), so the bots
        # just wait — with no wall-clock timeout — until the human has chosen,
        # then take whatever is left. (A previous boot-relative timeout let the
        # bots grab specialties before a slow human even reached the screen.)
        while server.game_status == "lobby":
            human = server.players.get(self.human_id)
            if human and human.get("specialty"):
                break
            await asyncio.sleep(0.3)
        await asyncio.sleep(0.3 + 0.3 * self.order)  # stagger the two bots
        if server.game_status == "lobby":
            await self._send({"type": "select_role", "role": self._available_specialty()})
            await asyncio.sleep(0.5)
            await self._send({"type": "ready", "ready": True})

        voted = False
        while True:
            await asyncio.sleep(0.45)
            status = server.game_status
            if status == "lobby":
                me = server.players.get(self.pid)
                if me and not me.get("specialty"):
                    await self._send({"type": "select_role", "role": self._available_specialty()})
                if me and me.get("specialty") and not me.get("ready"):
                    await self._send({"type": "ready", "ready": True})
                voted = False
            elif status == "voting":
                if not voted:
                    await self._send({"type": "difficulty_vote", "difficulty": "easy"})
                    voted = True
            elif status == "playing":
                await self._play()

    async def _play(self):
        me = server.players.get(self.pid)
        if not me or me.get("life_state") != "alive":
            return
        # If a challenge is open, answer it correctly (the answer is right here).
        session = me.get("active_challenge")
        if session and session.get("challenge"):
            challenge = session["challenge"]
            answer = challenge.get("answer", "")
            await self._send({
                "type": "submit_answer",
                "terminal_id": session.get("terminal_id"),
                "answer": answer,
            })
            return
        # Otherwise wander to a terminal and interact.
        now = server.now()
        if self._target is None or now >= self._retarget_at:
            self._target = random.choice(list(TERMINALS.keys()))
            self._retarget_at = now + random.uniform(4.0, 8.0)
        term = TERMINALS[self._target]
        dx = term["x"] - me["x"]
        dy = term["y"] - me["y"]
        dist = math.hypot(dx, dy) or 1.0
        if dist > INTERACTION_RANGE * 0.6:
            step = 8.0
            await self._send({"type": "move", "dx": step * dx / dist, "dy": step * dy / dist})
        else:
            await self._send({"type": "interact", "terminal_id": self._target})


class LocalBackend:
    """Drop-in replacement for the client's NetworkClient."""

    def __init__(self, uri=None):
        self.incoming = queue.Queue()
        self.outgoing = queue.Queue()
        self._human_sock = HumanSock(self.incoming)
        self._human_id = None

    def start(self):
        asyncio.ensure_future(self._boot())

    def send(self, message):
        self.outgoing.put(message)

    def close(self):
        pass

    async def _boot(self):
        # Reset any prior state, then seat the human and two bots.
        server.reset_state()
        self._human_id = await register_player(self._human_sock)
        self.incoming.put({"type": "connection", "connected": True})

        bots = []
        for order, name in enumerate(("AVA (bot)", "NOVA (bot)")):
            sock = BotSock()
            bot_id = await register_player(sock)
            bots.append(BotBrain(bot_id, sock, name, self._human_id, order))

        asyncio.ensure_future(server.broadcast_loop())
        asyncio.ensure_future(self._drain_human())
        for bot in bots:
            asyncio.ensure_future(bot.run())

    async def _drain_human(self):
        while True:
            await asyncio.sleep(0)
            try:
                while True:
                    message = self.outgoing.get_nowait()
                    if self._human_id:
                        await server.handle_message(self._human_sock, self._human_id, message)
            except queue.Empty:
                pass
            await asyncio.sleep(0.01)
