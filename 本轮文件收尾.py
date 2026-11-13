from pathlib import Path
import json,hashlib
P=Path(__file__).parent
LOG=Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
needles={'qiu':'var qiuData=','mcgy':'var mcIdentity='}
callkeys={};outputs={}
for n,l in enumerate(LOG.open(encoding='utf-8'),1):
    d=json.loads(l);q=d.get('payload',{})
    if q.get('type')=='function_call':
        args=q.get('arguments','')
        for k,needle in needles.items():
            if needle in str(args):callkeys[k]=q.get('call_id')
    elif q.get('type')=='function_call_output' and q.get('call_id'):
        outputs[q['call_id']]=(n,q.get('output',[]))
qualpath=P/'新增3账号资格核验.json';q=json.loads(qualpath.read_text())
for a in q:
    k='qiu' if a['handle']=='32571643812' else 'mcgy'
    cid=callkeys[k];n,blocks=outputs[cid]
    a['identity_video_id']={'32571643812':'7530952671742659892','89106176878':'7633093681914984306','83660160':'7507937839561067812'}[a['handle']]
    a['identity_source']={'session_path':str(LOG),'call_id':cid,'output_jsonl_line':n,'source_section':'qiuData.authorLinks/heading' if k=='qiu' else ('mcIdentity' if a['handle']=='89106176878' else 'gyIdentity'),'note':'observed author anchor from exact original video page, then profile URL'}
qualpath.write_text(json.dumps(q,ensure_ascii=False,indent=2))
newnames=['补源回执.py','逐条目录源回执映射.json','首批10条源回执映射.json','源映射验证.json','保存新增目录.py','新增3账号目录原始字段.json','新增3账号资格核验.json','新增206条目录.json','当前415条目录.json','当前415条目录.csv','本地CLI公开素材接入与证据层.md','外部通路调研收口.md','本轮续接回执.md','本轮补正验证.json','本轮文件收尾.py']
inventory_path=P/'生成物记录.json'
old=json.loads(inventory_path.read_text());paths={x['path'] for x in old['files']}
paths.update(str(P/n) for n in newnames)
paths.add(str(inventory_path))
assert all(Path(x).is_file() and Path(x).is_relative_to(P) for x in paths)
files=[{'path':x,'bytes':Path(x).stat().st_size,'purpose':'Owner research output/source mapping/PMO review; retain'} for x in sorted(paths)]
inventory_path.write_text(json.dumps({'source':'Explicit Owner-created paths only; excludes PMO task/acceptance/CLI receipts and tool Owner files','files':files,'temporary_media':[],'deleted_files':[],'note':'No media download, ASR/frame generation, installation or shared tool file writes'},ensure_ascii=False,indent=2))
print({'owned_artifacts':len(files),'total_bytes_before_inventory_update':sum(x['bytes'] for x in files),'new_public_media_bytes':0,'cleanup':False})
