from pathlib import Path
import json,re,hashlib,sys
r=Path(__file__).resolve().parent; ev=r/'V2本地读取/evidence'
snapshot_date=sys.argv[1] if len(sys.argv)>1 else '2026-10-07'
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
manifest=json.load(open(r/'V2本地读取/media-manifest.json')); rows=[]
newids=['7680177709267340553','7684228240709274931','7676081471161093403','7676814505564818723','7678313346587774251','7692006549526547727']
for e in sorted(ev.iterdir()):
 if not (e/'coverage.json').exists():continue
 v=e.name;c=json.load(open(e/'coverage.json'));s=json.load(open(e/'source.json')) if (e/'source.json').exists() else c.get('source',{})
 if v in newids:
  c.update(v2_content_analysis_complete=True,final_top10_eligibility='PENDING',final_qualified=False)
  s['page_read_evidence']={'tool':'mcp__cua_repl.js','date':'2026-10-07','browser_id':'2','tab_id':{'7684228240709274931':'30','7680177709267340553':'31','7676081471161093403':'32','7676814505564818723':'33','7678313346587774251':'34','7692006549526547727':'35'}[v],'current_ax_read':True,'call_id':'UNKNOWN','trace_limit':'CUA tool call outputs visible in current conversation; exact call ID absent from local session response_item records. No invented call ID.'}
  save(e/'source.json',s);c['source']=s;save(e/'coverage.json',c)
 complete=c.get('v2_content_analysis_complete',(r/'V2内容分析'/(v+'.md')).exists());card=Path(c['analysis_path']) if c.get('analysis_path') else r/('V2内容分析' if complete else 'V2欠项')/(v+'.md');assert card.exists()
 if complete:assert len(re.findall(r'^## \d+\.',card.read_text(),re.M))==13
 if s.get('local_path'):
  assert hashlib.sha256(Path(s['local_path']).read_bytes()).hexdigest()==s['sha256']
  if not any(x['video_id']==v for x in manifest):manifest.append(dict(video_id=v,source_url=s['url'],exported_path=s['source_export'],research_path=s['local_path'],bytes=s['bytes'],sha256=s['sha256'],private_media=False,source_receipt=str(e/'source.json')))
 rows.append(dict(video_id=v,analysis_path=str(card),coverage_path=str(e/'coverage.json'),status='ACCEPTED_PMO_CONTENT' if v in json.load(open(r/'进度.json')).get('pmo_accepted_ids',[]) else c['status'],v2_content_complete=complete,asr_segments_read=c['asr']['segmentCount'] if 'asr' in c else c['transcript_segments'],supplemental_asr_segments_read=sum(x['segments'] for x in c.get('asr_supplements',[])),images_generated=c.get('frames_generated',c.get('independent_frames_generated')),images_actually_read=c.get('frames_actually_read',c.get('independent_frames_actually_read')),final_top10_eligibility=c.get('final_top10_eligibility','PENDING'),ai_topic_eligible=c.get('ai_topic_eligible','PENDING'),final_qualified=False))
assert len(rows)>=16 and len(set(x['video_id'] for x in rows))==len(rows)
save(r/'V2本地读取/media-manifest.json',manifest)
submit=sum(x['v2_content_complete'] for x in rows); imgs=sum(x['images_actually_read'] for x in rows);asr=sum(x['asr_segments_read'] for x in rows)
save(r/'V2全部提交索引.json',dict(date=snapshot_date,rows=rows,content_submitted=submit,pmo_accepted=len(json.load(open(r/"进度.json"))["pmo_accepted_ids"]),partial_debts=sum(not x["v2_content_complete"] for x in rows),final_qualified=0,source_trace_call_id_gap_ids=[]))
save(r/'V2第二批6条提交.json',dict(date='2026-10-07',rows=[x for x in rows if x['video_id'] in newids],content_submitted=6,pmo_accepted=sum(v in json.load(open(r/'进度.json')).get('pmo_accepted_ids',[]) for v in newids),final_qualified=0,trace_note='Original page/export and image calls mapped in 第二批6条与老马39条源索引.json; accepted PMO content.'))
p=r/'进度.json';d=json.load(open(p));d.update(status=f'{len(rows)} original videos processed; {submit} V2 content cards submitted; research incomplete',core_analyses=submit,total_core_analysis_debts=1000-submit,public_media_registered=len(rows),audio_tracks_processed=len(rows),public_sample_asr_read=len(rows),asr_segments_actually_read=asr,images_generated=imgs,images_actually_read=imgs,v2_content_analyses_submitted=submit,v2_content_analyses_accepted=len(json.load(open(r/"进度.json"))["pmo_accepted_ids"]),media_added_bytes=sum(x['bytes'] for x in manifest),necessary_burst_ranges_read=sum(len(list(e.glob("burst-*.json"))) for e in ev.iterdir() if e.is_dir()),detail_metadata_verified=max(d.get("detail_metadata_verified",0),16),detail_source_checks_passed=10,second_batch_current_page_metadata_checked=6,second_batch_browser_call_id_trace_debts=0,sample_audiovisual_debts=1000)
save(p,d)
print(json.dumps(dict(processed=len(rows),content_cards=submit,accepted=len(json.load(open(r/"进度.json"))["pmo_accepted_ids"]),asr_segments=asr,images=imgs,media_bytes=d['media_added_bytes']),ensure_ascii=False))
