from pathlib import Path
import json, csv, re

r = Path(__file__).resolve().parent
s = r / '柱子哥TzFilm全量专项-20261007'
ev = r / 'V2本地读取/evidence'
def read(p): return json.loads(p.read_text())
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
progress = read(r / '进度.json')
accepted = set(progress['pmo_accepted_ids'])
catalog = read(s / '作品目录.json')
submitted = []
index = read(s / '证据索引.json')
index['media'] = []
for row in catalog['rows']:
    v = row['video_id']
    card = s / '内容分析' / (v + '.md')
    if not card.exists(): continue
    c = read(ev / v / 'coverage.json')
    assert c.get('v2_content_analysis_complete')
    assert len(re.findall(r'^## \d+\.', card.read_text(), re.M)) == 13
    submitted.append(v)
    row.update(content_status='ACCEPTED_PMO_CONTENT' if v in accepted else 'V2_SUBMITTED_PENDING_PMO', analysis_path=str(card))
    index['media'].append(dict(video_id=v, source=str(ev/v/'source.json'), coverage=str(ev/v/'coverage.json'), analysis=str(card)))
save(s/'作品目录.json', catalog)
fields = list(dict.fromkeys(k for x in catalog['rows'] for k in x))
with (s/'作品目录.csv').open('w', newline='') as f:
    writer=csv.DictWriter(f, fieldnames=fields);writer.writeheader();writer.writerows(catalog['rows'])
save(s/'证据索引.json', index)
sources = list(ev.glob('*/source.json'))
pending = [p.parent.name for p in sources if not (p.parent/'coverage.json').exists()]
registered_ids = {x['video_id'] for x in read(r/'V2本地读取/media-manifest.json')} | {p.parent.name for p in sources}
special_ids = {x['video_id'] for x in catalog['rows']}
inventory = read(r/'生成物记录.json')
paths = {Path(x['path']) for x in inventory['files']}
paths.update(p for p in r.rglob('*') if p.is_file() and p.name not in ['任务单.md', 'PMO验收-20261007.md'])
paths.update(Path(read(p)['source_export']) for p in sources if 'source_export' in read(p))
files = [dict(path=str(p), bytes=p.stat().st_size, mtime_unix=p.stat().st_mtime, purpose='Owner research or exact public export; retained') for p in sorted(paths) if p.is_file()]
total = sum(x['bytes'] for x in files)
cap = 2*1024**3
inventory.update(files=files,total_bytes=total,storage_cap_bytes=cap,storage_remaining_bytes=cap-total,deleted_files=[])
save(r/'生成物记录.json', inventory)
progress.update(public_media_registered=len(registered_ids),media_pending_analysis_ids=pending,media_registered_pending_ids=pending,specialty_media_registered=len(registered_ids & special_ids),specialty_content_read=len(submitted),specialty_content_submitted=len(submitted),specialty_content_debt=101-len(submitted),specialty_unread=101-len(submitted),original_asr_cache_segments_actually_read=progress['asr_segments_actually_read'],content_candidate_cards_written=progress['v2_content_analyses_submitted']+1,target_ai_content_eligible_at_most=progress['v2_content_analyses_submitted']-1)
scope_path=s/'AI相关筛选.json'
if scope_path.exists():
    scope=read(scope_path)
    progress.update(priority_specialty='TZFILM_AI_RELATED_ONLY',specialty_active_target=scope['ai_related_candidates'],specialty_active_read=scope['ai_related_cards_read'],specialty_active_unread=scope['ai_related_unread'],specialty_pending_relevance=scope['pending_relevance'],specialty_excluded=scope['excluded'],specialty_content_debt=scope['ai_related_unread'],specialty_unread=scope['ai_related_unread'],specialty_catalog_unread=101-len(submitted))
save(r/'进度.json', progress)
recovery = read(r/'续接状态-20261007.json')
recovery.update(specialty_submitted=len(submitted),specialty_unread=101-len(submitted),total_processed=progress['audio_tracks_processed'],total_content=progress['v2_content_analyses_submitted'],total_accepted=len(accepted),media_pending=pending,next_video_ids=pending,storage_last_verified_bytes=total)
if scope_path.exists():
    recovery.update(priority='TZFILM_AI_RELATED_ONLY',specialty_active_target=scope['ai_related_candidates'],specialty_active_read=scope['ai_related_cards_read'],specialty_unread=scope['ai_related_unread'],specialty_pending_relevance=scope['pending_relevance'],specialty_excluded=scope['excluded'])
save(r/'续接状态-20261007.json',recovery)
validation=read(r/'本轮V2验证.json')
validation.update(processed_media=progress['audio_tracks_processed'],content_cards=progress['v2_content_analyses_submitted'],specialty_cards=len(submitted),asr_segments_read=progress['asr_segments_actually_read'],images_actually_read=progress['images_actually_read'],storage_bytes_including_original_exports=total,below_cap=total<cap)
save(r/'本轮V2验证.json',validation)
print(json.dumps(dict(specialty=len(submitted),pending=pending,storage_bytes=total,remaining_bytes=cap-total),ensure_ascii=False))
