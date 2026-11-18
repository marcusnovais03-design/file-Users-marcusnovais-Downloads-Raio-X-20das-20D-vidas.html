// Renderiza o trecho do Custo Brasil (foto + gráfico) e o cartão final, e monta o vídeo.
import { createRequire } from 'module'; import { spawn, execFileSync } from 'child_process'; import path from 'path'; import { fileURLToPath } from 'url';
const require=createRequire(import.meta.url); const { chromium }=require('playwright');
const dir=path.dirname(fileURLToPath(import.meta.url)); const FPS=30;
const INI=31, FIM=36, FOTO=1.6, FIMCARD=3.5;
const browser=await chromium.launch(); const page=await browser.newPage({viewport:{width:1080,height:1920}});
async function render(file, n, fn){
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-c:v','mjpeg','-framerate',String(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-r',String(FPS),file]);
  const done=new Promise(r=>ff.on('close',r));
  for(let f=0; f<n; f++){ const buf=await fn(f/FPS); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
  ff.stdin.end(); await done;
}
const shot=async(url,t,arg)=>{ if(page.url()!==url){ await page.goto(url); await page.evaluate(()=>document.fonts.ready); } await page.evaluate(([t,a])=>setT(t,a),[t,arg]); return page.screenshot({type:'jpeg',quality:92}); };
const u=f=>'file://'+path.join(dir,f);
const dur=FIM-INI, gdur=dur-FOTO;
await render(path.join(dir,'out','trecho.mp4'), Math.round(dur*FPS), t=> t<FOTO ? shot(u('foto.html'),t) : shot(u('grafico.html'),t-FOTO,gdur));
await render(path.join(dir,'out','fim.mp4'), Math.round(FIMCARD*FPS), t=> shot(u('fim.html'),t));
await browser.close();
const V=path.join(dir,'orig','video.mov');
execFileSync('ffmpeg',['-y','-loglevel','error','-i',V,'-itsoffset',String(INI),'-i',path.join(dir,'out','trecho.mp4'),'-i',path.join(dir,'out','fim.mp4'),
 '-f','lavfi','-t',String(FIMCARD),'-i','anullsrc=r=48000:cl=stereo',
 '-filter_complex',
 `[0:v]scale=1080:1920:flags=lanczos,setsar=1,fps=${FPS}[base];[base][1:v]overlay=0:0:eof_action=pass:enable='between(t,${INI},${FIM})'[v0];`+
 `[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];[2:v]fps=${FPS},setsar=1[v1];[3:a]aformat=channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]`,
 '-map','[v]','-map','[a]','-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-preset','medium','-c:a','aac','-b:a','160k','-movflags','+faststart',path.join(dir,'out','custo-brasil-final.mp4')]);
console.log('ok');
