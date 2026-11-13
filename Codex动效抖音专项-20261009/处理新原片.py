import pathlib,json,subprocess,concurrent.futures
P=pathlib.Path(__file__).resolve().parent
node='/Users/USER/.local/nodejs/node-v22.16.0-darwin-arm64/bin/node'
reader=P/'read-public-video.mjs';helper=P/'evidence-helper.py'
def process(f):
 vid=f.stem;e=P/'evidence'/vid;e.mkdir(exist_ok=True)
 for mode in ['info','analyze']:
  if mode=='analyze' and not (e/'analyze.json').exists():
   meta=json.loads((e/'info.json').read_text())['structuredContent']
   exports={json.loads(x.read_text())['source_export'] for x in P.glob('evidence/*/source.json')}
   current=sum(x.stat().st_size for x in P.parent.rglob('*') if x.is_file())+sum(pathlib.Path(x).stat().st_size for x in exports if pathlib.Path(x).exists())
   reserve=int(meta['durationSec']*32000)+20*1024**2
   if current+reserve>3*1024**3:
    (e/'cache-budget-block.json').write_text(json.dumps({'current_bytes':current,'audio_and_frames_reserved_bytes':reserve,'duration':meta['durationSec'],'limit_bytes':3*1024**3,'status':'BUDGET_BLOCKED_NO_ANALYSIS'}))
    return {'id':vid,'budget_blocked':True}
  if not (e/f'{mode}.json').exists():
   with (e/f'{mode}.log').open('w') as log:subprocess.run([node,str(reader),mode,vid],stdout=log,stderr=log,check=True)
 a=json.loads((e/'analyze.json').read_text())['structuredContent'];duration=a['info']['durationSec']
 if not (e/'burst-fullspan.json').exists():
  (e/'fullspan.request.json').write_text(json.dumps({'start_sec':0,'end_sec':max(1,duration-.2),'count':30,'inline_images':False,'response_format':'json'}))
  with (e/'burst-fullspan.log').open('w') as log:subprocess.run([node,str(reader),'burst',vid,'fullspan'],stdout=log,stderr=log,check=True)
 if not (e/'fullspan-1.jpg').exists():subprocess.run(['/Users/USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',str(helper),'sheets',vid,'fullspan'],check=True,stdout=subprocess.DEVNULL)
 return {'id':vid,'duration':duration,'processed_not_yet_read':True}
fs=[f for f in (P/'media').glob('*.mp4') if not (P/'内容卡'/f'{f.stem}.md').exists()]
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
 for x in pool.map(process,fs):print(json.dumps(x),flush=True)
