from pathlib import Path
import json,csv
s=Path(__file__).resolve().parent
catalog=json.loads((s/'作品目录.json').read_text())
rows=json.loads((s/'新增详情元数据.json').read_text())['rows']
original={x['video_id']:x for x in catalog['rows']}
assert len(rows)==101 and {x['video_id'] for x in rows}==set(original)
def number(v):return float(v.replace('万',''))*(10000 if '万' in v else 1)
for x in rows:
    x['title']=x.get('title',original[x['video_id']]['title'])
    x['content_status']=original[x['video_id']]['content_status']
rankings={}
for metric in ['likes','favorites']:
    ordered=sorted(rows,key=lambda x:(-number(x[metric]),original[x['video_id']]['order']))
    values=[number(x[metric]) for x in ordered]
    ranked=[]
    for x in ordered:
        rank=1+sum(v>number(x[metric]) for v in values)
        ranked.append(dict(video_id=x['video_id'],url=x['url'],title=x['title'],display=x[metric],approx_value=number(x[metric]),visible_rank=rank,content_status=x['content_status'],source=x['source']))
    rankings[metric]=ranked
tops={k:[x for x in v if x['visible_rank']<=10] for k,v in rankings.items()}
pool={x['video_id'] for v in tops.values() for x in v}
result=dict(date='2026-10-07',account_id='21397448654',scope='101 current public videos; all topics included',catalog_closed=True,metadata_pages_verified=101,metrics_complete=True,plays='UNKNOWN',method='Separate like and favorite ranks from displayed figures; same displayed value has same rank. Stable catalog order only formats ties. 万 figures are approximate, not exact counts.',rankings=rankings,top10=tops,candidate_union_ids=sorted(pool),candidate_union_count=len(pool),final_account_qualified=False,final_video_qualified=0,content_analyses_added=0)
(s/'全量点赞收藏排名.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
fields=list(dict.fromkeys(k for x in catalog['rows'] for k in x))
with (s/'作品目录.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(catalog['rows'])
validation=dict(rows=101,unique_ids=101,catalog_ids_match=True,all_like_favorite_comment_share_date_fields_present=all(all(x.get(k) for k in ['likes','favorites','comments','shares','published']) for x in rows),source_calls_present=all(x['source'].get('call_id') and x['source'].get('output_jsonl_line') for x in rows),missing_play_count=101,unknown_page_duration_count=sum(x['duration_sec']=='UNKNOWN' for x in rows),likes_top10_count=len(tops['likes']),favorites_top10_count=len(tops['favorites']),union_count=len(pool),content_read_unchanged=14,unread_content=87,final_qualified_videos=0)
(s/'全量排名验证.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2))
print(json.dumps(validation,ensure_ascii=False))
