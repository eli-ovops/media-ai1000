import json,pathlib,hashlib,datetime,wave,csv
P=pathlib.Path(__file__).resolve().parent
ids=[f.stem for f in sorted((P/'内容卡').glob('*.md'))]
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
coverage=[]
for vid in ids:
 e=P/'evidence'/vid;a=json.loads((e/'analyze.json').read_text())['structuredContent'];bs=json.loads((e/'burst-fullspan.json').read_text())['structuredContent']['frames']
 tr=a['transcript'];matches=[]
 for f in P.glob('cache/audio/*/transcript.json'):
  v=json.loads(f.read_text())
  if v.get('fullText')==tr['fullText']:matches.append((f,v))
 assert len(matches)==1
 f,v=matches[0]
 audio=f.parent/'audio.wav'
 if audio.is_file():
  with wave.open(str(audio)) as w:duration=w.getnframes()/w.getframerate()
 else:
  ledger=json.loads((P/'缓存清理回执.json').read_text())
  receipt=next(x for x in ledger['deleted'] if x['path']==str(audio) and x['kind']=='decoded_full_track_audio' and x['video_id']==vid)
  duration=receipt['duration']
 assert abs(duration-a['info']['durationSec'])<1
 x={'video_id':vid,'asr_fulltext_actually_read':True,'full_track_audio_duration':duration,'asr_cache':str(f),'full_segments':len(v['segments']),'last_segment':v['segments'][-1],'frames_actually_read':30,'sample_times':[b['timeSec'] for b in bs],'seen_contact_sheets':[str(e/f'fullspan-{i}.jpg') for i in range(1,6)],'unread_interval_images':len(a['frames']),'unread_interval_files_currently_retained':sum(pathlib.Path(z['path']).is_file() for z in a['frames']),'decoded_audio_currently_retained':audio.is_file(),'cleanup_receipt':'缓存清理回执.json','continuous_audiovisual':'UNKNOWN','tail_without_frames':[bs[-1]['timeSec'],a['info']['durationSec']],'source_sha256':hashlib.sha256((P/'media'/f'{vid}.mp4').read_bytes()).hexdigest(),'source':'source.json','card':str(P/'内容卡'/f'{vid}.md'),'pmo_acceptance':'PENDING'}
 if vid=='7685513042200694050':
  extra=json.loads((e/'burst-actioncheck.json').read_text())['structuredContent']['frames']
  x.update(frames_actually_read=42,extra_sample_times=[b['timeSec'] for b in extra],extra_seen_contact_sheets=[str(e/f'actioncheck-{i}.jpg') for i in range(1,3)])
 (e/'coverage.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');coverage.append(x)
known_in=known_out=unknown=0
for f in P.glob('账号*-可见目录.json'):
 rows=json.loads(f.read_text())
 for r in rows:
  if r['video_id'] in ids:r.update(content_read='V2_READ_PENDING_PMO',ai_relevance='ACTUAL_CONTENT_CONFIRMED_AI',coverage=f'evidence/{r["video_id"]}/coverage.json')
  if r['window']=='IN_WINDOW':known_in+=1
  elif r['window']=='OUTSIDE_WINDOW':known_out+=1
  else:unknown+=1
 f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 with f.with_suffix('.csv').open('w',encoding='utf-8-sig',newline='') as h:
  keys=list(dict.fromkeys(k for r in rows for k in r));wr=csv.DictWriter(h,fieldnames=keys or ['video_id']);wr.writeheader()
  for r in rows:wr.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
 table=list(csv.DictReader(f.with_suffix('.csv').open(encoding='utf-8-sig')))
 assert len(rows)==len(table)
 for r,c in zip(rows,table):
  for k,v in r.items():assert c[k]==(json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else str(v)),(r['video_id'],k)
accounts=json.loads((P/'5账号身份映射.json').read_text())
progress=json.loads((P/'进度.json').read_text());progress.update(status='PARTIAL_RESEARCH_CONTINUING_APPROVED_3GIB',new_V2_read=len(ids),added_since_first_delivery=len(ids)-3,directory_rows=known_in+known_out+unknown,identity_verified=sum(a['name']!='UNKNOWN' and a['douyin_id']!='UNKNOWN' for a in accounts),user_not_found_pages=0,failed_shortlinks=0,collection_cutoff=json.loads((P/'进度.json').read_text()).get('collection_cutoff','UNKNOWN'),known_in_window=known_in,known_outside_window=known_out,date_unknown=unknown,known_in_window_pending_read=known_in-len(ids),pmo_acceptance='PENDING',goal_complete=False);save('进度.json',progress)
cache=sum(f.stat().st_size for f in P.parent.rglob('*') if f.is_file())
exports={v['source_export'] for f in P.parent.glob('*/evidence/*/source.json') for v in [json.loads(f.read_text())] if v.get('source_export') and pathlib.Path(v['source_export']).is_file() and not pathlib.Path(v['source_export']).is_relative_to(P.parent)}
downloads=[{'path':str(f),'bytes':f.stat().st_size,'retained':True,'purpose':'browser exported public source; copied to exact research whitelist'} for f in map(pathlib.Path,sorted(exports))]
assert cache+sum(x['bytes'] for x in downloads)<3*1024**3
save('证据索引.json',{'owner':progress['owner'],'raw':'原始回执.json','continuation_raw':'续接原始回执.json','content_coverage':coverage,'scope':'AI_RELATED_ONLY_PER_CURRENT_USER','scope_human_message':'AI范围指令定位.json','stage':'01','routing':'ROUTING-2026-09-30-v3','handoff':'HANDOFF-2026-10-06-v1','actual_model':'UNKNOWN','actual_effort':'UNKNOWN','actual_speed':'UNKNOWN','read_method':'existing offline video CLI with exact file whitelist; full ASR text and actually viewed sample images; no cloud or network','browser':'same Owner IAB; getState and current tab recovery after kernel reset, no blind replay','resolved_previous_blockers':['three failed account identities now verified from exact shortlinks','long local ASR completed after own CLI wait adjustment'],'current_limits':['partial profile pagination or window coverage remains unconfirmed','exact video page/date/media failures recorded per ID','3GiB cache limit approved by human; completed audio/duplicate caches may be removed after evidence preservation'],'cache_decision':'预算调整待决.json','research_cache_and_sources_bytes':cache+sum(x['bytes'] for x in downloads),'cache_limit_bytes':3*1024**3,'external_download_files':downloads,'deleted':json.loads((P/'缓存清理回执.json').read_text())['deleted'] if (P/'缓存清理回执.json').exists() else [],'cleanup_receipt':'缓存清理回执.json'})
allrows=[r for f in sorted(P.glob('账号*-可见目录.json')) for r in json.loads(f.read_text())]
assert len(allrows)==len({r['video_id'] for r in allrows})
remaining=[{'video_id':r['video_id'],'url':r['url'],'published_at':r['published_at'],'window':r['window'],'content_read':r['content_read'],'ai_relevance':r['ai_relevance'],'last_page':r.get('latest_page_read'),'last_date_attempt':r.get('latest_date_attempt'),'last_media':r.get('latest_media_attempt')} for r in allrows if r['content_read']=='NOT_READ']
save('剩余与阻断.json',{'window_known_unread':[r for r in remaining if r['window']=='IN_WINDOW'],'date_unknown':[r for r in remaining if r['window']=='UNKNOWN'],'outside_window_not_deep_read':[r for r in remaining if r['window']=='OUTSIDE_WINDOW'],'unconfirmed_results_after_batch_timeout':['7691736815237139748','7691338033022389514','7690983927330951665','7688001768457850166'],'assumptions':'Unknown date does not prove in-window or out-of-window; title screening does not prove actual AI content; failures do not prove permanent deletion.'})
save('文档与数据自检.json',{'json_csv_equal_all_fields':True,'unique_directory_ids':len(allrows),'identity_verified':progress['identity_verified'],'V2_cards':len(ids),'asr_fulltext_actually_read':True,'actually_viewed_frames':sum(c['frames_actually_read'] for c in coverage),'cache_including_all_research_and_tracked_exports_below_limit':True,'cache_bytes':cache+sum(x['bytes'] for x in downloads),'pmo_acceptance':'PENDING','goal_complete':False})
readme=P/'README.md';s=readme.read_text();tag='<!-- CURRENT-RESEARCH -->'
if tag in s:s=s.split('<!-- END-CURRENT-RESEARCH -->',1)[1].lstrip()
readme.write_text(tag+f'\n2026-10-09最新：5/5身份已核，{len(allrows)}条部分目录，入窗{known_in}、出窗{known_out}、日期UNKNOWN{unknown}；实际V2已读{len(ids)}条（首批3条后新增{len(ids)-3}条），共实际看{sum(c["frames_actually_read"] for c in coverage)}图。非连续看听，PMO待验。仍未完成全量目标。\n\n[最新综合建议](综合建议-本轮实读.md) · [当前进度](进度.json) · [具体剩余ID/阻断](剩余与阻断.json) · [预算调整待决](预算调整待决.json) · [数据自检](文档与数据自检.json)\n\n此前3个身份访问阻断已解除；旧失败保留为历史。当前用户已批准3GiB预算及信息提取后清理任务缓存；剩余原片/日期/分页问题分别记录，不充完成数。下文为原首批历史。\n<!-- END-CURRENT-RESEARCH -->\n\n'+s)
files=[{'path':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'retained':True,'source':'authorized research or existing offline helper','purpose':'research artifact, source or reproducible evidence'} for f in sorted(P.rglob('*')) if f.is_file() and f.name!='文件记录.json']
cleanup=json.loads((P/'缓存清理回执.json').read_text()) if (P/'缓存清理回执.json').exists() else {'deleted':[]}
save('文件记录.json',{'owner':progress['owner'],'files':files,'external_downloads':downloads,'deleted':cleanup['deleted'],'cleanup_receipt':'缓存清理回执.json'})
print(json.dumps({k:progress[k] for k in ['directory_rows','new_V2_read','known_in_window','known_outside_window','date_unknown','goal_complete']},ensure_ascii=False));print('TOTAL_CACHE_AND_SOURCES',cache+sum(x['bytes'] for x in downloads))
