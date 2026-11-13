import {Client} from '/Volumes/EXTERNAL/自媒体/工具验证/video-mcp-20261007/upstream/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {StdioClientTransport} from '/Volumes/EXTERNAL/自媒体/工具验证/video-mcp-20261007/upstream/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
import {writeFileSync,existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url));
const target=path.join(root,'evidence','boundary','denied-inputs.json');
if(existsSync(target))throw new Error('Existing boundary receipt; do not repeat');
const c=new Client({name:'ai1000-boundary-check',version:'2.0.0'});
await c.connect(new StdioClientTransport({command:process.execPath,args:[path.join(root,'launch.mjs')],env:{PATH:'/usr/bin:/bin'},stderr:'pipe'}));
try{
 const checks=[];
 for(const source of [path.join(root,'media-manifest.json'),'https://example.com/video.mp4']){
  const r=await c.callTool({name:'video_info',arguments:{source,response_format:'json'}});
  checks.push({source,rejected:!!r.isError,receipt:r});
 }
 const allRejected=checks.every(x=>x.rejected);
 writeFileSync(target,JSON.stringify({allRejected,checks},null,2));
 console.log(JSON.stringify({allRejected,receipt:target}));
 if(!allRejected)process.exitCode=1;
}finally{await c.close();}
