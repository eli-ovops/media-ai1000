from pathlib import Path
import csv,json,statistics
P=Path(__file__).parent
U='UNKNOWN'
profiles={
'老马':{'name':'AI超能力老马','id':'87440545928','fans':'1.4万','total':49,'url':'https://www.douyin.com/user/MS4wLjABAAAAm3thU0vuwSUYHwllsWj8OeTwROImCxwv36JE1GEeTjc'},
'卡尔':{'name':'卡尔的AI沃茨','id':'88851320170','fans':'9.4万','total':318,'url':'https://www.douyin.com/user/MS4wLjABAAAAEzzpje5yWF2u-fVb77MLTlBdIgcWGKu0_WtMsyje5mStjRmOXgQ78WGY7D-ilFnT'},
'蓝点':{'name':'蓝点Ai','id':'1233488477nn','fans':'89.3万','total':141,'url':'https://www.douyin.com/user/MS4wLjABAAAAQGEi_JUIKYhpyiuzLtwOj4JBh7t92cWH9BUS-WASTHNsPUceA5Soibtt8iq-KLtX'}}
allrows=[]
for key,a in profiles.items():
 rows=list(csv.DictReader(P.joinpath(key+'-目录原始字段.tsv').open(),delimiter='\t'))
 a['captured']=len(rows)
 def val(v): return float(v[:-1])*10000 if v.endswith('万') else int(v)
 eligible=[r for r in rows if r['video_id']!='7521342122201599272']
 ranks=sorted(set(val(r['likes_display']) for r in eligible),reverse=True)
 for r in rows:
  r.update(author=a['name'],account_id=a['id'],url='https://www.douyin.com/video/'+r['video_id'],verified_date='2026-10-07',source='CUA IAB DOM 当前主页；人工投影标题正文，不含话题标签',play=U,favorites=U,comments=U,shares=U,published_at=U,duration=U,ai_topic_status='排除：非AI充电宝指南' if r['video_id']=='7521342122201599272' else '标题线索待内容核验',like_rank='排除' if r['video_id']=='7521342122201599272' else str(1+sum(val(x['likes_display'])>val(r['likes_display']) for x in eligible)),rank_scope=f'{len(eligible)}条已取得目录候选；非全历史',read_level='目录标题与赞数',content_complete=False)
  allrows.append(r)
 a['median_likes_display_scope']=statistics.median(val(r['likes_display']) for r in rows)
 a['scope_note']='49个ID与页面49条及终止文案一致；公开可见范围，删除/私密UNKNOWN' if key=='老马' else '只取得初始已链接作品；主页数量不一致，分页未闭合；非全账号TOP'
 # rounded 万 values only used to order display tiers, not exact statistics
 if key=='蓝点': a['median_likes_display_scope']='仅展示档位，不能作精确中位数'
P.joinpath('作品目录.json').write_text(json.dumps(allrows,ensure_ascii=False,indent=2))
fields=list(allrows[0].keys())
with P.joinpath('作品目录.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(allrows)
P.joinpath('账号目录核验.json').write_text(json.dumps(list(profiles.values()),ensure_ascii=False,indent=2))
# Direct page observations. Never count page chapters as content read.
specs=[
('老马','7674623106060799247','2026-08-16 21:37',88.8,'2713','89','4786','718','文案改稿','页面标题是模糊改稿指令改成七个动作；正文只有平台AI章节，非原片转录。','可见多条评论要求七条指令的文字版；一条评论整理了七个动作，属于评论者文字，不能当作者逐字稿。','00:00 优化一下的问题；00:43 七条改稿指令；01:06 检查事项（均为平台AI章节）','一个模糊指令→具体编辑动作→检查事实；只是待原片验证的我方结构设想。'),
('老马','7685352868332817707','2026-09-14 19:34',38.010998,'7464','771','1.2万','1677','文案改稿','标题称整理七条改稿指令，完整台词未取得。','评论反复求改稿指令；有评论请求提取结尾滑动截图。后者只证明观众请求，截图是否存在未核。',U,'一个常见错误→给文字清单→展示一次修改；应公开易复制文本，避免看完仍求入口。'),
('老马','7690167561530461503','2026-09-27 18:57',33.134875,'3215','657','5455','1092','文案去模板味','标题称七条比去掉AI味更具体的指令，实际视听与完整内容未读。','可见评论列七条建议，也有多条求指令；作者可见回复包含收到、好的、发你了。不能证明实际私信送达或转化。',U,'先点出抽象要求→一项具体改法→前后对照；不把加入事实当作编造事实授权。'),
('老马','7682715455454186790','2026-09-07 16:59',54.466667,'2.6万','336','2.7万','1.1万','AI漫剧工具','标题是漫剧制作门槛低的疑问；工具与步骤未由原片核实。','评论有会员费用、花费后效果不佳、入口缺失和版权疑问；全部是评论者自述，价格及效果未独立核实。',U,'展示一小段结果→明确工具/费用→保留失败→只教一步；成本要本人实际核验。'),
('卡尔','7613370565042130211','2026-03-04 20:07',20.533333,'18.9万','986','15.3万','2.5万','工具汇总','标题是2025与2026十类工具对照，20秒。逐项工具画面与台词未完整读。','可见评论围绕替代关系、价格、是否需要全部学习；有评论报告PPT文字多时字体乱和错字，属于其体验。',U,'任务→只选一个工具→成本/限制；不沿用所有工具都要学的负担。'),
('卡尔','7654922329579518885','2026-06-24 19:28',114.358005,'4751','97','363','133','模型工作流实测','标题称六个工作流；平台AI章节提示代码修复、网页、游戏、报告/PPT及多模态。原片及各案例完整证据未读。','评论问数学、代码、工作入口；有第三方自述识字成功。不能升级为模型性能验收。','00:07 代码；00:30 网页；00:47 小游戏；01:07 日常/多模态；01:36 总结（平台AI章节）','一个已有任务→两次修正→验收状态；比六案例同时做更适合个人起步。'),
('卡尔','7674224670610412987','2026-08-15 19:51',221.749002,'2536','23','177','31','视频模型比较','标题称9万积分；平台AI章节提示五类场景比较三个模型，不能确认真实测试输入、成本与所有结果。','作者可见评论称烧了十万积分，与标题9万存在口径差异；有人问降价，有人对暗部颜色持不同评价。','00:23 MV；00:54文字动画；01:24打斗；02:02广告；02:30大场面；03:04总结（平台AI章节）','同一任务、同一提示、逐个结果、失败记录与费用；本人只做一场景，避免照搬积分预算。'),
('蓝点','7674081798107926115','2026-08-15 10:36',58.7,'2.0万','118','233','172','电商图','标题称一招量产电商图；本轮未读操作、产品细节或音频。','可见评论问软件名、网页版/APP、版权、是否麻烦、产品细节还原。不能将宣传评论或点赞认作商家身份/销量。',U,'原图→一项设置→生成→核对实物细节；工具入口和失败例应公开。'),
('蓝点','7668610752106551168','2026-07-31 16:46',133.677007,'3.0万','119','396','321','Skill拆解视频','平台AI章节声称定制八维度框架与成片；未核真正读取视频方式，也不能据作者宣称证明我们的通路。','可见评论问八个维度具体是什么；其余多为评价，身份与是否复现UNKNOWN。','00:18 定制框架；00:57实用性；01:43成片；02:01结语（平台AI章节）','公开一个分析维度→用一条材料说明→给可复制模板；不能把AI摘要当原片读取。'),
('蓝点','7671969297027699961','2026-08-09 17:59',65.41,'2.7万','64','172','164','短剧Agent','平台AI章节提及小云雀、剧本、风格/画幅和角色；仅平台摘要，工具当前能力/可得性未验。','可见评论问能否接住细节设定、剧本是否逻辑混乱和运镜质感。不能由评论反推作者实际镜头。','00:12 小云雀；00:23 使用方法；00:49效果（平台AI章节）','一段故事→设定检查→结果→明确失败；不承诺一句话完成专业剧。')]
records=[];carddir=P/'首批10条欠项卡';carddir.mkdir(exist_ok=True)
lookup={r['video_id']:r for r in allrows}
for key,vid,date,dur,likes,comments,favs,shares,theme,obs,demand,chapter,suggestion in specs:
 r=lookup[vid];d=dict(r);d.update(published_at=date,duration=dur,likes_display=likes,comments=comments,favorites=favs,shares=shares,theme=theme,read_level='当前原页面标题/指标/可见评论/平台AI章节(若有)/播放器状态',observed=obs,comment_need=demand,ai_chapter_index=chapter,full_audio_read=False,full_dynamic_video_read=False,transcript=U,unread_range=f'00:00—{dur:.3f}秒的完整动态画面及音频均未读取',core_analysis_complete=False,like_rank=r['like_rank'],favorite_rank=U,play_rank=U,selection_reason='通路压力测试候选；在已取得目录的赞数前列，收藏全目录未核，尚非最终综合TOP10',our_structure_hypothesis=suggestion)
 records.append(d)
 a=profiles[key]
 text=f'''# {a['name']}｜{r['title']}

状态：页面初筛/欠项；不计完整声画或核心深拆。核验日期2026-10-07。

1. 身份与原件：账号{a['id']}；[原视频]({r['url']})；video ID {vid}；{date}；播放器时长{dur:.6f}秒。受众仅按标题推定，主题{theme}。
2. 页面指标（赞/评/藏/转）：{likes} / {comments} / {favs} / {shares}。播放UNKNOWN；万级保留展示约数，非精确值。
3. 选择：{a['captured']}条已取得目录中的赞数可见名次{r['like_rank']}，同档并列；收藏/播放名次UNKNOWN。{a['scope_note']}。这批只验证通路，不是最终各账号TOP10。通常表现基线仅目录赞数，未读普通内容。
4. 读取证据：CUA IAB原页面与播放器readyState=4、muted=true；页面可见文字。完整动态/音频/全字幕均0。未读范围为全片0—{dur:.3f}秒。原片未下载，不用少量截图代替全片。
5. 实际可知内容：{obs} 详细时序复述UNKNOWN。
6. 开头表达、结果时间、转折、信息密度与真实时长分配：UNKNOWN。可定位辅助：{chapter}。平台AI章节不能升级为作者内容读取。
7. 口播、眼神、表情、镜头、录屏比例、字幕样式、剪辑节奏、配乐/音效：UNKNOWN；本轮未听音/看全动态。
8. 证据与宣称：仅核页面存在这些标题和公开评论；省时、效果、测试成本及结果正确性未独立验证，不能变成我方成果。
9. 片内CTA：UNKNOWN。页面作者回复与评论求入口若有，不能替代片尾CTA或私信交付回执。
10. 评论需求：{demand} 只取当前可见便利样本，不能代表全部观众或付费意向。
11. 高表现解释：观察是公开赞/藏及评论需求；合理解释是具体工具/指令可能减少搜索成本；待验假设是结构、节奏或结果展示影响互动。作者已有受众、热点、发布时间和投流UNKNOWN，不能断言因果/完播率/自然流量。
12. 我方候选借鉴：{suggestion} 这是基于标题/评论的待验设计，非原片验证结构。单一文本或已有录屏任务约1.5—3小时（估计）；多模型/付费生成通常更高，作者工时UNKNOWN。
13. 可复述摘要：这条公开页面围绕“{theme}”，可见观众有上述需求；原片细节待完整声画读取。暂用结构设想：{suggestion}

欠项：完整动态画面、音频、全字幕、真实逐时序分析、视听、作者证据、片尾CTA、全目录收藏/播放排名。核心深拆计数0。
'''
 carddir.joinpath(vid+'.md').write_text(text)
P.joinpath('首批10条页面核验.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
with P.joinpath('首批10条清单.csv').open('w',newline='') as f:
 fields=['author','account_id','video_id','url','title','published_at','duration','play','likes_display','comments','favorites','shares','like_rank','favorite_rank','play_rank','rank_scope','read_level','unread_range','core_analysis_complete']
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(records)
# Provisional TOP10 by directory likes only, not combined final selection.
selected=[]
for key,a in profiles.items():
 rows=[r for r in allrows if r['author']==a['name'] and r['like_rank']!='排除']
 rows.sort(key=lambda r:(float(r['likes_display'][:-1])*10000 if r['likes_display'].endswith('万') else int(r['likes_display'])),reverse=True)
 # Blue only prioritizes explicit teaching/use titles. Remaining effects kept in directory but not forced into teaching top list.
 if key=='蓝点': rows=[r for r in rows if any(t in r['title'] for t in ['教','Agent','ChatGpt','PPT','Skill','导演','建筑'])]
 for r in rows[:10]:selected.append({**r,'selection_status':'暂选：仅按可见点赞，收藏未枚举；同档并列不可作精确排序'})
with P.joinpath('3账号可见点赞暂选10条.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(selected[0]));w.writeheader();w.writerows(selected)
assert len({r['video_id'] for r in allrows})==len(allrows)
assert len(records)==10 and len({r['video_id'] for r in records})==10
assert all(not r['core_analysis_complete'] for r in records)
P.joinpath('本批验证.json').write_text(json.dumps({'directory_rows':len(allrows),'directory_duplicate_ids':0,'sample_rows':10,'sample_duplicate_ids':0,'matching_local_cards':len(list(carddir.glob('*.md'))),'full_dynamic_and_audio':0,'core_analysis':0,'all_selected_sample_ids_in_directory':all(r['video_id'] in lookup for r in records),'media_download_bytes':0,'status':'字段与唯一性检查通过；业务最终验收未完成'},ensure_ascii=False,indent=2))
print(f'目录{len(allrows)}、页面10、卡10、暂选{len(selected)}、重复0；声画0、深拆0')
