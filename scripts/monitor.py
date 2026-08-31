import json
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
HISTORY = DATA / "history.json"
STATUS = DATA / "status.json"


def get(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "IPSCMC-Status/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read())


now = datetime.now(timezone.utc)

# -------------------------
# Minecraft
# -------------------------

online = False
players = 0
max_players = 0
latency = None
motd = ""
version = ""

try:
    d = get(
        "https://api.mcstatus.io/v2/status/java/"
        "play.ipscmc.fun:19145?query=false"
    )

    online = bool(d.get("online", False))

    if online:
        player_data = d.get("players", {}) or {}

        players = player_data.get("online", 0) or 0
        max_players = player_data.get("max", 0) or 0

        motd_data = d.get("motd", {}) or {}
        motd = (
            motd_data.get("clean")
            or motd_data.get("raw")
            or ""
        )

        version_data = d.get("version", {}) or {}
        version = version_data.get("name", "") or ""

        # mcstatus.io's latency is measured from their infrastructure.
        latency = d.get("latency")

except Exception as e:
    print("Minecraft check failed:", e)


# -------------------------
# Discord
# -------------------------

discord_members = None
discord_online = None

try:
    d = get(
        "https://discord.com/api/v10/invites/"
        "ipscmc?with_counts=true"
    )

    guild = d.get("guild", {}) or {}

    discord_members = guild.get("approximate_member_count")
    discord_online = guild.get("approximate_presence_count")

except Exception as e:
    print("Discord check failed:", e)


# -------------------------
# Uptime history
# -------------------------

if HISTORY.exists():
    try:
        history = json.loads(HISTORY.read_text())
    except Exception:
        history = []
else:
    history = []

history.append({
    "ts": now.isoformat(),
    "online": online
})

cutoff = now - timedelta(days=31)

history = [
    x for x in history
    if datetime.fromisoformat(x["ts"]) >= cutoff
]


def uptime(days):
    start = now - timedelta(days=days)

    rows = [
        x for x in history
        if datetime.fromisoformat(x["ts"]) >= start
    ]

    if not rows:
        return None

    percentage = (
        100
        * sum(1 for x in rows if x["online"])
        / len(rows)
    )

    return round(percentage, 2)


# -------------------------
# Save status
# -------------------------

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
        "30d": uptime(30)
    },

    "discord": {
        "members": discord_members,
        "online": discord_online
    }
}

DATA.mkdir(exist_ok=True)

HISTORY.write_text(
    json.dumps(history, indent=2)
)

STATUS.write_text(
    json.dumps(status, indent=2)
)

print(json.dumps(status, indent=2))
