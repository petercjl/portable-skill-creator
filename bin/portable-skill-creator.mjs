#!/usr/bin/env node
import {readFileSync} from 'node:fs';
import path from 'node:path';
import * as c from '../lib/core.mjs';

const contracts={
  'version':[], 'capabilities':[], 'help':[], 'install-notice':[],
  'doctor':['python'], 'prepare':['python','state-dir'],
  'validate':['path','profile','mode','python','state-dir'],
  'skill source':['name'], 'skill status':['agent','target'],
  'skill install':['agent','target'], 'skill update':['agent','target'],
  'update check':['state-dir'], 'update status':['state-dir'],
  'update install':['agent','target','yes','state-dir']
};
try {
  const args=process.argv.slice(2);let words=[],o={};
  while(args.length) {
    const a=args.shift();
    if(a==='--version') words.push('version');
    else if(a.startsWith('--')) {
      const k=a.slice(2);
      if(Object.hasOwn(o,k)) c.fail('INVALID_ARGUMENT','Duplicate option: '+a);
      if(['json','yes','help'].includes(k)) o[k]=true;
      else {if(!args.length||args[0].startsWith('--')) c.fail('INVALID_ARGUMENT','Missing option value: '+a);o[k]=args.shift();}
    } else words.push(a);
  }
  let cmd=words.join(' ')||'help';if(cmd==='--version') cmd='version';
  if(!Object.hasOwn(contracts,cmd)) c.fail('INVALID_ARGUMENT','Unknown command: '+cmd);
  for(const k of Object.keys(o)) if(!['json','help',...contracts[cmd]].includes(k)) c.fail('INVALID_ARGUMENT','Unsupported option --'+k);
  o.stateDir=o['state-dir'];
  const manifest=JSON.parse(readFileSync(path.join(c.root,'capabilities.json')));
  let result;
  if(cmd==='help'||o.help) result={...manifest,commands:manifest.commandContracts,guidance:'The current Agent resolves its exact Skill directory and passes --agent <valid-name> --target <absolute-directory>. See INSTALL.md and UPDATE.md.'};
  else if(cmd==='install-notice') result={ok:true,partial:true,message:'CLI bootstrap installed. The current Agent must read INSTALL.md, resolve skill source, synchronize its own explicit Skill target and verify discovery. npm success alone is incomplete.'};
  else if(cmd==='version') result={ok:true,package:c.pkg.name,version:c.pkg.version};
  else if(cmd==='capabilities') result=manifest;
  else if(cmd==='skill source') {
    if(o.name&&o.name!==c.name) c.fail('SKILL_NOT_FOUND','Unknown logical Skill');
    result={ok:true,name:c.name,package:c.pkg.name,version:c.pkg.version,path:c.source,complete:true,skills:[{name:c.name,package:c.pkg.name,version:c.pkg.version,path:c.source}]};
  } else if(cmd==='skill status') result=c.status(o);
  else if(cmd==='skill install'||cmd==='skill update') result=c.install(o);
  else if(cmd==='doctor') result=c.doctor(o);
  else if(cmd==='prepare'||cmd==='validate') {
    const update=await c.checkUpdate(o,true);
    result={...(cmd==='prepare'?c.doctor(o):c.validate(o)),update};
  } else if(cmd==='update check') result=await c.checkUpdate(o);
  else if(cmd==='update status') result={ok:true,automaticDetection:process.env.PORTABLE_SKILL_UPDATE_CHECK!=='0',automaticInstall:false,channel:'latest',ttlHours:24,timeoutMs:1500,disable:'PORTABLE_SKILL_UPDATE_CHECK=0'};
  else if(cmd==='update install') result=await c.update(o);
  process.stdout.write(o.json||cmd!=='version'?JSON.stringify(result,null,2)+'\n':c.pkg.version+'\n');
  if(result.ok===false) process.exitCode=1;
} catch(e) {process.stderr.write(JSON.stringify({ok:false,error:{code:e.code??'INTERNAL_ERROR',message:e.message,...e.details}},null,2)+'\n');process.exitCode=1;}
