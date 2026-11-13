from pathlib import Path
import json,csv,statistics
r=Path(__file__).resolve().parent
raw='''7687961830458740003 100 1 84 14 2026-09-21 20:18
7674242822328962331 91 3 84 22 2026-08-15 21:01
7680510584764239145 89 抢首评 41 7 2026-09-01 18:23
7681284402537712950 83 抢首评 37 9 2026-09-03 20:26
7675711697117580582 76 3 77 13 2026-08-19 20:01
7685734364553989419 70 36 92 16 2026-09-15 20:14
7688371473337027883 68 6 10 6 2026-09-22 22:48
7679401583641218331 63 1 51 21 2026-08-29 18:40
7690926428967144730 47 4 36 8 2026-09-29 20:02
7686092149917601059 45 2 15 1 2026-09-17 07:50
7680924972725980451 45 1 72 18 2026-09-02 21:11
7679034464034919529 43 1 43 8 2026-08-28 18:55
7675333317377428736 40 2 24 6 2026-08-18 19:33
7678677534011149614 39 抢首评 43 6 2026-08-27 19:50
7691298708675169563 37 1 22 4 2026-09-30 20:07
7681514720217648390 37 抢首评 18 1 2026-09-04 18:20
7676454232060398857 36 抢首评 18 6 2026-08-21 20:03
7681517730649951526 33 2 55 14 2026-09-05 18:35
7686089417747959074 30 1 23 4 2026-09-16 19:12
7692413519664303400 26 2 18 7 2026-10-03 20:13
7681519978285223183 24 抢首评 36 11 2026-09-06 18:40
7691674337455230217 23 3 22 6 2026-10-01 20:24
7689767526577835305 23 3 21 7 2026-09-26 19:30
7679812558240386344 22 抢首评 27 5 2026-08-30 21:15
7674990194566729003 21 1 20 6 2026-08-17 21:21
7677614527676042511 20 5 18 5 2026-08-24 23:05
7692779502711180595 18 6 10 1 2026-10-04 19:53
7677944215208332590 17 4 1 分享 2026-08-25 20:25
7690544610229161242 16 4 11 2 2026-09-28 19:21
7686506064203894062 11 1 7 3 2026-09-18 08:00
7683889655497968939 11 抢首评 9 1 2026-09-10 20:56
7689382819998485801 10 1 6 2 2026-09-25 16:12
7688661808160279817 10 抢首评 6 1 2026-09-23 17:34
7673835835849985289 10 1 1 1 2026-08-14 18:42
7689111016508050742 9 1 12 1 2026-09-24 22:37
7683103713891831092 9 抢首评 3 1 2026-09-08 18:06
7677193736392117555 7 抢首评 1 2 2026-08-23 19:52
7693156653553683763 4 抢首评 5 分享 2026-10-05 20:17
7686459514798886184 3 抢首评 1 1 2026-09-17 19:08'''
base={x['video_id']:x for x in json.load(open(r/'当前415条目录.json')) if x['author']=='AI超能力老马'}
rows=[]
for l in raw.splitlines():
 v,likes,comments,favs,shares,date,time=l.split();b=base[v]
 rows.append(dict(video_id=v,title=b['title'],url=b['url'],likes_display=likes,comments_display=comments,favorites_display=favs,shares_display=shares,published_at=date+' '+time,plays='UNKNOWN',checked_date='2026-10-07',read_level='public detail metadata only; no content reading inferred',source='CUA IAB browser2/tab36; h1 and visible body before comments; current conversation tool outputs; exact CUA call_id UNKNOWN'))
assert len(rows)==39
old=[x for x in json.load(open(r/'首批10条页面核验.json')) if x['author']=='AI超能力老马']
for x in old:rows.append(dict(video_id=x['video_id'],title=x['title'],url=x['url'],likes_display=x['likes_display'],comments_display=x['comments'],favorites_display=x['favorites'],shares_display=x['shares'],published_at=x['published_at'],plays='UNKNOWN',checked_date='2026-10-07',read_level='earlier same-day detail metadata with source receipts',source='首批10条页面核验.json and source receipt map'))
for v in ['7680177709267340553','7684228240709274931','7676081471161093403','7676814505564818723','7678313346587774251','7692006549526547727']:
 s=json.load(open(r/'V2本地读取/evidence'/v/'source.json'))['page_snapshot'];rows.append(dict(video_id=v,title=s['title'],url='https://www.douyin.com/video/'+v,likes_display=str(s['likes']),comments_display=str(s['comments']),favorites_display=str(s['favorites']),shares_display=str(s['shares']),published_at=s['published_at'],plays='UNKNOWN',checked_date='2026-10-07',read_level='current page metadata + V2 content read; pending acceptance',source='V2 evidence source.json; public AX reread this turn; precise CUA call_id UNKNOWN'))
assert len(rows)==49 and set(x['video_id'] for x in rows)==set(base)
def displayed(s):return float(s[:-1])*10000 if s.endswith('万') else int(s)
for x in rows:
 for field,out in [('likes_display','like_rank'),('favorites_display','favorite_rank')]:x[out]=1+sum(displayed(y[field])>displayed(x[field]) for y in rows)
 x['play_rank']='UNKNOWN';x['content_complete']=(r/'V2内容分析'/f"{x['video_id']}.md").exists()
 x['selected_candidate']=x['like_rank']<=10 or x['favorite_rank']<=10
rows.sort(key=lambda x:x['like_rank'])
selected=[x for x in rows if x['selected_candidate']];assert len(selected)==10
stats={'scope':'49/49 current visible catalog; not lifetime highest','published_range':[min(x['published_at'] for x in rows),max(x['published_at'] for x in rows)],'plays':'UNKNOWN','median_likes_display_basis':statistics.median(displayed(x['likes_display']) for x in rows),'median_favorites_display_basis':statistics.median(displayed(x['favorites_display']) for x in rows),'selection':'Union of like top10 and favorite top10, exactly same 10 IDs; no invented weighted score','v2_selected_content_cards':sum(x['content_complete'] for x in selected),'accepted_selected_content':1,'pmo_ranking_acceptance':'PENDING','final_account_qualified':False,'exact_cua_call_id_trace':'UNKNOWN for new page reads; page tool outputs preserved in current conversation'}
(r/'老马49条点赞收藏排名.json').write_text(json.dumps({'statistics':stats,'rows':rows},ensure_ascii=False,indent=2))
with open(r/'老马49条点赞收藏排名.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
report='# 老马账号可见范围TOP10候选｜点赞与收藏已对照\n\n49/49当前目录，2026-08-14至2026-10-05，采集2026-10-07；不能称全历史最高。播放UNKNOWN，按点赞与收藏独立排名；二者前10恰好是同10个视频，未使用虚构权重。点赞中位37，收藏中位22。9条内容卡、1条漫剧关键ASR漏段；PMO仅首条内容通过，排名与本账号整体待验收。\n\n|标题|点赞名次|收藏名次|内容状态|\n|---|---:|---:|---|\n'
for x in selected:report+=f"|[{x['title']}]({x['url']})|{x['like_rank']}|{x['favorite_rank']}|{('PMO内容已通过' if x['video_id']=='7685352868332817707' else 'V2内容卡待PMO验收') if x['content_complete'] else 'ASR欠项'}|\n"
report+='\n可见内容多以具体办公困境开场，给数字清单/可复制文本，结尾收藏或索取资料；九条已读内容支持该观察。完整声音、动态眼神、完播与投流UNKNOWN，不能判断模板导致传播或借用原作者效果。最高赞漫剧与其余写作提示词主题不同，且内容证据未足，暂不纳入完整账号总结。\n\n来源：排名JSON保留每行快照和读法；原目录及首批详情有已有源回执，新增39条页面精确CUA call_id未出现在本地session，保留追溯欠项；不能虚构call_id。\n'
(r/'老马TOP10候选与账号阶段分析.md').write_text(report)
p=r/'进度.json';s=json.load(open(p));s.update(detail_metadata_verified=55,ranking_complete_visible_accounts=1,ranking_pmo_accepted_accounts=0,current_page_metadata_only_additions=39);p.write_text(json.dumps(s,ensure_ascii=False,indent=2))
print(json.dumps(stats,ensure_ascii=False))
