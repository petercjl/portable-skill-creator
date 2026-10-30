import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {spawn,spawnSync} from 'node:child_process';
import {createServer} from 'node:http';
import {root,pkg,install,status} from '../lib/core.mjs';

const temporary=()=>fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'portable-packed-test-')));
function run(args,options={}) {return new Promise((resolve,reject)=>{const child=spawn(process.execPath,args,{...options,windowsHide:true});let stdout='',stderr='';child.stdout.on('data',v=>stdout+=v);child.stderr.on('data',v=>stderr+=v);child.on('error',reject);child.on('close',status=>resolve({status,stdout,stderr}));});}
function npm(args,cwd,env) {const r=spawnSync(process.platform==='win32'?'npm.cmd':'npm',args,{cwd,env,encoding:'utf8',timeout:60000,shell:process.platform==='win32'});assert.equal(r.status,0,r.stdout+r.stderr);return r;}

test('archived-updater-entry 0.1.0, real npm update, same-version repair, local-edits refusal and recovery',async()=>{
  // historical-mode: actual immutable published 0.1.0 copy-mode updater.
  const p=temporary(),candidate=path.join(p,'candidate-source');fs.mkdirSync(candidate);
  for(const f of ['package.json','capabilities.json','README.md','INSTALL.md','UPDATE.md','LICENSE','bin','lib','skills']) fs.cpSync(path.join(root,f),path.join(candidate,f),{recursive:true});
  const parts=pkg.version.split('.').map(Number);
  const next=[parts[0],parts[1],parts[2]+1].join('.');
  for(const f of ['package.json','capabilities.json','skills/portable-skill-creator/skill-manifest.json']) {const at=path.join(candidate,f),data=JSON.parse(fs.readFileSync(at));data.version=next;if(f==='package.json')delete data.scripts;fs.writeFileSync(at,JSON.stringify(data));}
  const config=path.join(p,'npmrc');fs.writeFileSync(config,'');
  const baseEnv={...process.env,npm_config_userconfig:config,npm_config_dry_run:'false',npm_config_json:'false',PORTABLE_SKILL_UPDATE_CHECK:'0'};
  npm(['pack','--ignore-scripts','--pack-destination',p],candidate,baseEnv);
  const tar=fs.readFileSync(path.join(p,'petercjl-portable-skill-creator-'+next+'.tgz'));
  const integrity='sha512-'+crypto.createHash('sha512').update(tar).digest('base64');
  let registryCalls=0,baseURL;
  const server=createServer((req,res)=>{
    registryCalls++;
    if(req.url==='/candidate.tgz') {res.end(tar);return;}
    res.setHeader('content-type','application/json');
    if(req.url.endsWith('/latest')) {res.end(JSON.stringify({version:next}));return;}
    res.end(JSON.stringify({name:pkg.name,'dist-tags':{latest:next},versions:{[next]:{name:pkg.name,version:next,dist:{tarball:baseURL+'/candidate.tgz',integrity},bin:{'portable-skill-creator':'bin/portable-skill-creator.mjs'}}}}));
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));baseURL='http://127.0.0.1:'+server.address().port;
  const env={...baseEnv,PORTABLE_SKILL_UPDATE_CHECK:'1',PORTABLE_SKILL_REGISTRY_URL:baseURL,npm_config_registry:baseURL};
  const archive=path.join(root,'test/fixtures/portable-skill-creator-0.1.0.tgz');
  const expected=JSON.parse(fs.readFileSync(path.join(root,'test/fixtures/0.1.0.json')));
  assert.equal('sha512-'+crypto.createHash('sha512').update(fs.readFileSync(archive)).digest('base64'),expected.integrity);
  npm(['install','--prefix',path.join(p,'archived'),'--ignore-scripts','--no-audit','--no-fund',archive],p,baseEnv);
  const oldEntry=path.join(p,'archived/node_modules/@petercjl/portable-skill-creator/bin/portable-skill-creator.mjs');
  const o={agent:'unlisted-agent',target:path.join(p,'agent-skill')};
  const initial=await run([oldEntry,'skill','install','--agent',o.agent,'--target',o.target,'--json'],{env:baseEnv});
  assert.equal(initial.status,0,initial.stderr);assert.equal(JSON.parse(initial.stdout).version,'0.1.0');
  const entry=path.join(o.target,'.runtime/bin/portable-skill-creator.mjs');
  try {
    const result=await run([entry,'update','install','--agent',o.agent,'--target',o.target,'--state-dir',path.join(p,'state'),'--yes','--json'],{env});
    assert.equal(result.status,0,result.stderr+result.stdout);
    const report=JSON.parse(result.stdout);assert.equal(report.version,next);assert.equal(report.packageChanged,true);
    assert.ok(fs.existsSync(path.join(report.transaction,'before','SKILL.md')));
    const version=await run([entry,'version','--json'],{env});assert.equal(JSON.parse(version.stdout).version,next);
    fs.unlinkSync(path.join(o.target,'references/index.md'));
    const repaired=await run([entry,'update','install','--agent',o.agent,'--target',o.target,'--state-dir',path.join(p,'state'),'--yes','--json'],{env});
    assert.equal(repaired.status,0,repaired.stderr);assert.equal(JSON.parse(repaired.stdout).packageChanged,false);
    fs.appendFileSync(path.join(o.target,'SKILL.md'),'\nlocal-edits');const calls=registryCalls;
    const refused=await run([entry,'update','install','--agent',o.agent,'--target',o.target,'--state-dir',path.join(p,'state'),'--yes','--json'],{env});
    assert.notEqual(refused.status,0);assert.equal(JSON.parse(refused.stderr).error.code,'LOCAL_EDITS');assert.equal(registryCalls,calls);
    // Recovery snapshot identity is independent of activated candidate resources.
    assert.equal(JSON.parse(fs.readFileSync(path.join(report.transaction,'before','skill-manifest.json'))).version,'0.1.0');
  } finally {await new Promise(r=>server.close(r));}
});
