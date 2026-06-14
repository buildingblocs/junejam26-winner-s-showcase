import asyncio
import json
import math
import os
import random
import time
import urllib.error
import urllib.request
import uuid

from challenges import (
    TERMINAL_TOPICS,
    TERMINOLOGY_CHANCE,
    answer_matches,
    make_local_challenge,
)
from config import (
    ABILITY_COOLDOWN_SECONDS,
    ATTACK_POINT_REWARD,
    BLACKOUT_DURATION_SECONDS,
    BROADCAST_HZ,
    DIFFICULTIES,
    GAME_DURATION_SECONDS,
    INFRASTRUCTURE_SYSTEMS,
    INTERACTION_RANGE,
    MALWARE_DAMAGE,
    MAX_X,
    MAX_Y,
    MIN_PLAYERS,
    MIN_X,
    MIN_Y,
    NORMAL_TERMINALS,
    PLAYER_RADIUS,
    ROLE_REVEAL_GRACE_SECONDS,
    SERVER_HOST,
    SERVER_PORT,
    SPAWN_POINTS,
    SPECIALTY_BONUS,
    SYSTEM_HEALTH_DELTA,
    SYSTEM_START_HEALTH,
    TASK_COOLDOWN_SECONDS,
    TERMINAL_COLLISION_PADDING,
    TERMINAL_HEIGHT,
    TERMINAL_WIDTH,
    TERMINALS,
    ROLE_COLORS,
)
from game_rules import (
    all_systems_offline as rules_all_systems_offline,
    all_systems_restored as rules_all_systems_restored,
    average_system_health as rules_average_system_health,
    challenge_track as rules_challenge_track,
    specialty_bonus_applies as rules_specialty_bonus_applies,
    sync_system_task,
    system_score_summary as rules_system_score_summary,
    system_status,
    timed_match_result,
)
from protocol import (
    ACTIVE_SOCIAL_ROLES,
    RESULT_ATTACKERS_WIN,
    RESULT_DEFENDERS_WIN,
    ROLE_ATTACKER,
    ROLE_DEFENDER,
)


clients = {}
players = {}
tasks = {}
game_started_at = None
game_status = "lobby"
game_result = None
game_over_reason = None
selected_difficulty = None
vote_result_started_at = None
vote_result_seconds = 3
vote_result_tied = False
vote_result_tied_options = []
roles_assigned = False
ability_blackouts = {}
openai_cache_inflight = set()
ATTACKER_ABILITIES = {
    "BLACKOUT": {"cost": 1},
    "FALSE_ALERT": {"cost": 2},
    "MALWARE_INJECTION": {"cost": 3},
}


def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)


load_env_file()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"


def fresh_tasks(base_difficulty="easy"):
    return {
        terminal_id: {
            "id": terminal_id,
            "system_name": INFRASTRUCTURE_SYSTEMS[terminal_id],
            "health": SYSTEM_START_HEALTH,
            "status": system_status(SYSTEM_START_HEALTH),
            "completed": SYSTEM_START_HEALTH >= 100,
            "cooldown_until": 0,
            "repair_cooldown_until": 0,
            "attack_cooldown_until": 0,
            "compromised": False,
            "difficulty": base_difficulty,
        }
        for terminal_id in NORMAL_TERMINALS
    }


def sync_task_health(task):
    sync_system_task(task)


tasks = fresh_tasks()


def now():
    return time.monotonic()


def current_timer():
    if game_started_at is None:
        return GAME_DURATION_SECONDS
    elapsed = max(0, now() - game_started_at)
    return max(0, GAME_DURATION_SECONDS - int(elapsed))


def task_cooldown_remaining(task, action=None):
    if action == "repair":
        cooldown_until = task.get("repair_cooldown_until", task.get("cooldown_until", 0))
    elif action == "attack":
        cooldown_until = task.get("attack_cooldown_until", task.get("cooldown_until", 0))
    else:
        return max(
            task_cooldown_remaining(task, "repair"),
            task_cooldown_remaining(task, "attack"),
        )
    return max(0, int(cooldown_until - now()))


def ability_cooldown_remaining(player, ability):
    cooldowns = player.get("ability_cooldowns", {})
    return max(0, int(cooldowns.get(ability, 0) - now()))


def learning_profile(player, terminal_id):
    profiles = player.setdefault("learning_profile", {})
    return profiles.setdefault(
        terminal_id,
        {
            "attempts": 0,
            "correct_streak": 0,
            "wrong_streak": 0,
            "last_missed_concept": "",
            "last_mastered_concept": "",
            "concepts": {},
        },
    )


def submitted_answer_label(challenge, answer):
    normalized = str(answer).strip()
    options = challenge.get("options", [])
    if len(normalized) == 1 and normalized.casefold() in ("a", "b", "c", "d"):
        index = ord(normalized.casefold()) - ord("a")
        if 0 <= index < len(options):
            return f"{normalized.upper()}. {options[index]}"
    if normalized.isdigit():
        index = int(normalized) - 1
        if 0 <= index < len(options):
            return f"{normalized}. {options[index]}"
    return normalized or "(blank)"


def record_learning_result(player, terminal_id, challenge, correct, answer=""):
    profile = learning_profile(player, terminal_id)
    profile["attempts"] += 1
    concept = challenge.get("concept") or challenge.get("category", "general")
    concept_stats = profile.setdefault("concepts", {}).setdefault(
        concept,
        {"attempts": 0, "correct": 0},
    )
    concept_stats["attempts"] += 1
    if correct:
        concept_stats["correct"] += 1
    if correct:
        profile["correct_streak"] += 1
        profile["wrong_streak"] = 0
        profile["last_mastered_concept"] = concept
    else:
        profile["wrong_streak"] += 1
        profile["correct_streak"] = 0
        profile["last_missed_concept"] = concept
        history = player.setdefault("answer_history", [])
        history.append(
            {
                "question": str(challenge.get("question", ""))[:260],
                "your_answer": submitted_answer_label(challenge, answer)[:120],
                "correct_answer": str(challenge.get("answer", ""))[:120],
                "topic": concept_display_name(concept),
                "system": INFRASTRUCTURE_SYSTEMS.get(terminal_id, "Lab"),
            }
        )
        del history[:-30]


def concept_display_name(concept):
    text = str(concept or "general").strip()
    if text.startswith("terminology:"):
        return f"Terminology: {text.split(':', 1)[1].upper()}"
    cleaned = text.replace("_", " ").replace("-", " ").replace(":", " ")
    return cleaned.title()


def learning_insights_for(player, include_history=False):
    concept_rows = []
    total_attempts = 0
    total_correct = 0
    for terminal_id, profile in player.get("learning_profile", {}).items():
        system_name = INFRASTRUCTURE_SYSTEMS.get(terminal_id, "Lab")
        for concept, stats in profile.get("concepts", {}).items():
            attempts = int(stats.get("attempts", 0))
            correct = int(stats.get("correct", 0))
            if attempts <= 0:
                continue
            total_attempts += attempts
            total_correct += correct
            concept_rows.append(
                {
                    "topic": concept_display_name(concept),
                    "system": system_name,
                    "attempts": attempts,
                    "correct": correct,
                    "accuracy": round((correct / attempts) * 100),
                }
            )

    strengths = sorted(
        [row for row in concept_rows if row["correct"] > 0],
        key=lambda row: (-row["accuracy"], -row["correct"], -row["attempts"], row["topic"]),
    )[:3]
    weaknesses = sorted(
        [row for row in concept_rows if row["correct"] < row["attempts"]],
        key=lambda row: (row["accuracy"], -row["attempts"], row["topic"]),
    )[:3]
    insight = {
        "player_id": player.get("id", ""),
        "name": player.get("name", "Player"),
        "specialty": player.get("specialty", ""),
        "attempts": total_attempts,
        "correct": total_correct,
        "accuracy": round((total_correct / total_attempts) * 100) if total_attempts else 0,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }
    if include_history:
        insight["mistakes"] = list(player.get("answer_history", []))
    return insight


def openai_challenge_schema():
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"},
            "category": {"type": "string"},
            "question": {"type": "string"},
            "options": {
                "type": "array",
                "items": {"type": "string"},
            },
            "correct_index": {"type": "integer"},
            "answer": {"type": "string"},
            "explanation": {"type": "string"},
            "lesson": {"type": "string"},
            "hint": {"type": "string"},
            "relevance": {"type": "string"},
            "concept": {"type": "string"},
        },
        "required": [
            "title",
            "category",
            "question",
            "options",
            "correct_index",
            "answer",
            "explanation",
            "lesson",
            "hint",
            "relevance",
            "concept",
        ],
    }


def extract_openai_text(response_data):
    if isinstance(response_data.get("output_text"), str):
        return response_data["output_text"]
    for item in response_data.get("output", []):
        for content in item.get("content", []):
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                return content["text"]
    return ""


def openai_prompt(player, terminal_id, difficulty, profile, force_short_answer=False):
    system_name = INFRASTRUCTURE_SYSTEMS[terminal_id]
    topic = TERMINAL_TOPICS[terminal_id]
    specialty = player.get("specialty") or "Unassigned"
    action = "attack" if player_attacks_system(player) else "repair"
    side = "Attacker" if action == "attack" else "Defender"
    focus = topic["attacker_focus"] if action == "attack" else topic["defender_focus"]
    concept_rotation = ""
    if terminal_id == "terminal_crypto":
        concept_rotation = (
            "Rotate Network Core questions across netcat, pwntools recvuntil, p64/packing, "
            "buffer overflow, bounds checks, stack canary, NX/DEP, ASLR, ROP, format strings, "
            "and safe input handling. Avoid asking about the exact same concept more than twice in a row. "
        )
    if profile["wrong_streak"] > 0:
        adaptation = (
            f"The player recently missed {profile['last_missed_concept']}. "
            "Ask from the same skill family, but use a new angle or adjacent concept instead of repeating the exact wording."
        )
    elif profile["correct_streak"] >= 2:
        adaptation = (
            f"The player is doing well after {profile['correct_streak']} correct answers. "
            "Switch to a different concept in the same specialty."
        )
    else:
        adaptation = "Treat this as a fresh player and ask a clear beginner-friendly question."
    if force_short_answer:
        format_instruction = (
            "This challenge MUST be a one-word cybersecurity terminology short-answer question. "
            "Do not provide answer options. Set options to [], correct_index to -1, "
            "and answer to the single correct word or acronym."
        )
    else:
        format_instruction = (
            "Usually return exactly four options with correct_index 0-3. "
            "Sometimes make it a one-word cybersecurity terminology short-answer question: "
            "set options to [], correct_index to -1, and answer to the single correct word or acronym."
        )
    return (
        f"Generate one fresh {difficulty} cybersecurity question for BREACH. "
        f"System: {system_name}. Domain: {topic['category']}. Player specialty: {specialty}. "
        f"Side: {side}. The question should be about {focus}. "
        f"{concept_rotation}"
        "The hackathon challenge statement wants Python Basics, Reverse Engineering, Pwn / binary exploitation, "
        "or expandable cybersecurity domains, so keep the content practical and gameplay-friendly. "
        "Frame the question as a short in-lab mission ticket, incident, recovery task, or attack simulation. "
        f"Attempts on this system: {profile['attempts']}. {adaptation} "
        f"Keep the question short enough for a Pygame popup. {format_instruction} "
        "Do not repeat the exact examples len(['a','b','c']), nc example.com, or strcmp(input,'open')."
    )


def call_openai_challenge(player, terminal_id, difficulty, profile, force_short_answer=False):
    if not OPENAI_API_KEY:
        return None
    payload = {
        "model": OPENAI_MODEL,
        "input": [
            {
                "role": "system",
                "content": (
                    "You generate concise cybersecurity training questions for a hackathon game. "
                    "Questions may be four-option MCQs or one-word terminology short answers. "
                    "The lesson field must be one short takeaway sentence a beginner can remember. "
                    "Return only data matching the supplied JSON schema."
                ),
            },
            {"role": "user", "content": openai_prompt(player, terminal_id, difficulty, profile, force_short_answer)},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "breach_challenge",
                "schema": openai_challenge_schema(),
                "strict": True,
            }
        },
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        print(f"OpenAI challenge generation failed; using local fallback: {exc}")
        return None
    try:
        return json.loads(extract_openai_text(response_data))
    except json.JSONDecodeError as exc:
        print(f"OpenAI challenge parse failed; using local fallback: {exc}")
        return None


def normalize_generated_challenge(raw, fallback, terminal_id, difficulty, require_short_answer=False):
    if not isinstance(raw, dict):
        return fallback
    options = [str(option).strip() for option in raw.get("options", []) if str(option).strip()]
    if len(options) not in (0, 4):
        return fallback
    if require_short_answer and options:
        return fallback
    try:
        correct_index = int(raw.get("correct_index", -1))
    except (TypeError, ValueError):
        return fallback
    if options:
        if correct_index not in range(4):
            return fallback
        correct_answer = options[correct_index]
        answers = [correct_answer, chr(ord("a") + correct_index), str(correct_index + 1)]
    else:
        if correct_index != -1:
            return fallback
        correct_answer = str(raw.get("answer", "")).strip()
        if not correct_answer or len(correct_answer.split()) != 1:
            return fallback
        answers = [correct_answer]
    challenge = {
        **fallback,
        "id": f"openai_{terminal_id}_{difficulty}_{random.randint(1000, 9999)}",
        "title": str(raw.get("title") or fallback["title"])[:60],
        "category": str(raw.get("category") or fallback["category"])[:40],
        "question": str(raw.get("question") or fallback["question"])[:240],
        "prompt": str(raw.get("question") or fallback["question"])[:240],
        "options": options,
        "answers": answers,
        "answer": correct_answer,
        "explanation": str(raw.get("explanation") or fallback["explanation"])[:300],
        "lesson": str(raw.get("lesson") or fallback.get("lesson") or fallback["explanation"])[:180],
        "hint": str(raw.get("hint") or fallback["hint"])[:160],
        "relevance": str(raw.get("relevance") or fallback["relevance"])[:300],
        "concept": str(raw.get("concept") or fallback.get("concept") or fallback["category"])[:50],
        "source": "openai",
    }
    return challenge


def challenge_cache_key(terminal_id, difficulty, action, force_short_answer):
    answer_mode = "short" if force_short_answer else "mixed"
    return f"{terminal_id}:{difficulty}:{action}:{answer_mode}"


def snapshot_learning_profile(profile):
    return {
        "attempts": int(profile.get("attempts", 0)),
        "correct_streak": int(profile.get("correct_streak", 0)),
        "wrong_streak": int(profile.get("wrong_streak", 0)),
        "last_missed_concept": str(profile.get("last_missed_concept", "")),
        "last_mastered_concept": str(profile.get("last_mastered_concept", "")),
        "concepts": dict(profile.get("concepts", {})),
    }


def snapshot_player_for_prompt(player, action):
    return {
        "id": player.get("id", ""),
        "specialty": player.get("specialty", ""),
        "social_role": ROLE_ATTACKER if action == "attack" else ROLE_DEFENDER,
        "life_state": "alive",
    }


async def cache_openai_challenge(
    player_id,
    cache_key,
    cache_epoch,
    terminal_id,
    difficulty,
    player_snapshot,
    profile_snapshot,
    force_short_answer,
    fallback,
):
    inflight_key = (player_id, cache_key)
    try:
        raw = await asyncio.to_thread(
            call_openai_challenge,
            player_snapshot,
            terminal_id,
            difficulty,
            profile_snapshot,
            force_short_answer,
        )
        challenge = normalize_generated_challenge(
            raw,
            fallback,
            terminal_id,
            difficulty,
            force_short_answer,
        )
        if challenge.get("source") != "openai":
            return
        challenge["terminal_id"] = terminal_id
        player = players.get(player_id)
        if not player:
            return
        if player.get("challenge_cache_epoch") != cache_epoch:
            return
        cache = player.setdefault("challenge_cache", {})
        cache[cache_key] = challenge
        while len(cache) > 8:
            cache.pop(next(iter(cache)))
    finally:
        openai_cache_inflight.discard(inflight_key)


def schedule_openai_cache(player, terminal_id, difficulty, action, force_short_answer, fallback, profile):
    if not OPENAI_API_KEY:
        return
    cache_key = challenge_cache_key(terminal_id, difficulty, action, force_short_answer)
    inflight_key = (player["id"], cache_key)
    if inflight_key in openai_cache_inflight:
        return
    openai_cache_inflight.add(inflight_key)
    asyncio.create_task(
        cache_openai_challenge(
            player["id"],
            cache_key,
            player.get("challenge_cache_epoch", 0),
            terminal_id,
            difficulty,
            snapshot_player_for_prompt(player, action),
            snapshot_learning_profile(profile),
            force_short_answer,
            fallback,
        )
    )


async def challenge_for_player(player, terminal_id, difficulty):
    profile = learning_profile(player, terminal_id)
    action = "attack" if player_attacks_system(player) else "repair"
    force_short_answer = profile["attempts"] % 3 == 2 or random.random() < TERMINOLOGY_CHANCE
    fallback = make_local_challenge(
        terminal_id,
        difficulty,
        profile,
        action,
        force_terminology=force_short_answer,
    )
    cache_key = challenge_cache_key(terminal_id, difficulty, action, force_short_answer)
    challenge = player.setdefault("challenge_cache", {}).pop(cache_key, None) or fallback
    schedule_openai_cache(
        player,
        terminal_id,
        difficulty,
        action,
        force_short_answer,
        fallback,
        profile,
    )
    challenge["terminal_id"] = terminal_id
    return challenge


def clean_expired_effects():
    current_time = now()
    expired_blackouts = [
        player_id for player_id, expires_at in ability_blackouts.items()
        if expires_at <= current_time
    ]
    for player_id in expired_blackouts:
        ability_blackouts.pop(player_id, None)


def serialize_effects(viewer_id):
    clean_expired_effects()
    blackout_expires_at = ability_blackouts.get(viewer_id)
    return {
        "blackout_remaining": 0
        if blackout_expires_at is None
        else max(0, int(blackout_expires_at - now())),
        "false_alert": None,
    }


def average_system_health():
    return rules_average_system_health(tasks)


def system_score_summary():
    return rules_system_score_summary(tasks, SYSTEM_START_HEALTH)


def all_systems_restored():
    return rules_all_systems_restored(tasks)


def all_systems_offline():
    return rules_all_systems_offline(tasks)


def active_players():
    return [player for player in players.values() if player.get("joined")]


def specialty_taken_by_other(player_id, specialty):
    return any(
        other_id != player_id
        and other.get("joined")
        and other.get("specialty") == specialty
        for other_id, other in players.items()
    )


def distance(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def point_distance(player, point):
    return math.hypot(player["x"] - point["x"], player["y"] - point["y"])


def terminal_in_range(player, terminal_id):
    terminal = TERMINALS[terminal_id]
    return point_distance(player, terminal) <= INTERACTION_RANGE


def circle_hits_rect(cx, cy, radius, rect):
    left, top, right, bottom = rect
    closest_x = max(left, min(cx, right))
    closest_y = max(top, min(cy, bottom))
    return math.hypot(cx - closest_x, cy - closest_y) < radius


def terminal_collision_rect(terminal):
    half_width = TERMINAL_WIDTH / 2 + TERMINAL_COLLISION_PADDING
    half_height = TERMINAL_HEIGHT / 2 + TERMINAL_COLLISION_PADDING
    return (
        terminal["x"] - half_width,
        terminal["y"] - half_height,
        terminal["x"] + half_width,
        terminal["y"] + half_height,
    )


def position_blocked(x, y):
    return any(
        circle_hits_rect(x, y, PLAYER_RADIUS, terminal_collision_rect(terminal))
        for terminal in TERMINALS.values()
    )


def move_player(player, dx, dy):
    next_x = max(MIN_X, min(MAX_X, player["x"] + dx))
    next_y = max(MIN_Y, min(MAX_Y, player["y"] + dy))

    if not position_blocked(next_x, player["y"]):
        player["x"] = next_x
    if not position_blocked(player["x"], next_y):
        player["y"] = next_y


def task_action_for_player(player):
    return "attack" if player_attacks_system(player) else "repair"


def task_cooldown_for_player(player, task):
    return task_cooldown_remaining(task, task_action_for_player(player))


def start_task_cooldown_for_player(player, task):
    key = (
        "attack_cooldown_until"
        if task_action_for_player(player) == "attack"
        else "repair_cooldown_until"
    )
    task[key] = now() + TASK_COOLDOWN_SECONDS


def serialize_tasks(viewer_id=None):
    viewer = players.get(viewer_id)
    result = {}
    for terminal_id, task in tasks.items():
        repair_cooldown = task_cooldown_remaining(task, "repair")
        attack_cooldown = task_cooldown_remaining(task, "attack")
        result[terminal_id] = {
            **task,
            "cooldown_remaining": (
                task_cooldown_for_player(viewer, task)
                if viewer
                else max(repair_cooldown, attack_cooldown)
            ),
            "repair_cooldown_remaining": repair_cooldown,
            "attack_cooldown_remaining": attack_cooldown,
            "label": TERMINALS[terminal_id]["label"],
            "x": TERMINALS[terminal_id]["x"],
            "y": TERMINALS[terminal_id]["y"],
        }
    return result


def serialize_player(player, viewer_id):
    is_self = player["id"] == viewer_id
    serialized = {
        "id": player["id"],
        "name": player["name"],
        "x": player["x"],
        "y": player["y"],
        "role": player.get("role", ""),
        "specialty": player.get("specialty", ""),
        "life_state": player.get("life_state", ""),
        "alive": player.get("alive", False),
        "color": player.get("color", (220, 220, 220)),
        "ready": player.get("ready", False),
        "joined": player.get("joined", False),
        "difficulty_vote": player.get("difficulty_vote", ""),
        "activity": player.get("activity", ""),
    }
    if is_self:
        serialized.update(
            {
                "social_role": player.get("social_role", ""),
                "attack_points": player.get("attack_points", 0),
                "attack_bonus": player.get("attack_bonus", 0),
                "ability_cooldowns_remaining": {
                    ability: ability_cooldown_remaining(player, ability)
                    for ability in ATTACKER_ABILITIES
                },
            }
        )
    elif game_status in ("win", "loss"):
        serialized["social_role"] = player.get("social_role", "")
    else:
        serialized["social_role"] = ""
    return serialized


def serialize_players(viewer_id):
    serialized = {}
    for player_id, player in players.items():
        serialized[player_id] = serialize_player(player, viewer_id)
    return serialized


def serialize_learning_insights(viewer_id):
    if game_status not in ("win", "loss"):
        return {"self": None, "players": []}
    player_summaries = [
        learning_insights_for(player)
        for player in sorted(active_players(), key=lambda item: item.get("name", ""))
    ]
    return {
        "self": learning_insights_for(players.get(viewer_id, {}), include_history=True),
        "players": player_summaries,
    }


def public_state(viewer_id):
    difficulty_votes = {difficulty: 0 for difficulty in DIFFICULTIES}
    for player in players.values():
        vote = player.get("difficulty_vote")
        if vote in difficulty_votes:
            difficulty_votes[vote] += 1

    phase = "game_over" if game_status in ("win", "loss") else game_status
    restored_progress = average_system_health() / 100
    return {
        "players": serialize_players(viewer_id),
        "tasks": serialize_tasks(viewer_id),
        "timer": current_timer(),
        "status": game_status,
        "phase": phase,
        "result": game_result,
        "game_over_reason": game_over_reason,
        "minimum_players": MIN_PLAYERS,
        "difficulties": DIFFICULTIES,
        "difficulty_votes": difficulty_votes,
        "selected_difficulty": selected_difficulty,
        "vote_result_seconds": vote_result_seconds,
        "vote_result_tied": vote_result_tied,
        "vote_result_tied_options": vote_result_tied_options,
        "global_progress": restored_progress,
        "score": system_score_summary(),
        "learning_insights": serialize_learning_insights(viewer_id),
        "effects": serialize_effects(viewer_id),
        "map_indicators": {
            "active_tasks": list(tasks),
            "compromised_tasks": [tid for tid, task in tasks.items() if task["compromised"]],
        },
    }


async def send(websocket, message):
    try:
        await websocket.send(json.dumps(message))
    except Exception:
        pass


async def send_error(websocket, message):
    await send(websocket, {"type": "error", "message": message})


def begin_voting_if_ready():
    global game_status
    eligible = [
        player
        for player in active_players()
        if player.get("joined") and player.get("specialty")
    ]
    if (
        game_status == "lobby"
        and len(eligible) >= MIN_PLAYERS
        and len(eligible) == len(active_players())
        and all(player["ready"] for player in eligible)
    ):
        game_status = "voting"
        for player in active_players():
            player["difficulty_vote"] = ""


def set_player_activity(player, activity):
    player["activity"] = activity


def start_game_if_voted():
    global game_status, selected_difficulty, vote_result_started_at
    global vote_result_tied, vote_result_tied_options
    if game_status != "voting":
        return
    voters = active_players()
    if len(voters) < MIN_PLAYERS:
        game_status = "lobby"
        for player in voters:
            player["ready"] = False
            player["difficulty_vote"] = ""
        return
    votes = [player.get("difficulty_vote", "") for player in voters]
    if not votes or any(vote not in DIFFICULTIES for vote in votes):
        return
    counts = {difficulty: votes.count(difficulty) for difficulty in DIFFICULTIES}
    highest_count = max(counts.values())
    winners = [difficulty for difficulty, count in counts.items() if count == highest_count]
    vote_result_tied = len(winners) > 1
    vote_result_tied_options = winners
    selected_difficulty = random.choice(winners)
    vote_result_started_at = now()
    game_status = "vote_results"


def assign_social_roles():
    global roles_assigned
    roster = active_players()
    attacker = random.choice(roster)
    for index, player in enumerate(roster):
        spawn = SPAWN_POINTS[index % len(SPAWN_POINTS)]
        player["x"] = spawn["x"]
        player["y"] = spawn["y"]
        player["social_role"] = ROLE_ATTACKER if player["id"] == attacker["id"] else ROLE_DEFENDER
        player["life_state"] = "alive"
        player["alive"] = True
        player["attack_points"] = 0
        player["attack_bonus"] = 0
        player["ability_cooldowns"] = {}
        player["learning_profile"] = {}
        player["answer_history"] = []
        player["active_challenge"] = None
        player["challenge_cache"] = {}
        player["challenge_cache_epoch"] = player.get("challenge_cache_epoch", 0) + 1
        player["activity"] = ""
    roles_assigned = True


def start_game_after_vote_results():
    global game_started_at, game_status, tasks
    if game_status != "vote_results" or vote_result_started_at is None:
        return
    if now() - vote_result_started_at >= vote_result_seconds:
        tasks = fresh_tasks(selected_difficulty)
        ability_blackouts.clear()
        assign_social_roles()
        game_status = "playing"
        game_started_at = now() + ROLE_REVEAL_GRACE_SECONDS


def reset_state():
    global game_started_at, game_status, selected_difficulty, game_result
    global game_over_reason
    global vote_result_started_at, vote_result_tied, vote_result_tied_options, tasks
    global roles_assigned
    global ability_blackouts
    game_started_at = None
    game_status = "lobby"
    game_result = None
    game_over_reason = None
    selected_difficulty = None
    vote_result_started_at = None
    vote_result_tied = False
    vote_result_tied_options = []
    tasks = fresh_tasks()
    roles_assigned = False
    ability_blackouts.clear()
    for index, player in enumerate(active_players()):
        player["x"] = 100 + (index % 6) * 45
        player["y"] = 600
        player["ready"] = False
        player["difficulty_vote"] = ""
        player["role"] = ""
        player["specialty"] = ""
        player["color"] = (220, 220, 220)
        player["social_role"] = ""
        player["life_state"] = "lobby"
        player["alive"] = False
        player["activity"] = ""
        player["attack_points"] = 0
        player["attack_bonus"] = 0
        player["ability_cooldowns"] = {}
        player["learning_profile"] = {}
        player["answer_history"] = []
        player["active_challenge"] = None
        player["challenge_cache"] = {}
        player["challenge_cache_epoch"] = player.get("challenge_cache_epoch", 0) + 1


def player_can_attempt_task(player):
    role = player.get("social_role")
    life_state = player.get("life_state")
    return role in ACTIVE_SOCIAL_ROLES and life_state == "alive"


def player_attacks_system(player):
    return player.get("social_role") == ROLE_ATTACKER and player.get("life_state") == "alive"


def system_available_for_player(player, task):
    if player_attacks_system(player):
        return task["health"] > 0
    if player.get("social_role") == ROLE_DEFENDER:
        return task["health"] < 100
    return False


def specialty_bonus_applies(player, challenge):
    return rules_specialty_bonus_applies(player.get("specialty"), challenge.get("role"))


def challenge_track(challenge):
    return rules_challenge_track(challenge.get("role"))


def specialty_bonus_info(player, challenge):
    applies = specialty_bonus_applies(player, challenge)
    track = challenge_track(challenge)
    if player_attacks_system(player):
        label = f"+{SPECIALTY_BONUS} attack"
    else:
        label = f"+{SPECIALTY_BONUS} repair"
    return {
        "applies": applies,
        "amount": SPECIALTY_BONUS if applies else 0,
        "label": label if applies else "",
        "track": track,
    }


def impact_payload(kind, terminal_id=None, text="", amount=0, color="yellow"):
    return {
        "kind": kind,
        "terminal_id": terminal_id,
        "text": text,
        "amount": amount,
        "color": color,
    }


def apply_system_success(player, task, challenge):
    role = player.get("social_role")
    bonus_applies = specialty_bonus_applies(player, challenge)
    if role == ROLE_DEFENDER and player.get("life_state") == "alive":
        repair_amount = SYSTEM_HEALTH_DELTA + (SPECIALTY_BONUS if bonus_applies else 0)
        task["health"] += repair_amount
        sync_task_health(task)
        bonus_text = f" Specialty bonus +{SPECIALTY_BONUS}." if bonus_applies else ""
        message = f"{task['system_name']} restored by {repair_amount} to {task['health']}%.{bonus_text}"
        impact = impact_payload(
            "repair",
            task["id"],
            f"+{repair_amount} REPAIR",
            repair_amount,
            "green",
        )
    elif role == ROLE_ATTACKER and player.get("life_state") == "alive":
        player["attack_points"] = player.get("attack_points", 0) + ATTACK_POINT_REWARD
        if bonus_applies:
            player["attack_bonus"] = player.get("attack_bonus", 0) + SPECIALTY_BONUS
        start_task_cooldown_for_player(player, task)
        bonus_text = (
            f" Specialty bonus banked: +{SPECIALTY_BONUS} malware damage."
            if bonus_applies
            else ""
        )
        message = (
            f"Attack Point acquired. "
            f"Balance: {player['attack_points']}.{bonus_text}"
        )
        impact_text = f"+{ATTACK_POINT_REWARD} AP"
        if bonus_applies:
            impact_text += f"  +{SPECIALTY_BONUS} BONUS"
        impact = impact_payload(
            "attack_point",
            task["id"],
            impact_text,
            ATTACK_POINT_REWARD,
            "orange",
        )
    else:
        message = "That system is no longer available to you."
        impact = impact_payload("blocked", task.get("id"), "NO EFFECT", 0, "yellow")
    return message, impact


def set_game_over(status, result, reason="objective"):
    global game_status, game_result, game_over_reason
    if game_status not in ("win", "loss"):
        game_status = status
        game_result = result
        game_over_reason = reason


def finish_match_by_timer():
    result = timed_match_result(tasks, SYSTEM_START_HEALTH)
    status = "win" if result == RESULT_DEFENDERS_WIN else "loss"
    set_game_over(status, result, "timer")


def force_timer_end_for_demo():
    global game_started_at
    if game_status != "playing":
        return False
    game_started_at = now() - GAME_DURATION_SECONDS
    finish_match_by_timer()
    return True


def check_win_loss():
    if game_status != "playing":
        return
    if all_systems_restored():
        set_game_over("win", RESULT_DEFENDERS_WIN, "objective")
    elif all_systems_offline():
        set_game_over("loss", RESULT_ATTACKERS_WIN, "objective")
    elif current_timer() <= 0:
        finish_match_by_timer()


def nearest_defender(attacker, requested_id=None):
    candidates = [
        player
        for player in active_players()
        if player["id"] != attacker["id"]
        and player.get("life_state") == "alive"
        and player.get("social_role") == ROLE_DEFENDER
    ]
    if requested_id:
        candidates = [player for player in candidates if player["id"] == requested_id]
    return min(candidates, key=lambda target: distance(attacker, target), default=None)


def healthy_system_ids():
    return [
        terminal_id
        for terminal_id, task in tasks.items()
        if task["health"] > 50
    ]


async def handle_message(websocket, player_id, message):
    message_type = message.get("type")
    player = players[player_id]

    if message_type == "join":
        if game_status != "lobby":
            await send_error(websocket, "A game is already in progress.")
            return
        name = str(message.get("name", "Player")).strip()[:20]
        player["name"] = name or "Player"
        player["joined"] = True
        begin_voting_if_ready()

    elif message_type == "select_role":
        if game_status != "lobby":
            await send_error(websocket, "Specialties can only be changed in the lobby.")
            return
        specialty = message.get("role")
        if specialty not in ROLE_COLORS:
            await send_error(websocket, "Unknown specialty.")
            return
        if specialty_taken_by_other(player_id, specialty):
            await send_error(websocket, f"{specialty} is already assigned.")
            return
        player["role"] = specialty
        player["specialty"] = specialty
        player["color"] = ROLE_COLORS[specialty]
        player["ready"] = False
        player["difficulty_vote"] = ""
        begin_voting_if_ready()

    elif message_type == "ready":
        if game_status != "lobby":
            return
        if not player["joined"] or not player["specialty"]:
            await send_error(websocket, "Enter a name and choose a specialty first.")
            return
        player["ready"] = bool(message.get("ready", True))
        begin_voting_if_ready()

    elif message_type == "difficulty_vote":
        if game_status != "voting":
            await send_error(websocket, "Difficulty voting is not active.")
            return
        difficulty = str(message.get("difficulty", "")).lower()
        if difficulty not in DIFFICULTIES:
            await send_error(websocket, "Unknown difficulty.")
            return
        player["difficulty_vote"] = difficulty
        start_game_if_voted()

    elif message_type == "move":
        if game_status != "playing":
            return
        try:
            dx = max(-8.0, min(8.0, float(message.get("dx", 0))))
            dy = max(-8.0, min(8.0, float(message.get("dy", 0))))
        except (TypeError, ValueError):
            await send_error(websocket, "Movement must be numeric.")
            return
        move_player(player, dx, dy)

    elif message_type == "interact":
        if game_status != "playing":
            await send_error(websocket, "Interactions are only available during play.")
            return
        terminal_id = message.get("terminal_id")
        if terminal_id not in tasks:
            await send_error(websocket, "Unknown terminal.")
            return
        task = tasks[terminal_id]
        if not player_can_attempt_task(player):
            await send_error(websocket, "Only active defenders and attackers can use infrastructure systems.")
            return
        if not system_available_for_player(player, task):
            if player_attacks_system(player):
                await send_error(websocket, "That system is already at 0%.")
            else:
                await send_error(websocket, "That system is already restored.")
            return
        cooldown_remaining = task_cooldown_for_player(player, task)
        if cooldown_remaining:
            action = "attack" if player_attacks_system(player) else "repair"
            await send_error(websocket, f"That {action} is locked for {cooldown_remaining}s.")
            return
        if not terminal_in_range(player, terminal_id):
            await send_error(websocket, "Move closer to the terminal.")
            return

        challenge = await challenge_for_player(player, terminal_id, task["difficulty"])
        player["active_challenge"] = {
            "terminal_id": terminal_id,
            "challenge": challenge,
            "opened_at": now(),
        }
        role_bonus = bool(challenge["role"] and player["specialty"] == challenge["role"])
        action = "Attack" if player_attacks_system(player) else "Repair"
        bonus_info = specialty_bonus_info(player, challenge)
        set_player_activity(player, "fixing")
        await send(
            websocket,
            {
                "type": "task_opened",
                "kind": "task",
                "terminal_id": terminal_id,
                "title": f"{action} {task['system_name']}",
                "category": challenge["category"],
                "difficulty": challenge["difficulty"],
                "question": challenge["question"],
                "options": challenge["options"],
                "hint": challenge["hint"] if role_bonus else "",
                "role_bonus": role_bonus,
                "specialty_bonus": bonus_info,
            },
        )

    elif message_type == "submit_answer":
        terminal_id = message.get("terminal_id")
        answer = message.get("answer", "")
        set_player_activity(player, "")
        if terminal_id not in tasks:
            await send_error(websocket, "Unknown terminal.")
            return
        task = tasks[terminal_id]
        if not player_can_attempt_task(player):
            await send_error(websocket, "That system is no longer available to you.")
            return
        if not system_available_for_player(player, task):
            if player_attacks_system(player):
                await send_error(websocket, "That system is already at 0%.")
            else:
                await send_error(websocket, "That system is already restored.")
            return
        cooldown_remaining = task_cooldown_for_player(player, task)
        if cooldown_remaining:
            action = "attack" if player_attacks_system(player) else "repair"
            await send_error(websocket, f"That {action} is locked for {cooldown_remaining}s.")
            return
        if not terminal_in_range(player, terminal_id):
            await send_error(websocket, "You moved too far from the terminal.")
            return

        session = player.get("active_challenge") or {}
        if session.get("terminal_id") != terminal_id or not session.get("challenge"):
            await send_error(websocket, "Open the challenge before submitting an answer.")
            return
        challenge = session["challenge"]
        correct = answer_matches(challenge, answer)
        record_learning_result(player, terminal_id, challenge, correct, answer)
        player["active_challenge"] = None
        if correct:
            result_message, impact = apply_system_success(player, task, challenge)
        elif player.get("life_state") == "alive":
            start_task_cooldown_for_player(player, task)
            action = "attack" if player_attacks_system(player) else "repair"
            result_message = f"Wrong answer. {action.title()} locked for {TASK_COOLDOWN_SECONDS}s."
            impact = impact_payload("wrong", terminal_id, "LOCKED", 0, "red")
        else:
            result_message = "That system is no longer available to you."
            impact = impact_payload("blocked", terminal_id, "NO EFFECT", 0, "yellow")
        check_win_loss()
        await send(
            websocket,
            {
                "type": "task_result",
                "terminal_id": terminal_id,
                "correct": correct,
                "message": result_message,
                "correct_answer": challenge["answer"],
                "lesson": challenge.get("lesson", challenge["explanation"]),
                "explanation": challenge["explanation"],
                "relevance": challenge["relevance"],
                "impact": impact,
            },
        )

    elif message_type == "cancel_interaction":
        set_player_activity(player, "")
        player["active_challenge"] = None

    elif message_type == "use_ability":
        if game_status != "playing" or player.get("social_role") != ROLE_ATTACKER or player.get("life_state") != "alive":
            return
        ability = str(message.get("ability", "")).upper()
        if ability not in ATTACKER_ABILITIES:
            await send_error(websocket, "Unknown attacker ability.")
            return
        cost = ATTACKER_ABILITIES[ability]["cost"]
        if player.get("attack_points", 0) < cost:
            await send_error(websocket, f"{ability} needs {cost} Attack Point(s).")
            return
        cooldown_remaining = ability_cooldown_remaining(player, ability)
        if cooldown_remaining:
            await send_error(websocket, f"{ability} cooldown: {cooldown_remaining}s.")
            return

        if ability == "BLACKOUT":
            target = nearest_defender(player, message.get("target_id"))
            if not target:
                await send_error(websocket, "No living defender available for BLACKOUT.")
                return
            ability_blackouts[target["id"]] = now() + BLACKOUT_DURATION_SECONDS
            result_message = f"BLACKOUT launched on {target['name']}."
            impact = impact_payload("blackout", None, "BLACKOUT", 0, "red")

        elif ability == "FALSE_ALERT":
            candidates = healthy_system_ids()
            if not candidates:
                await send_error(websocket, "No healthy system available for FALSE_ALERT.")
                return
            terminal_id = random.choice(candidates)
            task = tasks[terminal_id]
            task["health"] = min(task["health"], 25)
            task["compromised"] = True
            sync_task_health(task)
            check_win_loss()
            result_message = f"FALSE_ALERT forced {task['system_name']} into CRITICAL at {task['health']}%."
            impact = impact_payload("false_alert", terminal_id, "CRITICAL", 0, "red")

        else:
            terminal_id = message.get("terminal_id")
            if terminal_id not in tasks:
                await send_error(websocket, "Choose a valid infrastructure system.")
                return
            task = tasks[terminal_id]
            if task["health"] <= 0:
                await send_error(websocket, "That system is already at 0%.")
                return
            attack_bonus = player.get("attack_bonus", 0)
            malware_damage = MALWARE_DAMAGE + attack_bonus
            task["health"] -= malware_damage
            task["compromised"] = True
            sync_task_health(task)
            check_win_loss()
            player["attack_bonus"] = 0
            result_message = (
                f"MALWARE_INJECTION dealt {malware_damage} damage and reduced {task['system_name']} "
                f"to {task['health']}%."
            )
            impact = impact_payload(
                "malware",
                terminal_id,
                f"-{malware_damage} MALWARE",
                malware_damage,
                "red",
            )

        player["attack_points"] -= cost
        player.setdefault("ability_cooldowns", {})[ability] = now() + ABILITY_COOLDOWN_SECONDS
        await send(
            websocket,
            {
                "type": "ability_result",
                "ability": ability,
                "message": result_message,
                "impact": impact,
            },
        )

    elif message_type == "demo_end_match":
        force_timer_end_for_demo()

    elif message_type == "reset_game":
        reset_state()

    else:
        await send_error(websocket, "Unknown message type.")


async def connection_handler(websocket):
    player_id = uuid.uuid4().hex[:8]
    spawn_index = len(players)
    players[player_id] = {
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
    clients[player_id] = websocket
    await send(websocket, {"type": "welcome", "player_id": player_id})
    print(f"Player {player_id} connected")

    try:
        async for raw_message in websocket:
            try:
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                await send_error(websocket, "Messages must be valid JSON.")
                continue
            await handle_message(websocket, player_id, message)
    except Exception as exc:
        print(f"Player {player_id} connection closed: {exc}")
    finally:
        clients.pop(player_id, None)
        players.pop(player_id, None)
        begin_voting_if_ready()
        start_game_if_voted()
        check_win_loss()
        print(f"Player {player_id} disconnected")


async def broadcast_loop():
    while True:
        result = None
        start_game_after_vote_results()
        check_win_loss()
        if game_status in ("win", "loss") and game_result:
            result = game_result

        if clients:
            recipients = list(clients.values())
            await asyncio.gather(
                *(
                    client.send(
                        json.dumps(
                            {
                                "type": "state_update",
                                "state": public_state(player_id),
                            }
                        )
                    )
                    for player_id, client in list(clients.items())
                ),
                return_exceptions=True,
            )
            if result:
                game_over = json.dumps({"type": "game_over", "result": result})
                await asyncio.gather(
                    *(client.send(game_over) for client in recipients),
                    return_exceptions=True,
                )

        await asyncio.sleep(1 / BROADCAST_HZ)


async def main():
    import websockets

    print(f"BREACH server listening on ws://{SERVER_HOST}:{SERVER_PORT}")
    if OPENAI_API_KEY:
        print(f"Adaptive OpenAI challenges enabled with model {OPENAI_MODEL}")
    else:
        print("Adaptive OpenAI challenges disabled; using local randomized questions")
    async with websockets.serve(connection_handler, SERVER_HOST, SERVER_PORT):
        await broadcast_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
