"""Regenerate the file manifest for the two packaged studies."""
from pathlib import Path
import collections,concurrent.futures,hashlib,json,os,re

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','__pycache__','.venv','build','dist'}
TEXT={'.py','.json','.jsonl','.csv','.md','.txt','.toml','.yml','.yaml','.ps1','.log'}

def main():
    files={};total=0
    def paths():
        for directory,dirs,names in os.walk(ROOT):
            dirs[:]=[d for d in dirs if d not in EXCLUDED and not d.endswith('.egg-info') and not (Path(directory)==ROOT and d in {'runs','artifacts'})]
            for name in sorted(names):
                path=Path(directory)/name
                if path.name!='REPRODUCIBILITY_MANIFEST.json':yield path
    def read(path):
        rel=path.relative_to(ROOT)
        if path.suffix.lower()=='.docx':raise ValueError('Word document in distribution: '+str(rel))
        payload=path.read_bytes()
        if path.suffix.lower() in TEXT:
            text=payload.decode('utf-8-sig',errors='replace')
            if re.search(r'\bgh[pousr]_[A-Za-z0-9]{25,}|\bgithub_pat_[A-Za-z0-9_]{25,}',text):raise ValueError('Credential-like text in '+str(rel))
        return rel.as_posix(),{'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}
    iterator=iter(paths())
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        pending=collections.deque()
        for _ in range(48):
            p=next(iterator,None)
            if p is not None:pending.append(pool.submit(read,p))
        while pending:
            rel,record=pending.popleft().result();files[rel]=record;total+=record['bytes']
            p=next(iterator,None)
            if p is not None:pending.append(pool.submit(read,p))
    files=dict(sorted(files.items()))
    result={'project':'DSAI6707 historical fragment and insertion-position GP','scope':'Historical: four methods and 30 paired seeds. Position: three methods and 30 paired seeds.',
            'new_model_calls_during_packaging':0,'files':files}
    (ROOT/'REPRODUCIBILITY_MANIFEST.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sealed_files':len(files),'bytes':total}))

if __name__=='__main__':main()
