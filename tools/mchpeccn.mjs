const UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";
const part=process.argv[2]||"ATTINY817-MFR";
const jar={};
function store(setc){ for(const c of (setc||[])){ const [kv]=c.split(";"); const i=kv.indexOf("="); jar[kv.slice(0,i).trim()]=kv.slice(i+1).trim(); } }
function ch(){ return Object.entries(jar).map(([k,v])=>k+"="+v).join("; "); }
async function g(u, extra={}){ const r=await fetch(u,{headers:{"User-Agent":UA,"Accept-Language":"en-US,en;q=0.9",...extra,"Cookie":ch()},redirect:"manual"}); store(r.headers.getSetCookie?r.headers.getSetCookie():[]); return r; }
await g("https://www.microchipdirect.com/exportcontroldata/",{"Accept":"text/html"});
await g("https://www.microchipdirect.com/public/3b368268c29ca44bb15967c0988bebdaa41ffdc51a38",{"Accept":"*/*","Referer":"https://www.microchipdirect.com/exportcontroldata/"});
const H={"Accept":"application/json, text/plain, */*","X-Requested-With":"XMLHttpRequest","Referer":"https://www.microchipdirect.com/exportcontroldata/"};
for(const u of [
  `https://www.microchipdirect.com/api/ExportControlDataAPI/GetExactMatchCPNResult?CPN=${encodeURIComponent(part)}`,
  `https://www.microchipdirect.com/api/ExportControlDataAPI/GetComplainceData?searchType=partnumber&value=${encodeURIComponent(part)}`,
]){
  const r=await g(u,H); const t=await r.text();
  console.log("\nURL "+u+"\nSTATUS "+r.status+" LEN "+t.length+" CT "+(r.headers.get("content-type")||""));
  console.log(t.slice(0,1200));
}
