import json, urllib.request, urllib.parse
UA_BOT = "genealogy-mcp/0.2 (+https://github.com/igormel81/genealogy-mcp)"
UA_BR = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
def get(url, ua=UA_BOT):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:300]
    except Exception as e:
        return "ERR", str(e)
q = urllib.parse.quote
urls = [
 "https://archive.org/services/search/beta/page_production/?user_query=%22%D0%9A%D0%BE%D0%BB%D0%BE%D0%B4%D0%B8%D0%BD%22&service_backend=fts&hits_per_page=3&page_type=collection_details&aggregations=false",
 "https://archive.org/services/search/beta/page_production/?user_query=%22%D0%9A%D0%BE%D0%BB%D0%BE%D0%B4%D0%B8%D0%BD%22&service_backend=fts&hits_per_page=3",
 "https://archive.org/services/search/beta/page_production/?user_query=Kolodin&page_type=collection_search&hits_per_page=3&service_backend=fts",
 "https://archive.org/advancedsearch.php?q=%D0%9A%D0%BE%D0%BB%D0%BE%D0%B4%D0%B8%D0%BD+AND+mediatype%3Atexts&fl[]=identifier&rows=3&output=json",
 "https://be-api.us.archive.org/fts/v1/search?q=Kolodin",
 "https://chroniclingamerica.loc.gov/search/pages/results/?andtext=Lincoln&format=json&rows=2",
 "https://www.loc.gov/collections/chronicling-america/?q=Abraham+Lincoln&fo=json&c=2",
 "https://www.loc.gov/search/?q=Abraham+Lincoln&fa=partof:chronicling+america&fo=json&c=2",
 "https://ru.openlist.wiki/api.php?action=query&list=search&srsearch=%D0%9C%D0%B5%D0%BB%D1%8C%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2&format=json&srlimit=2",
 "https://api.openarch.nl/1.1/records/search.json?name=Jan%20Jansen&number_show=2&period=1850-1860&lang=en",
 "https://api.openarch.nl/1.1/records/search.json?name=Jan%20Jansen%201850-1860&number_show=2&lang=en",
]
for u in urls:
    for ua in (UA_BOT, UA_BR):
        st, body = get(u, ua)
        print("=====", st, "BR" if ua == UA_BR else "BOT", u[:140])
        print(body[:1500].replace("\n", " "))
        if st == 200:
            break
