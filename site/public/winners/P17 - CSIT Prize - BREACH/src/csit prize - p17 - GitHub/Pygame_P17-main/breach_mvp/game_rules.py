"""Pure game-rule helpers for infrastructure health and scoring."""

from protocol import RESULT_ATTACKERS_WIN, RESULT_DEFENDERS_WIN

SYSTEM_STATUS_RESTORED = "RESTORED"
SYSTEM_STATUS_STABLE = "STABLE"
SYSTEM_STATUS_DEGRADED = "DEGRADED"
SYSTEM_STATUS_CRITICAL = "CRITICAL"
SYSTEM_STATUS_OFFLINE = "OFFLINE"


def clamp_health(value):
    return max(0, min(100, int(value)))


def system_status(health):
    if health >= 100:
        return SYSTEM_STATUS_RESTORED
    if health <= 0:
        return SYSTEM_STATUS_OFFLINE
    if health <= 25:
        return SYSTEM_STATUS_CRITICAL
    if health <= 50:
        return SYSTEM_STATUS_DEGRADED
    return SYSTEM_STATUS_STABLE


def sync_system_task(task):
    task["health"] = clamp_health(task["health"])
    task["status"] = system_status(task["health"])
    task["completed"] = task["health"] >= 100
    if task["health"] >= 100:
        task["compromised"] = False


def average_system_health(tasks):
    if not tasks:
        return 0
    return sum(task["health"] for task in tasks.values()) / len(tasks)


def system_score_summary(tasks, baseline_health):
    if not tasks:
        return {
            "baseline_health": baseline_health,
            "average_health": 0,
            "net_health": -baseline_health,
            "defender_score": 0,
            "attacker_score": baseline_health,
        }
    average_health = round(average_system_health(tasks), 1)
    net_health = round(average_health - baseline_health, 1)
    return {
        "baseline_health": baseline_health,
        "average_health": average_health,
        "net_health": net_health,
        "defender_score": round(max(0, net_health), 1),
        "attacker_score": round(max(0, -net_health), 1),
    }


def all_systems_restored(tasks):
    return bool(tasks) and all(task["health"] >= 100 for task in tasks.values())


def all_systems_offline(tasks):
    return bool(tasks) and all(task["health"] <= 0 for task in tasks.values())


def timed_match_result(tasks, baseline_health):
    score = system_score_summary(tasks, baseline_health)
    if score["net_health"] >= 0:
        return RESULT_DEFENDERS_WIN
    return RESULT_ATTACKERS_WIN


def specialty_bonus_applies(player_specialty, challenge_role):
    return bool(challenge_role and player_specialty == challenge_role)


def challenge_track(challenge_role):
    tracks = {
        "Python Engineer": "programming",
        "Cryptographer": "pwn",
        "Network Analyst": "reverse engineering",
    }
    return tracks.get(challenge_role, "specialty")
