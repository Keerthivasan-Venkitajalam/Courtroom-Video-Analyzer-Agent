import urllib.request
import json
data = json.dumps({"query": "What was said about the blue vehicle?", "session_id": "test", "user_id": "test"}).encode("utf-8")
req = urllib.request.Request("http://localhost:8000/api/query", data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as res:
    print(res.read().decode("utf-8"))
