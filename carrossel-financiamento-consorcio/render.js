const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:1400},deviceScaleFactor:1});
await p.goto('file://'+path.join(__dirname,'index.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
for(let i=1;i<=7;i++)await p.locator('#s'+i).screenshot({path:path.join(__dirname,'slides',`slide-${i}.png`)});
await b.close()})();
