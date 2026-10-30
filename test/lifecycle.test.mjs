import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {createServer} from 'node:http';
import {root,pkg,source,install,status,checkUpdate} from '../lib/core.mjs';

const tmp=()=>fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'portable-creator-test-')));
const env={...process.env,PORTABLE_SKILL_UPDATE_CHECK:'0',PYTHONDONTWRITEBYTECODE:'1'};
function cli(args,entry=path.join(root,'bin/portable-skill-creator.mjs')) {return spawnSync(process.execPath,[entry,...args],{encoding:'utf8',env,timeout:30000});}

test('strict parser and target validation refuse before writing',()=>{
  const p=path.join(tmp(),'skill');
  for(const args of [['skill','install','--agent','generic'],['skill','install','--agent','bad/name','--target',p],['skill','install','--agent','generic','--target',p,'--unknown','x'],['skill','install','--agent','generic','--agent','other','--target',p]]) assert.notEqual(cli(args).status,0);
  assert.ok(!fs.existsSync(p));
});
test('unmanaged/edited targets protected; same-version missing repair and no-op',()=>{
  const parent=tmp(),target=path.join(parent,'skill'),o={agent:'any-new-host',target};
  fs.mkdirSync(target);fs.writeFileSync(path.join(target,'private.txt'),'user data');
  assert.throws(()=>install(o),{code:'UNMANAGED_TARGET'});fs.rmSync(target,{recursive:true});
  const first=install(o);assert.equal(first.current,true);assert.equal(first.physicalCopy,true);
  const m=fs.statSync(path.join(target,'SKILL.md')).mtimeMs;
  assert.equal(install(o).changed,false);assert.equal(fs.statSync(path.join(target,'SKILL.md')).mtimeMs,m);
  fs.unlinkSync(path.join(target,'references/index.md'));assert.equal(status(o).current,false);
  const repaired=install(o);assert.equal(repaired.current,true);assert.ok(fs.existsSync(path.join(repaired.backup,'skill','SKILL.md')));
  fs.appendFileSync(path.join(target,'SKILL.md'),'\nlocal edit');assert.throws(()=>install(o),{code:'LOCAL_EDITS'});
  assert.match(fs.readFileSync(path.join(target,'SKILL.md'),'utf8'),/local edit/);
});
test('custom host metadata and unmanaged files preserved across stale repair',()=>{
  const o={agent:'generic',target:path.join(tmp(),'skill')};install(o);
  const metadata=path.join(o.target,'agents/openai.yaml');fs.writeFileSync(metadata,'interface:\n  display_name: "自定义名称"\n');
  fs.writeFileSync(path.join(o.target,'my-notes.txt'),'notes');fs.unlinkSync(path.join(o.target,'references/index.md'));
  assert.equal(install(o).current,true);assert.match(fs.readFileSync(metadata,'utf8'),/自定义/);assert.equal(fs.readFileSync(path.join(o.target,'my-notes.txt'),'utf8'),'notes');
});
test('two physical hosts survive removal of bootstrap and one host',async()=>{
  const p=tmp(),bootstrap=path.join(p,'bootstrap');fs.mkdirSync(bootstrap);
  for(const f of ['package.json','capabilities.json','README.md','INSTALL.md','UPDATE.md','LICENSE','bin','lib','skills']) fs.cpSync(path.join(root,f),path.join(bootstrap,f),{recursive:true});
  const module=await import(pathToFileURL(path.join(bootstrap,'lib/core.mjs')));
  const a={agent:'alpha',target:path.join(p,'alpha')},b={agent:'beta',target:path.join(p,'beta')};module.install(a);module.install(b);
  if(process.platform!=='win32') assert.notEqual(fs.statSync(path.join(a.target,'SKILL.md')).ino,fs.statSync(path.join(b.target,'SKILL.md')).ino);
  fs.rmSync(bootstrap,{recursive:true});fs.rmSync(a.target,{recursive:true});
  const entry=path.join(b.target,'.runtime/bin/portable-skill-creator.mjs');
  assert.equal(JSON.parse(cli(['version','--json'],entry).stdout).version,pkg.version);
  const validated=cli(['validate','--path',b.target,'--mode','hybrid','--json'],entry);
  assert.equal(validated.status,0,validated.stderr+validated.stdout);
  assert.equal(JSON.parse(cli(['skill','status','--agent','beta','--target',b.target,'--json'],entry).stdout).current,true);
});
test('lock prevents concurrent mutations; symlinks and unsafe receipts refused',()=>{
  const p=tmp(),o={agent:'generic',target:path.join(p,'skill')};
  fs.mkdirSync(o.target+'.install-lock');assert.throws(()=>install(o),{code:'LOCKED'});fs.rmdirSync(o.target+'.install-lock');
  install(o);const rp=path.join(o.target,'.portable-skill-install.json'),receipt=JSON.parse(fs.readFileSync(rp));receipt.hashes['../outside']='a'.repeat(64);fs.writeFileSync(rp,JSON.stringify(receipt));
  assert.throws(()=>status(o),{code:'INVALID_RECEIPT'});
});
test('update check first/cached/expired/offline/disabled and malformed-cache preservation',async()=>{
  let calls=0;const server=createServer((req,res)=>{calls++;res.setHeader('content-type','application/json');res.end(JSON.stringify({version:'99.0.0'}));});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const oldURL=process.env.PORTABLE_SKILL_REGISTRY_URL,oldDisable=process.env.PORTABLE_SKILL_UPDATE_CHECK;
  process.env.PORTABLE_SKILL_REGISTRY_URL='http://127.0.0.1:'+server.address().port;delete process.env.PORTABLE_SKILL_UPDATE_CHECK;
  try {
    const o={stateDir:tmp()};const first=await checkUpdate(o,true);assert.equal(first.available,true);assert.equal(calls,1);
    assert.equal((await checkUpdate(o,true)).cached,true);assert.equal(calls,1);
    const p=path.join(o.stateDir,'update-cache.json'),data=JSON.parse(fs.readFileSync(p));data.checkedAt=0;fs.writeFileSync(p,JSON.stringify(data));await checkUpdate(o,true);assert.equal(calls,2);
    process.env.PORTABLE_SKILL_UPDATE_CHECK='0';assert.equal((await checkUpdate(o,true)).disabled,true);
    delete process.env.PORTABLE_SKILL_UPDATE_CHECK;fs.writeFileSync(p,'malformed');assert.equal((await checkUpdate(o,true)).code,'INVALID_CACHE');assert.equal(fs.readFileSync(p,'utf8'),'malformed');
    await new Promise(r=>server.close(r));assert.equal((await checkUpdate({stateDir:tmp()},true)).code,'REGISTRY_UNAVAILABLE');
  } finally {if(server.listening) await new Promise(r=>server.close(r));if(oldURL===undefined)delete process.env.PORTABLE_SKILL_REGISTRY_URL;else process.env.PORTABLE_SKILL_REGISTRY_URL=oldURL;if(oldDisable===undefined)delete process.env.PORTABLE_SKILL_UPDATE_CHECK;else process.env.PORTABLE_SKILL_UPDATE_CHECK=oldDisable;}
});
test('Python validators execute success and representative failure cases',()=>{
  const success=cli(['validate','--path',source,'--mode','hybrid','--json']);assert.equal(success.status,0,success.stdout+success.stderr);
  const p=tmp();fs.writeFileSync(path.join(p,'SKILL.md'),'---\nname: sample\ndescription: Sample\n---\nRead /'+'Users/example/private/data.');
  const failure=cli(['validate','--path',p,'--mode','hybrid','--json']);assert.notEqual(failure.status,0);
});
test('doctor resolves managed runtime and returns host-owned nested dependency; missing Python refused',()=>{
  const result=cli(['doctor','--json']);assert.equal(result.status,0,result.stderr);
  const report=JSON.parse(result.stdout);assert.equal(report.dependencies[0].name,'skill-creator');assert.equal(report.python.version[0],3);
  const r=spawnSync(process.execPath,[path.join(root,'bin/portable-skill-creator.mjs'),'doctor','--json'],{encoding:'utf8',env:{...env,PATH:'',VIRTUAL_ENV:'',PORTABLE_SKILL_PYTHON:''}});
  assert.notEqual(r.status,0);assert.equal(JSON.parse(r.stderr).error.code,'PYTHON_REQUIRED');
});
test('locked-directory rename uses backed-up in-place repair and preserves UI metadata',()=>{
  const o={agent:'generic',target:path.join(tmp(),'skill')};install(o);fs.unlinkSync(path.join(o.target,'references/index.md'));
  const rename=fs.renameSync;
  fs.renameSync=(from,to)=>{if(from===o.target)throw Object.assign(new Error('locked-directory rename'),{code:'EBUSY'});return rename(from,to);};
  try {const r=install(o);assert.equal(r.current,true);assert.ok(fs.existsSync(path.join(r.backup,'skill','SKILL.md')));}finally {fs.renameSync=rename;}
});
test('partial-failure state survives missing target and explicit recovery preserves original snapshot',()=>{
  const o={agent:'generic',target:path.join(tmp(),'skill')};install(o);fs.unlinkSync(path.join(o.target,'references/index.md'));
  const rename=fs.renameSync;
  fs.renameSync=(from,to)=>{if(from.includes('.stage-')&&to===o.target)throw Object.assign(new Error('injected activation failure'),{code:'EIO'});return rename(from,to);};
  let backup;
  try {assert.throws(()=>install(o),e=>{backup=e.details.backup;return e.code==='EIO';});}finally {fs.renameSync=rename;}
  const pending=status(o);assert.equal(pending.installed,false);assert.equal(pending.recovery.required,true);assert.equal(pending.recovery.operation.phase,'failed-sync');
  assert.ok(fs.existsSync(path.join(backup,'skill','SKILL.md')));
  const recovered=install(o);assert.equal(recovered.current,true);assert.equal(recovered.backup,backup);
});
