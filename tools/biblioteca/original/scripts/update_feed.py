#!/usr/bin/env python3
"""Update GeoPulso from OpenAlex without generating scientific claims."""
from __future__ import annotations
import datetime as dt
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data"/"posts.json"
TOPICS={
    "Tectónica activa":"active tectonics fault paleoseismology",
    "Geología minera":"economic geology mineral exploration ore deposit",
    "Volcanología":"volcanology volcanic eruption magma",
    "Geomorfología":"geomorphology landscape evolution remote sensing",
    "Geofísica":"seismic tomography geophysics subsurface",
    "Hidrogeología":"hydrogeology groundwater aquifer",
}
MAX_PER_TOPIC=5
USER_AGENT="GeoPulso/1.0 (https://github.com/henryconteron/feed-geologico)"

def request_json(url:str)->dict:
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.load(response)

def abstract_from_index(index:dict|None)->str:
    if not index:return ""
    positioned=[]
    for word,positions in index.items():
        positioned.extend((position,word) for position in positions)
    return " ".join(word for _,word in sorted(positioned))[:650]

def clean_doi(raw:str|None)->str:
    if not raw:return ""
    return re.sub(r"^https?://(dx\.)?doi\.org/","",raw.strip(),flags=re.I).lower()

def fetch_topic(topic:str,query:str)->list[dict]:
    since=(dt.date.today()-dt.timedelta(days=120)).isoformat()
    params=urllib.parse.urlencode({
        "search":query,
        "filter":f"from_publication_date:{since},has_doi:true,type:article",
        "sort":"publication_date:desc",
        "per-page":MAX_PER_TOPIC,
        "select":"id,doi,title,publication_date,authorships,primary_location,abstract_inverted_index",
    })
    payload=request_json("https://api.openalex.org/works?"+params)
    posts=[]
    for work in payload.get("results",[]):
        doi=clean_doi(work.get("doi"))
        if not doi or not work.get("title") or not work.get("publication_date"):continue
        authors=[a.get("author",{}).get("display_name","") for a in work.get("authorships",[])][:12]
        location=work.get("primary_location") or {}
        source=(location.get("source") or {}).get("display_name") or "Fuente académica"
        posts.append({
            "id":f"doi:{doi}","title":work["title"].strip(),"authors":[a for a in authors if a],
            "published":work["publication_date"],"topic":topic,"venue":source,
            "abstract_original":abstract_from_index(work.get("abstract_inverted_index")),
            "abstract_language":"source", "explanation_es":"", "application":"",
            "url":f"https://doi.org/{doi}","doi":doi,"status":"automatic","source":"OpenAlex",
        })
    return posts

def main()->None:
    current=json.loads(CATALOG.read_text(encoding="utf-8")) if CATALOG.exists() else {"posts":[]}
    existing={post["id"]:post for post in current.get("posts",[]) if post.get("source")!="demo"}
    added=0
    for topic,query in TOPICS.items():
        try:
            for post in fetch_topic(topic,query):
                if post["id"] not in existing:added+=1
                existing[post["id"]]=post
            time.sleep(1)
        except Exception as error:
            print(f"Warning: {topic}: {error}")
    posts=sorted(existing.values(),key=lambda item:(item.get("published",""),item.get("title","")),reverse=True)[:180]
    output={"updated":dt.date.today().isoformat(),"posts":posts}
    CATALOG.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Catalog: {len(posts)} records; {added} new")

if __name__=="__main__":main()
