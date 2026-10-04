"""Local word-timed captions, laid out inside an explicitly reserved safe band."""
from bisect import bisect_right
import json
from pathlib import Path
import re

from PIL import ImageDraw
from export_video import font
from reel_design import PANEL, LINE, TEXT, GOLD, TEAL

CAPTION_BOX=(90,1430,930,1590)
CAPTION_SIZE=43


def wrap_words(words,limit=780,size=CAPTION_SIZE):
    lines=[]
    line=[]
    for word in words:
        candidate=line+[word]
        if font(size).getlength(" ".join(w["text"] for w in candidate))>limit:
            if not line:
                raise ValueError("A caption word exceeds the safe width.")
            lines.append(line)
            line=[word]
        else:
            line=candidate
    if line:
        lines.append(line)
    return lines


def caption_groups(transcript):
    words=[]
    corrections={"ecuador":"Ecuador","galápagos.":"Galápagos.","mira":"Mira"}
    for segment in transcript["segments"]:
        for word in segment["words"]:
            text=word["text"].strip()
            text=corrections.get(text,text)
            if text:
                words.append(dict(start=float(word["start"]),end=float(word["end"]),text=text))
    # The script says "qué tan abajo". Recognition omitted the written accent.
    for i,word in enumerate(words[:-1]):
        if word["text"]=="que" and words[i+1]["text"]=="tan":
            word["text"]="qué"
    groups=[]
    group=[]
    for word in words:
        if group and (len(group)>=6 or word["end"]-group[0]["start"]>3.3
                      or word["start"]-group[-1]["end"]>.45 or len(wrap_words(group+[word]))>2):
            groups.append(group)
            group=[]
        group.append(word)
        if re.search(r"[.!?]$",word["text"]):
            groups.append(group)
            group=[]
    if group:
        groups.append(group)
    # Avoid flashing isolated final words such as "registros" or "kilómetros".
    # Rebalance the previous phrase without dropping/reordering any spoken word.
    for i,group in enumerate(groups):
        if i==0 or len(group)!=1 or len(groups[i-1])<4:
            continue
        previous=groups[i-1]
        if re.search(r"[.!?]$",previous[-1]["text"]) or group[0]["start"]-previous[-1]["end"]>.45:
            continue
        for take in [2,1]:
            candidate=previous[-take:]+group
            if len(previous)-take>=3 and candidate[-1]["end"]-candidate[0]["start"]<=3.3 and len(wrap_words(candidate))<=2:
                groups[i]=candidate
                groups[i-1]=previous[:-take]
                break
    result=[]
    for i,group in enumerate(groups):
        next_start=groups[i+1][0]["start"] if i+1<len(groups) else transcript["duration"]
        end=min(next_start,group[-1]["end"]+.24)
        if end<=group[0]["start"] or len(wrap_words(group))>2:
            raise ValueError("Invalid caption duration or layout.")
        result.append(dict(start=group[0]["start"],end=end,words=group,text=" ".join(w["text"] for w in group)))
    return result


def srt_time(second):
    milliseconds=round(second*1000)
    hours,remainder=divmod(milliseconds,3600000)
    minutes,remainder=divmod(remainder,60000)
    seconds,milliseconds=divmod(remainder,1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


class Captions:
    def __init__(self,folder):
        self.folder=Path(folder)
        transcript=json.loads((self.folder/"audio_transcript.json").read_text(encoding="utf-8"))
        self.groups=caption_groups(transcript)
        self.starts=[group["start"] for group in self.groups]
        self.layouts=[wrap_words(group["words"]) for group in self.groups]

    def save(self):
        (self.folder/"subtitulos.json").write_text(json.dumps(dict(method="Local word timestamps; approximately aligned, spelling reviewed against script",
                                                                  box=CAPTION_BOX,groups=self.groups),ensure_ascii=False,indent=2),encoding="utf-8")
        rows=[]
        for i,group in enumerate(self.groups,1):
            lines=wrap_words(group["words"])
            rows.append(f"{i}\n{srt_time(group['start'])} --> {srt_time(group['end'])}\n"+
                        "\n".join(" ".join(word["text"] for word in line) for line in lines)+"\n")
        (self.folder/"subtitulos.srt").write_text("\n".join(rows),encoding="utf-8")

    def current(self,second):
        index=bisect_right(self.starts,second)-1
        return index if index>=0 and second<self.groups[index]["end"] else None

    def draw(self,image,second):
        index=self.current(second)
        if index is None:
            return image
        draw=ImageDraw.Draw(image)
        draw.rounded_rectangle(CAPTION_BOX,radius=20,fill=PANEL,outline=LINE,width=2)
        draw.line((115,1448,175,1448),fill=TEAL,width=3)
        lines=self.layouts[index]
        y=1464 if len(lines)==2 else 1490
        space=draw.textlength(" ",font=font(CAPTION_SIZE))
        for line in lines:
            width=draw.textlength(" ".join(w["text"] for w in line),font=font(CAPTION_SIZE))
            x=510-width/2
            for word in line:
                active=word["start"]<=second<word["end"]
                draw.text((round(x),y),word["text"],font=font(CAPTION_SIZE),fill=GOLD if active else TEXT)
                x+=draw.textlength(word["text"],font=font(CAPTION_SIZE))+space
            y+=54
        return image
