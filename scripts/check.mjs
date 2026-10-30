import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root,pkg,source,files,readJSON,validate} from '../lib/core.mjs';

assert.equal(readJSON(path.join(root,'capabilities.json')).version,pkg.version,'capabilities version drift');
assert.equal(readJSON(path.join(source,'skill-manifest.json')).version,pkg.version,'Skill version drift');
assert.equal(readJSON(path.join(source,'skill-manifest.json')).package,pkg.name);
for(const f of ['README.md','INSTALL.md','UPDATE.md','LICENSE']) assert.ok(fs.statSync(path.join(root,f)).size>0);
for(const f of ['bin','lib','skills'].flatMap(d=>files(path.join(root,d)).map(f=>d+'/'+f))) {
  assert.ok(!/(__pycache__|\.pyc$)/.test(f),'Build cache leaked');
  const text=fs.readFileSync(path.join(root,f),'utf8');
  assert.ok(!/(?:\/Users\/|\/home\/)[A-Za-z0-9_.-]+\//.test(text),'Private path leaked: '+f);
}
const result=validate({path:source,profile:'shareable',mode:'hybrid'});
for(const r of result.results) if(!r.ok) process.stderr.write(r.stdout+r.stderr);
assert.ok(result.ok,'Bundled Skill validation failed');
console.log(JSON.stringify({ok:true,package:pkg.name,version:pkg.version,skillVersionVerified:true,checks:result.results.map(r=>({script:r.script,ok:r.ok})),externalBaseCreator:'host-resolved'}));
