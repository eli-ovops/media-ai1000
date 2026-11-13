from pathlib import Path
import json,re,csv,hashlib
P=Path(__file__).parent
L=Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
found=None
for n,line in enumerate(L.open(encoding='utf-8'),1):
    item=json.loads(line);q=item.get('payload',{})
    if q.get('type')!='function_call_output':continue
    if not isinstance(q.get('output'),list):continue
    for index,b in enumerate(q.get('output',[])):
        if not isinstance(b,dict):continue
        text=b.get('text','')
        if text.startswith('{"verifiedNewCatalogs":'):
            found=(json.loads(text)['verifiedNewCatalogs'],{'session_path':str(L),'call_id':q['call_id'],'output_jsonl_line':n,'content_block_index':index,'timestamp':item.get('timestamp','UNKNOWN'),'source_block_sha256':hashlib.sha256(text.encode()).hexdigest()})
assert found
accounts,source=found
added=[];qualified=[]
topic=re.compile(r'AI|Agent|豆包|Claude|Codex|ChatGPT|DeepSeek|Skill|Ollama|AIGC|n8n|大模型|人工智能|智能体',re.I)
teach=re.compile(r'教程|教学|学会|手把手|工具|实测|提示词|工作|入门|测评|横评|教你|玩法|全流程|全解|解析')
for ai,a in enumerate(accounts):
    author=a['title'].split('的抖音')[0];hits=[];teaching=[]
    for ri,r in enumerate(a['rows']):
        lines=[x.strip() for x in r['text'].splitlines() if x.strip()]
        if lines[0]=='置顶':lines=lines[1:]
        title=lines[-1];body=title.split('#')[0].strip()
        has_topic=bool(topic.search(body));has_teach=has_topic and bool(teach.search(body))
        v={'video_id':r['id'],'author':author,'account_id':a['handle'],'url':'https://www.douyin.com/video/'+r['id'],'title':body,'raw_title_with_tags':title,'likes_display':lines[0],'verified_date':'2026-10-07','published_at':'UNKNOWN','duration':'UNKNOWN','play':'UNKNOWN','favorites':'UNKNOWN','comments':'UNKNOWN','shares':'UNKNOWN','read_level':'profile directory titles/likes only','ai_topic_status':'AI主题标题线索' if has_topic else '非AI或主题待核：不强行纳入','instructional_title_signal':has_teach,'core_analysis_complete':False,'source':{**source,'source_section':f'verifiedNewCatalogs[{ai}].rows[{ri}]'}}
        added.append(v)
        if has_topic:hits.append(v)
        if has_teach:teaching.append(v)
    qualified.append({'name':author,'handle':a['handle'],'profile_url':a['profileUrl'],'fans_display':a['fans'],'works_display':a['works'],'captured_ids':len(a['rows']),'matched_count':a['matchedCount'],'end_text':a['end'],'full_visible_catalog_closed':len(a['rows'])==int(a['works']) and a['end'],'ai_topic_title_count':len(hits),'instructional_title_signal_count':len(teaching),'at_least_10_ai_title_gate':len(hits)>=10,'at_least_10_instructional_title_signals':len(teaching)>=10,'content_qualification':'UNKNOWN: titles only, no full audiovisual read','first10_ai_topic_ids':[x['video_id'] for x in hits[:10]],'first10_instructional_ids':[x['video_id'] for x in teaching[:10]],'source':{**source,'source_section':f'verifiedNewCatalogs[{ai}]'}})
assert len(added)==206==len(set(x['video_id'] for x in added))
(P/'新增3账号目录原始字段.json').write_text(json.dumps({'accounts':accounts,'source':source},ensure_ascii=False,indent=2))
(P/'新增3账号资格核验.json').write_text(json.dumps(qualified,ensure_ascii=False,indent=2))
(P/'新增206条目录.json').write_text(json.dumps(added,ensure_ascii=False,indent=2))
base=json.loads((P/'作品目录.json').read_text());mapping={x['video_id']:x for x in json.loads((P/'逐条目录源回执映射.json').read_text())}
merged=[]
for x in base:
    merged.append({**x,'raw_source_title':mapping[x['video_id']]['source_title'],'source_receipt':mapping[x['video_id']]['source'],'title_projection':mapping[x['video_id']]['title_projection']})
merged.extend(added)
assert len(merged)==415==len(set(x['video_id'] for x in merged))
(P/'当前415条目录.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2))
fields=['author','account_id','video_id','url','title','likes_display','play','favorites','comments','shares','published_at','duration','verified_date','read_level','ai_topic_status','core_analysis_complete','source_call_id','source_log_line','source_section']
with (P/'当前415条目录.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
    for x in merged:
        s=x.get('source') if isinstance(x.get('source'),dict) else x['source_receipt']
        w.writerow({**x,'source_call_id':s['call_id'],'source_log_line':s['output_jsonl_line'],'source_section':s['source_section']})
candidate=list(csv.DictReader((P/'候选账号28.csv').open()))
for x in candidate:
    match=next((a for a in qualified if a['name']==x['name']),None)
    if match:x.update(source=match['profile_url'],evidence_date='2026-10-07',level='原视频作者链接与当前主页/目录已核',eligibility='至少10条AI主题标题可见；内容资格UNKNOWN',directory_observed=match['captured_ids'])
with (P/'候选账号28.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(candidate[0]));w.writeheader();w.writerows(candidate)
print(json.dumps({'new_accounts':qualified,'current_directory_ids':415,'duplicate_ids':0,'full_audiovisual':0},ensure_ascii=False))
