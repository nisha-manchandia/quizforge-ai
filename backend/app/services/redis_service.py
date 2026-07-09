import redis
from app.config import settings
from typing import Optional

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True
)


def get_redis():
    return redis_client


def update_leaderboard(room_code: str, nickname: str, score: int):
    key = f"leaderboard:{room_code}"
    redis_client.zadd(key, {nickname: score})
    redis_client.expire(key, 86400)


def get_leaderboard(room_code: str, top_n: int = 10) -> list:
    key = f"leaderboard:{room_code}"
    results = redis_client.zrevrange(key, 0, top_n - 1, withscores=True)
    leaderboard = []
    for rank, (nickname, score) in enumerate(results, start=1):
        leaderboard.append({
            "rank": rank,
            "nickname": nickname,
            "score": int(score)
        })
    return leaderboard


def increment_score(room_code: str, nickname: str, points: int) -> float:
    key = f"leaderboard:{room_code}"
    new_score = redis_client.zincrby(key, points, nickname)
    redis_client.expire(key, 86400)
    return new_score


def set_room_state(room_code: str, state: dict):
    key = f"room:{room_code}"
    redis_client.hset(key, mapping=state)
    redis_client.expire(key, 86400)


def get_room_state(room_code: str) -> Optional[dict]:
    key = f"room:{room_code}"
    state = redis_client.hgetall(key)
    return state if state else None


def update_room_state(room_code: str, field: str, value: str):
    key = f"room:{room_code}"
    redis_client.hset(key, field, value)


def set_player_state(room_code: str, nickname: str, state: dict):
    key = f"player:{room_code}:{nickname}"
    redis_client.hset(key, mapping=state)
    redis_client.expire(key, 86400)


def get_player_state(room_code: str, nickname: str) -> Optional[dict]:
    key = f"player:{room_code}:{nickname}"
    state = redis_client.hgetall(key)
    return state if state else None


def increment_player_field(room_code: str, nickname: str, field: str, amount: int = 1):
    key = f"player:{room_code}:{nickname}"
    redis_client.hincrby(key, field, amount)


def record_answer(room_code: str, question_index: int, nickname: str) -> bool:
    key = f"answered:{room_code}:{question_index}:{nickname}"
    result = redis_client.set(key, "1", nx=True, ex=3600)
    return result is not None


def add_active_player(room_code: str, nickname: str):
    key = f"active_players:{room_code}"
    redis_client.sadd(key, nickname)
    redis_client.expire(key, 86400)


def get_active_players(room_code: str) -> set:
    key = f"active_players:{room_code}"
    return redis_client.smembers(key)


def remove_active_player(room_code: str, nickname: str):
    key = f"active_players:{room_code}"
    redis_client.srem(key, nickname)


def cleanup_room(room_code: str):
    keys_to_delete = [
        f"leaderboard:{room_code}",
        f"room:{room_code}",
        f"active_players:{room_code}"
    ]
    for key in keys_to_delete:
        redis_client.delete(key)