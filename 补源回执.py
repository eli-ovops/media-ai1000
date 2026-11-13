from pathlib import Path
import json,re,ast,csv,hashlib

ROOT=Path(__file__).parent
LOG=Path('/Users/USER/.codex/sessions/2026/10/07/rollout-2026-10-07T10-47-54-01a11442-a6d9-7413-88b3-191ce5cb037b.jsonl')
calls={}
for line_no,line in enumerate(LOG.open(encoding='utf-8'),1):
    item=json.loads(line); p=item.get('payload',{})
    if p.get('type')=='function_call_output' and p.get('call_id'):
        calls[p['call_id']]={'line':line_no,'timestamp':item.get('timestamp','UNKNOWN'),'blocks':p.get('output',[])}

def block(call,index): return calls[call]['blocks'][index]['text']
def pointer(call,index,section):
    s=block(call,index)
    return {'session_path':str(LOG),'call_id':call,'output_jsonl_line':calls[call]['line'],'content_block_index':index,'source_section':section,'source_block_sha256':hashlib.sha256(s.encode()).hexdigest(),'timestamp':calls[call]['timestamp']}
def js_string_field(text,key):
    # Decode printed JS string literals as data; never execute a source receipt.
    pattern=r"\b"+re.escape(key)+r":\s*((?:'(?:\\.|[^'\\])*'\s*\+?\s*)+)"
    m=re.search(pattern,text)
    if not m: raise ValueError('Missing printed string field '+key)
    return ''.join(ast.literal_eval(s) for s in re.findall(r"'(?:\\.|[^'\\])*'",m[1]))
def title_norm(t):
    t=re.sub(r'^第\d+集\s*\|\s*','',t).split('#')[0]
    return ''.join(c for c in t if c.isalnum())

directory=json.loads((ROOT/'作品目录.json').read_text())
mapped=[]
c49='call_0bbac9ff438941069d0fdad36eac432e'
cinitial='call_b18d35689baa46d68532385f02118119'
c101='call_9951aaea6845468bac9395bef8f07617'
raw49=json.JSONDecoder().raw_decode(block(c49,1))[0]
initial_text=block(cinitial,1)
initial=json.loads(initial_text[initial_text.index('{"bpData"'):])
sources={}
for call,index,section,rows in [(c49,1,'lmDirectory',raw49),(cinitial,1,'JSON object bpData/kpData: kpData.rows',initial['kpData']['rows']),(cinitial,1,'JSON object bpData/kpData: bpData.rows',initial['bpData']['rows'])]:
    for i,r in enumerate(rows):
        txt=r['text']; ls=[s.strip() for s in txt.splitlines() if s.strip()]
        if ls[0]=='置顶':ls=ls[1:]
        sources[r['id']]={'like':ls[0],'title':ls[-1],'pointer':pointer(call,index,section+'['+str(i)+']')}
for i,line in enumerate(block(c101,1).splitlines()):
    if not re.match(r'^\d{19}\t',line):continue
    vid,likes,title=line.split('\t',2)
    title=re.sub(r'\{ count: \d+, end: (?:true|false) \}$','',title).rstrip()
    sources[vid]={'like':likes,'title':title,'pointer':pointer(c101,1,'TSV row '+str(i+1)+'; video_id='+vid+'; exclude adjacent count output')}
for r in directory:
    src=sources[r['video_id']]
    check={'like_display_match':r['likes_display']==src['like'],'title_normalized_match':title_norm(r['title'])==title_norm(src['title']),'title_prefix_projection_match':title_norm(src['title']).startswith(title_norm(r['title']))}
    mapped.append({'video_id':r['video_id'],'author':r['author'],'source':src['pointer'],'source_title':src['title'],'local_title':r['title'],'title_projection':'exact normalized' if check['title_normalized_match'] else 'shortened prefix; full source title retained here','checks':check,'read_layer':'directory only; no audiovisual coverage'})
assert len(mapped)==209
directory_gaps=[x for x in mapped if not x['checks']['title_normalized_match']]
assert all(x['checks']['like_display_match'] and x['checks']['title_prefix_projection_match'] for x in mapped)
(ROOT/'逐条目录源回执映射.json').write_text(json.dumps(mapped,ensure_ascii=False,indent=2))

sample=json.loads((ROOT/'首批10条页面核验.json').read_text())
c7='call_f55a9ae015a542239b5e1f337e0e5c2e'
raw7=json.loads(block(c7,1)); tabs={str(i):vid for i,vid in zip(range(7,14),['7685352868332817707','7690167561530461503','7682715455454186790','7654922329579518885','7674224670610412987','7668610752106551168','7671969297027699961'])}
details={}
for i,x in enumerate(raw7):
    d=x['data'];details[tabs[x['tab']]]={'heading':d['heading'],'metadata':d['metadata'],'duration':d['video'][0]['duration'],'comments':d.get('comments',''),'pointer':pointer(c7,1,'pageEvidence['+str(i)+'].data'),'raw_title':d['heading']}
clm='call_be0acc2ca23d453a867a3fc2467a72b5'
lmraw=block(clm,2);lmbody=js_string_field(lmraw,'body')
lmheading=next(s for s in lmbody.splitlines() if s.startswith('Ai改稿，'))
details['7674623106060799247']={'heading':lmheading,'metadata':lmbody[lmbody.index(lmheading):].split('全部评论')[0],'duration':88.8,'comments':lmbody.split('全部评论')[1],'pointer':pointer(clm,2,'laomaData.body; heading through publication and comments'),'duration_pointer':pointer(clm,2,'laomaData.video[0].duration'),'raw_title':lmheading}
cblue='call_ea777ccd3685402ba14652379a56f4c3';bbody=block(cblue,2)
details['7674081798107926115']={'heading':bbody.splitlines()[0],'metadata':bbody.split('全部评论')[0],'duration':58.7,'comments':bbody.split('全部评论')[1],'pointer':pointer(cblue,2,'video body; heading through publication and comments'),'duration_pointer':pointer('call_dd95a3d51ec74d16ac023b267494cdb0',1,'blueData.video[0].duration'),'raw_title':bbody.splitlines()[0]}
kraw=block(cinitial,1);kbody=js_string_field(kraw,'text');kh=js_string_field(kraw,'heading')
details['7613370565042130211']={'heading':kh,'metadata':kbody.split('全部评论')[0],'duration':20.533333,'comments':kbody.split('全部评论')[1],'pointer':pointer(cinitial,1,'karlTab heading/text; metadata and comments'),'duration_pointer':pointer('call_dd95a3d51ec74d16ac023b267494cdb0',1,'karlData.video[0].duration'),'raw_title':kh}
sample_maps=[]
for r in sample:
    src=details[r['video_id']];m=src['metadata'];ls=[s.strip() for s in m.splitlines() if s.strip()]
    count_fields=['likes_display','comments','favorites','shares']
    parsed=dict(zip(count_fields,ls[1:5]));parsed['published_at']=re.search(r'发布时间：\s*(\d{4}-\d\d-\d\d \d\d:\d\d)',m)[1]
    checks={k:str(r[k])==v for k,v in parsed.items()}
    checks['duration_match']=abs(r['duration']-src['duration'])<1e-6
    checks['title_normalized_match']=title_norm(r['title'])==title_norm(src['heading'])
    sample_maps.append({'video_id':r['video_id'],'metadata_source':src['pointer'],'duration_source':src.get('duration_pointer',src['pointer']),'raw_source_heading':src['heading'],'normalized_source_heading':re.sub(r'^第\d+集\s*\|\s*','',src['heading']),'normalized_local_title':r['title'],'observed_metadata':parsed,'duration':src['duration'],'checks':checks,'coverage':'metadata/comments only; full audiovisual remains 0'})
assert len(sample_maps)==10
assert all(all(x['checks'].values()) for x in sample_maps), [(x['video_id'],x['checks']) for x in sample_maps if not all(x['checks'].values())]
(ROOT/'首批10条源回执映射.json').write_text(json.dumps(sample_maps,ensure_ascii=False,indent=2))
(ROOT/'源映射验证.json').write_text(json.dumps({'directory_ids':len(mapped),'sample_ids':len(sample_maps),'directory_like_checks_passed':209,'directory_full_title_normalized_match':len(mapped)-len(directory_gaps),'shortened_title_prefix_ids':[x['video_id'] for x in directory_gaps],'sample_metadata_checks_passed':10,'raw_source_session_read':'one exact session only; no full log copied','normalization':'strip episode prefix/hashtags and ignore punctuation/whitespace only; numerical facts unchanged; two shortened titles explicitly labeled','full_audiovisual':0},ensure_ascii=False,indent=2))
print('PASS: 209 directory mappings and 10 detail mappings; audiovisual=0')
