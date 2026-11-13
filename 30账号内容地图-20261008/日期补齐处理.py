import json,pathlib,re,datetime,csv,hashlib
P=pathlib.Path(__file__).resolve().parent
S=pathlib.Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
scope=json.loads((P.parents[1]/'流程协作/01-研究热点与选题/发布时间补齐范围-20261009.json').read_text())
rows=json.loads((P/'近期内容表.json').read_text()); IDS=set(scope['video_ids']); UNKNOWN={x['video_id'] for x in rows if x['published_at']=='UNKNOWN'}
BASE=P/'日期补齐基线-20261009.json'
if not BASE.exists():BASE.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert {x['video_id'] for x in rows}==IDS and len(rows)==237
date_re=re.compile(r'(?<!\d)(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})(?:[ T]+\d{1,2}:\d{2}(?::\d{2})?)?')
found=[]
def candidate(vid,raw,receipt,field,url=None):
 if vid not in IDS or not isinstance(raw,str):return
 m=date_re.search(raw)
 if not m:return
 value=m.group(0).replace('/','-').replace('.','-').replace('T',' ')
 try:datetime.datetime.fromisoformat(value)
 except ValueError:return
 found.append({'video_id':vid,'url':url or 'https://www.douyin.com/video/'+vid,'raw_date_text':raw,'published_at':value,'precision':'minute' if ':' in value else 'day','timezone':'UNKNOWN: page did not explicitly label timezone','checked_at_utc':receipt.get('timestamp'),'receipt':receipt,'source_field':field})
def walk(o,receipt):
 if isinstance(o,list):
  for x in o:walk(x,receipt)
 elif isinstance(o,dict):
  vid=str(o.get('video_id',o.get('id',''))); url=o.get('url',o.get('href',''))
  if isinstance(url,str) and '/video/' in url:vid=url.split('/video/')[-1].split('?')[0]
  for key in ['published','published_at','publishedAt','publish_time','publication_date']:
   if key in o:candidate(vid,o[key],receipt,key,url)
  if vid in IDS:
   for key in ['snapshot','text','body','metadata','ax','page']:
    if isinstance(o.get(key),str):
     pub=re.search(r'发布时间[：:]?\s*(20\d{2}-\d{2}-\d{2}(?: \d{2}:\d{2})?)',o[key])
     if pub:candidate(vid,pub.group(0),receipt,key+' paired with exact video URL',url)
  for key,x in o.items():
   if isinstance(x,(list,dict)):walk(x,receipt)
def text_objects(text,receipt):
 dec=json.JSONDecoder()
 for m in re.finditer(r'[\[{]',text):
  try:o,_=dec.raw_decode(text[m.start():])
  except Exception:continue
  walk(o,receipt)
lines=S.read_text().splitlines()
browser_calls={}
for line in lines:
 if 'mcp__cua_repl' not in line:continue
 try:e=json.loads(line);p=e.get('payload',{})
 except Exception:continue
 if p.get('type')=='function_call' and p.get('namespace')=='mcp__cua_repl':browser_calls[p['call_id']]=p
for i,line in enumerate(lines,1):
 if not any(vid in line for vid in IDS):continue
 try:e=json.loads(line)
 except Exception:continue
 payload=e.get('payload',{}); item=payload.get('item',{})
 if e.get('type')=='event_msg' and item.get('type')=='McpToolCall' and item.get('server')=='cua_repl':
  blocks=item.get('result',{}).get('content',[]);call_id=item.get('id');tool=item.get('server')+'.'+item.get('tool')
 elif e.get('type')=='response_item' and payload.get('type')=='function_call_output' and payload.get('call_id') in browser_calls:
  blocks=payload.get('output',[]);call_id=payload.get('call_id');tool='mcp__cua_repl.js'
  if isinstance(blocks,str):blocks=[{'type':'text','text':blocks}]
 else:continue
 receipt={'session':str(S),'line':i,'call_id':call_id,'timestamp':e.get('timestamp'),'tool':tool}
 for c in blocks:
  if c.get('type') not in ['text','input_text']:continue
  text=c['text'];text_objects(text,receipt)
  # AX tool state explicitly pairs current video URL with the visible publish date.
  for part in re.split(r'(?=Browser tab:)',text):
   header=re.search(r'Browser tab:.*?URL: "https://www\.douyin\.com/video/(\d+)"',part)
   if header:
    pub=re.search(r'发布时间[：:]?\s*(20\d{2}-\d{2}-\d{2}(?: \d{2}:\d{2})?)',part)
    if pub:candidate(header.group(1),pub.group(0),receipt,'AX current-page URL and 发布时间')
# De-duplicate receipts; never derive a date from an ID.
uniq={}
for x in found:uniq[(x['video_id'],x['published_at'],x['receipt']['line'])]=x
found=list(uniq.values())
(P/'日期旧原始回执恢复-20261009.json').write_text(json.dumps(found,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
known={x['video_id'] for x in found}; recovered=UNKNOWN&known
print(json.dumps({'legacy_date_receipts':len(found),'scope_ids_with_receipts':len(IDS&known),'new_unknown_ids_recoverable':len(recovered),'recoverable_ids':sorted(recovered)},ensure_ascii=False))
