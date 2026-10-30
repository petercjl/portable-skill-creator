import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {root,pkg,source,readJSON} from '../lib/core.mjs';
// npm version lifecycle owns these generated version fields. Preserve previous bytes.
for(const p of [path.join(root,'capabilities.json'),path.join(source,'skill-manifest.json')]) {
  const stat=fs.statSync(p),data=readJSON(p);
  const backup=path.join(root,'evidence','version-backups',crypto.randomUUID(),path.relative(root,p));
  fs.mkdirSync(path.dirname(backup),{recursive:true});fs.copyFileSync(p,backup,fs.constants.COPYFILE_EXCL);
  data.version=pkg.version;fs.writeFileSync(p,JSON.stringify(data,null,2)+'\n',{mode:stat.mode});
  if(readJSON(p).version!==pkg.version||!fs.existsSync(backup)) throw Error('Version synchronization failed');
}
