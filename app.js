let CFG,PROFILES,FORM_KEYS={},currentProfile='OWNER',storageVersions={};const $=s=>document.querySelector(s);const norm=s=>s.toUpperCase().replace(/[^A-Z0-9]+/g,'_');
async function init(){CFG=await (await fetch('config.json')).json();PROFILES=await (await fetch('access_profiles.json')).json();FORM_KEYS=await (await fetch('form_data_keys.json')).json(); $('#version').textContent=CFG.version; const ps=$('#profile'); Object.entries(PROFILES).forEach(([k,v])=>ps.add(new Option(v.label,k))); ps.onchange=()=>{currentProfile=ps.value;renderNav();home()}; renderNav();}
function allowed(m,f){let p=PROFILES[currentProfile];if(!p.modules.includes(m.id))return false;if(!p.keywords)return true;let n=norm(f.path);return p.keywords.some(k=>n.includes(k));}
function renderNav(){let nav=$('#nav');nav.innerHTML='';let p=PROFILES[currentProfile];$('#scope').textContent='Scope: '+p.scope+' • '+p.actions.join(', ');CFG.modules.forEach(m=>{let fs=m.forms.filter(f=>allowed(m,f));if(!fs.length)return;let d=document.createElement('div');d.className='module';let b=document.createElement('button');b.textContent=m.id+' · '+m.name;b.onclick=()=>d.querySelector('.forms').classList.toggle('hidden');let list=document.createElement('div');list.className='forms hidden';fs.forEach(f=>{let x=document.createElement('button');x.className='formbtn';x.textContent=f.name;x.onclick=()=>openForm(m,f);list.appendChild(x)});d.append(b,list);nav.appendChild(d)});}
async function openForm(m,f){
 $('#home').style.display='none';$('#workspace').style.display='flex';$('#title').textContent=m.name+' / '+f.name+' · Syncing…';document.querySelector('.app').classList.remove('menu');
 const keys=FORM_KEYS[f.path]||[];
 try{
  if(keys.length){let q=new URLSearchParams();keys.forEach(k=>q.append('key',k));let data=await (await fetch('/api/storage?'+q)).json();let found=new Set();(data.items||[]).forEach(x=>{found.add(x.storage_key);storageVersions[x.storage_key]=x.version;localStorage.setItem(x.storage_key,JSON.stringify(x.payload))});keys.filter(k=>!found.has(k)).forEach(k=>localStorage.removeItem(k));}
  const frame=$('#frame');frame.onload=()=>installAdapter(frame,m,f,keys);frame.src='/'+f.path.split('/').map(encodeURIComponent).join('/');$('#title').textContent=m.name+' / '+f.name;
 }catch(e){$('#title').textContent=m.name+' / '+f.name+' · OFFLINE';alert('Central data engine is not reachable. Start GEMS through START_GEMS.bat/server.py; this form will not be treated as centrally synchronized.');$('#frame').src='/'+f.path.split('/').map(encodeURIComponent).join('/');}
}
function installAdapter(frame,m,f,keys){
 try{const w=frame.contentWindow,proto=w.Storage.prototype,orig=proto.setItem;if(w.__gemsAdapter)return;w.__gemsAdapter=true;
  proto.setItem=function(k,v){let out=orig.call(this,k,v);if(keys.includes(k)){let payload;try{payload=JSON.parse(v)}catch(e){payload=v}syncStorage(k,payload,m,f)}return out};
  const badge=document.getElementById('syncState');if(badge)badge.textContent='CENTRAL SYNC ACTIVE';
 }catch(e){console.error('GEMS adapter',e)}
}
async function syncStorage(key,payload,m,f){
 try{let body={key,payload,actor:currentProfile,module_id:m.id,form_path:f.path};if(storageVersions[key])body.version=storageVersions[key];let r=await fetch('/api/storage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let x=await r.json();if(r.status===409){alert('Another user updated this data. Reload the form before saving again.');return}if(!r.ok)throw Error(x.error||'sync failed');storageVersions[key]=x.version;window.dispatchEvent(new CustomEvent('gems-sync',{detail:{key,version:x.version}}));}catch(e){alert('Central save failed. Your change is not yet confirmed in the company database.');console.error(e)}
}
function home(){ $('#workspace').style.display='none';$('#frame').src='about:blank';$('#home').style.display='block';}
function toggleMenu(){document.querySelector('.app').classList.toggle('menu')}
window.addEventListener('message',e=>{if(e.data&&e.data.type==='GEMS_RECORD_SAVED')console.log('GEMS event',e.data)});init();