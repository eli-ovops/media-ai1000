from pathlib import Path
import json,ast
r=Path(__file__).resolve().parent;session=Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
ins={};outs={}
for n,l in enumerate(session.open(),1):
 x=json.loads(l);d=x.get('payload',{})
 if d.get('type')=='function_call' and d.get('name','').endswith('js'):ins[d['call_id']]=(n,d.get('arguments',''),x['timestamp'])
 if d.get('type')=='function_call_output' and d.get('call_id'):outs[d['call_id']]=(n,d.get('output',''))
mp={'7680177709267340553':('call_ZpknkeIX0h4Qdac2yjRSxgVY','call_Oct0sH4bVg2VmtnHwTOWm1sY'),'7684228240709274931':('call_ZpknkeIX0h4Qdac2yjRSxgVY','call_ElRxA3AURqbmWr9pqSylYD4k'),'7676081471161093403':('call_ElRxA3AURqbmWr9pqSylYD4k','call_5hsU32GJK6tj90fx8YYpd7u1'),'7676814505564818723':('call_5hsU32GJK6tj90fx8YYpd7u1','call_Xs1M2lJ3hb2HaO6GRJLfhiOf'),'7678313346587774251':('call_Xs1M2lJ3hb2HaO6GRJLfhiOf','call_GMXaEcyBYiagVFuAbGaFLQ3t'),'7692006549526547727':('call_GMXaEcyBYiagVFuAbGaFLQ3t','call_hydAuSVNbY8HbNcwTbLAcfnh')}
index=[]
for v,(page,download) in mp.items():
 e=r/'V2本地读取/evidence'/v;s=json.load(open(e/'source.json'));refs=[]
 for kind,cid in [('page',page),('download',download)]:
  n,code,stamp=ins[cid];o,output=outs[cid];assert v in code and v in str(output)
  if kind=='download':assert Path(s['source_export']).name in str(output)
  refs.append(dict(kind=kind,call_id=cid,input_jsonl_line=n,output_jsonl_line=o,timestamp_utc=stamp,session_path=str(session),output_has_expected_video_id=True))
 s['original_browser_source_receipts']=refs;s['exact_browser_call_id_gap_resolved']=True
 (e/'source.json').write_text(json.dumps(s,ensure_ascii=False,indent=2));c=json.load(open(e/'coverage.json'));c['source']=s;(e/'coverage.json').write_text(json.dumps(c,ensure_ascii=False,indent=2));index.append(dict(video_id=v,receipts=refs))
rank=json.load(open(r/'老马49条点赞收藏排名.json'));found={}
for cid,(n,code,stamp) in ins.items():
 if 'readMaRanking' not in code or cid not in outs:continue
 o,output=outs[cid]
 if isinstance(output,str):
  try:output=ast.literal_eval(output)
  except (ValueError,SyntaxError):continue
 if not isinstance(output,list):continue
 for bi,b in enumerate(output):
  t=b.get('text','')
  offset=0
  while offset<len(t):
   try:d,consumed=json.JSONDecoder().raw_decode(t[offset:])
   except (ValueError,TypeError):break
   if isinstance(d,dict) and d.get('video_id') and d.get('section'):found[d['video_id']]={'raw':d,'call_id':cid,'input_jsonl_line':n,'output_jsonl_line':o,'content_block_index':bi,'text_offset':offset,'timestamp_utc':stamp,'session_path':str(session)}
   offset+=consumed

print("Located ranking raw rows:",len(found)); assert len(found)==39
for x in rank['rows']:
 if x['video_id'] not in found:continue
 f=found[x['video_id']];d=f['raw'];fields=d['section'][len(d['title']):].strip().splitlines()
 assert fields[:4]==[x['likes_display'],x['comments_display'],x['favorites_display'],x['shares_display']]
 assert fields[-1]=='发布时间：'+x['published_at']
 x['source_receipt']={k:v for k,v in f.items() if k!='raw'};x['source_fields_exact_match']=True
rank['statistics']['exact_cua_call_id_trace']='39 original outputs mapped and exact metric/date strings matched; PMO independent source audit pending'
(r/'老马49条点赞收藏排名.json').write_text(json.dumps(rank,ensure_ascii=False,indent=2))
(r/'第二批6条与老马39条源索引.json').write_text(json.dumps({'six_media':index,'ranking39':found,'validation':'39 exact first four metric fields and dates match saved ranking; no rerun'},ensure_ascii=False,indent=2))
print('6 media page/export receipt pairs mapped; 39 raw ranking outputs verified')
