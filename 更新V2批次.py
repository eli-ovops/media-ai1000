from pathlib import Path
import json, re, hashlib

root=Path(__file__).resolve().parent
ev=root/'V2本地读取/evidence'
session=Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
rows=[]; manifest=json.loads((root/'V2本地读取/media-manifest.json').read_text())
metadata={x['video_id']:x for x in json.loads((root/'首批10条页面核验.json').read_text())}
for folder in sorted(ev.iterdir()):
    if not folder.name.isdigit() or not (folder/'coverage.json').exists(): continue
    vid=folder.name; p=folder/'coverage.json'; c=json.loads(p.read_text())
    if vid=='7654922329579518885':
        source=json.loads((folder/'asr-supplement-source.json').read_text())
        source.update(text=(folder/'asr-supplement.txt').read_text(),vtt_path=str(folder/'asr-supplement.vtt'),
                      full_returned_text_actually_read=True,segments=10,offset_sec=94)
        c['asr_supplements']=[source];c['asr_tail_silence']='Not silence; missing closing speech supplied by supplemental ASR'
        c['asr_key_speech_missing']=False
    if vid=='7682715455454186790':
        source=json.loads((folder/'asr-supplement-source.json').read_text())
        source.update(text=(folder/'asr-supplement.txt').read_text(),vtt_path=str(folder/'asr-supplement.vtt'),
                      full_returned_text_actually_read=True,segments=3,timestamps_reliable=False)
        c['asr_supplements']=[source];c['asr_key_speech_missing']=True
        c['status']='PARTIAL_ASR_KEY_SPEECH_MISSING';c['v2_content_analysis_complete']=False
    if vid=='7668610752106551168':
        c['native_frame_supplements']=[dict(path=str(folder/name),requested_time_sec=t,actually_read=True,
             method='existing ffmpeg source extraction; full resolution; original retained')
             for name,t in [('interface-native.jpg',24),('interface-native-28.jpg',28),('interface-native-32.jpg',32)]]
        c['frames_generated']=45;c['frames_actually_read']=45
        c['tool_identity_check']='28-second native frame sidebar explicitly reads Doubao in Chinese'
        c['time_precision_warning']='Native 24 sec is presenter; interval nominal 24 sec shows UI. Nominal times are approximate, not exact edit points.'
        calls=[]
        for line_no,line in enumerate(session.read_text().splitlines(),1):
            x=json.loads(line).get('payload',{});t=x.get('arguments',x.get('input',''))
            if x.get('name')=='exec' and isinstance(t,str) and 'view_image' in t and vid+'/interface-native' in t:
                calls.append(dict(call_id=x.get('call_id'),input_jsonl_line=line_no,tool='exec'))
        c['native_image_read_calls']=calls
    c['final_top10_eligibility']='PENDING';c['final_qualified']=False
    if vid not in ['7685352868332817707','7682715455454186790']:
        c['status']='SUBMITTED_PENDING_PMO';c['v2_content_analysis_complete']=True
    if vid in metadata and vid in ['7654922329579518885','7674224670610412987','7668610752106551168','7671969297027699961']:
        c['source']['page_snapshot']={k:metadata[vid][k] for k in ['title','author','account_id','likes_display','favorites','comments','shares','published_at']}
        c['source']['current_page_metrics_same_as_original_snapshot']=True
        (folder/'source.json').write_text(json.dumps(c['source'],ensure_ascii=False,indent=2))
    if vid=='7613370565042130211': c['visible_catalog_like_median_display_basis']=384.5;c['visible_catalog_count']=130
    p.write_text(json.dumps(c,ensure_ascii=False,indent=2))
    complete=vid!='7682715455454186790'
    card=root/('V2内容分析' if complete else 'V2欠项')/(vid+'.md')
    assert card.exists()
    text=card.read_text()
    assert len(re.findall(r'^## \d+\.',text,re.M))==13 if complete else len(re.findall(r'^\d+\.',text,re.M))==13
    rows.append(dict(video_id=vid,analysis_path=str(card),coverage_path=str(p),
       status='ACCEPTED_PMO_CONTENT' if vid=='7685352868332817707' else c['status'],
       v2_content_complete=complete,asr_segments_read=c['asr']['segmentCount'] if 'asr' in c else c['transcript_segments'],
       supplemental_asr_segments_read=sum(x['segments'] for x in c.get('asr_supplements',[])),
       images_generated=c.get('frames_generated',c.get('independent_frames_generated')),images_actually_read=c.get('frames_actually_read',c.get('independent_frames_actually_read')),
       final_top10_eligibility='PENDING',final_qualified=False))
    if not any(x['video_id']==vid for x in manifest):
        s=c['source']; media=Path(s['local_path']);assert hashlib.sha256(media.read_bytes()).hexdigest()==s['sha256']
        manifest.append(dict(video_id=vid,source_url=s['url'],exported_path=s['source_export'],research_path=s['local_path'],bytes=s['bytes'],sha256=s['sha256'],private_media=False,source_receipt=str(folder/'source.json')))
assert len(rows)==10 and len({x['video_id'] for x in rows})==10
(root/'V2本地读取/media-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(root/'V2首批10条提交.json').write_text(json.dumps(dict(date='2026-10-07',standard='V2',rows=rows,content_submitted=9,pmo_accepted=1,partial_debts=1,final_qualified=0),ensure_ascii=False,indent=2))
p=root/'进度.json';s=json.loads(p.read_text());s.update(core_analyses=9,total_core_analysis_debts=991,
 public_media_registered=10,audio_tracks_processed=10,public_sample_asr_read=10,
 asr_segments_actually_read=sum(x['asr_segments_read'] for x in rows),
 supplemental_asr_segments_actually_read=sum(x['supplemental_asr_segments_read'] for x in rows),
 images_generated=sum(x['images_generated'] for x in rows),images_actually_read=sum(x['images_actually_read'] for x in rows),
 v2_content_analyses_submitted=9,v2_content_analyses_accepted=1,first_batch_v2_analysis_debts=1,
 final_qualified_unique_videos=0,final_qualified_video_debts=1000,full_audiovisual=0,
 media_added_bytes=sum(x['bytes'] for x in manifest),status='First 10 processed; 9 V2 content cards submitted, 1 ASR debt; expanding research',
 next_actions=['Retain unresolved drama ASR debt; do not repeat unchanged parameters','Expand to 50 content analyses','Complete per-account visible like/favorite ranking before final TOP10 qualification'])
p.write_text(json.dumps(s,ensure_ascii=False,indent=2))
print(json.dumps({k:s[k] for k in ['core_analyses','v2_content_analyses_accepted','images_actually_read','asr_segments_actually_read','supplemental_asr_segments_actually_read','media_added_bytes']}))
