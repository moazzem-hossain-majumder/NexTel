import pandas as pd, pathlib, pytest
D = pathlib.Path(__file__).parent.parent / "data"
N = ["Dim_Customers","Dim_Employees_HR","Dim_Date","Dim_Division","Dim_Plans","Dim_Towers","Dim_Distributors","Fact_Subscriptions","Fact_Usage_Monthly",
     "Fact_Billing","Fact_Recharge_Sales","Fact_Network_Service_Calls","Fact_Network_Performance","Fact_Network_Outages","Fact_Marketing_Campaigns","Fact_Digital_Streaming_VAS"]
DIVS = {"Barishal","Chattogram","Dhaka","Khulna","Mymensingh","Rajshahi","Rangpur","Sylhet"}
@pytest.fixture(scope="module")
def d(): return {n: pd.read_csv(D/f"{n}.csv") for n in N}
def test_eight_divisions(d):
    assert set(d["Dim_Division"].Division) == DIVS
    for t in ["Dim_Customers","Dim_Towers","Dim_Employees_HR"]: assert set(d[t].Division) <= DIVS, t
def test_pks(d):
    for t,k in [("Dim_Customers","CustomerID"),("Dim_Employees_HR","EmployeeID"),("Dim_Date","Date"),("Dim_Towers","SiteID"),("Dim_Distributors","DistributorID"),("Fact_Billing","InvoiceID")]:
        assert d[t][k].is_unique, t
def test_fks(d):
    c=set(d["Dim_Customers"].CustomerID)
    for f in ["Fact_Subscriptions","Fact_Usage_Monthly","Fact_Billing","Fact_Recharge_Sales","Fact_Network_Service_Calls","Fact_Digital_Streaming_VAS"]: assert d[f].CustomerID.isin(c).all(), f
    assert d["Fact_Network_Service_Calls"].EmployeeID.isin(d["Dim_Employees_HR"].EmployeeID).all()
    s=set(d["Dim_Towers"].SiteID)
    for f in ["Fact_Network_Performance","Fact_Network_Outages"]: assert d[f].SiteID.isin(s).all(), f
    assert d["Fact_Recharge_Sales"].DistributorID.isin(d["Dim_Distributors"].DistributorID).all()
def test_dates_in_calendar(d):
    cal=set(d["Dim_Date"].Date)
    for f in ["Fact_Recharge_Sales","Fact_Network_Service_Calls","Fact_Digital_Streaming_VAS","Fact_Usage_Monthly","Fact_Billing","Fact_Network_Performance","Fact_Network_Outages","Fact_Marketing_Campaigns"]:
        assert d[f].Date.isin(cal).all(), f
    assert d["Fact_Subscriptions"].ChurnDate.dropna().isin(cal).all()
def test_no_nulls(d):
    for n,df in d.items():
        cols=[c for c in df.columns if not (n=="Fact_Subscriptions" and c in ("ChurnDate","ChurnType"))]
        assert not df[cols].isna().any().any(), n
def test_ranges(d):
    n=d["Fact_Network_Performance"]
    assert n.Availability_Pct.between(95,100).all() and n.CSSR_Pct.between(90,100).all() and n.CallDropRate_Pct.ge(0).all()
    b=d["Fact_Billing"]; assert (b.Paid_BDT<=b.Billed_BDT).all() and (b.WrittenOff_BDT<=b.Billed_BDT).all()
    assert d["Fact_Usage_Monthly"].DataGB.gt(0).all()
def test_churn_and_nps_plausible(d):
    c=d["Dim_Customers"]; assert 0.10 < c.IsChurned.mean() < 0.25
    nps=((c.NPS_Score>=9).mean()-(c.NPS_Score<=6).mean())*100; assert -10 < nps < 60
def test_churn_dates_consistent(d):
    s=d["Fact_Subscriptions"]; assert (s.ChurnDate.notna()==(s.Status=="Churned")).all()
def test_insights_hold(d):
    t=d["Fact_Network_Service_Calls"].merge(d["Dim_Customers"],on="CustomerID"); r=t.groupby("IssueCategory").IsChurned.mean()
    assert r["4G/5G Speed Drop"] > r["Billing Dispute"]*1.3
    rc=d["Fact_Recharge_Sales"].groupby("Channel").Amount_BDT.mean(); assert rc["Mobile App"] > rc["Retail Shop"]*1.2
    c=d["Dim_Customers"]; o=c.assign(o=c.CustomerID.isin(d["Fact_Digital_Streaming_VAS"].CustomerID)).groupby("o").IsChurned.mean(); assert o[True] < o[False]*0.85
    u=d["Fact_Usage_Monthly"]; u["R"]=u.VoiceRev+u.DataRev+u.SMSRev+u.VASRev; a=u.groupby("Network").R.mean(); assert a["5G"] > a["4G"]*1.2
def test_date_table_sort_key(d):
    dd=d["Dim_Date"]; assert (dd.YearMonth==dd.Year*100+dd.Month).all()
    assert dd.groupby("MonthName").YearMonth.nunique().max()==1
