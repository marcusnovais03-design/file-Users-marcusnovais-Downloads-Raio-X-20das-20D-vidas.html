import json, datetime as dt
def bcb(p):
    out={}
    for i in (1,2,3):
        for r in json.load(open(f'{p}{i}.json')):
            d=dt.datetime.strptime(r['data'],'%d/%m/%Y').date(); out[d]=float(r['valor'])
    return dict(sorted(out.items()))
def yh(f):
    r=json.load(open(f))['chart']['result'][0]; out={}
    for t,c in zip(r['timestamp'], r['indicators']['quote'][0]['close']):
        if c: out[dt.datetime.utcfromtimestamp(t).date()]=c
    return out
cdi,usd,spx,tr=bcb('cdi'),bcb('usd'),yh('spx.json'),yh('spxtr.json')
print(len(cdi),len(usd),len(spx),len(tr), max(cdi),max(usd),max(spx))
START,END=dt.date(2006,10,31),dt.date(2026,10,30)
def last(d,s):
    k=max(x for x in s if x<=d); return s[k]
# month ends
me=[]; y,m=2006,10
while (y,m)<=(2026,10):
    ny,nm=(y+1,1) if m==12 else (y,m+1)
    me.append(min(dt.date(ny,nm,1)-dt.timedelta(days=1),END)); y,m=ny,nm
# CDI accumulation: rate of day d applies from d to next business day
idx={}; acc=1.0; 
days=sorted(cdi)
cum={}
for d in days:
    cum[d]=acc            # value at start of day d
    acc*=1+cdi[d]/100
def cdiv(d):  # value at close of day d = product of rates of days <= d... use start-of-next
    return [cum[x]*(1+cdi[x]/100) for x in days if x<=d][-1]
base_c=cdiv(START); bs=last(START,spx)*last(START,usd); bt=last(START,tr)*last(START,usd)
rows=[]
for d in me:
    rows.append(dict(d=d.isoformat(), cdi=round(1000*cdiv(d)/base_c,2), sp=round(1000*last(d,spx)*last(d,usd)/bs,2),
        sptr=round(1000*last(d,tr)*last(d,usd)/bt,2), spx=round(last(d,spx),2), usd=round(last(d,usd),4)))
json.dump(rows,open('series.json','w'))
for r in rows[:2]+rows[-3:]: print(r)
n=20
for k in('cdi','sp','sptr'):
    f=rows[-1][k]; print(k,f, f'{(f/1000-1)*100:.1f}%', f'{((f/1000)**(1/n)-1)*100:.2f}% aa')
print('spx usd only', rows[-1]['spx']/rows[0]['spx'], 'usd', rows[-1]['usd']/rows[0]['usd'])
print('min sp', min(rows,key=lambda r:r['sp']))
