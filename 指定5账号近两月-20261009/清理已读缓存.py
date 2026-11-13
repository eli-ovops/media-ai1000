import pathlib,json,hashlib,wave,subprocess,datetime
P=pathlib.Path(__file__).resolve().parent
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
budget=json.loads((P/'预算调整待决.json').read_text())
assert budget['human_approval_received'] and budget['cache_cleanup_authorization']=='缓存用完提取完信息需要删除缓存'
ledger=json.loads((P/'缓存清理回执.json').read_text())
done={(x['video_id'],x['path']) for x in ledger['deleted']}
ready=[]
for card in sorted((P/'内容卡').glob('*.md')):
 e=P/'evidence'/card.stem
 if not (e/'coverage.json').exists():continue
 c=json.loads((e/'coverage.json').read_text());s=json.loads((e/'source.json').read_text())
 assert c['asr_fulltext_actually_read'] and c['frames_actually_read']>=30
 assert all(pathlib.Path(x).is_file() for x in c['seen_contact_sheets'])
 tr=pathlib.Path(c['asr_cache']);assert tr.is_file()
 f=tr.parent/'audio.wav'
 if f.is_file() and not f.is_symlink():
  with wave.open(str(f)) as w:d=w.getnframes()/w.getframerate()
  assert abs(d-c['full_track_audio_duration'])<.1
  ready.append({'video_id':card.stem,'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'kind':'decoded_full_track_audio','retained_evidence':[str(card),str(tr),str(e/'coverage.json')],'duration':d})
 export=pathlib.Path(s['source_export']);media=pathlib.Path(s['local_media'])
 if (card.stem,str(export)) not in done and export.is_file() and not export.is_symlink() and media.is_file():
  h=sha(export)
  if h==c['source_sha256'] and sha(media)==h:
   ready.append({'video_id':card.stem,'path':str(export),'bytes':export.stat().st_size,'sha256':h,'kind':'verified_browser_export_duplicate','retained_media':str(media)})
 a=json.loads((e/'analyze.json').read_text())['structuredContent']
 used={x['path'] for x in json.loads((e/'burst-fullspan.json').read_text())['structuredContent']['frames']}
 if (e/'burst-actioncheck.json').exists():used.update(x['path'] for x in json.loads((e/'burst-actioncheck.json').read_text())['structuredContent']['frames'])
 for x in a['frames']:
  f=pathlib.Path(x['path'])
  if str(f) not in used and f.is_file() and not f.is_symlink():
   ready.append({'video_id':card.stem,'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'kind':'unread_interval_sample','retained_evidence':[str(card),str(e/'coverage.json')],'retained_media':str(media)})
save('缓存清理计划.json',{'authorization':ledger['authorization'],'ready_exact_files':ready,'preserve':'research originals, transcripts, cards, sampled images and all acceptance/source evidence','status':'PREPARED_EXACT_PATHS'})
if not ready:
 print('NO_NEW_COMPLETED_CACHE');raise SystemExit
before=subprocess.check_output(['df','-k',str(P),'/Users/USER/Downloads'],text=True)
for x in ready:
 f=pathlib.Path(x['path'])
 assert f.is_file() and not f.is_symlink() and f.stat().st_size==x['bytes'] and sha(f)==x['sha256']
 if x['kind']=='decoded_full_track_audio':assert f.name=='audio.wav' and f.is_relative_to(P/'cache'/'audio') and all(pathlib.Path(t).is_file() for t in x['retained_evidence'])
 elif x['kind']=='verified_browser_export_duplicate':assert f.parent==pathlib.Path('/Users/USER/Downloads') and sha(pathlib.Path(x['retained_media']))==x['sha256']
 elif x['kind']=='unread_interval_sample':assert f.parent.name=='interval' and f.is_relative_to(P/'cache'/'frames') and pathlib.Path(x['retained_media']).is_file() and all(pathlib.Path(t).is_file() for t in x['retained_evidence'])
 else:raise ValueError('unapproved kind')
 f.unlink();ledger['deleted'].append(dict(x,deleted_at=datetime.datetime.now(datetime.timezone.utc).isoformat()));save('缓存清理回执.json',ledger)
after=subprocess.check_output(['df','-k',str(P),'/Users/USER/Downloads'],text=True)
ledger['batches'].append({'df_before':before,'df_after':after,'removed_files':len(ready),'removed_file_bytes':sum(x['bytes'] for x in ready),'retained_evidence_and_media':True,'measurement_limit':'df may include concurrent filesystem activity; removed bytes are not the actual df release amount'})
save('缓存清理回执.json',ledger)
print(before);print(after);print('EXACT_FILES_REMOVED',len(ready))
