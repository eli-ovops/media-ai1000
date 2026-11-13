from pathlib import Path
import json, re

r=Path(__file__).resolve().parent
s=r/'柱子哥TzFilm全量专项-20261007'
log=Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
titles={'读取投资Vlog与赛道片指标','读取手机体验与Token出海指标','读取知识库与AIGC预算指标','读取麦收Vlog与AI视频工作流指标'}
calls={}; records=[]
def decode_blocks(blocks):
    for block_no,block in enumerate(blocks):
        text=block.get('text','');offset=0
        if not text.startswith('{"url":'):continue
        while offset<len(text):
            while offset<len(text) and text[offset].isspace():offset+=1
            if offset==len(text):break
            data,end=json.JSONDecoder().raw_decode(text,offset)
            yield block_no,offset,data
            offset=end
for line_no,line in enumerate(log.open(),1):
    event=json.loads(line);p=event.get('payload',{})
    if p.get('type')=='function_call':
        a=p.get('arguments','')
        try:a=json.loads(a)
        except (ValueError,TypeError):continue
        if a.get('title') in titles or a.get('title','').startswith('专项目录详情批次'):calls[p['call_id']]=(line_no,event.get('timestamp'))
    elif p.get('type')=='function_call_output' and p.get('call_id') in calls:
        blocks=p['output']
        if not isinstance(blocks,list):continue
        for block_no,text_offset,data in decode_blocks(blocks):
            snap=data['snapshot'].replace('\\n','\n').replace('\\"','"')
            before=snap.split('- generic: 举报')[0]
            numbers=re.findall(r'^- generic: "?([0-9.]+万?)"?$',before,re.M)
            assert len(numbers)==4,(data['url'],numbers)
            date=re.search(r'发布时间：([^\n]+)',snap).group(1)
            source=dict(session_path=str(log),call_id=p['call_id'],input_jsonl_line=calls[p['call_id']][0],output_jsonl_line=line_no,content_block_index=block_no,text_offset=text_offset,timestamp_utc=calls[p['call_id']][1])
            records.append(dict(video_id=data['url'].rsplit('/',1)[1],url=data['url'],title=data['title'],likes=numbers[0],comments=numbers[1],favorites=numbers[2],shares=numbers[3],published=date,duration_sec=data['videos'][0]['duration'] or 'UNKNOWN',plays='UNKNOWN',content_analysis_added_by_this_receipt=False,source=source,snapshot_excerpt=snap))
manual_source=dict(session_path=str(log),call_id='call_aaWQAlcJrUF6hIg4Y1usDJLn',input_jsonl_line=5731,output_jsonl_line=5734)
for v,likes,comments,favs,shares,date,duration in [('7657727877504437538','12.4万','2593','5.8万','1.9万','2026-07-02 08:55',533.534),('7645203889066724646','11.7万','2106','8.3万','4.9万','2026-05-29 14:55',367.59)]:
    records.append(dict(video_id=v,url='https://www.douyin.com/video/'+v,likes=likes,comments=comments,favorites=favs,shares=shares,published=date,duration_sec=duration,plays='UNKNOWN',content_analysis_added_by_this_receipt=False,source=manual_source))
unique={x['video_id']:x for x in records}
catalog=json.loads((s/'作品目录.json').read_text())
for row in catalog['rows']:
    if row['video_id'] in unique:
        x=unique[row['video_id']]
        row.update({k:x[k] for k in ['likes','comments','favorites','shares','published','duration_sec']})
        row.update(detail_page_checked=True,detail_source=x['source'])
(s/'作品目录.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
(s/'新增详情元数据.json').write_text(json.dumps(dict(date='2026-10-07',standard='PAGE_METADATA_ONLY',content_analyses_added=0,rows=list(unique.values())),ensure_ascii=False,indent=2))
print(json.dumps(dict(metadata_rows=len(unique),ids=list(unique)),ensure_ascii=False))
