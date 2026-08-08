#!/usr/bin/env python3
from pathlib import Path
import sys,re,json
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
TERMS=[r"\bCWC\b",r"\btoken\b",r"\bwallet\b",r"\bcollectible\b",r"art\s*collection",r"\bNFC\b",r"\btrading?\b",r"\bmarketplace\b",r"copyright\s*exchange",r"revenue\s*split",r"38\.2\s*%",r"61\.8\s*%",r"平台币",r"代币",r"钱包",r"藏品",r"艺术收藏",r"交易中心",r"版权交易",r"实体唱片",r"收益分成"]
PATTERN=re.compile("|".join(f"(?:{t})" for t in TERMS),re.I)
SKIP_DIRS={'.git','node_modules','dist','build','.next','.nuxt','.venv','venv','__pycache__','coverage','.cache','archive','archives'}
TEXT_EXTS={'.ts','.tsx','.js','.jsx','.vue','.svelte','.py','.go','.rs','.java','.kt','.swift','.dart','.json','.yaml','.yml','.toml','.md','.txt','.html','.css','.scss','.sql','.graphql','.gql'}
matches=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or any(part in SKIP_DIRS for part in p.parts) or p.suffix.lower() not in TEXT_EXTS: continue
    if p.name=='scan_legacy_concepts.py': continue
    try: text=p.read_text(encoding='utf-8',errors='ignore')
    except Exception: continue
    for i,line in enumerate(text.splitlines(),1):
        if PATTERN.search(line): matches.append({'file':str(p.relative_to(ROOT)),'line':i,'text':line.strip()[:300]})
print(json.dumps({'root':str(ROOT),'count':len(matches),'matches':matches},ensure_ascii=False,indent=2))
raise SystemExit(2 if matches else 0)
