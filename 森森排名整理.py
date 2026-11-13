from pathlib import Path
import json,ast,csv,re,unicodedata,statistics
r=Path(__file__).resolve().parent;cat=json.load(open(r/'森森当前目录.json'));base={x['video_id']:x for x in cat['rows']};session=Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl');ins={};found={}
for n,l in enumerate(session.open(),1):
 z=json.loads(l);d=z.get('payload',{})
 if d.get('type')=='function_call' and d.get('name','').endswith('js'):ins[d.get('call_id')]=(n,d.get('arguments',''),z['timestamp'])
 if d.get('type')!='function_call_output' or d.get('call_id') not in ins:continue
 cid=d['call_id'];start,code,stamp=ins[cid]
 if not any(t in code for t in ['readSenRanking','senLikeTopBody','senOldH']):continue
 out=d.get('output',[])
 if isinstance(out,str):
  try:out=ast.literal_eval(out)
  except (ValueError,SyntaxError):continue
 if not isinstance(out,list):continue
 for bi,b in enumerate(out):
  t=b.get('text','');offset=0
  while offset<len(t):
   try:x,used=json.JSONDecoder().raw_decode(t[offset:])
   except (ValueError,TypeError):break
   if isinstance(x,dict) and x.get('video_id') in base and x.get('section'):
    found[x['video_id']]={'raw':x,'source_receipt':{'session_path':str(session),'call_id':cid,'input_jsonl_line':start,'output_jsonl_line':n,'content_block_index':bi,'text_offset':offset,'timestamp_utc':stamp}}
   offset+=used
assert set(found)==set(base), (len(found),set(base)-set(found))
def norm(t):return re.sub(r'[\W_]','',unicodedata.normalize('NFKC',re.sub(r'^第\d+集\s*\|\s*','',t))).casefold()
rows=[]
for v,f in found.items():
 x=f['raw'];expected=base[v];assert x['url']=='https://www.douyin.com/video/'+v
 assert norm(x['title'])==norm(expected['title']), (v,x['title'],expected['title'])
 metrics=x['section'][len(x['title']):].strip().splitlines();assert len(metrics)>=6
 assert all(re.fullmatch(r'\d+(?:\.\d+)?万?',s) for s in metrics[:4]);assert metrics[-1].startswith('发布时间：')
 row=dict(video_id=v,author='森森AI日记',account_id='Guuuoooiii',title=x['title'],url=x['url'],likes_display=metrics[0],comments_display=metrics[1],favorites_display=metrics[2],shares_display=metrics[3],published_at=metrics[-1].split('发布时间：',1)[1],plays='UNKNOWN',checked_date='2026-10-07',source_receipt=f['source_receipt'],title_matches_profile=True,content_card_exists=(r/'V2内容分析'/f'{v}.md').exists())
 rows.append(row)
val=lambda s:float(s[:-1])*10000 if s.endswith('万') else int(s)
for x in rows:
 x['like_rank']=1+sum(val(y['likes_display'])>val(x['likes_display']) for y in rows);x['favorite_rank']=1+sum(val(y['favorites_display'])>val(x['favorites_display']) for y in rows);x['play_rank']='UNKNOWN';x['in_front_union']=x['like_rank']<=10 or x['favorite_rank']<=10
rows.sort(key=lambda x:(x['like_rank'],x['favorite_rank']))
stats=dict(date='2026-10-07',current_public_video_count=68,public_end_observed=True,visible_note_cards=1,displayed_works=171,full_history=False,like_median_display_basis=statistics.median(val(x['likes_display']) for x in rows),favorite_median_display_basis=statistics.median(val(x['favorites_display']) for x in rows),front_union_candidates=sum(x['in_front_union'] for x in rows),final10_selected=False,plays='UNKNOWN',source_field_and_title_checks='68/68 PASS against original own-session UI outputs; PMO independent source acceptance pending')
(r/'森森68条点赞收藏排名.json').write_text(json.dumps({'statistics':stats,'rows':rows},ensure_ascii=False,indent=2))
with open(r/'森森68条点赞收藏排名.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps(stats,ensure_ascii=False))
for x in rows:
 if x['in_front_union']:print(x['video_id'],x['like_rank'],x['favorite_rank'],x['title'][:68])
