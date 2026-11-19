"""QA estático de dist/: enlaces internos, H1, títulos, descripciones, alt, JSON-LD, href="#", textos prohibidos."""
import json, pathlib, re, sys
from html.parser import HTMLParser
D = pathlib.Path(sys.argv[1])
class P(HTMLParser):
    def __init__(s): super().__init__(); s.links=[]; s.ids=set(); s.h1=0; s.title=''; s._t=False; s.desc=''; s.imgs=[]; s.ld=[]; s._ld=False; s._buf=''
    def handle_starttag(s, t, a):
        a=dict(a)
        if 'id' in a: s.ids.add(a['id'])
        if t=='a' and 'href' in a: s.links.append(a['href'])
        if t=='h1': s.h1+=1
        if t=='title': s._t=True
        if t=='meta' and a.get('name')=='description': s.desc=a.get('content','')
        if t=='img': s.imgs.append(a)
        if t=='script' and a.get('type')=='application/ld+json': s._ld=True; s._buf=''
    def handle_endtag(s, t):
        if t=='title': s._t=False
        if t=='script' and s._ld: s._ld=False; s.ld.append(s._buf)
    def handle_data(s, d):
        if s._t: s.title+=d
        if s._ld: s._buf+=d
pages={}; errs=[]
for f in D.rglob('*.html'):
    rel='/'+str(f.relative_to(D)).replace('index.html','')
    p=P(); txt=f.read_text(encoding='utf-8'); p.feed(txt); pages[rel]=(p,txt)
def exists(path):
    path=path.split('#')[0].split('?')[0]
    if not path: return True
    q=D/path.lstrip('/')
    return q.is_file() or (q/'index.html').is_file()
titles={}; descs={}
for rel,(p,txt) in pages.items():
    if rel.startswith('/estilos'): continue
    if p.h1!=1: errs.append(f'{rel}: {p.h1} H1')
    titles.setdefault(p.title,[]).append(rel); descs.setdefault(p.desc,[]).append(rel)
    for h in p.links:
        if h=='#': errs.append(f'{rel}: href="#"')
        elif h.startswith('/') and not exists(h): errs.append(f'{rel}: enlace roto {h}')
        elif h.startswith('#') and h[1:] not in p.ids: errs.append(f'{rel}: ancla rota {h}')
    for i in p.imgs:
        if 'alt' not in i: errs.append(f'{rel}: img sin alt {i.get("src","")[:60]}')
    for l in p.ld:
        try: json.loads(l)
        except Exception as ex: errs.append(f'{rel}: JSON-LD inválido {ex}')
    for bad in ['lorem','Lorem','[tu email','null<','undefined','Blue Jacket','SVariant','LISCENSED','Go to Ig','fashion news','$75']:
        if bad in re.sub(r'<script.*?</script>','',txt,flags=re.S): errs.append(f'{rel}: texto prohibido "{bad}"')
for t,rs in titles.items():
    if len(rs)>1: errs.append(f'Título repetido "{t}": {rs}')
for t,rs in descs.items():
    if len(rs)>1: errs.append(f'Descripción repetida: {rs}')
print(f'{len(pages)} páginas revisadas'); print('\n'.join(errs) if errs else 'SIN ERRORES')
