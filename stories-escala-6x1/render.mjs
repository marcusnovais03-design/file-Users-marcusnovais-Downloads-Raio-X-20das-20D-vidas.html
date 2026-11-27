// Gera os stories: PNG para todos e MP4 (com animação) para os que têm data-video.
import { createRequire } from 'module'; import { spawn } from 'child_process'; import { fileURLToPath } from 'url'; import path from 'path';
const require=createRequire(import.meta.url); const { chromium }=require('playwright');
const dir=path.dirname(fileURLToPath(import.meta.url)); const FPS=30;
const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(dir,'stories.html')); await p.evaluate(()=>document.fonts.ready);
const info=await p.evaluate(()=>[...document.querySelectorAll('.st')].map(s=>+s.dataset.video||0));
for(let i=0;i<info.length;i++){ const n=String(i+1).padStart(2,'0');
  await p.evaluate(i=>{show(i);setT(99);},i); await p.locator('.st.on').screenshot({path:path.join(dir,`story-${n}.png`)});
  if(!info[i]||process.env.STILL) continue;
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-i','-','-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac',path.join(dir,`story-${n}.mp4`)]);
  for(let f=0;f<info[i]*FPS;f++){ await p.evaluate(t=>setT(t),f/FPS); ff.stdin.write(await p.locator('.st.on').screenshot({type:'jpeg',quality:92})); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); console.log('mp4',n); }
await b.close();
