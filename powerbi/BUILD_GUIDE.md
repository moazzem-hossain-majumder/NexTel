# NexTel in Power BI: complete build guide

## Is it possible in Power BI?
**Yes, about 90% of it is native.** You will get the same pages, KPI cards, charts, call-drop heatmap, scorecard, Bangladesh division map, slicers, and click-to-filter behaviour (click a bar, slice, month or map division and every visual on every page reacts). Differences you should expect:
- **Glow / neon and bar-grow animation** do not exist in Power BI. The dark cards, borders, gradients and glow are drawn into the 9 background PNGs instead, so the look is very close.
- **Concentric health rings** become 5 small gauges.
- **Map value labels:** the Shape map shows names and tooltips; the ranked bar chart next to it shows the values.
- **Live insights** are DAX text measures in a multi-row card.
- Menu names move slightly between Power BI Desktop releases. If you cannot find an option, type its name in the search box at the top of the Format pane.

Time needed the first time: about 4 to 6 hours. Work in this order: Part A (data and model) > Part B (formatting recipes, read once) > Part C (page by page) > Part D (test).

---
# PART A: Data, model, measures, theme

## A1. Before you start
1. Windows PC with the latest **Power BI Desktop** (Microsoft Store or powerbi.microsoft.com). Sign-in is not needed.
2. Unzip the project to `D:\nextel-portfolio\`. You will use the `data`, `dax`, `theme`, `geo` and `powerbi\backgrounds` folders.
3. Open Power BI Desktop > close the welcome screen > **File > Save as** > `D:\nextel-portfolio\nextel_telecom_master.pbix`. Save often.

## A2. Load the 16 tables
Repeat for each file in `D:\nextel-portfolio\data\`: **Home > Get data > Text/CSV** > pick the file > **Load** (do not click Transform yet).
Files: Dim_Customers, Dim_Employees_HR, Dim_Date, Dim_Division, Dim_Plans, Dim_Towers, Dim_Distributors, Fact_Subscriptions, Fact_Usage_Monthly, Fact_Billing, Fact_Recharge_Sales, Fact_Network_Service_Calls, Fact_Network_Performance, Fact_Network_Outages, Fact_Marketing_Campaigns, Fact_Digital_Streaming_VAS.
Table names must stay exactly the file names (the DAX depends on them).

## A3. Check data types
**Home > Transform data**. Click each query in the left list and look at the icon in each column header (calendar = Date, 123 = number, ABC = text):
- Every column called `Date` in every table = **Date**. `Dim_Date[YearMonth]` = **Whole number**.
- `Fact_Subscriptions[ActivationDate]` and `[ChurnDate]` = **Date** (ChurnDate has blanks, that is correct).
- All `ID` columns = **Text**.
- To fix a column: click its header > **Transform** tab > **Data type** > choose the type.
Then **Home > Close & Apply**.

## A4. Relationships (Model view)
Click the **Model view** icon (three connected boxes, left bar) > **Home > Manage relationships > New**. Create each row below: choose the table, click the column, pick the second table and column, **Cardinality: One to many (1:*)**, **Cross filter direction: Single**, tick **Make this relationship active** (except row 25). Delete any extra relationships Power BI auto-created.

| # | One side (table[column]) | Many side (table[column]) |
|---|---|---|
| 1 | Dim_Division[Division] | Dim_Customers[Division] |
| 2 | Dim_Division[Division] | Dim_Towers[Division] |
| 3 | Dim_Division[Division] | Fact_Marketing_Campaigns[Division] |
| 4 | Dim_Plans[PlanName] | Dim_Customers[PlanType] |
| 5 to 10 | Dim_Customers[CustomerID] | Fact_Subscriptions, Fact_Usage_Monthly, Fact_Billing, Fact_Recharge_Sales, Fact_Network_Service_Calls, Fact_Digital_Streaming_VAS (each `[CustomerID]`) |
| 11 | Dim_Employees_HR[EmployeeID] | Fact_Network_Service_Calls[EmployeeID] |
| 12 to 13 | Dim_Towers[SiteID] | Fact_Network_Performance[SiteID], Fact_Network_Outages[SiteID] |
| 14 | Dim_Distributors[DistributorID] | Fact_Recharge_Sales[DistributorID] |
| 15 to 22 | Dim_Date[Date] | `[Date]` of: Fact_Recharge_Sales, Fact_Network_Service_Calls, Fact_Digital_Streaming_VAS, Fact_Usage_Monthly, Fact_Billing, Fact_Network_Performance, Fact_Network_Outages, Fact_Marketing_Campaigns |
| 23 | Dim_Date[Date] | Fact_Subscriptions[ActivationDate] (active) |
| 24 | Dim_Date[Date] | Fact_Subscriptions[ChurnDate] (**untick "Make this relationship active"**) |

Important: do **not** link `Dim_Division` to `Dim_Employees_HR`. That would create two filter paths to the tickets table and Power BI would reject it. The workforce measures handle the Division filter with `TREATAS` instead (already written in the DAX).
Tidy the diagram: drag Dim_ tables to the top and Fact_ tables below so it looks like a star.

## A5. Date table and month sorting
1. **Data view** (table icon, left bar) > click `Dim_Date` > **Table tools > Mark as date table** > Date column: `Date` > OK.
2. Click the column `MonthName` > **Column tools > Sort by column > YearMonth**. (Do not sort by Month: that mixes years.)

## A6. Measures
1. **Home > Enter data** > in the first column header type `x`, leave one empty row > Name: `_Key_Metrics` > **Load**.
2. Select `_Key_Metrics` in the Data pane > **Home > New measure** (or Table tools > New measure). In the formula bar paste ONE line from `dax\measures.dax` (the whole `Name = formula`) > Enter. Repeat for every measure (about 60). Lines that start with `//` are comments or instructions, do not paste those.
3. Set formats (select the measure > **Measure tools** tab > Format): 
   - **Percentage, 1 decimal:** Churn Rate %, FCR %, SLA Compliance %, Collection Efficiency %, Bad Debt %, Employee Turnover %, Congested Site-Weeks %, Retention %
   - **Percentage, 2 decimals:** Monthly Churn Rate %
   - **Custom format** (type in the Format box) `0.00"%"`: Call Drop Rate %, CSSR %, Site Availability %
   - **Decimal, 1 place:** NPS, Avg CSAT, Data per Sub GB, Avg Performance Rating, Tickets per Agent, Map Metric Value, LTV to CAC, Campaign ROI, Ad Cost per GB
   - **Whole number with thousands separator:** the rest (revenue, subscribers, ARPU, LTV, CAC, MOU, MTTR, counts)
4. When a measure shows an error, read the message: it is almost always a table or column name typed differently (A2) or a missing relationship (A4).

## A7. Helper tables and calculated columns
**Modeling (or Table tools) > New table**, paste each, Enter: `_Mix`, `_NPS`, `_MapMetric` (all in `dax\measures.dax`). Do **not** relate them to anything.
**Table tools > New column** (select the table in the Data pane first):
- `Dim_Customers` > `OTT User = IF(COUNTROWS(RELATEDTABLE(Fact_Digital_Streaming_VAS)) > 0, "With OTT", "No OTT")`
- `Fact_Billing` > `Aging Bucket = SWITCH(TRUE(), Fact_Billing[Paid_BDT] >= Fact_Billing[Billed_BDT], "Paid", Fact_Billing[DaysLate] <= 30, "1-30d", Fact_Billing[DaysLate] <= 60, "31-60d", Fact_Billing[DaysLate] <= 90, "61-90d", "90d+")`
- `Fact_Network_Service_Calls` > `Customer Churned = RELATED(Dim_Customers[IsChurned])`

## A8. Theme
**View > Themes** (click the small arrow) > **Browse for themes** > `D:\nextel-portfolio\theme\nextel_theme.json` > Open. This sets the palette (yellow, orange, red) and switches off visual backgrounds, borders and titles, because the background image draws them.

## A9. Pages, canvas, background, global filter
1. Make 9 pages: click **+** next to the page tabs 8 times. Double-click each tab to rename: Command Center, Revenue & ARPU, Subscribers & Churn, Network Performance, Customer Experience, Usage & Digital, Billing & Collections, Sales & Distribution, Workforce.
2. For **each** page: click an empty spot on the canvas > **Format pane (paint roller icon) > Page tab**:
   - **Canvas settings > Type: Custom; Width 1920; Height 1080** (pixels).
   - **Canvas background > Image > Browse** > pick that page's PNG from `powerbi\backgrounds\` (names are numbered 01 to 09 in page order). **Image fit: Fit. Transparency: 0%.**
   - **Wallpaper > Color #05060A, Transparency 0%.**
   - **View > Page view > Fit to page.**
3. Report-wide date limit (hides the partial June 2026): in the **Filters pane** > **Filters on all pages** > drag `Dim_Date[Date]` there > Filter type **Advanced filtering** > "is on or before" > 31 May 2026 > **Apply filter**.

---
# PART B: Formatting recipes (read once; Part C refers to them)
Select a visual > **Format visual (paint roller)**. Every visual: **General tab > Title: Off; Effects > Background: Off; Visual border: Off**.

**R0 KPI card.** Visualization **Card**. Visual tab: **Callout value** font Segoe UI Semibold, size 30, color given in the step; Display units Auto; **Category label: Off**.

**R1 Slicer.** Visual tab > **Slicer settings > Options**: Style Tile (or Dropdown for Month), Orientation Horizontal (tiles only), **Multi-select with Ctrl/Cmd: Off** (so each click toggles), **Show "Select all": Off**. **Slicer header: Off**. **Values/Items:** font Segoe UI 10, color #C9C5BB; background #14110A; border color #FF7A00 transparency 60%; for the selected state set background #FF7A00 and font color #000000. Menu labels vary: look for Default / Hover / Selected states.

**R2 Column chart (also the dual chart).** X-axis: Values font color #8A8F98, size 9; Title Off. Y-axis: Off. Gridlines: Horizontal, color #2A2A2A. Columns: color per step; Layout: Space between categories (inner padding) 25%. Data labels Off. Legend Off (dual: On, top, #C9C5BB).

**R3 Area chart.** Same axes as R2. Lines: color per step, Stroke width 3. Shaded area: On, transparency 60%. Markers: Off. Legend Off.

**R4 Bar chart.** Y-axis: Values font color #D8D3C8, size 11, Title Off. X-axis: Off. Gridlines: Off. Bars: color per step, inner padding 35%. Data labels: On, color #8A8F98, size 10, Position Outside end. Sort descending by the measure.

**R5 Donut.** Slices: Inner radius 70%. Colors come from the theme in order (yellow, orange, red, brown, grey...). Detail labels: Off. Legend: On, position Right, font #D8D3C8, size 11.

**R6 Matrix (heatmap and scorecard).** Style: None. Grid: Horizontal gridlines color #2A2A2A. Row headers font #D8D3C8 size 11. Column headers font #FFC107 size 9, background Off. Values font #F5F1E8 size 10. Row subtotals Off, Column subtotals Off. **Cell elements > Background color: On > fx**: Format style Gradient, Apply to Values only, Based on the field shown in the step, **Lowest #1A0F02, Highest #E5262B** for bad-is-high measures (call drop, churn) or **Highest #FFC107** for the others. For the scorecard repeat the fx for each value column. For the heatmap set column width about 38 (Format > Column headers > Auto-size column width Off).

**R7 Gauge.** Gauge axis: Min 0, Max and Target per step. Colors: Fill #FFC107 (use the color in the step), Background #1E1B16, Target #FF7A00. Data label font size 20, color #F5F1E8. Target label Off.

**R8 Multi-row card.** Callout values: font Segoe UI 12, color #F5F1E8. Category labels: Off. Cards > Accent bar: On, color #FF7A00, width 3. Background Off.

**R9 Shape map (Bangladesh).** Add the visual **Shape map** (if it is missing: File > Options > Preview features, enable Shape map visual, restart). Format visual > **Map settings > Map type > Custom map > Add map** (the upload button) > `D:\nextel-portfolio\geo\bd_divisions.topojson`. The shapes must appear; the property that matches is `Division`. Colors: **Default color** off, use gradient on Color saturation: Minimum #1A0F02, Center #FF7A00, Maximum #FFC107. Border color #05060A, width 2. Legend Off. Auto zoom On. Projection Mercator.


# PART C - Build the 9 pages
For every page: (1) add the page, (2) apply the background, (3) add the 4 slicers, (4) add the KPI cards, (5) add the panels. Coordinates are in pixels on the 1920 x 1080 canvas. "Position" = Horizontal / Vertical, "Size" = Width / Height (Format visual > General > Properties). Titles are already drawn in the background image, so every visual has Title OFF.


## Page 1: Command Center
Background file: `powerbi/backgrounds/01_home.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[Total Subscribers]`: Position 254 / 180, Size 182 x 54. Callout value color #FFC107.
- Card `[Active Subscribers]`: Position 462 / 180, Size 182 x 54. Callout value color #FF7A00.
- Card `[Churn Rate %]`: Position 671 / 180, Size 182 x 54. Callout value color #E5262B.
- Card `[ARPU]`: Position 879 / 180, Size 182 x 54. Callout value color #FFC107.
- Card `[NPS]`: Position 1088 / 180, Size 182 x 54. Callout value color #FF7A00.
- Card `[Call Drop Rate %]`: Position 1296 / 180, Size 182 x 54. Callout value color #E5262B.
- Card `[Site Availability %]`: Position 1505 / 180, Size 182 x 54. Callout value color #FFC107.
- Card `[Collection Efficiency %]`: Position 1713 / 180, Size 182 x 54. Callout value color #FF7A00.

**Panels**

- **Division density map** (3 visuals):
  1. Slicer `_MapMetric[Metric]`, Tile, horizontal, single-select (Selection: Single select ON, Select all OFF): Position 258 / 288, Size 1078 x 32.
  2. Shape map: Position 258 / 326, Size 592 x 288. Location `Dim_Division[Division]`, Color saturation `[Map Metric Value]`. Recipe R9.
  3. Clustered bar chart: Position 860 / 326, Size 475 x 288. Y-axis `Dim_Division[Division]`, X-axis `[Map Metric Value]`, sort descending. Recipe R4 (color #FFC107).
- **Network & customer health**: five Gauge visuals (recipe R7), each Size 166 x 157. Build one, then copy 4 times:
  - Gauge 1: Value `[Collection Efficiency %]`, Maximum 1, fill #FFC107. Position 1370 / 292.
  - Gauge 2: Value `[Site Availability %]`, Maximum 100, fill #FF7A00. Position 1544 / 292.
  - Gauge 3: Value `[FCR %]`, Maximum 1, fill #E5262B. Position 1718 / 292.
  - Gauge 4: Value `[SLA Compliance %]`, Maximum 1, fill #C4891A. Position 1370 / 453.
  - Gauge 5: Value `[Retention %]`, Maximum 1, fill #FF9E57. Position 1544 / 453.
- **Service revenue (M BDT)**: Clustered column chart. Position 258 / 676, Size 522 x 147. X-axis `Dim_Date[MonthName]`; Y-axis [Service Revenue]. Recipe R2, main color #FFC107. 
- **Gross adds vs churned**: Clustered column chart. Position 814 / 676, Size 522 x 147. X-axis `Dim_Date[MonthName]`; Y-axis [Gross Adds], [Churned (by date)]. Recipe R2. Series colors: first measure #FFC107, second #E5262B. Legend On (top, font #C9C5BB).
- **Revenue mix**: Donut chart. Position 1370 / 676, Size 522 x 147. Legend `_Mix[Service]`; Values [Mix Value]. Recipe R5. Needs table `_Mix` (Part A7).
- **Division scorecard**: Matrix. Position 258 / 885, Size 1078 x 166. Rows Dim_Division[Division] | [Total Subscribers], [Population Density], [Subscriber Density], [Tower Density], [Churn Rate %], [ARPU], [Call Drop Rate %], [Site Availability %], [Avg CSAT]. Recipe R6. 
- **Live insights**: Multi-row card. Position 1370 / 885, Size 522 x 166. [Insight Drop], [Insight Density], [Insight Churn], [Insight Collections]. Recipe R8. 

## Page 2: Revenue & ARPU
Background file: `powerbi/backgrounds/02_rev.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[Service Revenue]`: Position 254 / 180, Size 391 x 54. Callout value color #FFC107.
- Card `[ARPU]`: Position 671 / 180, Size 391 x 54. Callout value color #FF7A00.
- Card `[LTV]`: Position 1088 / 180, Size 391 x 54. Callout value color #E5262B.
- Card `[LTV to CAC]`: Position 1505 / 180, Size 391 x 54. Callout value color #FFC107.

**Panels**

- **Monthly service revenue (৳ M)**: Clustered column chart. Position 258 / 292, Size 800 x 349. X-axis `Dim_Date[MonthName]`; Y-axis [Service Revenue]. Recipe R2, main color #FFC107. 
- **ARPU trend (৳)**: Area chart. Position 1092 / 292, Size 800 x 349. X-axis `Dim_Date[MonthName]`; Y-axis [ARPU]. Recipe R3, main color #FF7A00. 
- **Revenue mix**: Donut chart. Position 258 / 703, Size 522 x 349. Legend `_Mix[Service]`; Values [Mix Value]. Recipe R5. Needs table `_Mix` (Part A7).
- **ARPU by network tech (৳)**: Clustered bar chart. Position 814 / 703, Size 522 x 349. Y-axis `Dim_Customers[Network]`; X-axis [ARPU]. Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Revenue by division (৳ M)**: Clustered bar chart. Position 1370 / 703, Size 522 x 349. Y-axis `Dim_Division[Division]`; X-axis [Service Revenue]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 3: Subscribers & Churn
Background file: `powerbi/backgrounds/03_sub.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[Total Subscribers]`: Position 254 / 180, Size 391 x 54. Callout value color #FFC107.
- Card `[Active Subscribers]`: Position 671 / 180, Size 391 x 54. Callout value color #FF7A00.
- Card `[Churn Rate %]`: Position 1088 / 180, Size 391 x 54. Callout value color #E5262B.
- Card `[Monthly Churn Rate %]`: Position 1505 / 180, Size 391 x 54. Callout value color #FFC107.

**Panels**

- **Gross adds vs churned**: Clustered column chart. Position 258 / 292, Size 800 x 212. X-axis `Dim_Date[MonthName]`; Y-axis [Gross Adds], [Churned (by date)]. Recipe R2. Series colors: first measure #FFC107, second #E5262B. Legend On (top, font #C9C5BB).
- **Net adds**: Clustered column chart. Position 1092 / 292, Size 800 x 212. X-axis `Dim_Date[MonthName]`; Y-axis [Net Adds]. Recipe R2, main color #FFC107. 
- **Churn type**: Donut chart. Position 258 / 566, Size 522 x 212. Legend `Fact_Subscriptions[ChurnType]`; Values [Churned Subscribers]. Recipe R5. 
- **Churn by division %**: Clustered bar chart. Position 814 / 566, Size 522 x 212. Y-axis `Dim_Division[Division]`; X-axis [Churn Rate %]. Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Churn by network %**: Clustered bar chart. Position 1370 / 566, Size 522 x 212. Y-axis `Dim_Customers[Network]`; X-axis [Churn Rate %]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Churn by ticket issue %**: Clustered bar chart. Position 258 / 840, Size 800 x 212. Y-axis `Fact_Network_Service_Calls[IssueCategory]`; X-axis [Ticket Churn Rate %]. Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **OTT effect on churn %**: Clustered bar chart. Position 1092 / 840, Size 800 x 212. Y-axis `Dim_Customers[OTT User]`; X-axis [Churn Rate %]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 4: Network Performance
Background file: `powerbi/backgrounds/04_net.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[Call Drop Rate %]`: Position 254 / 180, Size 307 x 54. Callout value color #FFC107.
- Card `[CSSR %]`: Position 587 / 180, Size 307 x 54. Callout value color #FF7A00.
- Card `[Avg Throughput Mbps]`: Position 921 / 180, Size 307 x 54. Callout value color #E5262B.
- Card `[Site Availability %]`: Position 1254 / 180, Size 307 x 54. Callout value color #FFC107.
- Card `[MTTR min]`: Position 1588 / 180, Size 307 x 54. Callout value color #FF7A00.

**Panels**

- **Call drop heatmap: division x month (%)**: Matrix. Position 258 / 292, Size 1634 x 143. Rows `Dim_Division[Division]`; Columns `Dim_Date[MonthName]`; Values `[Call Drop Rate %]`. Recipe R6. 
- **Call drop trend (%)**: Area chart. Position 258 / 497, Size 800 x 143. X-axis `Dim_Date[MonthName]`; Y-axis [Call Drop Rate %]. Recipe R3, main color #E5262B. 
- **Outages per month**: Clustered column chart. Position 1092 / 497, Size 800 x 143. X-axis `Dim_Date[MonthName]`; Y-axis [Outage Count]. Recipe R2, main color #FF7A00. 
- **Outage causes**: Donut chart. Position 258 / 703, Size 522 x 143. Legend `Fact_Network_Outages[Cause]`; Values [Outage Count]. Recipe R5. 
- **MTTR by cause (min)**: Clustered bar chart. Position 814 / 703, Size 522 x 143. Y-axis `Fact_Network_Outages[Cause]`; X-axis [MTTR min]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Most congested sites (PRB %)**: Clustered bar chart. Position 1370 / 703, Size 522 x 143. Y-axis `Dim_Towers[SiteID]`; X-axis [Avg PRB Utilization] (Top N 8). Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending. Filters pane > this visual > drag the category field > Filter type Top N > Show items Top 8 > By value: the measure > Apply filter.
- **Throughput by area (Mbps)**: Clustered bar chart. Position 258 / 908, Size 800 x 143. Y-axis `Dim_Towers[Area]`; X-axis [Avg Throughput Mbps]. Recipe R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending.
- **Availability by division %**: Clustered bar chart. Position 1092 / 908, Size 800 x 143. Y-axis `Dim_Division[Division]`; X-axis [Site Availability %]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 5: Customer Experience
Background file: `powerbi/backgrounds/05_cx.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[NPS]`: Position 254 / 180, Size 391 x 54. Callout value color #FFC107.
- Card `[Avg CSAT]`: Position 671 / 180, Size 391 x 54. Callout value color #FF7A00.
- Card `[FCR %]`: Position 1088 / 180, Size 391 x 54. Callout value color #E5262B.
- Card `[SLA Compliance %]`: Position 1505 / 180, Size 391 x 54. Callout value color #FFC107.

**Panels**

- **Tickets per month**: Clustered column chart. Position 258 / 292, Size 800 x 212. X-axis `Dim_Date[MonthName]`; Y-axis [Ticket Count]. Recipe R2, main color #FF7A00. 
- **NPS mix**: Donut chart. Position 1092 / 292, Size 383 x 212. Legend `_NPS[Group]`; Values [NPS Group Count]. Recipe R5. Needs table `_NPS` (Part A7).
- **Ticket channels**: Donut chart. Position 1509 / 292, Size 383 x 212. Legend `Fact_Network_Service_Calls[TicketChannel]`; Values [Ticket Count]. Recipe R5. 
- **CSAT by issue**: Clustered bar chart. Position 258 / 566, Size 522 x 212. Y-axis `Fact_Network_Service_Calls[IssueCategory]`; X-axis [Avg CSAT]. Recipe R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending.
- **FCR % by channel**: Clustered bar chart. Position 814 / 566, Size 522 x 212. Y-axis `Fact_Network_Service_Calls[TicketChannel]`; X-axis [FCR %]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **SLA % by issue**: Clustered bar chart. Position 1370 / 566, Size 522 x 212. Y-axis `Fact_Network_Service_Calls[IssueCategory]`; X-axis [SLA Compliance %]. Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Resolution time (min)**: Clustered bar chart. Position 258 / 840, Size 1634 x 212. Y-axis `Fact_Network_Service_Calls[IssueCategory]`; X-axis [Avg Ticket Resolution]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 6: Usage & Digital
Background file: `powerbi/backgrounds/06_use.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[MOU]`: Position 254 / 180, Size 391 x 54. Callout value color #FFC107.
- Card `[Data per Sub GB]`: Position 671 / 180, Size 391 x 54. Callout value color #FF7A00.
- Card `[Total Data Consumed TB]`: Position 1088 / 180, Size 391 x 54. Callout value color #E5262B.
- Card `[Streaming Ad Spend]`: Position 1505 / 180, Size 391 x 54. Callout value color #FFC107.

**Panels**

- **Data per subscriber (GB)**: Area chart. Position 258 / 292, Size 800 x 212. X-axis `Dim_Date[MonthName]`; Y-axis [Data per Sub GB]. Recipe R3, main color #FFC107. 
- **Voice minutes per subscriber**: Area chart. Position 1092 / 292, Size 800 x 212. X-axis `Dim_Date[MonthName]`; Y-axis [MOU]. Recipe R3, main color #FF7A00. 
- **Network mix**: Donut chart. Position 258 / 566, Size 522 x 212. Legend `Dim_Customers[Network]`; Values [Total Subscribers]. Recipe R5. 
- **Streaming by platform (GB)**: Clustered bar chart. Position 814 / 566, Size 522 x 212. Y-axis `Fact_Digital_Streaming_VAS[Platform]`; X-axis [Streaming GB]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Ad spend per GB (৳)**: Clustered bar chart. Position 1370 / 566, Size 522 x 212. Y-axis `Fact_Digital_Streaming_VAS[Platform]`; X-axis [Ad Cost per GB]. Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Monthly streaming (GB)**: Clustered column chart. Position 258 / 840, Size 1634 x 212. X-axis `Dim_Date[MonthName]`; Y-axis [Streaming GB]. Recipe R2, main color #FF7A00. 

## Page 7: Billing & Collections
Background file: `powerbi/backgrounds/07_bill.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[Collection Efficiency %]`: Position 254 / 180, Size 391 x 54. Callout value color #FFC107.
- Card `[Bad Debt %]`: Position 671 / 180, Size 391 x 54. Callout value color #FF7A00.
- Card `[Overdue Amount]`: Position 1088 / 180, Size 391 x 54. Callout value color #E5262B.
- Card `[Billed]`: Position 1505 / 180, Size 391 x 54. Callout value color #FFC107.

**Panels**

- **Collection efficiency (%)**: Area chart. Position 258 / 292, Size 800 x 349. X-axis `Dim_Date[MonthName]`; Y-axis [Collection Efficiency %]. Recipe R3, main color #FFC107. 
- **Overdue aging (৳ M)**: Clustered column chart. Position 1092 / 292, Size 800 x 349. X-axis `Fact_Billing[Aging Bucket]`; Y-axis [Overdue Amount] (filter out Paid). Recipe R2, main color #E5262B. Filters pane > this visual > `Aging Bucket` > Basic filtering > untick `Paid`. Sort axis > Aging Bucket > Sort ascending (alphabetical order is already 1-30d, 31-60d, 61-90d, 90d+).
- **Collection gauge**: Gauge. Position 258 / 703, Size 522 x 349. Value `[Collection Efficiency %]`; Minimum 0; Maximum 1; Target 0.95. Recipe R7. 
- **Bad debt % by division**: Clustered bar chart. Position 814 / 703, Size 522 x 349. Y-axis `Dim_Division[Division]`; X-axis [Bad Debt %]. Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Collection % by division**: Clustered bar chart. Position 1370 / 703, Size 522 x 349. Y-axis `Dim_Division[Division]`; X-axis [Collection Efficiency %]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 8: Sales & Distribution
Background file: `powerbi/backgrounds/08_mkt.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[Campaign CAC]`: Position 254 / 180, Size 530 x 54. Callout value color #FFC107.
- Card `[Campaign ROI]`: Position 810 / 180, Size 530 x 54. Callout value color #FF7A00.
- Card `[LTV to CAC]`: Position 1366 / 180, Size 530 x 54. Callout value color #E5262B.

**Panels**

- **Campaign spend (৳ M)**: Clustered column chart. Position 258 / 292, Size 800 x 349. X-axis `Dim_Date[MonthName]`; Y-axis [Campaign Spend]. Recipe R2, main color #FF7A00. 
- **Acquisition channels**: Donut chart. Position 1092 / 292, Size 383 x 349. Legend `Fact_Subscriptions[AcquisitionChannel]`; Values [Gross Adds]. Recipe R5. 
- **Top-up by distributor tier**: Donut chart. Position 1509 / 292, Size 383 x 349. Legend `Dim_Distributors[Tier]`; Values [Recharge Sales]. Recipe R5. 
- **CAC by channel (৳)**: Clustered bar chart. Position 258 / 703, Size 522 x 349. Y-axis `Fact_Marketing_Campaigns[Channel]`; X-axis [Campaign CAC]. Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **ROI by channel (x)**: Clustered bar chart. Position 814 / 703, Size 522 x 349. Y-axis `Fact_Marketing_Campaigns[Channel]`; X-axis [Campaign ROI]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Top distributors (৳ K)**: Clustered bar chart. Position 1370 / 703, Size 522 x 349. Y-axis `Dim_Distributors[Name]`; X-axis [Recharge Sales] (Top N 8). Recipe R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending. Filters pane > this visual > drag the category field > Filter type Top N > Show items Top 8 > By value: the measure > Apply filter.

## Page 9: Workforce
Background file: `powerbi/backgrounds/09_hr.png`

**Slicers** (recipe R1; add the first one, then copy it to the other pages, see C-Sync):

- Slicer `Dim_Division[Division]`: Tile, horizontal. Position 254 / 110, Size 728 x 30.
- Slicer `Dim_Customers[Network]`: Tile, horizontal. Position 1006 / 110, Size 198 x 30.
- Slicer `Dim_Customers[Segment]`: Tile, horizontal. Position 1228 / 110, Size 198 x 30.
- Slicer `Dim_Date[MonthName]`: Dropdown, multi-select. Position 1450 / 110, Size 446 x 30.

**KPI cards** (recipe R0):

- Card `[Headcount]`: Position 254 / 180, Size 391 x 54. Callout value color #FFC107.
- Card `[Employee Turnover %]`: Position 671 / 180, Size 391 x 54. Callout value color #FF7A00.
- Card `[Avg Performance Rating]`: Position 1088 / 180, Size 391 x 54. Callout value color #E5262B.
- Card `[Tickets per Agent]`: Position 1505 / 180, Size 391 x 54. Callout value color #FFC107.

**Panels**

- **Resolution by dept (min)**: Clustered bar chart. Position 258 / 292, Size 522 x 349. Y-axis `Dim_Employees_HR[Department]`; X-axis [Avg Ticket Resolution]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **CSAT by dept**: Clustered bar chart. Position 814 / 292, Size 522 x 349. Y-axis `Dim_Employees_HR[Department]`; X-axis [Avg CSAT]. Recipe R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending.
- **Turnover % by dept**: Clustered bar chart. Position 1370 / 292, Size 522 x 349. Y-axis `Dim_Employees_HR[Department]`; X-axis [Employee Turnover %]. Recipe R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Performance mix**: Donut chart. Position 258 / 703, Size 522 x 349. Legend `Dim_Employees_HR[PerformanceRating]`; Values [Headcount]. Recipe R5. 
- **Headcount by division**: Clustered bar chart. Position 814 / 703, Size 522 x 349. Y-axis `Dim_Division[Division]`; X-axis [Headcount]. Recipe R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Avg salary by dept (৳ K)**: Clustered bar chart. Position 1370 / 703, Size 522 x 349. Y-axis `Dim_Employees_HR[Department]`; X-axis [Avg Salary]. Recipe R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending.

## C-Sync. Make the slicers work on every page
1. On page 1 select the Division slicer > View > Sync slicers > in the pane tick every page in BOTH the Sync and Visible columns.
2. Repeat for the Network, Segment and Month slicers.
3. Copy/paste a slicer to other pages only if you prefer; with Sync slicers you add each slicer once per page anyway (Ctrl+C on page 1, Ctrl+V on page 2 pastes at the same position).

## C-Nav. Page navigator
Page 1 > Insert > Buttons > Navigator > Page navigator. Position 12 / 100, Size 206 x 560. Format visual > Style > Text: font Segoe UI 12, color #F5F1E8. Fill: Default #14110A, Hover #FF7A00 (text #000000), Selected #FF7A00 at 30% transparency 70. Shape > Round corners 8. Layout > Orientation Vertical, Padding 6. Copy it to all 9 pages (same position). Rename the pages first so the labels read well (Command Center, Revenue & ARPU, Subscribers & Churn, Network Performance, Customer Experience, Usage & Digital, Billing & Collections, Sales & Distribution, Workforce).


---
# PART D: Test it

## D1. Numbers you should see (all slicers cleared)
| Measure | Expected |
|---|---|
| Total Subscribers | 10,000 |
| Churn Rate % | 15.19% |
| Service Revenue | 45,725,052 |
| ARPU | 325 |
| NPS | 20.3 |
| Call Drop Rate % | 0.99 |
| Collection Efficiency % | 90.7% |
| With Division = Dhaka: Total Subscribers / Churn | 2,736 / 14.55% |
| Division = Dhaka and Network = 5G: Total Subscribers | 668 |

If a value is off: check A4 (relationships), A9 step 3 (date filter), and that Dim_Date is marked as a date table.

## D2. Interactions to try (same as the HTML dashboard)
1. Click a division on the map: every page's KPIs and charts change; the other divisions dim.
2. Click **5G** in the Network slicer: ARPU rises (about +45% vs 4G).
3. Click a column in a monthly chart: all visuals cross-filter to that month (click again to clear).
4. Click `4G/5G Speed Drop` in the churn-by-issue bar: ticket visuals filter.
5. Hold Ctrl and click two bars to multi-select.
6. Switch the Map metric tiles: the map and ranked bar change colour and values.
7. Go to another page: the slicers keep their selection (Sync slicers).

## D3. If something is wrong
- **Matrix/bars show only one row or "(Blank)":** the relationship in A4 is missing or the column is typed differently.
- **A measure error mentions "ambiguous path":** you created Dim_Division > Dim_Employees_HR. Delete it.
- **Churned (by date) shows 0:** relationship 24 must exist and be inactive; ChurnDate must be a Date column.
- **Months in wrong order:** redo A5 step 2 (sort by YearMonth).
- **Shape map blank:** re-add the custom map (R9); the Location field must be `Dim_Division[Division]`.
- **Cards show wrong totals after a click:** Format tab > Edit interactions only if you intentionally want a visual not to react; leave defaults.
- **Slow:** none expected; the largest table has about 141,000 rows.

## D4. Finish and share
Save the .pbix. Take screenshots (Win+Shift+S) of each page into `screenshots\`. For GitHub, commit the project folder (the .pbix is a binary; keep it under 100 MB). To publish online use Home > Publish (needs a work/school Power BI account).
