import { chromium } from "playwright";
const parts = process.argv.slice(2);
const browser = await chromium.launch({ channel:"chrome", headless: true, args:["--no-sandbox"] });
const ctx = await browser.newContext({ userAgent:"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", locale:"en-US", viewport:{width:1400,height:1000} });
const page = await ctx.newPage();

async function search(part){
  console.log("\n##### "+part+" #####");
  let postBody=null;
  const handler = async r=>{ if(/FetchExport/i.test(r.url())){ try{postBody=await r.text();}catch{} } };
  page.on("response", handler);
  await page.goto("https://www.analog.com/exportclassification/search",{waitUntil:"domcontentloaded",timeout:35000}).catch(()=>{});
  // wait for app to hydrate (search.js + exportClassification.min.mjs)
  await page.waitForTimeout(7000);
  const ta = await page.$("textarea#textarea-1");
  if(!ta){ console.log("NO TEXTAREA"); page.off("response",handler); return; }
  await ta.click();
  await page.keyboard.type(part, {delay:50});
  await page.waitForTimeout(400);
  // click Search and wait for the FetchExport POST
  const [resp] = await Promise.all([
    page.waitForResponse(r=>/FetchExport/i.test(r.url()), {timeout:20000}).catch(()=>null),
    page.click("button.adi__button[type='submit']").catch(e=>console.log("clickerr",e.message)),
  ]);
  if(resp){ try{postBody=await resp.text();}catch{} }
  let row=null;
  for(let i=0;i<20;i++){
    await page.waitForTimeout(700);
    const rows = await page.$$eval("table tr", rs=>rs.map(r=>[...r.querySelectorAll("td")].map(c=>c.textContent.trim())).filter(a=>a.join("").replace(/\s/g,"").length)).catch(()=>[]);
    const hit = rows.find(r=>r.join(" ").toUpperCase().includes(part.toUpperCase().slice(0,8)));
    if(hit){ row=hit; break; }
  }
  console.log("RENDERED DATA ROW (human-visible): "+JSON.stringify(row));
  if(postBody){ try{ const j=JSON.parse(postBody); const m=(j.Results||[]).find(x=>x.ModelNumber&&x.ModelNumber.toUpperCase().includes(part.toUpperCase().slice(0,8))); if(m) console.log("XHR CONFIRM: "+m.ModelNumber+" | ECCN="+m.ECCN+" | HTS="+m.US_Commodity_Code); }catch{} }
  page.off("response", handler);
}
for(const p of parts) await search(p);
await browser.close();
