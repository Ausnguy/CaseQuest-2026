import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'public');
mkdirSync(out, { recursive: true });
copyFileSync(join(root, '../prototype/parvius.html'), join(out, 'index.html'));
copyFileSync(join(root, '../prototype/fieldwork.js'), join(out, 'fieldwork.js'));
copyFileSync(join(root, '../data/model/predictions.json'), join(out, 'model.json'));
