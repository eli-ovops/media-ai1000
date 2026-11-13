from pathlib import Path
import json,re

s=Path(__file__).resolve().parent
catalog=json.loads((s/'作品目录.json').read_text())
excluded={
'7613632402225518912','7693329038437272883','7678721079619095818',
'7664836560172420386','7661427628527668520','7655929148405239046',
'7631423156305038619','7627020092957560118','7626003445854696000',
'7622527949773868331','7612849202427205620','7611337363885009588',
'7609172561171250676','7605432434842422863','7604286670153731378',
'7564451016972815668','7514980094625074451','7486407473658711296'}
pending={
'7687223099644742975','7663641387790863626','7651445780917521714',
'7649247380734233871','7647837495219981595','7645203889066724646',
'7628171122265758080','7623284022780710185','7621476241194929427',
'7610192341270103138'}
rows=[]
for x in catalog['rows']:
    v=x['video_id'];card=s/'内容分析'/(v+'.md')
    if v in excluded:
        scope='EXCLUDED';reason='Personal goals, daily life, general business, photography or non-AI topic in visible title; not scheduled for reading.'
    elif v in pending:
        scope='PENDING_RELEVANCE';reason='Visible title/context is insufficient to confirm substantive AI relevance; not counted or automatically read.'
    else:
        scope='AI_RELATED';reason='Explicit AI tools/models/workflows/industry/robots in title, description or existing content analysis.'
    row=dict(video_id=v,url=x['url'],title=x['title'],scope=scope,scope_reason=reason,content_card_exists=card.exists(),classification_evidence='existing content card' if card.exists() else 'public title/description only',final_qualified=False)
    rows.append(row);x.update(ai_scope=scope,ai_scope_reason=reason)
groups={k:[x for x in rows if x['scope']==k] for k in ['AI_RELATED','EXCLUDED','PENDING_RELEVANCE']}
result=dict(date='2026-10-07',authorization='User narrowed specialty to AI-related content only; no requirement to read all101',original_catalog_count=101,ai_related_candidates=len(groups['AI_RELATED']),ai_related_cards_read=sum(x['content_card_exists'] for x in groups['AI_RELATED']),ai_related_unread=sum(not x['content_card_exists'] for x in groups['AI_RELATED']),excluded=len(groups['EXCLUDED']),pending_relevance=len(groups['PENDING_RELEVANCE']),rows=rows,notes=['Title-based screening is provisional and does not prove full content or final sample eligibility.','AI-related includes tools, models, workflows, industry, AI careers and robots. Pure Vlog/general business is excluded.','Existing non-AI evidence is retained; no file deletion. Original1000 target remains.'])
(s/'AI相关筛选.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(s/'作品目录.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
rank=json.loads((s/'全量点赞收藏排名.json').read_text())
allowed={x['video_id'] for x in groups['AI_RELATED']}
filtered={}
for metric in ['likes','favorites']:
    subset=[dict(x) for x in rank['rankings'][metric] if x['video_id'] in allowed]
    statuses={x['video_id']:x['content_status'] for x in catalog['rows']}
    for x in subset:x['content_status']=statuses[x['video_id']]
    for x in subset:x['ai_scope_rank']=1+sum(y['approx_value']>x['approx_value'] for y in subset)
    filtered[metric]=subset
pool={x['video_id'] for values in filtered.values() for x in values if x['ai_scope_rank']<=10}
(s/'AI相关点赞收藏排名.json').write_text(json.dumps(dict(date='2026-10-07',scope='AI_RELATED candidates only; pending/excluded outside active ranking',candidate_count=len(allowed),rankings=filtered,top10_union_ids=sorted(pool),final_qualified=False,plays='UNKNOWN'),ensure_ascii=False,indent=2))
text=['# AI相关内容读取范围','','用户已将专项收窄为只读取AI相关内容。原101条目录仅作为索引。',f"当前筛选：{result['ai_related_candidates']}条AI相关候选（已读{result['ai_related_cards_read']}、未读{result['ai_related_unread']}），{result['excluded']}条不安排读取，{result['pending_relevance']}条相关性待判。",'', '工具、模型、工作流、AI产业/就业及机器人保留。纯日常、家具、普通商业故事、摄影等不进入当前读取队列。题名不明确的待判条目不凑进目标；已有原件和分析卡保留。','','筛选主要依据题名/说明，已读作品另有内容证据；不等于候选均已读或最终入选。当前原片导出阻断仍存在，未增加下载重试。']
(s/'AI相关读取范围.md').write_text('\n'.join(text)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['rows','notes']},ensure_ascii=False))
