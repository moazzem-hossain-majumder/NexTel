import pandas as pd, numpy as np, zipfile, os
from datetime import datetime, timedelta
rng = np.random.default_rng(42)
NC, NE, NR, NT, NS = 10000, 150, 40000, 18000, 20000
START = datetime(2025, 1, 1); DAYS = 540
regions = ['Barishal','Chattogram','Dhaka','Khulna','Mymensingh','Rajshahi','Rangpur','Sylhet']
plans = ['Unlimited Data Max','Prepaid Saver 30D','Postpaid Corporate','Student Special 4G','Family Bundle']
rd = lambda n: [START + timedelta(days=int(x)) for x in rng.integers(0, DAYS, n)]

cust = pd.DataFrame({'CustomerID':[f'CUST-{10000+i}' for i in range(NC)],
 'Age':rng.integers(18,65,NC),'Gender':rng.choice(['Male','Female'],NC),
 'Region':rng.choice(regions,NC,p=[.06,.19,.28,.10,.08,.11,.10,.08]),
 'DeviceBrand':rng.choice(['Samsung S23 Ultra','iPhone 15 Pro','Xiaomi Redmi Note 12','Realme 11','Vivo Y20'],NC),
 'PlanType':rng.choice(plans,NC,p=[.25,.35,.15,.15,.10]),
 'TenureMonths':rng.integers(1,72,NC),'NPS_Score':rng.integers(1,11,NC)})
cust['Segment']=np.where(cust.PlanType.isin(['Postpaid Corporate','Family Bundle']),'Postpaid','Prepaid')

emp = pd.DataFrame({'EmployeeID':[f'EMP-{500+i}' for i in range(NE)],'Name':[f'Agent_{i}' for i in range(NE)],
 'Department':rng.choice(['Customer Support','Retail Sales','Network Operations','Enterprise Sales'],NE),
 'Region':rng.choice(regions,NE),'MonthlySalary':rng.integers(25000,95000,NE),
 'PerformanceRating':rng.choice([1,2,3,4,5],NE,p=[.05,.15,.5,.2,.1]),'TenureYears':rng.integers(0,12,NE),
 'LeftCompany':rng.choice([0,1],NE,p=[.88,.12])})

tick = pd.DataFrame({'TicketID':[f'TCK-{50000+i}' for i in range(NT)],
 'CustomerID':rng.choice(cust.CustomerID,NT),'EmployeeID':rng.choice(emp.EmployeeID,NT),'Date':rd(NT),
 'IssueCategory':rng.choice(['4G/5G Speed Drop','Billing Dispute','SIM Swap','OTT Activation','Network Outage'],NT,p=[.28,.22,.15,.15,.20]),
 'ResolutionTimeMinutes':rng.integers(5,240,NT),'SatisfactionScore':rng.choice([1,2,3,4,5],NT,p=[.1,.15,.25,.35,.15])})

stream = pd.DataFrame({'StreamID':[f'STR-{80000+i}' for i in range(NS)],'CustomerID':rng.choice(cust.CustomerID,NS),
 'Date':rd(NS),'Platform':rng.choice(['Toffee OTT','SonyLIV Pass','Spotify Data Pack','Gaming Boost'],NS,p=[.4,.2,.25,.15]),
 'DataConsumed_GB':rng.uniform(.5,12.5,NS).round(2),'SessionDurationMin':rng.integers(10,180,NS),
 'AdSpend_BDT':rng.integers(5,60,NS)})

# network quality columns (separate RNG so earlier data is unchanged)
r2=np.random.default_rng(7)
sd=(tick.IssueCategory.isin(['4G/5G Speed Drop','Network Outage'])).values
tick['Latency_ms']=np.where(sd,r2.normal(95,25,NT),r2.normal(45,12,NT)).clip(10,300).round(0).astype(int)
tick['NetworkDropRate_Pct']=np.where(sd,r2.uniform(2,9,NT),r2.uniform(0.2,2.5,NT)).round(2)
tick['SLA_Met']=(tick.ResolutionTimeMinutes<=120).astype(int)

# churn driven by behaviour (so insights are real, not claimed)
sp = tick[tick.IssueCategory=='4G/5G Speed Drop'].groupby('CustomerID').size()
ott = set(stream.CustomerID)
p = np.full(NC,.14)
p += cust.CustomerID.map(sp).fillna(0).clip(0,3).values*.07
p -= np.where(cust.CustomerID.isin(ott),.05,0)
p += np.where(cust.NPS_Score<=4,.06,0)
cust['IsChurned']=(rng.random(NC)<np.clip(p,.02,.7)).astype(int)
cust['RiskScore']=(np.clip(p,0,1)*100).round(1)

ch = rng.choice(['Mobile App','USSD *121#','Retail Shop','Bank Transfer'],NR,p=[.35,.3,.25,.1])
base = np.where(ch=='Mobile App',[.12,.25,.28,.2,.1,.05][0],0)
amts=[]
for c in ch:
    pr=[.12,.22,.26,.20,.12,.08] if c=='Mobile App' else [.22,.32,.24,.13,.06,.03]
    amts.append(rng.choice([99,199,349,599,999,1499],p=pr))
rech = pd.DataFrame({'TransactionID':[f'TXN-{100000+i}' for i in range(NR)],'CustomerID':rng.choice(cust.CustomerID,NR),
 'Date':rd(NR),'Amount_BDT':amts,'Channel':ch})

sub = cust[['CustomerID','PlanType','Segment']].copy()
sub['ActivationDate']=[START - timedelta(days=int(t)*30) for t in cust.TenureMonths]
sub['Status']=np.where(cust.IsChurned==1,'Churned','Active')
sub['AcquisitionChannel']=rng.choice(['Retail','Online','Referral','Agent'],NC)
sub['CAC_BDT']=rng.integers(300,1500,NC)
sub.insert(0,'SubscriptionID',[f'SUB-{i}' for i in range(NC)])

dd = pd.DataFrame({'Date':pd.date_range(START,periods=DAYS)})
dd['Year']=dd.Date.dt.year; dd['Month']=dd.Date.dt.month; dd['MonthName']=dd.Date.dt.strftime('%b %Y')
dd['Quarter']='Q'+dd.Date.dt.quarter.astype(str)
dd['YearMonth']=dd.Year*100+dd.Month  # sort key for MonthName


# ================= v2: full telecom coverage (separate RNG, earlier data unchanged) =================
r3=np.random.default_rng(11); END=pd.Timestamp('2026-06-15'); S0=pd.Timestamp(START)
D8=lambda x: pd.Series(x).dt.strftime('%Y-%m-%d').values
# subscriptions: activation, churn date, churn type
ad=pd.Series([END-pd.Timedelta(days=int(t)*30) for t in cust.TenureMonths])
lo=ad.where(ad>S0,S0); span=(END-lo).dt.days.clip(lower=1)
cd=lo+pd.to_timedelta((r3.random(NC)*span).astype(int),unit='D')
ch_=cust.IsChurned.values==1
sub['ActivationDate']=D8(ad)
sub['ChurnDate']=np.where(ch_,D8(cd),None)
sub['ChurnType']=np.where(ch_,r3.choice(['Voluntary','Involuntary'],NC,p=[.7,.3]),None)
cust['NPS_Score']=np.clip(cust.NPS_Score+3,1,10)  # shift so NPS is realistic; order preserved
cust['Network']=r3.choice(['3G','4G','5G'],NC,p=[.10,.65,.25])
tick['TicketChannel']=r3.choice(['Call Center','App Chat','Retail Store','Social Media'],NT,p=[.4,.3,.2,.1])
tick['FirstContactResolved']=r3.choice([0,1],NT,p=[.28,.72])
# dimensions: region, plans, towers, distributors
div_d=pd.DataFrame({'Division':regions,'Area_km2':[13297,33909,31119,22285,10485,18174,16185,12635],
 'Population_M':[9.3,33.2,39.2,17.4,12.2,20.4,17.6,11.1]})  # approx. 2022 census, verify before publishing
div_d['PopDensity_per_km2']=(div_d.Population_M*1e6/div_d.Area_km2).round(0).astype(int)
plans_d=pd.DataFrame({'PlanName':plans,'Segment':['Prepaid','Prepaid','Postpaid','Prepaid','Postpaid'],
 'MonthlyPrice_BDT':[999,349,1499,199,1199],'DataAllowance_GB':[100,30,150,20,120],'ValidityDays':[30,30,30,30,30]})
NTW=300
tw=pd.DataFrame({'SiteID':[f'SITE-{1000+i}' for i in range(NTW)],'Region':r3.choice(regions,NTW,p=[.07,.17,.22,.11,.09,.12,.12,.10]),
 'Area':r3.choice(['Urban','Semi-Urban','Rural'],NTW,p=[.4,.3,.3]),'Technology':r3.choice(['4G','5G','4G+5G'],NTW,p=[.5,.2,.3]),
 'LaunchYear':r3.integers(2015,2025,NTW)})
ND=80
dist=pd.DataFrame({'DistributorID':[f'DST-{i}' for i in range(ND)],'Name':[f'Distributor_{i}' for i in range(ND)],
 'Region':r3.choice(regions,ND),'Tier':r3.choice(['Gold','Silver','Bronze'],ND,p=[.2,.35,.45])})
dist=pd.concat([dist,pd.DataFrame([{'DistributorID':'DIGITAL','Name':'Digital / Self-service','Region':'All','Tier':'Digital'}])],ignore_index=True)
w=r3.dirichlet(np.ones(ND)*.7)
rech['DistributorID']=np.where(rech.Channel=='Retail Shop',r3.choice(dist.DistributorID[:ND],NR,p=w),'DIGITAL')
# weekly network performance per site
weeks=pd.date_range(S0,END,freq='7D')
npf=pd.MultiIndex.from_product([tw.SiteID,weeks],names=['SiteID','Date']).to_frame(index=False); n=len(npf)
rural=npf.SiteID.map(dict(zip(tw.SiteID,tw.Area))).eq('Rural').values.astype(float)
npf['CallDropRate_Pct']=(r3.gamma(2,.4,n)+rural*.6).round(2)
npf['CSSR_Pct']=(99.2-r3.gamma(2,.25,n)-rural*.5).clip(90,100).round(2)
npf['Throughput_Mbps']=(r3.normal(28,7,n)-rural*8).clip(3,120).round(1)
npf['Availability_Pct']=(99.9-r3.gamma(1.5,.12,n)-rural*.2).clip(95,100).round(2)
npf['PRB_Utilization_Pct']=r3.normal(58,14,n).clip(10,99).round(1)
npf['TrafficTB']=r3.uniform(.2,3,n).round(2)
npf['Date']=D8(npf.Date)
# outages
NO=900
og=pd.DataFrame({'OutageID':[f'OUT-{i}' for i in range(NO)],'SiteID':r3.choice(tw.SiteID,NO),
 'Date':D8([S0+pd.Timedelta(days=int(x)) for x in r3.integers(0,DAYS-30,NO)]),
 'Cause':r3.choice(['Power Failure','Fiber Cut','Hardware Fault','Congestion','Weather'],NO,p=[.3,.25,.2,.1,.15])})
og['DurationMin']=(r3.gamma(2,60,NO)+10).round(0).astype(int)+np.where(og.Cause=='Fiber Cut',90,0)
og['CustomersImpacted']=r3.integers(200,6000,NO); og['SLA_Breach']=(og.DurationMin>240).astype(int)
# monthly usage (only months a subscriber is active)
months=pd.date_range(S0,'2026-05-01',freq='MS')
u=cust[['CustomerID','Segment','Network']].merge(sub[['CustomerID','ActivationDate','ChurnDate']],on='CustomerID').merge(pd.DataFrame({'Date':months}),how='cross')
a_=pd.to_datetime(u.ActivationDate); c_=pd.to_datetime(u.ChurnDate)
u=u[(a_<=u.Date+pd.offsets.MonthEnd(0))&(c_.isna()|(c_>=u.Date))].reset_index(drop=True); m=len(u)
pre=(u.Segment=='Postpaid').values; g5=(u.Network=='5G').values
u['VoiceMin']=(r3.gamma(3,90,m)*(1+pre*.6)).round(0)
u['SMS']=r3.poisson(40,m)
u['DataGB']=(r3.gamma(2.5,2,m)*(1+g5*1.2+pre*.4)).round(2)
u['VoiceRev']=(u.VoiceMin*.45).round(0); u['DataRev']=(u.DataGB*22).round(0); u['SMSRev']=(u.SMS*.3).round(0)
u['VASRev']=(r3.binomial(1,.35,m)*r3.choice([20,49,99],m)).astype(int)
# postpaid billing & collections
b=u[u.Segment=='Postpaid'][['CustomerID','Date','VoiceRev','DataRev','SMSRev','VASRev']].copy(); k=len(b)
b['Billed_BDT']=(b.VoiceRev+b.DataRev+b.SMSRev+b.VASRev+300).round(0)
x=r3.random(k)
b['Paid_BDT']=np.where(x<.06,0,np.where(x<.15,(b.Billed_BDT*r3.uniform(.3,.9,k)).round(0),b.Billed_BDT))
b['DaysLate']=np.where(b.Paid_BDT<b.Billed_BDT,r3.integers(5,130,k),r3.integers(0,4,k))
b['WrittenOff_BDT']=np.where((b.DaysLate>90)&(b.Paid_BDT<b.Billed_BDT),b.Billed_BDT-b.Paid_BDT,0)
b=b[['CustomerID','Date','Billed_BDT','Paid_BDT','DaysLate','WrittenOff_BDT']]; b['Date']=D8(b.Date)
b.insert(0,'InvoiceID',[f'INV-{i}' for i in range(k)])
u=u[['CustomerID','Date','Network','VoiceMin','SMS','DataGB','VoiceRev','DataRev','SMSRev','VASRev']]; u['Date']=D8(u.Date)
# marketing campaigns
NM=72
cp=pd.DataFrame({'CampaignID':[f'CMP-{i}' for i in range(NM)],'Date':D8([S0+pd.Timedelta(days=int(x)) for x in r3.integers(0,DAYS-30,NM)]),
 'Channel':r3.choice(['Digital Ads','Retail Promo','Referral','TV/Radio','Agent Drive'],NM),'Region':r3.choice(regions,NM),
 'Spend_BDT':r3.integers(100000,700000,NM),'Leads':r3.integers(800,4000,NM)})
cp['Conversions']=(cp.Leads*r3.uniform(.05,.2,NM)).astype(int)
cp['RevenueGenerated_BDT']=(cp.Conversions*r3.uniform(1800,4200,NM)).round(0)
T={'Dim_Customers':cust,'Dim_Employees_HR':emp,'Dim_Date':dd,'Dim_Division':div_d,'Dim_Plans':plans_d,'Dim_Towers':tw,'Dim_Distributors':dist,
 'Fact_Subscriptions':sub,'Fact_Usage_Monthly':u,'Fact_Billing':b,'Fact_Recharge_Sales':rech,'Fact_Network_Service_Calls':tick,
 'Fact_Network_Performance':npf,'Fact_Network_Outages':og,'Fact_Marketing_Campaigns':cp,'Fact_Digital_Streaming_VAS':stream}
os.makedirs('data',exist_ok=True)
for nme,df in T.items():
    df=df.rename(columns={'Region':'Division'}); df.to_csv(f'data/{nme}.csv',index=False); print(nme,len(df))
