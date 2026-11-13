import pathlib,json,re,csv,shutil,datetime
P=pathlib.Path(__file__).resolve().parent
R=P.parent/'V2本地读取'
S=pathlib.Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
records=[]
for n,line in enumerate(S.read_text().splitlines(),1):
 if not any(s in line for s in ['ACCOUNT_BATCH ','ACCOUNT_SCOPED ','ACCOUNT_PAGE ','AI_VIDEO_PAGE ','AI_MEDIA_RECEIPT ','WINDOW_DATE ']):continue
 e=json.loads(line);item=e.get('payload',{}).get('item',{})
 if e.get('type')!='event_msg' or item.get('type')!='McpToolCall':continue
 for c in item.get('result',{}).get('content',[]):
  if c.get('type')!='text':continue
  for marker in ['ACCOUNT_BATCH ','ACCOUNT_SCOPED ','ACCOUNT_PAGE ','AI_VIDEO_PAGE ','AI_MEDIA_RECEIPT ','WINDOW_DATE ']:
   for m in re.finditer(marker,c['text']):
    try:v,_=json.JSONDecoder().raw_decode(c['text'][m.end():])
    except Exception:continue
    values=v if marker=='WINDOW_DATE ' and isinstance(v,list) else [v]
    for value in values:records.append({'kind':marker.strip(),'data':value,'receipt':{'session':str(S),'line':n,'call_id':item.get('id'),'timestamp':e.get('timestamp')}})
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
save('原始回执.json',records)
accounts={};pages=[]
for r in records:
 if r['kind'].startswith('ACCOUNT'):
  for a in (r['data'] if isinstance(r['data'],list) else [r['data']]):
   short=a['short'];acc=accounts.setdefault(short,{'short':short,'name':'UNKNOWN','homepage':'UNKNOWN','douyin_id':'UNKNOWN','videos':{},'receipts':[]})
   acc['receipts'].append(r['receipt'])
   if a.get('url'):acc['homepage']=a['url']
   if a.get('headings'):acc['name']=a['headings'][0]
   if a.get('name'):acc['name']=a['name']
   txt=a.get('text','');m=re.search(r'抖音号[：:]\s*([^\s]+)',txt)
   if m:acc['douyin_id']=m.group(1)
   if '用户不存在' in txt:acc['status']='PAGE_REPORTS_USER_NOT_FOUND'
   if a.get('error'):acc['status']='SHORTLINK_NAVIGATION_FAILED';acc['error']=a['error']
   if 'videos' in a:videos=a['videos']
   else:
    main=txt.split('搜索 Ta 的作品')[-1].split('广告投放')[0]
    videos=[v for v in a.get('video_links',[]) if v['text'] and v['text'] in main]
   for v in videos:
    vid=re.search(r'/video/(\d+)',v['url']).group(1)
    acc['videos'][vid]={'video_id':vid,'url':v['url'],'directory_text':v['text'],'published_at':'UNKNOWN','window':'UNKNOWN','ai_relevance':'TITLE_SCREEN_ONLY','content_read':'NOT_READ','receipt':r['receipt']}
 for a in accounts.values():
  if a['videos']:a['status']='PARTIAL_DIRECTORY_PAGINATION_SERVICE_ERROR'
for r in records:
 if r['kind']=='WINDOW_DATE' and r['data'].get('video_id')==r['data'].get('requested_id'):
  v=r['data'];vid=v['video_id'];m=re.search(r'20\d{2}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?',v.get('raw_date_text',''))
  if m:
   for a in accounts.values():
    if vid in a['videos']:a['videos'][vid].update(published_at=m.group(0),raw_date_text=v['raw_date_text'],date_receipt=r['receipt'],window='IN_WINDOW' if '2026-08-09'<=m.group(0)[:10]<='2026-10-09' else 'OUTSIDE_WINDOW',timezone='UNKNOWN: page does not label timezone')
 if r['kind']=='AI_VIDEO_PAGE':
  v=r['data'];vid=re.search(r'/video/(\d+)',v['url']).group(1);m=re.search(r'发布时间[：:]\s*(20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2})',v.get('text',''))
  if m:
   for a in accounts.values():
    if vid in a['videos']:a['videos'][vid].update(published_at=m.group(1),raw_date_text=m.group(0),date_receipt=r['receipt'],window='IN_WINDOW',timezone='UNKNOWN: page does not label timezone')
summary=[]
order=['https://v.douyin.com/Myhv2svszM4/','https://v.douyin.com/fUyAO3EP6x8/','https://v.douyin.com/kbtZsRxkbGk/','https://v.douyin.com/FSK_tsJE1W4/','https://v.douyin.com/hI80WJn7s3U/']
for i,a in enumerate([accounts[k] for k in order],1):
 videos=list(a.pop('videos').values());save(f'账号{i}-可见目录.json',videos)
 with (P/f'账号{i}-可见目录.csv').open('w',encoding='utf-8-sig',newline='') as f:
  keys=list(dict.fromkeys(k for v in videos for k in v));w=csv.DictWriter(f,fieldnames=keys or ['video_id']);w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else v for k,v in x.items()} for x in videos)
 a.update(visible_directory_rows=len(videos),window_complete=False,window_count='UNKNOWN',directory=f'账号{i}-可见目录.json');summary.append(a)
save('5账号身份映射.json',summary)
source=pathlib.Path('/Users/USER/Downloads/download.mp4');dest=P/'media/7693510647572647211.mp4'
if source.exists() and not dest.exists():
 dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
 if sum(f.stat().st_size for f in R.rglob('*') if f.is_file())+sum(f.stat().st_size for f in P.rglob('*') if f.is_file())>2*1024**3:raise RuntimeError('Research cache budget exceeded')
 save('allowed-files.json',[str(dest)])
 for n in ['launch.mjs','read-public-video.mjs']:shutil.copy2(R/n,P/n)
allowed=json.loads((P/'allowed-files.json').read_text())
for r in records:
 if r['kind']=='AI_MEDIA_RECEIPT' and r['data'].get('path'):
  v=r['data'];vid=re.search(r'/video/(\d+)',v['url']).group(1);src=pathlib.Path(v['path']);dst=P/'media'/f'{vid}.mp4'
  if not dst.exists():shutil.copy2(src,dst)
  if str(dst) not in allowed:allowed.append(str(dst))
  e=P/'evidence'/vid;e.mkdir(parents=True,exist_ok=True);(e/'source.json').write_text(json.dumps({'url':v['url'],'video_id':vid,'source_export':str(src),'local_media':str(dst),'receipt':r['receipt']},ensure_ascii=False,indent=2))
save('allowed-files.json',allowed)
save('进度.json',{'status':'IN_PROGRESS_PARTIAL_DIRECTORY','owner':'01a11442-a6d9-7413-88b3-191ce5cb037b','window_start':'2026-08-09','collection_cutoff':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'content_scope':'AI_RELATED_ONLY_PER_CURRENT_USER','identity_verified':2,'user_not_found_pages':1,'failed_shortlinks':2,'directory_rows':sum(a['visible_directory_rows'] for a in summary),'window_total':'UNKNOWN','new_V2_read':0,'goal_complete':False,'pmo_acceptance':'PENDING','media_source':str(source),'local_media':str(dest),'browser_download_receipt':next((r['receipt'] for r in records if r['kind']=='AI_MEDIA_RECEIPT'),None)})
print(json.dumps([{'name':a['name'],'rows':a['visible_directory_rows'],'status':a.get('status')} for a in summary],ensure_ascii=False));print(dest.stat().st_size if dest.exists() else 'NO_MEDIA')
