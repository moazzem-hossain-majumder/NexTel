"""Generates Power BI page backgrounds (1920x1080 PNG) and BUILD_GUIDE.md (step-by-step with exact positions)."""
import pathlib, pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from spec import PAGES, FIELDS, p
R=pathlib.Path(__file__).resolve().parent.parent; OUT=R/'powerbi'; (OUT/'backgrounds').mkdir(parents=True,exist_ok=True)
W,H,NAV,PAD,GAP=1920,1080,230,18,14; X0=NAV+PAD
def F(s,b=False):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
    except Exception: return ImageFont.load_default()
COL=[(255,193,7),(255,122,0),(229,38,43)]; HEX=lambda c:'#%02X%02X%02X'%c; CH={'y':'#FFC107','o':'#FF7A00','r':'#E5262B'}
SLICERS=[('DIVISION','Dim_Division[Division]','Tile, horizontal',248,740),('NETWORK','Dim_Customers[Network]','Tile, horizontal',1000,210),('SEGMENT','Dim_Customers[Segment]','Tile, horizontal',1222,210),('MONTH','Dim_Date[MonthName]','Dropdown, multi-select',1444,458)]
HOME=dict(id='home',rw=[1.9,1,1.1],t='Command Center',sub='NexTel Communications - Bangladesh - 8 divisions',
 kpis=[['subs','Subscribers'],['active','Active'],['churn','Churn'],['arpu','ARPU / month'],['nps','NPS'],['drop','Call drop'],['avail','Availability'],['collect','Collections']],
 panels=[p('Division density map','map','map',8),p('Network & customer health','rings','rings',4),p('Service revenue (M BDT)','col','revM',4,'y'),
  p('Gross adds vs churned','dual','gaCh',4),p('Revenue mix','mixd','mix',4),p('Division scorecard','score','score',8),p('Live insights','text','text',4)])
FIELDS.update(map='see steps',rings='see steps',score='Rows Dim_Division[Division] | [Total Subscribers], [Population Density], [Subscriber Density], [Tower Density], [Churn Rate %], [ARPU], [Call Drop Rate %], [Site Availability %], [Avg CSAT]',
 text='[Insight Drop], [Insight Density], [Insight Churn], [Insight Collections]')
VIS=dict(col='Clustered column chart',line='Area chart',bars='Clustered bar chart',donut='Donut chart',mixd='Donut chart',dual='Clustered column chart',heat='Matrix',gauge='Gauge',score='Matrix',text='Multi-row card')
REC=dict(col='R2',dual='R2',line='R3',bars='R4',donut='R5',mixd='R5',heat='R6',gauge='R7',score='R6',text='R8')
MEAS=dict(rev='Service Revenue',arpu='ARPU',ltv='LTV',ltvcac='LTV to CAC',subs='Total Subscribers',active='Active Subscribers',churn='Churn Rate %',mch='Monthly Churn Rate %',drop='Call Drop Rate %',cssr='CSSR %',
 thr='Avg Throughput Mbps',avail='Site Availability %',mttr='MTTR min',nps='NPS',csat='Avg CSAT',fcr='FCR %',sla='SLA Compliance %',mou='MOU',dgb='Data per Sub GB',tb='Total Data Consumed TB',ad='Streaming Ad Spend',
 collect='Collection Efficiency %',bad='Bad Debt %',overdue='Overdue Amount',billed='Billed',cac='Campaign CAC',roi='Campaign ROI',hc='Headcount',turn='Employee Turnover %',perf='Avg Performance Rating',tpa='Tickets per Agent')
SY,KY,KH=96,152,88
def layout(g):
    cw=(W-X0-PAD-11*GAP)/12; y=SY+46+10; K=[]
    if g.get('kpis'):
        n=len(g['kpis']); kw=(W-X0-PAD-(n-1)*GAP)/n; K=[(g['kpis'][i],int(X0+i*(kw+GAP)),KY,int(kw),KH) for i in range(n)]; y=KY+KH+GAP
    rows=[[]]; c=0
    for x in g['panels']:
        if c+x['w']>12: rows.append([]); c=0
        rows[-1].append((x,c)); c+=x['w']
    avail=H-y-PAD-(len(rows)-1)*GAP; wt=g.get('rw',[1]*len(rows)); hs=[avail*w/sum(wt) for w in wt]; ys=[y+sum(hs[:i])+i*GAP for i in range(len(rows))]
    return K,[(x,int(X0+c*(cw+GAP)),int(ys[ri]),int(x['w']*cw+(x['w']-1)*GAP),int(hs[ri])) for ri,r in enumerate(rows) for x,c in r]
def glow(img,col,box,r,a,bl):
    L=Image.new('RGBA',img.size,(0,0,0,0)); ImageDraw.Draw(L).rounded_rectangle(box,r,outline=col+(a,),width=3)
    return Image.alpha_composite(img.convert('RGBA'),L.filter(ImageFilter.GaussianBlur(bl))).convert('RGB')
def frame(img,box,title,col=(255,122,0),fill=(14,11,8),ts=13):
    img=glow(img,col,list(box),10,70,7); d=ImageDraw.Draw(img,'RGBA'); x,y,x2,y2=box
    d.rounded_rectangle(box,10,fill=fill+(238,),outline=col+(75,),width=1); d.rectangle([x,y,x+40,y+3],fill=col)
    d.text((x+14 if ts>10 else x+10,y+(14 if ts>10 else 3)),title,font=F(ts,ts>10),fill=(255,193,7) if ts>10 else (138,143,152)); return img
# ---------- backgrounds ----------
for n,g in enumerate([HOME]+PAGES[1:]):
    K,P=layout(g); img=Image.new('RGB',(W,H),(5,6,10)); d=ImageDraw.Draw(img,'RGBA')
    for gx in range(0,W,32): d.line([(gx,0),(gx,H)],fill=(255,255,255,9))
    for gy in range(0,H,32): d.line([(0,gy),(W,gy)],fill=(255,255,255,9))
    for col,(cx,cy,rr) in [((255,122,0),(1700,0,420)),((229,38,43),(200,1080,380))]:
        L=Image.new('RGBA',img.size,(0,0,0,0)); ImageDraw.Draw(L).ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=col+(60,)); img=Image.alpha_composite(img.convert('RGBA'),L.filter(ImageFilter.GaussianBlur(120))).convert('RGB')
    d=ImageDraw.Draw(img,'RGBA'); d.rectangle([0,0,NAV,H],fill=(7,8,13)); d.line([(NAV,0),(NAV,H)],fill=(255,122,0,110),width=2)
    d.text((26,26),'NEXTEL',font=F(26,True),fill=(255,150,0)); d.text((26,60),'INTELLIGENCE HUB',font=F(11),fill=(138,143,152))
    d.text((X0,16),g['t'].upper(),font=F(28,True),fill=(245,241,232)); d.text((X0,56),g.get('sub',''),font=F(14),fill=(138,143,152))
    d.rounded_rectangle([W-210,26,W-PAD,54],14,outline=(255,122,0,140),width=1); d.text((W-196,32),'SYNTHETIC DATA',font=F(12),fill=(255,193,7))
    for t,_,_,sx,sw in SLICERS: img=frame(img,(sx,SY,sx+sw,SY+46),t,fill=(10,9,8),ts=9)
    for i,(k,x,y,w,h) in enumerate(K): img=frame(img,(x,y,x+w,y+h),k[1].upper(),COL[i%3],(16,13,8),11); ImageDraw.Draw(img,'RGBA').rectangle([x+8,y,x+w-8,y+3],fill=COL[i%3])
    for x,px,py,w,h in P: img=frame(img,(px,py,px+w,py+h),x['t'].upper())
    img.save(OUT/'backgrounds'/f"{n+1:02d}_{g['id']}.png")
# ---------- validation numbers ----------
rd=lambda n:pd.read_csv(R/'data'/f'{n}.csv'); c=rd('Dim_Customers'); us=rd('Fact_Usage_Monthly'); nf=rd('Fact_Network_Performance'); bl=rd('Fact_Billing'); d=c[c.Division=='Dhaka']
rev=(us.VoiceRev+us.DataRev+us.SMSRev+us.VASRev); nf=nf[nf.Date<='2026-05-31']
V=[('Total Subscribers',f"{len(c):,}"),('Churn Rate %',f"{c.IsChurned.mean()*100:.2f}%"),('Service Revenue',f"{rev.sum():,.0f}"),('ARPU',f"{rev.mean():,.0f}"),('NPS',f"{((c.NPS_Score>=9).mean()-(c.NPS_Score<=6).mean())*100:.1f}"),
 ('Call Drop Rate %',f"{nf.CallDropRate_Pct.mean():.2f}"),('Collection Efficiency %',f"{bl.Paid_BDT.sum()/bl.Billed_BDT.sum()*100:.1f}%"),('With Division = Dhaka: Total Subscribers / Churn',f"{len(d):,} / {d.IsChurned.mean()*100:.2f}%"),
 ('Division = Dhaka and Network = 5G: Total Subscribers',f"{len(d[d.Network=='5G']):,}")]
# ---------- guide ----------
G=[]; a=G.append
a(open(pathlib.Path(__file__).parent/'guide_part_a.md').read())
a("\n# PART C - Build the 9 pages\nFor every page: (1) add the page, (2) apply the background, (3) add the 4 slicers, (4) add the KPI cards, (5) add the panels. Coordinates are in pixels on the 1920 x 1080 canvas. \"Position\" = Horizontal / Vertical, \"Size\" = Width / Height (Format visual > General > Properties). Titles are already drawn in the background image, so every visual has Title OFF.\n")
for n,g in enumerate([HOME]+PAGES[1:]):
    K,P=layout(g); a(f"\n## Page {n+1}: {g['t']}\nBackground file: `powerbi/backgrounds/{n+1:02d}_{g['id']}.png`\n")
    a("**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):\n")
    for t,fld,sty,sx,sw in SLICERS: a(f"- Slicer `{fld}`: {sty}. Position {sx+6} / {SY+14}, Size {sw-12} x 30.")
    if K: a("\n**KPI cards** (recipe R0):\n")
    for i,(k,x,y,w,h) in enumerate(K): a(f"- Card `[{MEAS[k[0]]}]`: Position {x+6} / {y+28}, Size {w-12} x {h-34}. Callout value color {HEX(COL[i%3])}.")
    a("\n**Panels**\n")
    for x,px,py,w,h in P:
        ix,iy,iw,ih=px+10,py+38,w-20,h-48; v=x['v']; t=x['t']
        if v=='map':
            a(f"- **{t}** (3 visuals):\n  1. Slicer `_MapMetric[Metric]`, Tile, horizontal, single-select (Selection: Single select ON, Select all OFF): Position {ix} / {iy-4}, Size {iw} x 32.\n  2. Shape map: Position {ix} / {iy+34}, Size {int(iw*.55)} x {ih-34}. Location `Dim_Division[Division]`, Color saturation `[Map Metric Value]`. Recipe R9.\n  3. Clustered bar chart: Position {ix+int(iw*.55)+10} / {iy+34}, Size {int(iw*.45)-10} x {ih-34}. Y-axis `Dim_Division[Division]`, X-axis `[Map Metric Value]`, sort descending. Recipe R4 (color #FFC107).")
        elif v=='rings':
            a(f"- **{t}**: five Gauge visuals (recipe R7), each Size {int(iw/3)-8} x {int(ih/2)-4}. Build one, then copy 4 times:")
            for j,(m,mx,cl) in enumerate([('Collection Efficiency %',1,'#FFC107'),('Site Availability %',100,'#FF7A00'),('FCR %',1,'#E5262B'),('SLA Compliance %',1,'#C4891A'),('Retention (new measure `Retention % = 1 - [Churn Rate %]`)',1,'#FF9E57')]):
                a(f"  - Gauge {j+1}: Value `[{m.split(' (')[0] if j<4 else 'Retention %'}]`, Maximum {mx}, fill {cl}. Position {ix+(j%3)*(int(iw/3))} / {iy+(j//3)*int(ih/2)}.")
        else:
            wl=FIELDS.get(x['k'],'').split(' | ')
            if v in('col','line','dual'): wells=f"X-axis `{wl[0]}`; Y-axis {wl[1]}"
            elif v=='bars': wells=f"Y-axis `{wl[0]}`; X-axis {wl[1]}"
            elif v in('donut','mixd'): wells=f"Legend `{wl[0]}`; Values {wl[1]}"
            elif v=='heat': wells=f"Rows `Dim_Division[Division]`; Columns `Dim_Date[MonthName]`; Values `[Call Drop Rate %]`"
            elif v=='gauge': wells="Value `[Collection Efficiency %]`; Minimum 0; Maximum 1; Target 0.95"
            else: wells=wl[0] if v=='text' else f"{FIELDS['score']}"
            extra=[]
            if v=='bars': extra.append("Sort: ... > Sort axis > the measure > Sort descending.")
            if x.get('top'): extra.append(f"Filters pane > this visual > drag the category field > Filter type Top N > Show items Top {x['top']} > By value: the measure > Apply filter.")
            if x.get('skip'): extra.append(f"Filters pane > this visual > `Aging Bucket` > Basic filtering > untick `Paid`. Sort axis > Aging Bucket > Sort ascending (alphabetical order is already 1-30d, 31-60d, 61-90d, 90d+).")
            if v=='dual': extra.append("Series colors: first measure #FFC107, second #E5262B. Legend On (top, font #C9C5BB).")
            if x['k'] in('mix',): extra.append("Needs table `_Mix` (Part A7).")
            if x['k']=='npsMix': extra.append("Needs table `_NPS` (Part A7).")
            a(f"- **{t}**: {VIS[v]}. Position {ix} / {iy}, Size {iw} x {ih}. {wells}. Recipe {REC[v]}"+(f", main color {CH[x['c']]}" if v in('col','line','bars') else "")+". "+" ".join(extra))
a("\n## C-Sync. Make the slicers work on every page\n1. On page 1 select the Division slicer > View > Sync slicers > in the pane tick every page in BOTH the Sync and Visible columns.\n2. Repeat for the Network, Segment and Month slicers.\n3. Copy/paste a slicer to other pages only if you prefer; with Sync slicers you add each slicer once per page anyway (Ctrl+C on page 1, Ctrl+V on page 2 pastes at the same position).\n\n## C-Nav. Page navigator\nPage 1 > Insert > Buttons > Navigator > Page navigator. Position 12 / 100, Size 206 x 560. Format visual > Style > Text: font Segoe UI 12, color #F5F1E8. Fill: Default #14110A, Hover #FF7A00 (text #000000), Selected #FF7A00 at 30% transparency 70. Shape > Round corners 8. Layout > Orientation Vertical, Padding 6. Copy it to all 9 pages (same position). Rename the pages first so the labels read well (Command Center, Revenue & ARPU, Subscribers & Churn, Network Performance, Customer Experience, Usage & Digital, Billing & Collections, Sales & Distribution, Workforce).\n")
a(open(pathlib.Path(__file__).parent/'guide_part_d.md').read().replace('__VALID__','\n'.join(f"| {k} | {v} |" for k,v in V)))
(OUT/'BUILD_GUIDE.md').write_text('\n'.join(G)); print('guide',len('\n'.join(G))//1024,'KB')
