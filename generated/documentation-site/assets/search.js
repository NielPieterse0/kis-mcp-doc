const B="/kis-mcp-doc";
const TOKEN_RE=/[A-Za-z0-9][A-Za-z0-9_-]*/g;
function kisRankSearch(i,q,limit=i.default_limit){
 if(!Number.isInteger(limit)||limit<1)throw new Error('search limit must be a positive integer');
 const ts=(q.match(TOKEN_RE)||[]).map(t=>t.toLowerCase()).filter(t=>t.length>=i.minimum_token_length);
 const weight=i.contract.title_weight;
 return i.documents.map(d=>{const score=ts.reduce((s,t)=>s+(d.terms[t]||0)+weight*(d.title_terms[t]||0),0);const matched_terms=ts.reduce((n,t)=>n+((d.terms[t]||d.title_terms[t])?1:0),0);return {score,matched_terms,d};})
  .filter(x=>x.score>0).sort((a,b)=>b.matched_terms-a.matched_terms||b.score-a.score||(a.d.route<b.d.route?-1:a.d.route>b.d.route?1:0)).slice(0,limit);
}
globalThis.kisRankSearch=kisRankSearch;
if(typeof document!=='undefined'&&typeof fetch!=='undefined'){fetch(B+'/search-index.json').then(r=>r.json()).then(i=>{
 const f=document.querySelector('#search-form'),q=document.querySelector('#q'),o=document.querySelector('#results');
 f.addEventListener('submit',e=>{e.preventDefault();const rs=kisRankSearch(i,q.value);o.replaceChildren();
  for(const x of rs){const li=document.createElement('li'),a=document.createElement('a');a.href=B+x.d.route;a.textContent=x.d.title;li.append(a,document.createTextNode(' - '+x.d.family));o.appendChild(li);}
 });
});}
