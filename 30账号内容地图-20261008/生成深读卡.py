import pathlib,json,re
P=pathlib.Path(__file__).resolve().parent; OLD=P.parent
items=json.loads((P/'代表内容选择.json').read_text()); out=[]
def section(text,n):
 m=re.search(r'## '+str(n)+r'[.．、\s][^\n]*\n+(.*?)(?=\n## |\Z)',text,re.S)
 return m.group(1).strip() if m else '参见原内容卡对应章节'
(P/'深读卡').mkdir(exist_ok=True)
for x in items:
 vid=x['id']; files=list((OLD/'V2内容分析').glob(vid+'.md'))+list((OLD/'柱子哥TzFilm全量专项-20261007/内容分析').glob(vid+'.md'))
 original=files[0]; text=original.read_text(); ev=OLD/'V2本地读取/evidence'/vid
 coverage=json.loads((ev/'coverage.json').read_text()); source_path=ev/'source.json' if (ev/'source.json').exists() else ev/'coverage.json'; analyze=json.loads((ev/'analyze.json').read_text())
 s=analyze.get('structuredContent',{}); s=s.get('data',s); trans=s.get('transcript',{})
 frames=coverage.get('independent_frames_actually_read',coverage.get('frames_actually_read','UNKNOWN'))
 row={**x,'original_card':str(original),'source':str(source_path),'coverage':str(ev/'coverage.json'),'asr_receipt':str(ev/'analyze.json'),'prior_pmo_status':coverage.get('status','UNKNOWN'),'prior_full_asr_read':coverage.get('transcript_fulltext_actually_read',coverage.get('asr_full_text_actually_read','UNKNOWN')),'historical_frames_seen':frames,'returned_segment_count':len(trans.get('segments',[])),'fulltext_chars':len(trans.get('fullText','')),'new_processing':False,'continuous_audio_video':'UNKNOWN; no continuous listening/viewing in this round','this_round_status':'REUSE_ANALYSIS_PENDING_PMO'}
 out.append(row)
 body=f'''# {x['name']}｜{vid}

本轮复用同一Owner既有V2原件，不重新下载、转录或抽帧。原PMO状态：{row['prior_pmo_status']}；本轮整理待PMO验收，不自行通过。完整动态听看/语气/眼神UNKNOWN。

选样：{x['sample']}。依据：{x['basis']}。初句/前2—5秒语义：{x['opening']}。首次可见结果：{x['first_result']}。时间沿用ASR与采样的近似区间，不是精确剪切表；原ASR错词不作逐字引用。

本轮跟学判断：{x['learn']}。

## 具体内容、步骤与结果

{section(text,5)}

## 成本与坑：作者宣称和证据分开

{section(text,8)}

## 画面、PIP、字幕与转场

{section(text,7)}

## CTA及可见评论中的复现障碍

{section(text,9)}

{section(text,10)}

## 原始证据与限制

[原13项内容卡]({original})｜[源片登记]({source_path})｜[ASR回执]({ev/'analyze.json'})｜[采样覆盖及原查看回执]({ev/'coverage.json'})。

本轮实际补读原分析全文及开头ASR段；全音轨全文与实际看图记录复用先前同Owner原件。返回段数{row['returned_segment_count']}，部分长片返回上限200，尾段完整读取凭覆盖原件，不把当前返回段数当全段数。历史已看帧数量字段：{frames}（若为UNKNOWN，精确数量见原覆盖清单）。不计算竞品完播或因果；不把原PMO内容通过当本次30账号目录闭合/最终1000入选。
'''
 (P/'深读卡'/f'{vid}.md').write_text(body,encoding='utf-8')
(P/'深读证据索引.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='# 15份代表内容：复用对照\n\n9份原PMO内容通过、6份待验；本轮均为整理待验。高互动10份，普通相对对照3份，补充对照2份。老马和卡尔严格普通样本仍缺，不用“非第一名”冒充普通。三实操方法组（老马/卡尔/森森）和两头部观察组（蓝点/柱子）；森森粉丝较大，只借可缩小的任务方法，不声称其团队资源与本人一致。\n\n|作者/ID|样本/基线|开头和结果时点|可借及缺口|\n|---|---|---|---|\n'
for x in out:md+=f"|{x['name']} / [{x['id']}](深读卡/{x['id']}.md)|{x['sample']}；{x['basis']}|{x['opening']}；{x['first_result']}|{x['learn']}|\n"
(P/'代表内容对照.md').write_text(md,encoding='utf-8')
print(json.dumps({'cards':len(out),'prior_pmo_accepted':sum(x['prior_pmo_status']=='ACCEPTED_PMO_CONTENT' for x in out),'ordinary_gap_accounts':2,'new_media_processing':False},ensure_ascii=False))
