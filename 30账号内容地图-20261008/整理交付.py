import json,pathlib,re,csv,datetime
P=pathlib.Path(__file__).resolve().parent; OLD=P.parent
def read(name): return json.loads((P/name).read_text())
def save(name,data): (P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def clean(s): return s.replace('\\n','\n').replace('\\"','"') if isinstance(s,str) else s
def topic(title):
 for words,label in [('FDE|企业|商业|商单|交付','企业AI/项目与交付'),('成本|积分|价格|收费|免费|省钱','费用/选型'),('PPT|汇报|报告|表格|Excel|会议|办公','办公任务'),('稿|标题|写作|文章|文案','写作与内容表达'),('视频|短剧|电影|分镜|特效|广告片|配音|音频|声音','AI内容创作'),('代码|编程|网站|建模|游戏|Codex|Vibe','AI编程/项目'),('Skill|技能|工作流','可复用流程'),('Agent|智能体|管家','Agent与自动化'),('模型|发布|手机|芯片|硬件','模型/产品/设备'),('学|科普|术语|知识','AI学习/解释')]:
  if re.search(words,title,re.I):return '题名初筛：'+label
 return '题名初筛：AI经验/产品观察，正文待核'
judgment=read('账号判断.json'); profiles=read('当前主页目录汇总.json'); search=read('账号搜索原始读取.json')
identities={}
for ev in search:
 d=ev['data']
 if not isinstance(d,dict) or 'query' not in d:continue
 name=d['query']
 for u in d.get('users',[]):
  if clean(u.get('text','')).split('\n')[0].replace(' ','')==name.replace(' ','') and name not in identities:identities[name]={**u,'receipt':ev['receipt']}
# Existing source files enrich metadata without reprocessing media.
source_by_id={}
source_files=[OLD/'首批10条页面核验.json',OLD/'柱子哥TzFilm全量专项-20261007/新增详情元数据.json']+list((OLD/'V2本地读取/evidence').glob('*/source.json'))
def visit(obj,path):
 if isinstance(obj,list):
  for x in obj:visit(x,path)
 elif isinstance(obj,dict):
  vid=str(obj.get('video_id',''))
  if vid and any(k in obj for k in ['published','published_at','page_snapshot']):
   o=obj.get('page_snapshot',obj); pub=o.get('published_at',o.get('published','UNKNOWN'))
   if pub!='UNKNOWN':source_by_id[vid]={'published_at':pub,'metrics_snapshot':o,'metadata_source':str(path),'date':o.get('verified_date',obj.get('date','2026-10-07'))}
  for x in obj.values():
   if isinstance(x,(dict,list)):visit(x,path)
for f in source_files:
 if f.exists():visit(json.loads(f.read_text()),f)
for d in read('逐条日期补核.json'):
 if d.get('published'):
  vid=d['url'].split('/video/')[-1].split('?')[0];source_by_id[vid]={'published_at':d['published'].replace('发布时间：',''),'metrics_snapshot':d.get('metadata',''),'metadata_source':d['receipt'],'date':'2026-10-08'}
accounts=[]; works=[]; excluded=[]
exclude_ids={'7694045671120325930','7693329038437272883','7677992118283218422','7668299359222091135','7688923048283557174','7694252772195110185','7690586315393355048'}
for name,j in judgment.items():
 prof=profiles.get(name,{}); ident=identities.get(name,{})
 header=clean(prof.get('header','')); text=clean(ident.get('text',''))
 aid=re.search(r'抖音号：\s*([^\s\n]+)',header); fans=re.search(r'粉丝\n([^\n]+)',header)
 search_fans=re.search(r'获赞(\d+(?:\.\d+)?(?:万|亿)?)粉丝',text)
 nameworks=[]
 for w in prof.get('works',[]):
  vid=w['url'].split('/video/')[-1].split('?')[0]; txt=clean(w['text']); lines=txt.split('\n'); title=' '.join(x.strip() for x in lines[1:] if x.strip()).split('#')[0].strip()
  if vid in exclude_ids:
   excluded.append({'name':name,'video_id':vid,'title':title,'reason':'主题非AI知识/经验或相关性不足；不以AI话题标签算合格'});continue
  md=source_by_id.get(vid,{})
  pub=md.get('published_at','UNKNOWN')
  try: window='近90天' if datetime.datetime.fromisoformat(pub[:16])>=datetime.datetime(2026,7,10) else '已扩到90天以前'
  except Exception:window='窗口UNKNOWN：发布时间待核'
  row={'name':name,'platform':'抖音','video_id':vid,'url':w['url'],'title':title[:120], 'published_at':pub,'window':window,'likes_display':lines[0].strip(),'plays':'UNKNOWN','comments':'UNKNOWN','favorites':'UNKNOWN','shares':'UNKNOWN','read_level':'L1主页目录，不能复述操作正文','topic':j[1],'verified_date':'2026-10-08','source_receipt':prof.get('receipt'),'date_source':md.get('metadata_source','UNKNOWN'),'interaction_detail':md.get('metrics_snapshot','UNKNOWN')}
  if isinstance(md.get('metrics_snapshot'),dict):
   for k in ['comments','favorites','shares']:row[k]=md['metrics_snapshot'].get(k,'UNKNOWN')
  row['topic']=topic(title)
  if isinstance(md.get('metrics_snapshot'),str):
   values=[v.strip() for v in clean(md['metrics_snapshot']).split('举报')[0].splitlines() if v.strip()][:4]
   if len(values)==4:
    for key,value in zip(['likes_display','comments','favorites','shares'],values):
     if re.fullmatch(r'\d+(?:\.\d+)?(?:万|亿)?',value):row[key]=value
  nameworks.append(row)
 works+=nameworks
 profile_url=prof.get('url',ident.get('url','UNKNOWN'))
 accounts.append({'name':name,'group':j[0],'platform':'抖音','account_id':aid.group(1) if aid else 'UNKNOWN','profile_sec_uid':profile_url.split('/user/')[-1].split('?')[0] if '/user/' in profile_url else 'UNKNOWN','profile_url':profile_url,'fans_display':fans.group(1) if fans else search_fans.group(1) if search_fans else 'UNKNOWN','search_scale_raw':text.split('\n\n')[1] if '\n\n' in text else text,'evidence_date':'2026-10-08','audience_and_problem_inference':j[1],'content_pillars':j[1],'visual_form_and_evidence':j[2],'adaptation_effort_estimate':j[3],'learn_and_avoid':j[4],'current_directory_rows':len(nameworks),'eligibility':'V2部分支持' if '已有V2' in j[2] else '候选初筛，尚非最终合格','team_size_actual':'UNKNOWN','production_time_actual':'UNKNOWN','group_basis':'制作方法可局部借用的实操候选；不以粉丝小等于资源近' if j[0]=='实操对标' else '领域内相对头部观察候选；非平台认证排名','source_receipt':prof.get('receipt',ident.get('receipt','UNKNOWN'))})
save('账号表.json',accounts);save('近期内容表.json',works);save('非AI与相关性剔除.json',excluded)
for name,data in [('账号表.csv',accounts),('近期内容表.csv',works)]:
 with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(data[0]) if data else []);wr.writeheader()
  for row in data:wr.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})
print(json.dumps({'accounts':len(accounts),'groups':{g:sum(a['group']==g for a in accounts) for g in ['实操对标','头部候选']},'directory_rows':len(works),'date_known':sum(w['published_at']!='UNKNOWN' for w in works),'directory_gaps':[(a['name'],a['current_directory_rows']) for a in accounts if a['current_directory_rows']<10],'excluded':len(excluded)},ensure_ascii=False))
