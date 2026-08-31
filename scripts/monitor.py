import json,urllib.request
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"; H=DATA/"history.json"
def get(u):
 r=urllib.request.Request(u,headers={"User-Agent":"IPSCMC-Status/1.0"})
 with urllib.request.urlopen(r,timeout=12) as x:return json.loads(x.read())
now=datetime.now(timezone.utc)
try:
 d=get("https://api.mcstatus.io/v2/status/java/play.ipsmc.fun:19145?query=false"); online=bool(d.get("online")); latency=d.get("latency"); players=(d.get("players") or {}).get("online",0)
except: online=False;latency=None;players=0
try:
 d=get("https://discord.com/api/v10/invites/ipscmc?with_counts=true");g=d.get("guild") or {};members=g.get("approximate_member_count");online_dc=g.get("approximate_presence_count")
except: members=online_dc=None
hist=json.loads(H.read_text()) if H.exists() else [];hist.append({"ts":now.isoformat(),"online":online});cut=now-timedelta(days=31);hist=[x for x in hist if datetime.fromisoformat(x["ts"])>=cut]
def pct(days):
 rows=[x for x in hist if datetime.fromisoformat(x["ts"])>=now-timedelta(days=days)]
 return f'{100*sum(x["online"] for x in rows)/len(rows):.2f}%' if rows else "—"
status={"lastChecked":now.isoformat(),"uptime":{"24h":pct(1),"7d":pct(7),"30d":pct(30)},"online":online,"latency":latency,"players":players,"discord":{"members":members,"online":online_dc}}
H.write_text(json.dumps(hist,indent=2));(DATA/"status.json").write_text(json.dumps(status,indent=2));print(json.dumps(status,indent=2))