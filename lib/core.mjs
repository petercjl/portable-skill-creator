import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json')));
export const name = 'portable-skill-creator';
export const source = path.join(root, 'skills', name);
export const receiptName = '.portable-skill-install.json';
export const readJSON = p => JSON.parse(fs.readFileSync(p, 'utf8'));
export const exists = p => {try {fs.lstatSync(p); return true;} catch(e) {if(e.code==='ENOENT') return false; throw e;}};
export function fail(code, message, details={}) {throw Object.assign(new Error(message), {code, details});}
export function create(p, bytes) {if(exists(p)) fail('TARGET_EXISTS', 'Refusing existing file', {path:p}); fs.mkdirSync(path.dirname(p),{recursive:true}); fs.writeFileSync(p,bytes,{flag:'wx'});}
export function files(dir, prefix='') {
  return fs.readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(d=>{
    const rel=path.posix.join(prefix,d.name), p=path.join(dir,d.name);
    if(d.isSymbolicLink()) fail('UNSAFE_LINK','Symbolic links are not distributable resources',{path:p});
    return d.isDirectory()?files(p,rel):[rel];
  });
}
export const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function hashes(dir) {return Object.fromEntries(files(dir).map(f=>[f,hash(path.join(dir,f))]));}
export function copy(from,to) {if(exists(to)) fail('TARGET_EXISTS','Copy destination exists',{path:to}); fs.cpSync(from,to,{recursive:true,dereference:false,errorOnExist:true,force:false});}
export function targetOf(o) {
  if(!o.agent || !/^[a-z][a-z0-9-]{0,63}$/.test(o.agent)) fail('INVALID_AGENT','Supply a valid Agent identifier and its resolved --target');
  if(!o.target || !path.isAbsolute(o.target)) fail('TARGET_REQUIRED','--target must be the absolute exact Skill directory resolved by the current Agent');
  const t=path.resolve(o.target);
  const ownInstalledRuntime = root===path.join(t,'.runtime');
  if(t===path.parse(t).root || t===os.homedir() || t===root || t===source || (!ownInstalledRuntime&&root.startsWith(t+path.sep)) || t.startsWith(root+path.sep)) fail('UNSAFE_TARGET','Target overlaps a protected or source directory');
  let p=path.dirname(t);
  while(p!==path.dirname(p)) {if(exists(p)&&fs.lstatSync(p).isSymbolicLink()) fail('UNSAFE_TARGET','Parent path contains a symlink',{path:p}); p=path.dirname(p);}
  return t;
}
export function status(o) {
  const target=targetOf(o), installed=exists(target), rp=path.join(target,receiptName);
  let receipt=null;
  if(installed && !fs.lstatSync(target).isSymbolicLink() && exists(rp)) {
    try {receipt=readJSON(rp);}catch {fail('INVALID_RECEIPT','Receipt is malformed; preserve it before recovery',{path:rp});}
  }
  const managed=Boolean(receipt?.package===pkg.name && receipt?.name===name && receipt?.target===target && receipt?.agent===o.agent);
  if(managed && (!receipt.hashes || typeof receipt.hashes!=='object' || Object.entries(receipt.hashes).some(([f,h])=>path.isAbsolute(f)||f.split(/[\\/]/).includes('..')||typeof h!=='string'||!/^[a-f0-9]{64}$/.test(h)))) fail('INVALID_RECEIPT','Receipt hashes missing or unsafe');
  const edited=managed?Object.entries(receipt.hashes).filter(([f,h])=>exists(path.join(target,f)) && (fs.lstatSync(path.join(target,f)).isSymbolicLink() || hash(path.join(target,f))!==h)).map(([f])=>f):[];
  const missing=managed?Object.keys(receipt.hashes).filter(f=>!exists(path.join(target,f))):[];
  const canonical=managed && exists(path.join(target,'agents/openai.yaml')) && Object.entries(hashes(source)).filter(([f])=>f!=='agents/openai.yaml').every(([f,h])=>exists(path.join(target,f))&&hash(path.join(target,f))===h) && runtimeFiles().every(f=>exists(path.join(target,'.runtime',f))&&hash(path.join(target,'.runtime',f))===hash(path.join(root,f)));
  const verified=managed && edited.length===0 && missing.length===0;
  return {ok:true,name,package:pkg.name,version:pkg.version,target,agent:o.agent,installed,managed,current:Boolean(verified&&canonical&&receipt.version===pkg.version),edited,missing,verification:{verified,algorithm:'sha256'},recovery:{required:managed&&!verified,backup:receipt?.backup??null},entry:path.join(target,'.runtime','bin',name+'.mjs'),hostDiscovery:{authority:'host',status:'pending'}};
}
export function install(o) {
  const before=status(o), t=before.target;
  if(before.installed&&!before.managed) fail('UNMANAGED_TARGET','Existing Skill is user-owned; move it to a verified backup before installing',{target:t});
  if(before.edited.length) fail('LOCAL_EDITS','Managed files have local edits; preserve and reconcile them first',{edited:before.edited});
  if(before.current) return {...before,changed:false};
  fs.mkdirSync(path.dirname(t),{recursive:true});
  const lock=t+'.install-lock';
  try {fs.mkdirSync(lock);} catch(e) {if(e.code==='EEXIST') fail('LOCKED','Another maintenance operation may be active',{lock});throw e;}
  let stage,backup=null;
  try {
    stage=fs.mkdtempSync(t+'.stage-');
    for(const f of files(source)) {const p=path.join(stage,f);fs.mkdirSync(path.dirname(p),{recursive:true});fs.copyFileSync(path.join(source,f),p,fs.constants.COPYFILE_EXCL);}
    const runtime=path.join(stage,'.runtime');fs.mkdirSync(runtime);
    for(const f of runtimeFiles()) {const p=path.join(runtime,f);fs.mkdirSync(path.dirname(p),{recursive:true});fs.copyFileSync(path.join(root,f),p,fs.constants.COPYFILE_EXCL);}
    if(before.installed) {
      const again=status(o);
      if(again.edited.length) fail('LOCAL_EDITS','Concurrent modification detected');
      backup=fs.mkdtempSync(t+'.backup-');
      copy(t,path.join(backup,'skill'));
      for(const f of files(t)) {
        if(f===receiptName || f==='agents/openai.yaml' || f.startsWith('.runtime/') || Object.hasOwn(readJSON(path.join(t,receiptName)).hashes,f)) continue;
        if(exists(path.join(stage,f))) fail('UNMANAGED_COLLISION','Unmanaged file collides with new managed resource',{file:f,backup});
        fs.mkdirSync(path.dirname(path.join(stage,f)),{recursive:true});fs.copyFileSync(path.join(t,f),path.join(stage,f));
      }
      const metadata=path.join(t,'agents/openai.yaml');
      if(exists(metadata)) fs.copyFileSync(metadata,path.join(stage,'agents/openai.yaml'));
    }
    const owned=Object.keys(hashes(source)).filter(f=>f!=='agents/openai.yaml').concat(runtimeFiles().map(f=>'.runtime/'+f));
    const digest=Object.fromEntries(owned.map(f=>[f,hash(path.join(stage,f))]));
    create(path.join(stage,receiptName),JSON.stringify({schemaVersion:1,name,package:pkg.name,version:pkg.version,target:t,agent:o.agent,hashes:digest,backup,installedAt:new Date().toISOString()},null,2)+'\n');
    if(before.installed) {
      try {fs.renameSync(t,path.join(backup,'previous'));}
      catch(e) {
        if(!['EPERM','EACCES','EBUSY'].includes(e.code)) throw e;
        // Recoverable copy fallback for a live host that locks directory rename.
        const old=readJSON(path.join(t,receiptName));
        for(const f of Object.keys(old.hashes)) if(exists(path.join(t,f))) fs.rmSync(path.join(t,f),{force:true});
        fs.rmSync(path.join(t,receiptName));
        fs.cpSync(stage,t,{recursive:true,force:true});
        fs.rmSync(stage,{recursive:true});stage=null;
      }
    }
    if(stage) {fs.renameSync(stage,t);stage=null;}
    const result=status(o);
    if(!result.current) fail('VERIFICATION_FAILED','Skill synchronization incomplete',{backup,target:t});
    return {...result,changed:true,backup,physicalCopy:true};
  } catch(e) {
    e.details={...e.details,backup,target:t,recovery:backup?'Original copy is in backup/skill; inspect state before retrying':'Inspect target and lock before retrying'};
    throw e;
  } finally {if(stage&&exists(stage)) fs.rmSync(stage,{recursive:true,force:true});fs.rmSync(lock,{recursive:true,force:true});}
}
export function runtimeFiles() {
  return ['package.json','capabilities.json','README.md','INSTALL.md','UPDATE.md','LICENSE',...['bin','lib','skills'].flatMap(d=>files(path.join(root,d)).map(f=>d+'/'+f))];
}
export function python(o={}) {
  const candidates=[o.python,process.env.PORTABLE_SKILL_PYTHON,process.env.VIRTUAL_ENV&&path.join(process.env.VIRTUAL_ENV,process.platform==='win32'?'Scripts/python.exe':'bin/python'),'python3','python',...(process.platform==='win32'?['py']:[])].filter(Boolean);
  for(const command of [...new Set(candidates)]) {
    const args=command==='py'?['-3']:[];
    const r=spawnSync(command,[...args,'-c','import json,sys; print(json.dumps({"version":list(sys.version_info[:3]),"executable":sys.executable}))'],{encoding:'utf8',timeout:5000,windowsHide:true});
    if(r.status===0) {try {const p=JSON.parse(r.stdout);if(p.version[0]===3&&p.version[1]>=10) return {command,args,...p};}catch {}}
  }
  fail('PYTHON_REQUIRED','Python 3.10+ is required. Supply --python or configure PORTABLE_SKILL_PYTHON. No third-party Python modules are required.');
}
export function doctor(o) {
  const p=python(o);
  return {ok:true,package:pkg.name,version:pkg.version,node:process.version,python:p,dependencies:[{name:'skill-creator',required:true,resolution:'Current Agent must resolve exact advertised logical name and read complete SKILL.md',status:'host-verification-required'}],hostDiscovery:{authority:'host',status:'pending'},paidServices:[]};
}
export function validate(o) {
  if(!o.path||!path.isAbsolute(o.path)||!exists(path.join(o.path,'SKILL.md'))) fail('INVALID_INPUT','--path must be an existing absolute Skill directory');
  if(!['shareable','internal','platform','local'].includes(o.profile??'shareable')) fail('INVALID_INPUT','Invalid profile');
  if(!['direct','hybrid','knowledge-compiled'].includes(o.mode??'direct')) fail('INVALID_INPUT','Invalid knowledge mode');
  const p=python(o), commands=[['validate_portability.py',o.path,'--profile',o.profile??'shareable'],['validate_knowledge_layer.py',o.path,'--mode',o.mode??'direct']];
  if(exists(path.join(o.path,'capabilities.json'))) commands.push(['validate_capability_contract.py',o.path]);
  const results=commands.map(([script,...args])=>{
    const r=spawnSync(p.command,[...p.args,path.join(source,'scripts',script),...args],{encoding:'utf8',timeout:30000,windowsHide:true});
    return {script,ok:r.status===0,exitCode:r.status,stdout:r.stdout,stderr:r.stderr,error:r.error?.code};
  });
  return {ok:results.every(r=>r.ok),package:pkg.name,version:pkg.version,results,baseFormatValidation:'Current Agent must also run its dynamically resolved base creator validator'};
}
function cacheDir(o) {return o.stateDir??process.env.PORTABLE_SKILL_STATE_DIR??path.join(os.homedir(),'.portable-skill-creator');}
export async function checkUpdate(o={}, automatic=false) {
  if(process.env.PORTABLE_SKILL_UPDATE_CHECK==='0') return {ok:true,disabled:true};
  const dir=cacheDir(o), cache=path.join(dir,'update-cache.json');
  let previous=null;
  if(exists(cache)) {try {previous=readJSON(cache);}catch {return {ok:false,code:'INVALID_CACHE',cache,preserved:true};}}
  if(automatic&&previous&&Date.now()-previous.checkedAt<24*3600000) return {...previous,cached:true};
  fs.mkdirSync(dir,{recursive:true}); const lock=path.join(dir,'update-check-lock');
  try {fs.mkdirSync(lock);}catch(e) {if(e.code==='EEXIST') return {ok:true,deferred:true,reason:'concurrent-check'};throw e;}
  try {
    let result;
    try {
      const url=process.env.PORTABLE_SKILL_REGISTRY_URL??'https://registry.npmjs.org';
      const response=await fetch(url+'/'+encodeURIComponent(pkg.name)+'/latest',{signal:AbortSignal.timeout(1500)});
      if(!response.ok) throw new Error('registry-status-'+response.status);
      const data=await response.json();
      if(!/^\d+\.\d+\.\d+$/.test(data.version)) throw new Error('invalid-registry-version');
      result={ok:true,package:pkg.name,current:pkg.version,latest:data.version,available:compareVersions(data.version,pkg.version)>0,checkedAt:Date.now(),channel:'latest',automaticInstall:false};
    } catch(e) {result={ok:false,code:'REGISTRY_UNAVAILABLE',checkedAt:Date.now(),retained:true,reason:e.name==='TimeoutError'?'timeout':'offline-or-invalid-response'};}
    const temp=path.join(dir,'update-cache-'+crypto.randomUUID()+'.json');create(temp,JSON.stringify(result)+'\n');
    // Cache is exclusively package-owned; preserve its previous bytes for recovery.
    if(exists(cache)) fs.renameSync(cache,path.join(dir,'update-cache.previous-'+crypto.randomUUID()+'.json'));
    fs.renameSync(temp,cache);return result;
  } finally {fs.rmSync(lock,{recursive:true,force:true});}
}
export function compareVersions(a,b) {const aa=a.split(/[.-]/).slice(0,3).map(Number),bb=b.split(/[.-]/).slice(0,3).map(Number);for(let i=0;i<3;i++) if(aa[i]!==bb[i]) return aa[i]-bb[i];return 0;}
export async function update(o) {
  if(!o.yes) fail('CONFIRMATION_REQUIRED','Package update requires --yes within the caller authorization');
  const before=status(o);
  if(before.installed&&!before.managed) fail('UNMANAGED_TARGET','Resolve existing user-owned target before acquisition');
  if(before.edited.length) fail('LOCAL_EDITS','Reconcile local edits before package acquisition');
  const check=await checkUpdate(o);
  if(!check.ok) fail(check.code,'Registry evidence unavailable; current installation retained');
  if(!check.available) return {...install(o),packageChanged:false,update:check};
  fs.mkdirSync(path.dirname(before.target),{recursive:true});
  const transaction=fs.mkdtempSync(before.target+'.update-');
  if(before.installed) copy(before.target,path.join(transaction,'before'));
  create(path.join(transaction,'operation.json'),JSON.stringify({phase:'acquisition',target:before.target,from:pkg.version,to:check.latest,backup:before.installed?path.join(transaction,'before'):null})+'\n');
  const cmd=process.platform==='win32'?'npm.cmd':'npm';
  const r=spawnSync(cmd,['install','--prefix',path.join(transaction,'candidate'),'--ignore-scripts','--no-audit','--no-fund',pkg.name+'@'+check.latest],{encoding:'utf8',timeout:120000,windowsHide:true,shell:process.platform==='win32'});
  if(r.status!==0) fail('ACQUISITION_FAILED','npm acquisition failed; original installation retained',{transaction,exitCode:r.status});
  const candidate=path.join(transaction,'candidate/node_modules',pkg.name),actual=readJSON(path.join(candidate,'package.json'));
  if(actual.version!==check.latest) fail('VERSION_MISMATCH','Candidate package identity mismatch',{transaction});
  const sync=spawnSync(process.execPath,[path.join(candidate,'bin',name+'.mjs'),'skill','update','--agent',o.agent,'--target',before.target,'--json'],{encoding:'utf8',timeout:120000,windowsHide:true});
  if(sync.status!==0) fail('SKILL_SYNC_FAILED','Candidate retained for recovery; synchronize its entry without acquiring again',{transaction,exitCode:sync.status,candidateEntry:path.join(candidate,'bin',name+'.mjs')});
  return {ok:true,package:pkg.name,version:check.latest,packageChanged:true,transaction,entry:path.join(before.target,'.runtime/bin',name+'.mjs'),synchronization:JSON.parse(sync.stdout),hostDiscovery:{authority:'host',status:'pending'}};
}
