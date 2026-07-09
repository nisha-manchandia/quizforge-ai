import sys
sys.path.insert(0, '.')
from app.services.redis_service import (
    update_leaderboard,
    increment_score,
    get_leaderboard
)

room = 'TEST01'

update_leaderboard(room, 'Nisha', 0)
update_leaderboard(room, 'Arjun', 0)
update_leaderboard(room, 'Priya', 0)

increment_score(room, 'Nisha', 1450)
increment_score(room, 'Arjun', 1200)
increment_score(room, 'Priya', 980)

leaderboard = get_leaderboard(room)
print('Live Leaderboard:')
for entry in leaderboard:
    print(f"  {entry['rank']}. {entry['nickname']} - {entry['score']} pts")

print('Redis leaderboard test SUCCESS')