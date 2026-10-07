from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import sqlite3,json,uuid,datetime,threading,os
ROOT=Path(__file__).parent; DB=ROOT/'data'/'gems.db'; DB.parent.mkdir(exist_ok=True)
os.chdir(ROOT); lock=threading.Lock()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def conn():
 c=sqlite3.connect(DB,timeout=15); c.row_factory=sqlite3.Row; c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA foreign_keys=ON'); return c
def initdb():
 with conn() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY,module_id TEXT NOT NULL,form_path TEXT NOT NULL,record_type TEXT,status TEXT DEFAULT 'DRAFT',payload TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,created_by TEXT,updated_at TEXT NOT NULL,updated_by TEXT,project TEXT,site TEXT);
CREATE INDEX IF NOT EXISTS ix_records_form ON records(form_path,updated_at);
CREATE TABLE IF NOT EXISTS audit_log(id TEXT PRIMARY KEY,record_id TEXT,event TEXT,module_id TEXT,form_path TEXT,actor TEXT,at TEXT,version INTEGER,snapshot TEXT);
CREATE TABLE IF NOT EXISTS master_data(kind TEXT,key TEXT,value TEXT,active INTEGER DEFAULT 1,updated_at TEXT,PRIMARY KEY(kind,key));
CREATE TABLE IF NOT EXISTS shared_storage(storage_key TEXT PRIMARY KEY,payload TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1,updated_at TEXT NOT NULL,updated_by TEXT);
CREATE TABLE IF NOT EXISTS entities(id TEXT PRIMARY KEY,kind TEXT NOT NULL,code TEXT NOT NULL,name TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'ACTIVE',payload TEXT NOT NULL DEFAULT '{}',version INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,created_by TEXT,updated_at TEXT NOT NULL,updated_by TEXT,UNIQUE(kind,code));
CREATE INDEX IF NOT EXISTS ix_entities_kind ON entities(kind,status,name);
CREATE TABLE IF NOT EXISTS entity_links(id TEXT PRIMARY KEY,from_id TEXT NOT NULL,to_id TEXT NOT NULL,relation TEXT NOT NULL,created_at TEXT NOT NULL,created_by TEXT,UNIQUE(from_id,to_id,relation),FOREIGN KEY(from_id) REFERENCES entities(id),FOREIGN KEY(to_id) REFERENCES entities(id));''')
  seeds={
   'company':{'GFE':'GREENAGRO FOOD EMPORIUM'},
   'farm':{'WIKICHI':'WIKICHI','ITURIKE':'ITURIKE','IGAWA':'IGAWA'},
   'depot':{'NJOMBE_GREENAGRI_DEPOT':'NJOMBE GREENAGRI DEPOT','IGAWA_GREENAGRO_DEPOT':'IGAWA GREENAGRO DEPOT'},
   'project':{'POULTRY':'Poultry','GOAT':'Goat','CROPS':'Crops','FEED_MANUFACTURING':'Feed Manufacturing'},
   'poultry_subproject':{'LAYERS':'Layers','BROILER':'Broiler','HYBRID':'Hybrid','INDIGENOUS':'Indigenous / Kienyeji','SASSO':'Sasso'},
   'department':{'EXECUTIVE':'Executive Department','HR_ADMIN':'HR & Administration','PRODUCTION_OPERATIONS':'Production and Operations','PROCUREMENT_STORES_LOGISTICS':'Procurement, Store, Depots, Logistics & Distribution','FINANCE':'Finance','SALES_MARKETING_CS':'Sales, Marketing and Customer Services','QUALITY_ASSURANCE':'Quality Assurance & Improvement'}
  }
  t=now()
  for kind,items in seeds.items():
   for k,v in items.items(): c.execute('INSERT OR IGNORE INTO master_data(kind,key,value,active,updated_at) VALUES(?,?,?,?,?)',(kind,k,v,1,t))
  canonical={'site':{'WIKICHI':'WIKICHI Farm','ITURIKE':'ITURIKE Farm','IGAWA':'IGAWA Farm','NJOMBE_GREENAGRI_DEPOT':'NJOMBE GREENAGRI DEPOT','IGAWA_GREENAGRO_DEPOT':'IGAWA GREENAGRO DEPOT'},'project':{'POULTRY':'Poultry','GOAT':'Goat','CROPS':'Crops','FEED_MANUFACTURING':'Feed Manufacturing'},'subproject':{'LAYERS':'Layers','BROILER':'Broiler','HYBRID':'Hybrid','INDIGENOUS':'Indigenous / Kienyeji','SASSO':'Sasso'}}
  for kind,items in canonical.items():
   for code,name in items.items():
    eid=str(uuid.uuid5(uuid.NAMESPACE_URL,'gems:'+kind+':'+code)); c.execute('INSERT OR IGNORE INTO entities(id,kind,code,name,status,payload,version,created_at,created_by,updated_at,updated_by) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(eid,kind,code,name,'ACTIVE','{}',1,t,'SYSTEM_SEED',t,'SYSTEM_SEED'))
initdb()
class H(SimpleHTTPRequestHandler):
 def _json(self,obj,code=200):
  b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(b)
 def _body(self):
  try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
  except:return None
 def do_GET(self):
  u=urlparse(self.path)
  if u.path=='/api/health':
   with conn() as c: rc=c.execute('SELECT COUNT(*) n FROM records').fetchone()['n']; ac=c.execute('SELECT COUNT(*) n FROM audit_log').fetchone()['n']; mc=c.execute('SELECT COUNT(*) n FROM master_data WHERE active=1').fetchone()['n']
   return self._json({'ok':True,'service':'GEMS Central Data Engine','version':'1.4.4','database':DB.name,'records':rc,'audit_events':ac,'master_items':mc,'time':now()})
  if u.path=='/api/storage':
   q=parse_qs(u.query); keys=q.get('key',[])
   with conn() as c:
    if keys:
     ph=','.join('?'*len(keys)); rows=[dict(r) for r in c.execute(f'SELECT * FROM shared_storage WHERE storage_key IN ({ph})',keys)]
    else: rows=[dict(r) for r in c.execute('SELECT * FROM shared_storage ORDER BY storage_key')]
   for r in rows:r['payload']=json.loads(r['payload'])
   return self._json({'items':rows})
  if u.path=='/api/master-data':
   q=parse_qs(u.query); kind=q.get('kind',[None])[0]; sql='SELECT kind,key,value,active,updated_at FROM master_data'; vals=[]
   if kind: sql+=' WHERE kind=? AND active=1'; vals=[kind]
   else: sql+=' WHERE active=1'
   sql+=' ORDER BY kind,value'
   with conn() as c: rows=[dict(r) for r in c.execute(sql,vals)]
   return self._json({'items':rows})
  if u.path=='/api/entities':
   q=parse_qs(u.query); kind=q.get('kind',[None])[0]; code=q.get('code',[None])[0]; wh=['status<>?']; vals=['DELETED']
   if kind: wh.append('kind=?'); vals.append(kind)
   if code: wh.append('code=?'); vals.append(code)
   with conn() as c: rows=[dict(r) for r in c.execute('SELECT * FROM entities WHERE '+ ' AND '.join(wh)+' ORDER BY kind,name',vals)]
   for r in rows:r['payload']=json.loads(r['payload'])
   return self._json({'items':rows})
  if u.path=='/api/entity-links':
   q=parse_qs(u.query); eid=q.get('entity_id',[None])[0]
   sql='SELECT * FROM entity_links'; vals=[]
   if eid: sql+=' WHERE from_id=? OR to_id=?'; vals=[eid,eid]
   with conn() as c: rows=[dict(r) for r in c.execute(sql,vals)]
   return self._json({'items':rows})
  if u.path=='/api/records':
   q=parse_qs(u.query); wh=[]; vals=[]
   for key,col in [('module_id','module_id'),('form_path','form_path'),('project','project'),('site','site')]:
    if q.get(key): wh.append(col+'=?'); vals.append(q[key][0])
   sql='SELECT * FROM records'+((' WHERE '+' AND '.join(wh)) if wh else '')+' ORDER BY updated_at DESC LIMIT 500'
   with conn() as c: rows=[dict(r) for r in c.execute(sql,vals)]
   for r in rows:r['payload']=json.loads(r['payload'])
   return self._json({'records':rows})
  if u.path=='/api/audit':
   q=parse_qs(u.query); rid=q.get('record_id',[None])[0]; sql='SELECT * FROM audit_log'+(' WHERE record_id=?' if rid else '')+' ORDER BY at DESC LIMIT 1000'
   with conn() as c: rows=[dict(r) for r in c.execute(sql,([rid] if rid else []))]
   return self._json({'events':rows})
  return super().do_GET()
 def do_POST(self):
  if self.path=='/api/storage':
   x=self._body() or {}; key=x.get('key'); payload=x.get('payload'); actor=x.get('actor','DEVELOPMENT_USER'); expected=x.get('version')
   if not key or payload is None:return self._json({'error':'key and payload required'},400)
   t=now()
   with lock,conn() as c:
    old=c.execute('SELECT * FROM shared_storage WHERE storage_key=?',(key,)).fetchone()
    if old:
     if expected is not None and old['version']!=expected:return self._json({'error':'version_conflict','current_version':old['version']},409)
     nv=old['version']+1; c.execute('UPDATE shared_storage SET payload=?,version=?,updated_at=?,updated_by=? WHERE storage_key=?',(json.dumps(payload,ensure_ascii=False),nv,t,actor,key))
    else:
     nv=1; c.execute('INSERT INTO shared_storage VALUES(?,?,?,?,?)',(key,json.dumps(payload,ensure_ascii=False),nv,t,actor))
    c.execute('INSERT INTO audit_log VALUES(?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),'STORAGE:'+key,'SYNC','SHARED','shared_storage',actor,t,nv,json.dumps(payload,ensure_ascii=False)))
   return self._json({'ok':True,'key':key,'version':nv,'updated_at':t},201 if nv==1 else 200)
  if self.path=='/api/entities':
   x=self._body() or {}; kind=(x.get('kind') or '').strip().lower(); code=(x.get('code') or '').strip().upper(); name=(x.get('name') or '').strip(); actor=x.get('actor','DEVELOPMENT_USER')
   if kind not in {'employee','supplier','customer','item','site','project','subproject','flock_batch_cycle'}: return self._json({'error':'unsupported_entity_kind'},400)
   if not code or not name:return self._json({'error':'kind, code and name required'},400)
   rid=x.get('id') or str(uuid.uuid4()); t=now(); payload=x.get('payload') or {}
   try:
    with lock,conn() as c:
     c.execute('INSERT INTO entities(id,kind,code,name,status,payload,version,created_at,created_by,updated_at,updated_by) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(rid,kind,code,name,x.get('status','ACTIVE'),json.dumps(payload,ensure_ascii=False),1,t,actor,t,actor))
     c.execute('INSERT INTO audit_log VALUES(?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),rid,'ENTITY_CREATE','MASTER',kind,actor,t,1,json.dumps({'code':code,'name':name,'payload':payload},ensure_ascii=False)))
    return self._json({'ok':True,'id':rid,'kind':kind,'code':code,'version':1},201)
   except sqlite3.IntegrityError:return self._json({'error':'duplicate_entity','message':'This kind/code already exists. Reuse the canonical record instead of creating a duplicate.'},409)
  if self.path=='/api/entity-links':
   x=self._body() or {}; a=x.get('from_id'); b=x.get('to_id'); rel=(x.get('relation') or '').strip().upper(); actor=x.get('actor','DEVELOPMENT_USER')
   if not a or not b or not rel:return self._json({'error':'from_id, to_id and relation required'},400)
   try:
    with lock,conn() as c:
     if c.execute('SELECT COUNT(*) n FROM entities WHERE id IN (?,?)',(a,b)).fetchone()['n']!=2:return self._json({'error':'entity_not_found'},404)
     lid=str(uuid.uuid4()); c.execute('INSERT INTO entity_links VALUES(?,?,?,?,?,?)',(lid,a,b,rel,now(),actor))
    return self._json({'ok':True,'id':lid},201)
   except sqlite3.IntegrityError:return self._json({'error':'duplicate_link'},409)
  if self.path=='/api/master-data':
   x=self._body() or {}; kind=x.get('kind'); key=x.get('key'); value=x.get('value')
   if not all([kind,key,value]): return self._json({'error':'kind, key and value required'},400)
   with lock,conn() as c: c.execute('INSERT INTO master_data(kind,key,value,active,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(kind,key) DO UPDATE SET value=excluded.value,active=1,updated_at=excluded.updated_at',(kind,key,value,1,now()))
   return self._json({'ok':True,'kind':kind,'key':key},201)
  if self.path!='/api/records': return self._json({'error':'not_found'},404)
  x=self._body()
  if not x or not x.get('module_id') or not x.get('form_path') or 'payload' not in x:return self._json({'error':'module_id, form_path and payload required'},400)
  rid=x.get('id') or str(uuid.uuid4()); t=now(); actor=x.get('actor','DEVELOPMENT_USER')
  with lock,conn() as c:
   c.execute('INSERT INTO records(id,module_id,form_path,record_type,status,payload,version,created_at,created_by,updated_at,updated_by,project,site) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(rid,x['module_id'],x['form_path'],x.get('record_type'),x.get('status','DRAFT'),json.dumps(x['payload'],ensure_ascii=False),1,t,actor,t,actor,x.get('project'),x.get('site')))
   c.execute('INSERT INTO audit_log VALUES(?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),rid,'CREATE',x['module_id'],x['form_path'],actor,t,1,json.dumps(x['payload'],ensure_ascii=False)))
  return self._json({'ok':True,'id':rid,'version':1,'updated_at':t},201)
 def do_PUT(self):
  if self.path.startswith('/api/entities/'):
   rid=self.path.rsplit('/',1)[-1]; x=self._body() or {}; expected=x.get('version'); actor=x.get('actor','DEVELOPMENT_USER')
   if expected is None:return self._json({'error':'version required for concurrency control'},400)
   with lock,conn() as c:
    old=c.execute('SELECT * FROM entities WHERE id=?',(rid,)).fetchone()
    if not old:return self._json({'error':'entity_not_found'},404)
    if old['version']!=expected:return self._json({'error':'version_conflict','current_version':old['version']},409)
    nv=expected+1;t=now(); payload=x.get('payload',json.loads(old['payload'])); name=x.get('name',old['name']); status=x.get('status',old['status'])
    c.execute('UPDATE entities SET name=?,status=?,payload=?,version=?,updated_at=?,updated_by=? WHERE id=?',(name,status,json.dumps(payload,ensure_ascii=False),nv,t,actor,rid))
    c.execute('INSERT INTO audit_log VALUES(?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),rid,'ENTITY_UPDATE','MASTER',old['kind'],actor,t,nv,json.dumps({'code':old['code'],'name':name,'payload':payload},ensure_ascii=False)))
   return self._json({'ok':True,'id':rid,'version':nv,'updated_at':t})
  if not self.path.startswith('/api/records/'):return self._json({'error':'not_found'},404)
  rid=self.path.rsplit('/',1)[-1]; x=self._body() or {}; expected=x.get('version'); actor=x.get('actor','DEVELOPMENT_USER')
  if expected is None:return self._json({'error':'version required for concurrency control'},400)
  with lock,conn() as c:
   old=c.execute('SELECT * FROM records WHERE id=?',(rid,)).fetchone()
   if not old:return self._json({'error':'record_not_found'},404)
   if old['version']!=expected:return self._json({'error':'version_conflict','current_version':old['version'],'message':'Record changed by another user. Reload before updating.'},409)
   nv=expected+1;t=now(); payload=x.get('payload',json.loads(old['payload']))
   c.execute('UPDATE records SET payload=?,status=?,version=?,updated_at=?,updated_by=?,project=?,site=? WHERE id=?',(json.dumps(payload,ensure_ascii=False),x.get('status',old['status']),nv,t,actor,x.get('project',old['project']),x.get('site',old['site']),rid))
   c.execute('INSERT INTO audit_log VALUES(?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),rid,'UPDATE',old['module_id'],old['form_path'],actor,t,nv,json.dumps(payload,ensure_ascii=False)))
  return self._json({'ok':True,'id':rid,'version':nv,'updated_at':t})
 def log_message(self,fmt,*args): print('[GEMS]',fmt%args)
print('GEMS V1.4.4 running at http://127.0.0.1:8765')
ThreadingHTTPServer(('0.0.0.0',8765),H).serve_forever()
