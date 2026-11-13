import json,pathlib,re,csv,datetime
P=pathlib.Path(__file__).resolve().parent
S=pathlib.Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
rows=json.loads((P/'近期内容表.json').read_text()); base=json.loads((P/'日期补齐基线-20261009.json').read_text()); ids={x['video_id'] for x in base}; assert len(ids)==237 and {x['video_id'] for x in rows}==ids
F=P/'日期本轮原始回执-20261009.json'; receipts=json.loads(F.read_text()) if F.exists() else []
seen={(x['requested_id'],x['receipt']['line']) for x in receipts}
for n,line in enumerate(S.read_text().splitlines(),1):
 if 'PUB_DATE_BATCH ' not in line:continue
 try:e=json.loads(line)
 except json.JSONDecodeError:continue
 p=e.get('payload',{}); item=p.get('item',{})
 if e.get('type')!='event_msg' or item.get('type')!='McpToolCall':continue
 for c in item.get('result',{}).get('content',[]):
  if c.get('type')!='text':continue
  text=c['text']
  for m in re.finditer('PUB_DATE_BATCH ',text):
   try:batch,_=json.JSONDecoder().raw_decode(text[m.end():])
   except Exception:continue
   for x in batch:
    if x.get('requested_id') not in ids or (x['requested_id'],n) in seen:continue
    x['receipt']={'session':str(S),'line':n,'call_id':item.get('id'),'timestamp':e.get('timestamp'),'tool':'mcp__cua_repl.js'}
    x['checked_at_utc']=e.get('timestamp');receipts.append(x);seen.add((x['requested_id'],n))
F.write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
legacy=json.loads((P/'日期旧原始回执恢复-20261009.json').read_text()); candidates=[]
for r in receipts:
 if r.get('video_id')!=r['requested_id'] or not r.get('raw_date_text'):continue
 m=re.search(r'20\d{2}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?',r['raw_date_text'])
 if not m:continue
 pub=m.group(0)
 try:datetime.datetime.fromisoformat(pub)
 except Exception:continue
 candidates.append({'video_id':r['video_id'],'url':r['url'],'published_at':pub,'raw_date_text':r['raw_date_text'],'precision':'minute' if ':' in pub else 'day','timezone':'UNKNOWN: page did not explicitly label timezone','receipt':r['receipt'],'checked_at_utc':r['checked_at_utc'],'source_field':'visible 发布时间 on exact video page'})
candidates=legacy+candidates
byid={}
for r in candidates:byid.setdefault(r['video_id'],[]).append(r)
conflicts=[]; new=0
for row in rows:
 vid=row['video_id']; choices=byid.get(vid,[]); values={r['published_at'] for r in choices}
 if len(values)>1:
  conflicts.append({'video_id':vid,'values':sorted(values),'receipts':choices});continue
 if row['published_at']=='UNKNOWN' and choices:
  ev=choices[-1];row['published_at']=ev['published_at'];row['date_source']=ev['receipt'];row['publication_date_evidence']=ev;new+=1
 elif choices and row['published_at']!='UNKNOWN' and row['published_at'] not in values:
  conflicts.append({'video_id':vid,'existing':row['published_at'],'receipts':choices})
 if row['published_at']!='UNKNOWN' and 'publication_date_evidence' not in row:
  row['publication_date_evidence']={'video_id':vid,'published_at':row['published_at'],'raw_date_text':row['published_at'],'precision':'minute' if ':' in row['published_at'] else 'day','timezone':'UNKNOWN: accepted source did not explicitly label timezone','source_reference':row.get('date_source'),'source_field':'existing accepted published_at source; not re-read','accepted_at_dispatch':True}
 if row['published_at']!='UNKNOWN':
  row['window']='近90天（2026-10-09研究日）' if row['published_at'][:10]>='2026-07-11' else '已扩到90天以前（2026-10-09研究日）'
allowed={'published_at','window','date_source','publication_date_evidence'}; original={x['video_id']:x for x in base}
assert all({k:v for k,v in r.items() if k not in allowed}=={k:v for k,v in original[r['video_id']].items() if k not in allowed} for r in rows)
(P/'近期内容表.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (P/'近期内容表.csv').open('w',encoding='utf-8-sig',newline='') as f:
 keys=list(dict.fromkeys(k for r in rows for k in r));wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader()
 for r in rows:wr.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
(P/'日期冲突-20261009.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
unknown=[r['video_id'] for r in rows if r['published_at']=='UNKNOWN'];blocked=[]
for vid in unknown:
 attempts=[r for r in receipts if r['requested_id']==vid]
 blocked.append({'video_id':vid,'status':'ATTEMPTED_UNRESOLVED' if attempts else 'NOT_ATTEMPTED_YET','attempts':attempts})
(P/'日期剩余与阻断-20261009.json').write_text(json.dumps(blocked,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
status={'scope':'publication_dates_only','date':'2026-10-09','total':237,'known':237-len(unknown),'unknown':len(unknown),'added_this_batch':new,'unchanged_id_set':True,'non_date_fields_unchanged':True,'conflicts':len(conflicts),'other_gaps':'DEFERRED_BY_USER','actual_model':'UNKNOWN','actual_effort':'UNKNOWN','actual_speed':'UNKNOWN','pmo_acceptance':'PENDING'}
(P/'日期补齐进度-20261009.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
progress=json.loads((P/'进度.json').read_text());progress.update(status='PUBLICATION_DATE_COMPLETION_IN_PROGRESS',active_scope='237_frozen_publication_dates_only',verified_publish_dates=status['known'],unknown_publish_dates=status['unknown'],other_gaps_disposition='DEFERRED_BY_USER_2026-10-09',date_completion_status_reference=str(P/'日期补齐进度-20261009.json'))
(P/'进度.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(status,ensure_ascii=False));print('NEXT_IDS '+json.dumps(unknown[:30]))
