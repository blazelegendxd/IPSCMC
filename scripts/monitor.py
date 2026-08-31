import json
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HISTORY = DATA / "history.json"
STATUS = DATA / "status.json"

MINECRAFT_HOST = "play.ipsmc.fun:19145"
DISCORD_INVITE = "ipscmc"


def get_json(url, timeout=20):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "IPSCMC-Status/2.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


now = datetime.now(timezone.utc)

# Minecraft status
online = False
players = 0
max_players = 0
latency = None
motd = ""
version = ""

try:
    data = get_json(
        "https://api.mcstatus.io/v2/status/java/"
        + MINECRAFT_HOST
        + "?query=false"
    )

    online = bool(data.get("online", False))
    player_data = data.get("players") or {}
    players = int(player_data.get("online") or 0)
    max_players = int(player_data.get("max") or 0)

    motd_data = data.get("motd") or {}
    motd = (
        motd_data.get("clean")
        or motd_data.get("raw")
        or ""
    )

    version_data = data.get("version") or {}
    version = version_data.get("name") or ""
    latency = data.get("latency")

except Exception as error:
    print("Minecraft check failed:", repr(error))


# Discord invite counts
discord_members = None
discord_online = None

try:
    data = get_json(
        "https://discord.com/api/v10/invites/"
        + DISCORD_INVITE
        + "?with_counts=true"
    )

    guild = data.get("guild") or {}
    discord_members = guild.get("approximate_member_count")
    discord_online = guild.get("approximate_presence_count")

except Exception as error:
    print("Discord check failed:", repr(error))


# Load and update uptime history
if HISTORY.exists():
    try:
        history = json.loads(HISTORY.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            history = []
    except Exception:
        history = []
else:
    history = []

history.append({
    "ts": now.isoformat(),
    "online": online,
})

cutoff = now - timedelta(days=31)
clean_history = []

for item in history:
    try:
        timestamp = datetime.fromisoformat(item["ts"])
        if timestamp >= cutoff:
            clean_history.append(item)
    except (KeyError, TypeError, ValueError):
        continue

history = clean_history


def uptime(days):
    start = now - timedelta(days=days)
    rows = []

    for item in history:
        try:
            timestamp = datetime.fromisoformat(item["ts"])
            if timestamp >= start:
                rows.append(item)
        except (KeyError, TypeError, ValueError):
            continue

    if not rows:
        return None

    return round(
        100 * sum(1 for item in rows if item.get("online") is True) / len(rows),
        2,
    )


status = {
    "lastChecked": now.isoformat(),
    "online": online,
    "players": players,
    "maxPlayers": max_players,
    "latency": latency,
    "motd": motd,
    "version": version,
    "uptime": {
        "24h": uptime(1),
        "7d": uptime(7),
        "30d": uptime(30),
    },
    "discord": {
        "members": discord_members,
        "online": discord_online,
    },
}

DATA.mkdir(parents=True, exist_ok=True)
HISTORY.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

print(json.dumps(status, indent=2))
