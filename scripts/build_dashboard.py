"""Builds compact summary cubes from ../data and injects them into dashboard/template.html (client-side filter engine)."""
import pandas as pd, numpy as np, json, pathlib
from spec import PAGES
R=pathlib.Path(__file__).resolve().parent.parent; L=lambda n:pd.read_csv(R/'data'/f'{n}.csv')
c,e,s,rc,tk,st,us,bl,tw,nf,og,cp,ds,dv=[L(n) for n in 'Dim_Customers Dim_Employees_HR Fact_Subscriptions Fact_Recharge_Sales Fact_Network_Service_Calls Fact_Digital_Streaming_VAS Fact_Usage_Monthly Fact_Billing Dim_Towers Fact_Network_Performance Fact_Network_Outages Fact_Marketing_Campaigns Dim_Distributors Dim_Division'.split()]
M=lambda x:pd.to_datetime(x).dt.strftime('%Y-%m')
for d in (us,bl,nf,og,cp,tk,st,rc): d['M']=M(d.Date)
mk=sorted(us.M.unique())
def cube(df,dims,**m):
    df=df[df.M.isin(mk)] if 'M' in dims else df
    g=df.groupby(dims,observed=True).agg(**m).reset_index().fillna(0)
    return {'h':list(g.columns),'r':[[round(v,2) if isinstance(v,float) else v for v in r] for r in g.values.tolist()]}
cc=c[['CustomerID','Division','Network','Segment','IsChurned']].copy()
c['OTT']=np.where(c.CustomerID.isin(st.CustomerID),'With OTT','No OTT')
c['pro']=(c.NPS_Score>=9)*1; c['pas']=c.NPS_Score.between(7,8)*1; c['det']=(c.NPS_Score<=6)*1
us=us.merge(cc[['CustomerID','Division','Segment']],on='CustomerID')
tk=tk.merge(cc[['CustomerID','Division','IsChurned']],on='CustomerID').merge(e[['EmployeeID','Department']],on='EmployeeID').rename(columns={'IssueCategory':'Issue','TicketChannel':'TChan','Department':'Dept'})
nf=nf.merge(tw[['SiteID','Division','Area']],on='SiteID').rename(columns={'SiteID':'Site'}); og=og.merge(tw[['SiteID','Division']],on='SiteID')
bl=bl.merge(cc[['CustomerID','Division']],on='CustomerID'); bl['unp']=bl.Billed_BDT-bl.Paid_BDT
bl['Aging']=np.select([bl.Paid_BDT>=bl.Billed_BDT,bl.DaysLate<=30,bl.DaysLate<=60,bl.DaysLate<=90],['Paid','1-30d','31-60d','61-90d'],'90d+')
st=st.merge(cc[['CustomerID','Division']],on='CustomerID')
rd=rc[rc.DistributorID!='DIGITAL'].merge(ds[['DistributorID','Division']],on='DistributorID').rename(columns={'DistributorID':'Dist'})
rc=rc.merge(cc[['CustomerID','Division']],on='CustomerID').merge(ds[['DistributorID','Tier']],on='DistributorID').rename(columns={'Channel':'RChan'})
cp=cp.rename(columns={'Channel':'CChan'}); e=e.rename(columns={'Department':'Dept'}); e['Rating']='Rating '+e.PerformanceRating.astype(str)
sx=s.drop(columns=['Segment']).merge(cc[['CustomerID','Division','Network','Segment']],on='CustomerID').rename(columns={'AcquisitionChannel':'Acq'})
ga=sx[pd.to_datetime(sx.ActivationDate)>='2025-01-01'].assign(M=lambda x:M(x.ActivationDate),ChurnType='-',ga=1,ch=0)
ch=sx.dropna(subset=['ChurnDate']).assign(M=lambda x:M(x.ChurnDate),ga=0,ch=1)
ev=pd.concat([ga,ch])
tkm=dict(n=('Issue','size'),res=('ResolutionTimeMinutes','sum'),cs=('SatisfactionScore','sum'),fcr=('FirstContactResolved','sum'),sla=('SLA_Met','sum'))
Tb=dict(
 usage=cube(us,['Division','M','Network','Segment'],n=('CustomerID','size'),vr=('VoiceRev','sum'),dr=('DataRev','sum'),sr=('SMSRev','sum'),vs=('VASRev','sum'),vm=('VoiceMin','sum'),dg=('DataGB','sum')),
 cust=cube(c,['Division','Network','Segment','OTT'],n=('CustomerID','size'),ch=('IsChurned','sum'),pro=('pro','sum'),pas=('pas','sum'),det=('det','sum')),
 ev=cube(ev,['Division','M','Network','Segment','Acq','ChurnType'],ga=('ga','sum'),ch=('ch','sum')),
 tick=cube(tk,['Division','M','Issue','TChan'],chf=('IsChurned','sum'),**tkm),
 tickd=cube(tk,['Division','M','Dept'],**tkm),
 net=cube(nf,['Division','M','Area'],n=('Site','size'),dp=('CallDropRate_Pct','sum'),cs2=('CSSR_Pct','sum'),th=('Throughput_Mbps','sum'),av=('Availability_Pct','sum'),pb=('PRB_Utilization_Pct','sum')),
 site=cube(nf,['Site','Division','Area','M'],n=('Area','size'),pb=('PRB_Utilization_Pct','sum')),
 out=cube(og,['Division','M','Cause'],n=('Cause','size'),du=('DurationMin','sum')),
 bill=cube(bl,['Division','M','Aging'],bd=('Billed_BDT','sum'),pd=('Paid_BDT','sum'),wo=('WrittenOff_BDT','sum'),un=('unp','sum')),
 stream=cube(st,['Division','M','Platform'],n=('Platform','size'),gb=('DataConsumed_GB','sum'),ad=('AdSpend_BDT','sum')),
 rech=cube(rc,['Division','M','RChan','Tier'],n=('RChan','size'),am=('Amount_BDT','sum')),
 rechd=cube(rd,['Dist','Division','M'],am=('Amount_BDT','sum')),
 camp=cube(cp,['Division','M','CChan'],sp=('Spend_BDT','sum'),ld=('Leads','sum'),cv=('Conversions','sum'),rv=('RevenueGenerated_BDT','sum')),
 emp=cube(e.assign(M=mk[0]).drop(columns='M'),['Division','Dept','Rating'],hc=('Dept','size'),lf=('LeftCompany','sum'),sl=('MonthlySalary','sum'),rt=('PerformanceRating','sum')))
dd=dv.set_index('Division'); DIV=[dict(n=d,area=int(dd.Area_km2[d]),pop=float(dd.Population_M[d]),pd=int(dd.PopDensity_per_km2[d]),sites=int((tw.Division==d).sum())) for d in dd.index]
D=dict(mk=mk,t=Tb,div=DIV,map=json.load(open(R/'geo'/'map_paths.json')),pages=PAGES)
out=(R/'dashboard'/'template.html').read_text().replace('__DATA__',json.dumps(D,default=lambda o:float(o) if isinstance(o,(np.floating,np.integer)) else str(o),separators=(',',':')))
(R/'dashboard'/'nextel_dashboard.html').write_text(out); print('built',len(out)//1024,'KB',{k:len(v['r']) for k,v in Tb.items()})
