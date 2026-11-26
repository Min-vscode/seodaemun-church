"""Refresh the bundled homepage from the church's YouTube feed."""
from datetime import date, datetime
from html import escape
from pathlib import Path
import re
import unicodedata
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

CHANNEL = 'UCSON-wrEbmmOZFGYrb4B2Kg'
NS = {'a':'http://www.w3.org/2005/Atom', 'yt':'http://www.youtube.com/xml/schemas/2015', 'm':'http://search.yahoo.com/mrss/'}
page = Path(__file__).resolve().parents[1] / 'index.html'
html = page.read_text()
with urlopen('https://www.youtube.com/feeds/videos.xml?channel_id=' + CHANNEL, timeout=25) as response:
    feed = ET.parse(response)
today = datetime.now(ZoneInfo('Asia/Seoul')).date()
services = []
for entry in feed.findall('a:entry', NS):
    title = unicodedata.normalize('NFC', entry.findtext('a:title', '', NS))
    if not re.search(r'주일\s*오전\s*예배', title):
        continue
    match = re.search(r'(\d{1,2})\s*월\s*(\d{1,2})\s*일', title)
    video = entry.findtext('yt:videoId', '', NS)
    if not match or not re.fullmatch(r'[\w-]{11}', video, re.ASCII) or entry.findtext('yt:channelId', '', NS) != CHANNEL:
        continue
    published = datetime.fromisoformat(entry.findtext('a:published', namespaces=NS)).date()
    month, day = map(int, match.groups())
    candidates = [date(year, month, day) for year in range(published.year-1, published.year+2) if not (month == 2 and day == 29) or year % 4 == 0]
    service = min(candidates, key=lambda d: abs((d-published).days))
    if service.weekday() == 6 and service <= today:
        services.append((service, video, entry.findtext('m:group/m:description', '', NS)))
if not services:
    raise SystemExit('No verified Sunday service in feed')
service, video, description = max(services, key=lambda item: item[0])
current = re.search(r'<!-- sermon (\d{4}-\d{2}-\d{2}) -->', html)
if service < date.fromisoformat(current[1]):
    raise SystemExit('Keeping newer service already on homepage')
fields = dict(re.findall(r'^\s*(성경|본문|제목|설교|설교자)\s*[-:：]\s*(.+?)\s*$', description, re.M))
heading = escape(fields.get('제목', '주일오전예배'))
details = ' · '.join(escape(value) for value in [fields.get('성경') or fields.get('본문'), fields.get('설교자') or fields.get('설교')] if value)
label = f'{service.year}년 {service.month}월 {service.day}일 · 주일오전예배'
section = f'''<!-- sermon {service} -->
        <div><p class="eyebrow">{label}</p><h1 id="welcome">{heading}</h1><p class="hero-copy">{details}</p>
        <div class="actions"><a class="button button-gold" href="https://www.youtube.com/watch?v={video}">유튜브에서 보기</a><a class="button button-outline" href="#worship">예배 안내</a></div></div>
        <iframe class="featured" title="{label}" src="https://www.youtube-nocookie.com/embed/{video}" referrerpolicy="strict-origin-when-cross-origin" allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>
        <!-- /sermon -->'''
updated, count = re.subn(r'<!-- sermon [^>]+ -->.*?<!-- /sermon -->', lambda _: section, html, flags=re.S)
if count != 1:
    raise SystemExit('Homepage marker mismatch')
if updated != html:
    page.write_text(updated)
print(service, video, heading, details)
