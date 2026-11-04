import requests

urls = [
    'https://media26.bechirot.gov.il/files/expc.csv',
    'https://votes26.bechirot.gov.il/cityresults',
    'https://data.gov.il/api/3/action/package_show?id=votes-knesset',
]
for url in urls:
    try:
        r = requests.get(url, timeout=12)
        print(url, r.status_code, len(r.content), r.headers.get('content-type'), repr(r.text[:200]))
    except requests.RequestException as e:
        print(url, type(e).__name__, str(e)[:180])
