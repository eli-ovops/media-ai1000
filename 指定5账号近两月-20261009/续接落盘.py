import pathlib,json,re,shutil,hashlib
P=pathlib.Path(__file__).resolve().parent
S=pathlib.Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
records=[];incomplete=[]
markers=['AI_READ_BATCH ','AI_MEDIA_RECEIPT ','WINDOW_DATE ','PROFILE_RECHECK ']
for n,line in enumerate(S.read_text().splitlines(),1):
 if not any(m in line for m in markers):continue
 try:e=json.loads(line)
 except json.JSONDecodeError:
  incomplete.append(n);continue
 item=e.get('payload',{}).get('item',{})
 if e.get('type')!='event_msg' or item.get('type')!='McpToolCall':continue
 for c in item.get('result',{}).get('content',[]):
  if c.get('type')!='text':continue
  for marker in markers:
   for m in re.finditer(marker,c['text']):
    try:v,_=json.JSONDecoder().raw_decode(c['text'][m.end():])
    except Exception:continue
    for x in (v if isinstance(v,list) else [v]):records.append({'kind':marker.strip(),'data':x,'receipt':{'session':str(S),'line':n,'call_id':item.get('id'),'timestamp':e.get('timestamp')}})
(P/'续接原始回执.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
(P/'原始日志读取限制.json').write_text(json.dumps({'incomplete_jsonl_lines':incomplete,'interpretation':'session log may still be appending; incomplete lines are not accepted evidence'},ensure_ascii=False,indent=2)+'\n')
allowed=json.loads((P/'allowed-files.json').read_text());new=[]
for r in records:
 v=r['data']
 if r['kind']=='AI_MEDIA_RECEIPT' and v.get('path'):
  vid=re.search(r'/video/(\d+)',v['url']).group(1);src=pathlib.Path(v['path']);dst=P/'media'/f'{vid}.mp4'
  if not dst.exists():
   exports={json.loads(f.read_text())['source_export'] for f in P.glob('evidence/*/source.json')}
   current=sum(f.stat().st_size for f in P.parent.rglob('*') if f.is_file())+sum(pathlib.Path(f).stat().st_size for f in exports if pathlib.Path(f).exists())
   if current+src.stat().st_size*2>3*1024**3:
    (P/'缓存预算阻断.json').write_text(json.dumps({'current_bytes':current,'next_source':str(src),'next_source_bytes':src.stat().st_size,'copy_and_export_additional_bytes':src.stat().st_size*2,'limit_bytes':3*1024**3,'copied':False,'deleted':False},ensure_ascii=False,indent=2))
    raise RuntimeError('Cache budget prevents next source copy; exact receipt saved')
   shutil.copy2(src,dst);new.append(vid)
  if str(dst) not in allowed:allowed.append(str(dst))
  ep=P/'evidence'/vid;ep.mkdir(parents=True,exist_ok=True)
  if not (ep/'source.json').exists():(ep/'source.json').write_text(json.dumps({'url':v['url'],'video_id':vid,'source_export':str(src),'local_media':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'receipt':r['receipt']},ensure_ascii=False,indent=2))
(P/'allowed-files.json').write_text(json.dumps(allowed,ensure_ascii=False,indent=2)+'\n')
accounts=json.loads((P/'5账号身份映射.json').read_text())
for rec in records:
 if rec['kind']!='PROFILE_RECHECK':continue
 v=rec['data'];a=next((a for a in accounts if a['short']==v['short']),None)
 if not a or not v.get('name'):continue
 if a.get('error'):
  a.setdefault('historical_errors',[])
  if a['error'] not in a['historical_errors']:a['historical_errors'].append(a['error'])
  a.pop('error',None)
 a.update(name=v['name'],homepage=v['url'],status='IDENTITY_VERIFIED_PARTIAL_DIRECTORY',latest_receipt=rec['receipt'])
 m=re.search(r'抖音号[：:]\s*([^\s]+)',v.get('text',''))
 if m:a['douyin_id']=m.group(1)
 m=re.search(r'作品\s*(\d+)',v.get('text',''))
 if m:a['profile_reported_works']=int(m.group(1))
 f=P/a['directory'];rows=json.loads(f.read_text());by={x['video_id']:x for x in rows}
 for x in v.get('videos',[]):
  vid=re.search(r'/(?:video|note)/(\d+)',x['url']).group(1)
  if vid not in by:by[vid]={'video_id':vid,'url':x['url'],'directory_text':x['text'],'published_at':'UNKNOWN','window':'UNKNOWN','ai_relevance':'TITLE_SCREEN_ONLY','content_read':'NOT_READ','receipt':rec['receipt']}
 f.write_text(json.dumps(list(by.values()),ensure_ascii=False,indent=2)+'\n');a['visible_directory_rows']=len(by)
 a['window_complete']=False
(P/'5账号身份映射.json').write_text(json.dumps(accounts,ensure_ascii=False,indent=2)+'\n')
for f in P.glob('账号*-可见目录.json'):
 rows=json.loads(f.read_text());byid={r['video_id']:r for r in rows}
 for rec in records:
  v=rec['data'];vid=v.get('requested_id');row=byid.get(vid)
  if not row:continue
  if rec['kind']=='AI_READ_BATCH':row['latest_page_read']=rec
  if rec['kind']=='WINDOW_DATE':row['latest_date_attempt']=rec
  if rec['kind']=='AI_MEDIA_RECEIPT':row['latest_media_attempt']=rec
  if v.get('video_id')==vid and v.get('raw_date_text'):
   m=re.search(r'20\d{2}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?',v['raw_date_text'])
   if m:row.update(published_at=m.group(0),raw_date_text=v['raw_date_text'],date_receipt=rec['receipt'],window='IN_WINDOW' if '2026-08-09'<=m.group(0)[:10]<='2026-10-09' else 'OUTSIDE_WINDOW')
 for row in rows:
  if row['published_at']!='UNKNOWN':row.update(date_precision='minute' if ':' in row['published_at'] else 'day',timezone='UNKNOWN: page does not explicitly label timezone')
 f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('NEW_MEDIA',new)
