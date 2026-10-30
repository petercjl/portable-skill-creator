import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {root,python} from '../lib/core.mjs';
test('bundled validator behavioral regression',()=>{
 const p=python();
 for(const f of fs.readdirSync(path.join(root,'test')).filter(f=>f.startsWith('test_')&&f.endsWith('.py'))) {
  const r=spawnSync(p.command,[...p.args,path.join(root,'test',f)],{encoding:'utf8',timeout:30000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1',PYTHONPATH:path.join(root,'skills/portable-skill-creator/scripts')}});
  assert.equal(r.status,0,r.stdout+r.stderr);
 }
});
