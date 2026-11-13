import json, pathlib, re, csv, datetime
ROOT = pathlib.Path(__file__).resolve().parent
OLD = ROOT.parent
SESSION = pathlib.Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
def save(name, data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
profiles=[]
searches=[]
details=[]
for i,line in enumerate(SESSION.read_text().splitlines(),1):
    if not any(tag in line for tag in ['BENCHMARK_PROFILE ', 'BENCHMARK_SEARCH ', 'BENCHMARK_DETAIL']): continue
    try:
        event=json.loads(line)
        payload=event.get('payload',{})
        if event.get('type')=='event_msg' and payload.get('type')=='item_completed':
            item=payload.get('item',{})
            if item.get('type')!='McpToolCall': continue
            raw='\n'.join(c.get('text','') for c in item.get('result',{}).get('content',[]) if c.get('type')=='text')
            payload={'call_id':item.get('id')}
        elif event.get('type')=='response_item' and payload.get('type')=='function_call_output': raw=payload.get('output','')
        else: continue
        if not isinstance(raw,str): raw=json.dumps(raw,ensure_ascii=False)
        # Tool output may hold escaped JSON text blocks. Decode each text block first.
        try:
            obj=json.loads(raw)
            texts=[c.get('text','') for c in obj.get('content',[]) if c.get('type')=='text'] if isinstance(obj,dict) else []
            if texts: raw='\n'.join(texts)
        except Exception: pass
        dec=json.JSONDecoder()
        for match in re.finditer('BENCHMARK_PROFILE ',raw):
            try:
                row,_=dec.raw_decode(raw[match.end():]); row['receipt']={'session':str(SESSION),'line':i,'call_id':payload.get('call_id'),'timestamp':event.get('timestamp')}; profiles.append(row)
            except Exception: pass
        for match in re.finditer('BENCHMARK_SEARCH ',raw):
            try:
                row,_=dec.raw_decode(raw[match.end():]); searches.append({'data':row,'receipt':{'session':str(SESSION),'line':i,'call_id':payload.get('call_id'),'timestamp':event.get('timestamp')}})
            except Exception: pass
        for tag in ['BENCHMARK_DETAIL ', 'BENCHMARK_DETAILS ']:
            for match in re.finditer(tag,raw):
                try:
                    row,_=dec.raw_decode(raw[match.end():]); batch=row if isinstance(row,list) else [row]
                    for row in batch:
                        row['receipt']={'session':str(SESSION),'line':i,'call_id':payload.get('call_id'),'timestamp':event.get('timestamp')}; details.append(row)
                except Exception: pass
    except Exception: pass
save('主页原始读取.json',profiles)
save('账号搜索原始读取.json',searches)
save('逐条日期补核.json',details)
latest={}
for row in profiles:
    name=row.get('requested',row.get('name'))
    if not name: continue
    if name not in latest or row.get('name') and (len(row.get('works',[]))>=len(latest[name].get('works',[]))): latest[name]=row
save('当前主页目录汇总.json',latest)
old=json.loads((OLD/'当前合并目录.json').read_text())
authors=sorted(set(x['author'] for x in old))
rows=[]
for author in authors:
    subset=[x for x in old if x['author']==author]
    subset.sort(key=lambda x:int(x['video_id']),reverse=True)
    for x in subset[:10]:
        row=dict(x); row['reuse_source']=str(OLD/'当前合并目录.json'); row['recent_window']='2026-10-07已取公开目录中ID降序，精确发布时间及近期完整性另核'; row['read_level']='L1目录，非深读'; rows.append(row)
save('既有账号近期候选目录.json',rows)
save('存储预算.json',{'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'research_root':str(OLD),'research_root_bytes':sum(x.stat().st_size for x in OLD.rglob('*') if x.is_file()),'cap_bytes':2*1024**3,'new_media_bytes':0,'historical_total_including_external_exports_bytes':1640967983,'external_exports_current_bytes':'UNKNOWN; no new media download until reconciled','note':'root measured; prior total includes external export records; no deletion'})
print(json.dumps({'profile_receipts':len(profiles),'legacy_accounts':len(authors),'legacy_directory_rows':len(rows)},ensure_ascii=False))
