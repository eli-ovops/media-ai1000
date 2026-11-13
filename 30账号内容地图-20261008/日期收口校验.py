import pathlib,json,csv,datetime,hashlib
P=pathlib.Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text())
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
rows=read('近期内容表.json');base=read('日期补齐基线-20261009.json')
allowed={'published_at','window','date_source','publication_date_evidence'}
assert len(rows)==237 and len({r['video_id'] for r in rows})==237
frozen=json.loads((P.parents[1]/'流程协作/01-研究热点与选题/发布时间补齐范围-20261009.json').read_text())['video_ids']
assert {r['video_id'] for r in rows}==set(frozen)
assert [r['video_id'] for r in rows]==[r['video_id'] for r in base]
assert all({k:v for k,v in r.items() if k not in allowed}=={k:v for k,v in b.items() if k not in allowed} for r,b in zip(rows,base))
with (P/'近期内容表.csv').open(encoding='utf-8-sig',newline='') as f:c=list(csv.DictReader(f))
assert len(c)==237
for r,v in zip(rows,c):
 for k,x in r.items():assert v[k]==(json.dumps(x,ensure_ascii=False) if isinstance(x,(dict,list)) else str(x)),(r['video_id'],k)
known=[r for r in rows if r['published_at']!='UNKNOWN'];unknown=[r['video_id'] for r in rows if r['published_at']=='UNKNOWN']
assert len(known)+len(unknown)==237
K=len(known);U=len(unknown);added=K-25
assert all(r.get('publication_date_evidence',{}).get('raw_date_text') for r in known)
assert not read('日期冲突-20261009.json')
old=read('逐条日期补核.json');oldids={x.get('video_id') for x in old if x.get('date_completion_20261009')}
for r,b in zip(rows,base):
 if b['published_at']=='UNKNOWN' and r['published_at']!='UNKNOWN' and r['video_id'] not in oldids:
  old.append(dict(r['publication_date_evidence'],date_completion_20261009=True))
save('逐条日期补核.json',old)
status=read('日期补齐进度-20261009.json');status.update(status='DATE_PARTIAL_BLOCKED' if U else 'DATE_COMPLETE_PENDING_PMO',added_since_dispatch=added,goal_complete=not U,remaining_ids=unknown,blocker=f'{U}条精确原页有限复核仍无可接受日期；导航超时、重定向或未呈现发布时间。浏览器当前已恢复，不推断作品永久不可用。' if U else None,pmo_acceptance='PENDING')
save('日期补齐进度-20261009.json',status)
progress=read('进度.json');progress['status']=f'DATE_PARTIAL_BLOCKED_{K}_OF_237' if U else 'DATE_COMPLETE_PENDING_PMO';save('进度.json',progress)
idx=read('证据索引.json');idx['publication_date_completion_20261009']={'total':237,'known':K,'unknown':U,'added':added,'baseline':'日期补齐基线-20261009.json','raw_receipts':'日期本轮原始回执-20261009.json','unresolved':'日期剩余与阻断-20261009.json','status':'日期补齐进度-20261009.json','validation':'日期收口校验-20261009.json','source_timezone':'UNKNOWN unless visible source labels it','browser_recovery':'same Owner IAB recovery; limited continuation recheck only remaining IDs; exact per-ID raw receipts retained','other_gaps':'DEFERRED_BY_USER'};save('证据索引.json',idx)
save('日期收口校验-20261009.json',{'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'total':237,'known':K,'unknown':U,'added_since_dispatch':added,'same_order_and_ids':True,'non_date_fields_unchanged':True,'csv_json_equal':True,'known_rows_have_evidence':True,'date_conflicts':0,'research_complete':not U,'pmo_acceptance':'PENDING'})
doc=read('文档自检.json');doc['publication_date_validation_20261009']=read('日期收口校验-20261009.json');save('文档自检.json',doc)
readme=P/'README.md';s=readme.read_text();marker='<!-- DATE-RECEIPT-20261009 -->'
latest='<!-- DATE-LATEST-20261009 -->'
if latest in s:s=s.split('<!-- END-DATE-LATEST -->',1)[1].lstrip()
readme.write_text(latest+f'\n2026-10-09最新日期回执：已核{K}/237，新增{added}条，剩余{U}条UNKNOWN。ID集合、顺序与非日期字段不变；JSON/CSV一致、无日期冲突。'+('目标全部补齐，待PMO验收。' if not U else '有限复核已收口，具体阻断保留。')+'详见[日期进度](日期补齐进度-20261009.json)及[校验](日期收口校验-20261009.json)。下文此前数字保留为阶段历史。\n<!-- END-DATE-LATEST -->\n\n'+s)
if marker not in s:readme.write_text(marker+'\n2026-10-09日期补核：221/237已核，新增196条，16条有限复核受阻，目标未全部完成。原ID、顺序及非日期字段不变。详见[校验回执](日期收口校验-20261009.json)、[具体阻断](日期剩余与阻断-20261009.json)。其他30账号缺口仍暂缓；5账号专项顺序进入，正文深读遵从本会话最新用户要求，仅AI相关。\n\n'+s)
files=[]
for f in sorted(P.rglob('*')):
 if f.is_file() and f.name!='文件记录.json':files.append({'path':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'retained':True})
save('文件记录.json',{'owner_thread':'01a11442-a6d9-7413-88b3-191ce5cb037b','directory':str(P),'files':files,'deleted':[]})
print(json.dumps(status,ensure_ascii=False))
