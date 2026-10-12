import json, urllib.request
UA = "genealogy-mcp/0.2 (+https://github.com/igormel81/genealogy-mcp)"
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())
d = get("https://archive.org/services/search/beta/page_production/?user_query=%22%D0%9F%D0%B0%D0%BC%D1%8F%D1%82%D0%BD%D0%B0%D1%8F%20%D0%BA%D0%BD%D0%B8%D0%B6%D0%BA%D0%B0%20%D0%A2%D1%83%D0%BB%D1%8C%D1%81%D0%BA%D0%BE%D0%B9%22&service_backend=fts&hits_per_page=2")
print("KEYS", list(d.keys()))
resp = d.get("response", {})
print("RESP KEYS", list(resp.keys()))
body = resp.get("body", {})
print("BODY KEYS", list(body.keys()))
print(json.dumps(body.get("hits", body), ensure_ascii=False)[:3000])
d = get("https://be-api.us.archive.org/fts/v1/search?q=%22%D0%9F%D0%B0%D0%BC%D1%8F%D1%82%D0%BD%D0%B0%D1%8F%20%D0%BA%D0%BD%D0%B8%D0%B6%D0%BA%D0%B0%22&size=2")
print("BE KEYS", list(d.keys()))
print(json.dumps(d.get("hits", {}), ensure_ascii=False)[:2500])
