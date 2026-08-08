#!/usr/bin/env python3
from pathlib import Path
import sys,re,json
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd().resolve()
CORE={'auditory':[r'auditory',r'听觉'],'analysis':[r'analysis',r'analy[sz]e',r'分析',r'检测'],'evidence':[r'evidence',r'证据'],'judgment':[r'judg(e)?ment',r'判断',r'诊断'],'verification':[r'verif',r'验证'],'case':[r'\bcase\b',r'案例']}
LEGACY=[r'\bCWC\b',r'平台币',r'代币',r'艺术收藏',r'交易中心',r'\bcollectible\b',r'\bwallet\b',r'\btoken\b']
SKIP_DIRS={'.git','node_modules','dist','build','.next','.venv','venv','archive','archives'}
TEXT_EXTS={'.ts','.tsx','.js','.jsx','.vue','.svelte','.py','.json','.yaml','.yml','.md','.html','.dart','.swift','.kt'}
parts=[]; legacy=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or any(part in SKIP_DIRS for part in p.parts) or p.suffix.lower() not in TEXT_EXTS: continue
    try: text=p.read_text(encoding='utf-8',errors='ignore')
    except Exception: continue
    parts.append(text)
    if any(re.search(pat,text,re.I) for pat in LEGACY): legacy.append(str(p.relative_to(ROOT)))
corpus='\n'.join(parts)
coverage={k:any(re.search(p,corpus,re.I) for p in pats) for k,pats in CORE.items()}
res={'core_coverage':coverage,'legacy_active_files':sorted(set(legacy)),'aligned':all(coverage.values()) and not legacy}
print(json.dumps(res,ensure_ascii=False,indent=2)); raise SystemExit(0 if res['aligned'] else 3)
