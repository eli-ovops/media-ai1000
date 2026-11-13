import {Client} from 'file:///Volumes/EXTERNAL/自媒体/工具验证/video-mcp-20261007/upstream/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {StdioClientTransport} from 'file:///Volumes/EXTERNAL/自媒体/工具验证/video-mcp-20261007/upstream/node_modules/@modelcontextprotocol/sdk/dist/esm/client/stdio.js';
import {writeFileSync} from 'node:fs';
const transport=new StdioClientTransport({command:process.execPath,args:['/Volumes/EXTERNAL/自媒体/工具验证/video-mcp-20261007/launch.mjs'],env:{PATH:'/usr/bin:/bin'},stderr:'pipe'});
const client=new Client({name:'pmo-local-video-cli-check',version:'1.0.0'});
try{
 await client.connect(transport);
 const list=await client.listTools();
 const schemas=list.tools.filter(t=>['video_info','video_transcribe'].includes(t.name)).map(t=>({name:t.name,inputSchema:t.inputSchema}));
 const result=await client.callTool({name:'video_info',arguments:{source:'/Users/USER/Downloads/c0cbfe9ad16458a5845756d9a3ae9fe3_raw.mp4',response_format:'json'}},undefined,{timeout:180000});
 writeFileSync('/Volumes/EXTERNAL/自媒体/AI博主1000视频研究-20261007/CLI接入复核/pmo-cli-info-receipt.json',JSON.stringify({checkedOn:'2026-10-07',tools:list.tools.map(t=>t.name),schemas,result},null,2),{flag:'wx'});
 console.log(JSON.stringify({isError:result.isError??false,tool:'video_info',info:result.structuredContent,schemas},null,2));
 if(result.isError)process.exitCode=1;
}finally{await client.close();}
