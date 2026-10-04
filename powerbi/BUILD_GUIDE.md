# NexTel in Power BI: complete build guide

## Is it possible in Power BI?
**Yes, about 90% of it is native.** You will get the same pages, KPI cards, charts, call-drop heatmap, scorecard, Bangladesh division map, slicers, and click-to-filter behaviour (click a bar, slice, month or map division and every visual on every page reacts). Differences you should expect:
- **Glow / neon and bar-grow animation:** Power BI has no animations and no true glow. You get dark cards, rounded orange borders, yellow titles and a soft orange shadow from normal visual formatting, which comes very close. Everything is built natively (visuals, shapes, text boxes), no images.
- **Concentric health rings** become 5 small gauges.
- **Map value labels:** the Shape map shows names and tooltips; the ranked bar chart next to it shows the values.
- **Live insights** are DAX text measures in a multi-row card.
- Menu names move slightly between Power BI Desktop releases. If you cannot find an option, type its name in the search box at the top of the Format pane.

Time needed the first time: about 4 to 6 hours. Work in this order: Part A (data and model) > Part B (formatting recipes, read once) > Part C (page by page) > Part D (test).

---
# PART A: Data, model, measures, theme

## A1. Before you start
1. Windows PC with the latest **Power BI Desktop** (Microsoft Store or powerbi.microsoft.com). Sign-in is not needed.
2. Unzip the project to `D:\nextel-portfolio\`. You will use the `data`, `dax`, `theme` and `geo` folders.
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
**View > Themes** (click the small arrow) > **Browse for themes** > `D:\nextel-portfolio\theme\nextel_theme.json` > Open. This sets the palette (yellow, orange, red) and makes every new visual look like a card: near-black background, dark-orange rounded border, yellow left-aligned title, no visual header icons. **Check it:** insert any visual; if it does not look like that, apply recipe R-BOX (Part B) to it once and copy the look to others with **Home > Format painter**.

## A9. Pages, canvas, background, global filter
1. Make 9 pages: click **+** next to the page tabs 8 times. Double-click each tab to rename: Command Center, Revenue & ARPU, Subscribers & Churn, Network Performance, Customer Experience, Usage & Digital, Billing & Collections, Sales & Distribution, Workforce.
2. For **each** page: click an empty spot on the canvas > **Format pane (paint roller icon) > Page tab**:
   - **Canvas settings > Type: Custom; Width 1920; Height 1080** (pixels).
   - **Canvas background > Color #05060A, Transparency 0%.**
   - **Wallpaper > Color #05060A, Transparency 0%.**
   - **View > Page view > Fit to page.**
3. Report-wide date limit (hides the partial June 2026): in the **Filters pane** > **Filters on all pages** > drag `Dim_Date[Date]` there > Filter type **Advanced filtering** > "is on or before" > 31 May 2026 > **Apply filter**.

---
# PART B: Formatting recipes (read once; Part C refers to them)
Select a visual > **Format visual (paint roller)**.

**R-BOX Card look (every visual).** General tab: **Title: On**, text as given in the step, font Segoe UI Semibold 12, color #FFC107, alignment Left, title background Off. **Effects > Background: On**, color #0E0B08, transparency 4%. **Effects > Visual border: On**, color #5C2D00, rounded corners 10 px. **Effects > Shadow: On**, color #FF7A00, transparency 80%, blur 14, offset 0 / 0 (labels vary: choose "Custom" shadow if you see presets). **Header icons: Off** (Format > General > Header icons). Padding (General > Properties > Padding) 8 px all sides.

**R0 KPI card.** Visualization **Card**. R-BOX, but Title text = the KPI name in capitals, font Segoe UI 10, color #8A8F98. Visual tab: **Callout value** font Segoe UI Semibold, size 30, color given in the step; Display units Auto; **Category label: Off**. Then add a thin colour strip on the card top: Insert > Shapes > Rectangle, 3 px high, same width as the card, same X, Y = card Y, fill = callout color, line Off (bring it to front in the Selection pane).

**R1 Slicer.** Visual tab > **Slicer settings > Options**: Style Tile (or Dropdown for Month), Orientation Horizontal (tiles only), **Multi-select with Ctrl/Cmd: Off** (so each click toggles), **Show "Select all": Off**. **Slicer header: On**, text the field name in capitals, font Segoe UI 9, color #8A8F98. **Values/Items:** font Segoe UI 10, color #C9C5BB; background #14110A; border color #FF7A00 transparency 60%; for the selected state set background #FF7A00 and font color #000000. Menu labels vary: look for Default / Hover / Selected states.

**R2 Column chart (also the dual chart).** X-axis: Values font color #8A8F98, size 9; Title Off. Y-axis: Off. Gridlines: Horizontal, color #2A2A2A. Columns: color per step; Layout: Space between categories (inner padding) 25%. Data labels Off. Legend Off (dual: On, top, #C9C5BB).

**R3 Area chart.** Same axes as R2. Lines: color per step, Stroke width 3. Shaded area: On, transparency 60%. Markers: Off. Legend Off.

**R4 Bar chart.** Y-axis: Values font color #D8D3C8, size 11, Title Off. X-axis: Off. Gridlines: Off. Bars: color per step, inner padding 35%. Data labels: On, color #8A8F98, size 10, Position Outside end. Sort descending by the measure.

**R5 Donut.** Slices: Inner radius 70%. Colors come from the theme in order (yellow, orange, red, brown, grey...). Detail labels: Off. Legend: On, position Right, font #D8D3C8, size 11.

**R6 Matrix (heatmap and scorecard).** Style: None. Grid: Horizontal gridlines color #2A2A2A. Row headers font #D8D3C8 size 11. Column headers font #FFC107 size 9, background Off. Values font #F5F1E8 size 10. Row subtotals Off, Column subtotals Off. **Cell elements > Background color: On > fx**: Format style Gradient, Apply to Values only, Based on the field shown in the step, **Lowest #1A0F02, Highest #E5262B** for bad-is-high measures (call drop, churn) or **Highest #FFC107** for the others. For the scorecard repeat the fx for each value column. For the heatmap set column width about 38 (Format > Column headers > Auto-size column width Off).

**R7 Gauge.** Gauge axis: Min 0, Max and Target per step. Colors: Fill #FFC107 (use the color in the step), Background #1E1B16, Target #FF7A00. Data label font size 20, color #F5F1E8. Target label Off.

**R8 Multi-row card.** Callout values: font Segoe UI 12, color #F5F1E8. Category labels: Off. Cards > Accent bar: On, color #FF7A00, width 3. Background Off.

**R9 Shape map (Bangladesh).** Add the visual **Shape map** (if it is missing: File > Options > Preview features, enable Shape map visual, restart). Format visual > **Map settings > Map type > Custom map > Add map** (the upload button) > `D:\nextel-portfolio\geo\bd_divisions.topojson`. The shapes must appear; the property that matches is `Division`. Colors: **Default color** off, use gradient on Color saturation: Minimum #1A0F02, Center #FF7A00, Maximum #FFC107. Border color #05060A, width 2. Legend Off. Auto zoom On. Projection Mercator.


# PART C: Build the 9 pages (all native, no images)
Coordinates are pixels on the 1920 x 1080 canvas. Set them in **Format visual > General > Properties > Size / Position** (Horizontal = X, Vertical = Y; for shapes and text boxes the same fields are under Format shape / Format text box > Size & position). Open **View > Selection pane** to select, rename, hide and reorder objects. Each chart is a visual that already looks like a card (recipe R-BOX), so no separate frames are needed.

## C0. Page chrome (build once on page 1, then copy to all 9 pages)
1. **Sidebar:** Insert > Shapes > Rectangle. Position 0 / 0, Size 230 x 1080. Format shape: Fill #07080D, Line Off. Selection pane: send to back.
2. **Sidebar edge:** Rectangle, Position 229 / 0, Size 2 x 1080, Fill #FF7A00, transparency 45%, Line Off.
3. **Logo:** Insert > Text box, text `NEXTEL`, Position 20 / 14, Size 190 x 46, font Segoe UI Semibold 26, color #FF9600. Second text box `INTELLIGENCE HUB`, Position 20 / 58, Size 190 x 22, font Segoe UI 10, color #8A8F98.
4. **Page title:** Text box, Position 248 / 8, Size 1200 x 44, font Segoe UI Semibold 28, color #F5F1E8, all capitals. **Subtitle:** Text box, Position 248 / 52, Size 1200 x 28, font Segoe UI 13, color #8A8F98.
5. **Badge:** Insert > Shapes > Rectangle (rounded corners 14), Position 1690 / 18, Size 212 x 30, Fill Off, Line #FF7A00 1 px. Type `SYNTHETIC DATA` in it: Segoe UI 11, color #FFC107, centered.
6. **Navigator:** Insert > Buttons > Navigator > Page navigator. Position 12 / 100, Size 206 x 560. Format visual > Style > Text: Segoe UI 12, color #F5F1E8. Fill: Default #14110A, Hover #FF7A00 (text #000000), Selected #FF7A00 at transparency 70%. Shape > Round corners 8. Layout > Orientation Vertical, Padding 6. Title Off, Background Off, Border Off.
7. Select items 1 to 6 (Selection pane, Ctrl+click) > Ctrl+C > go to page 2 > Ctrl+V (they paste at the same position). Repeat for pages 3 to 9. On each page change only the title and subtitle texts (given in each page below).


## Page 1: Command Center
Page title text: `COMMAND CENTER`. Subtitle: `NexTel Communications - Bangladesh - 8 divisions`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[Total Subscribers]`, title `SUBSCRIBERS`: Position 248 / 152, Size 194 x 88. Callout color #FFC107. Color strip: rectangle 194 x 3 at 248 / 152, fill #FFC107.
- Card `[Active Subscribers]`, title `ACTIVE`: Position 456 / 152, Size 194 x 88. Callout color #FF7A00. Color strip: rectangle 194 x 3 at 456 / 152, fill #FF7A00.
- Card `[Churn Rate %]`, title `CHURN`: Position 665 / 152, Size 194 x 88. Callout color #E5262B. Color strip: rectangle 194 x 3 at 665 / 152, fill #E5262B.
- Card `[ARPU]`, title `ARPU / MONTH`: Position 873 / 152, Size 194 x 88. Callout color #FFC107. Color strip: rectangle 194 x 3 at 873 / 152, fill #FFC107.
- Card `[NPS]`, title `NPS`: Position 1082 / 152, Size 194 x 88. Callout color #FF7A00. Color strip: rectangle 194 x 3 at 1082 / 152, fill #FF7A00.
- Card `[Call Drop Rate %]`, title `CALL DROP`: Position 1290 / 152, Size 194 x 88. Callout color #E5262B. Color strip: rectangle 194 x 3 at 1290 / 152, fill #E5262B.
- Card `[Site Availability %]`, title `AVAILABILITY`: Position 1499 / 152, Size 194 x 88. Callout color #FFC107. Color strip: rectangle 194 x 3 at 1499 / 152, fill #FFC107.
- Card `[Collection Efficiency %]`, title `COLLECTIONS`: Position 1707 / 152, Size 194 x 88. Callout color #FF7A00. Color strip: rectangle 194 x 3 at 1707 / 152, fill #FF7A00.

**Panels**

- **Division density map** (3 visuals):
  1. Slicer `_MapMetric[Metric]`: Tile, horizontal, **Single select ON**, Select all OFF, header `MAP METRIC`. Position 248 / 254, Size 1098 x 56. Recipes R-BOX + R1.
  2. Shape map, title `DIVISION DENSITY MAP`: Position 248 / 324, Size 636 x 300. Location `Dim_Division[Division]`, Color saturation `[Map Metric Value]`. Recipes R-BOX + R9.
  3. Clustered bar chart, title `RANKING`: Position 898 / 324, Size 448 x 300. Y-axis `Dim_Division[Division]`, X-axis `[Map Metric Value]`, sort descending. Recipes R-BOX + R4 (color #FFC107).
- **Network & customer health**: six Gauge visuals (recipes R-BOX + R7), each Size 171 x 178. Build the first, then copy/paste it 5 times and change fields and titles:
  - Gauge 1, title `COLLECTIONS`: Value `[Collection Efficiency %]`, Minimum 0, Maximum 1, Target 0.95, fill #FFC107. Position 1360 / 254.
  - Gauge 2, title `AVAILABILITY`: Value `[Site Availability %]`, Minimum 95, Maximum 100, Target 99.5, fill #FF7A00. Position 1545 / 254.
  - Gauge 3, title `FIRST-CONTACT RESOLUTION`: Value `[FCR %]`, Minimum 0, Maximum 1, Target 0.8, fill #E5262B. Position 1730 / 254.
  - Gauge 4, title `SLA MET`: Value `[SLA Compliance %]`, Minimum 0, Maximum 1, Target 0.9, fill #C4891A. Position 1360 / 446.
  - Gauge 5, title `RETENTION`: Value `[Retention %]`, Minimum 0, Maximum 1, Target 0.9, fill #FF9E57. Position 1545 / 446.
  - Gauge 6, title `CSAT`: Value `[Avg CSAT]`, Minimum 0, Maximum 5, Target 4, fill #FFC107. Position 1730 / 446.
- **Service revenue (M BDT)**, title `SERVICE REVENUE (M BDT)`: Clustered column chart. Position 248 / 638, Size 542 x 195. X-axis `Dim_Date[MonthName]`; Y-axis [Service Revenue]. Recipes R-BOX + R2, main color #FFC107. Display units: Millions.
- **Gross adds vs churned**, title `GROSS ADDS VS CHURNED`: Clustered column chart. Position 804 / 638, Size 542 x 195. X-axis `Dim_Date[MonthName]`; Y-axis [Gross Adds], [Churned (by date)]. Recipes R-BOX + R2. Series colors: first measure #FFC107, second #E5262B. Legend On (top, #C9C5BB).
- **Revenue mix**, title `REVENUE MIX`: Donut chart. Position 1360 / 638, Size 542 x 195. Legend `_Mix[Service]`; Values [Mix Value]. Recipes R-BOX + R5. Needs table `_Mix` (A7).
- **Division scorecard**, title `DIVISION SCORECARD`: Matrix. Position 248 / 847, Size 1098 x 214. Rows Dim_Division[Division] | [Total Subscribers], [Population Density], [Subscriber Density], [Tower Density], [Churn Rate %], [ARPU], [Call Drop Rate %], [Site Availability %], [Avg CSAT]. Recipes R-BOX + R6. 
- **Live insights**, title `LIVE INSIGHTS`: Multi-row card. Position 1360 / 847, Size 542 x 214. [Insight Drop], [Insight Density], [Insight Churn], [Insight Collections]. Recipes R-BOX + R8. 

## Page 2: Revenue & ARPU
Page title text: `REVENUE & ARPU`. Subtitle: `Service revenue across voice, data, SMS and VAS`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[Service Revenue]`, title `SERVICE REVENUE`: Position 248 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 248 / 152, fill #FFC107.
- Card `[ARPU]`, title `ARPU / MONTH`: Position 665 / 152, Size 403 x 88. Callout color #FF7A00. Color strip: rectangle 403 x 3 at 665 / 152, fill #FF7A00.
- Card `[LTV]`, title `LTV (35% MARGIN ASSUMED)`: Position 1082 / 152, Size 403 x 88. Callout color #E5262B. Color strip: rectangle 403 x 3 at 1082 / 152, fill #E5262B.
- Card `[LTV to CAC]`, title `LTV : CAC`: Position 1499 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 1499 / 152, fill #FFC107.

**Panels**

- **Monthly service revenue (৳ M)**, title `MONTHLY SERVICE REVENUE (৳ M)`: Clustered column chart. Position 248 / 254, Size 820 x 397. X-axis `Dim_Date[MonthName]`; Y-axis [Service Revenue]. Recipes R-BOX + R2, main color #FFC107. Display units: Millions.
- **ARPU trend (৳)**, title `ARPU TREND (৳)`: Area chart. Position 1082 / 254, Size 820 x 397. X-axis `Dim_Date[MonthName]`; Y-axis [ARPU]. Recipes R-BOX + R3, main color #FF7A00. 
- **Revenue mix**, title `REVENUE MIX`: Donut chart. Position 248 / 665, Size 542 x 397. Legend `_Mix[Service]`; Values [Mix Value]. Recipes R-BOX + R5. Needs table `_Mix` (A7).
- **ARPU by network tech (৳)**, title `ARPU BY NETWORK TECH (৳)`: Clustered bar chart. Position 804 / 665, Size 542 x 397. Y-axis `Dim_Customers[Network]`; X-axis [ARPU]. Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Revenue by division (৳ M)**, title `REVENUE BY DIVISION (৳ M)`: Clustered bar chart. Position 1360 / 665, Size 542 x 397. Y-axis `Dim_Division[Division]`; X-axis [Service Revenue]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 3: Subscribers & Churn
Page title text: `SUBSCRIBERS & CHURN`. Subtitle: `Acquisition, retention and churn drivers`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[Total Subscribers]`, title `SUBSCRIBERS`: Position 248 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 248 / 152, fill #FFC107.
- Card `[Active Subscribers]`, title `ACTIVE`: Position 665 / 152, Size 403 x 88. Callout color #FF7A00. Color strip: rectangle 403 x 3 at 665 / 152, fill #FF7A00.
- Card `[Churn Rate %]`, title `CHURN RATE`: Position 1082 / 152, Size 403 x 88. Callout color #E5262B. Color strip: rectangle 403 x 3 at 1082 / 152, fill #E5262B.
- Card `[Monthly Churn Rate %]`, title `MONTHLY CHURN`: Position 1499 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 1499 / 152, fill #FFC107.

**Panels**

- **Gross adds vs churned**, title `GROSS ADDS VS CHURNED`: Clustered column chart. Position 248 / 254, Size 820 x 260. X-axis `Dim_Date[MonthName]`; Y-axis [Gross Adds], [Churned (by date)]. Recipes R-BOX + R2. Series colors: first measure #FFC107, second #E5262B. Legend On (top, #C9C5BB).
- **Net adds**, title `NET ADDS`: Clustered column chart. Position 1082 / 254, Size 820 x 260. X-axis `Dim_Date[MonthName]`; Y-axis [Net Adds]. Recipes R-BOX + R2, main color #FFC107. 
- **Churn type**, title `CHURN TYPE`: Donut chart. Position 248 / 528, Size 542 x 260. Legend `Fact_Subscriptions[ChurnType]`; Values [Churned Subscribers]. Recipes R-BOX + R5. 
- **Churn by division %**, title `CHURN BY DIVISION %`: Clustered bar chart. Position 804 / 528, Size 542 x 260. Y-axis `Dim_Division[Division]`; X-axis [Churn Rate %]. Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Churn by network %**, title `CHURN BY NETWORK %`: Clustered bar chart. Position 1360 / 528, Size 542 x 260. Y-axis `Dim_Customers[Network]`; X-axis [Churn Rate %]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Churn by ticket issue %**, title `CHURN BY TICKET ISSUE %`: Clustered bar chart. Position 248 / 802, Size 820 x 260. Y-axis `Fact_Network_Service_Calls[IssueCategory]`; X-axis [Ticket Churn Rate %]. Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **OTT effect on churn %**, title `OTT EFFECT ON CHURN %`: Clustered bar chart. Position 1082 / 802, Size 820 x 260. Y-axis `Dim_Customers[OTT User]`; X-axis [Churn Rate %]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 4: Network Performance
Page title text: `NETWORK PERFORMANCE`. Subtitle: `Quality, capacity and outage KPIs by division`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[Call Drop Rate %]`, title `CALL DROP`: Position 248 / 152, Size 319 x 88. Callout color #FFC107. Color strip: rectangle 319 x 3 at 248 / 152, fill #FFC107.
- Card `[CSSR %]`, title `CSSR`: Position 581 / 152, Size 319 x 88. Callout color #FF7A00. Color strip: rectangle 319 x 3 at 581 / 152, fill #FF7A00.
- Card `[Avg Throughput Mbps]`, title `THROUGHPUT`: Position 915 / 152, Size 319 x 88. Callout color #E5262B. Color strip: rectangle 319 x 3 at 915 / 152, fill #E5262B.
- Card `[Site Availability %]`, title `AVAILABILITY`: Position 1248 / 152, Size 319 x 88. Callout color #FFC107. Color strip: rectangle 319 x 3 at 1248 / 152, fill #FFC107.
- Card `[MTTR min]`, title `MTTR`: Position 1582 / 152, Size 319 x 88. Callout color #FF7A00. Color strip: rectangle 319 x 3 at 1582 / 152, fill #FF7A00.

**Panels**

- **Call drop heatmap: division x month (%)**, title `CALL DROP HEATMAP: DIVISION X MONTH (%)`: Matrix. Position 248 / 254, Size 1654 x 191. Rows `Dim_Division[Division]`; Columns `Dim_Date[MonthName]`; Values `[Call Drop Rate %]`. Recipes R-BOX + R6. 
- **Call drop trend (%)**, title `CALL DROP TREND (%)`: Area chart. Position 248 / 459, Size 820 x 191. X-axis `Dim_Date[MonthName]`; Y-axis [Call Drop Rate %]. Recipes R-BOX + R3, main color #E5262B. 
- **Outages per month**, title `OUTAGES PER MONTH`: Clustered column chart. Position 1082 / 459, Size 820 x 191. X-axis `Dim_Date[MonthName]`; Y-axis [Outage Count]. Recipes R-BOX + R2, main color #FF7A00. 
- **Outage causes**, title `OUTAGE CAUSES`: Donut chart. Position 248 / 665, Size 542 x 191. Legend `Fact_Network_Outages[Cause]`; Values [Outage Count]. Recipes R-BOX + R5. 
- **MTTR by cause (min)**, title `MTTR BY CAUSE (MIN)`: Clustered bar chart. Position 804 / 665, Size 542 x 191. Y-axis `Fact_Network_Outages[Cause]`; X-axis [MTTR min]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Most congested sites (PRB %)**, title `MOST CONGESTED SITES (PRB %)`: Clustered bar chart. Position 1360 / 665, Size 542 x 191. Y-axis `Dim_Towers[SiteID]`; X-axis [Avg PRB Utilization] (Top N 8). Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending. Filters pane > this visual > drag the category field in > Filter type Top N > Show items Top 8 > By value: the measure > Apply filter.
- **Throughput by area (Mbps)**, title `THROUGHPUT BY AREA (MBPS)`: Clustered bar chart. Position 248 / 870, Size 820 x 191. Y-axis `Dim_Towers[Area]`; X-axis [Avg Throughput Mbps]. Recipes R-BOX + R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending.
- **Availability by division %**, title `AVAILABILITY BY DIVISION %`: Clustered bar chart. Position 1082 / 870, Size 820 x 191. Y-axis `Dim_Division[Division]`; X-axis [Site Availability %]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 5: Customer Experience
Page title text: `CUSTOMER EXPERIENCE`. Subtitle: `Satisfaction, support quality and SLA`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[NPS]`, title `NPS`: Position 248 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 248 / 152, fill #FFC107.
- Card `[Avg CSAT]`, title `CSAT (1-5)`: Position 665 / 152, Size 403 x 88. Callout color #FF7A00. Color strip: rectangle 403 x 3 at 665 / 152, fill #FF7A00.
- Card `[FCR %]`, title `FIRST-CONTACT RESOLUTION`: Position 1082 / 152, Size 403 x 88. Callout color #E5262B. Color strip: rectangle 403 x 3 at 1082 / 152, fill #E5262B.
- Card `[SLA Compliance %]`, title `SLA MET`: Position 1499 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 1499 / 152, fill #FFC107.

**Panels**

- **Tickets per month**, title `TICKETS PER MONTH`: Clustered column chart. Position 248 / 254, Size 820 x 260. X-axis `Dim_Date[MonthName]`; Y-axis [Ticket Count]. Recipes R-BOX + R2, main color #FF7A00. 
- **NPS mix**, title `NPS MIX`: Donut chart. Position 1082 / 254, Size 403 x 260. Legend `_NPS[Group]`; Values [NPS Group Count]. Recipes R-BOX + R5. Needs table `_NPS` (A7).
- **Ticket channels**, title `TICKET CHANNELS`: Donut chart. Position 1499 / 254, Size 403 x 260. Legend `Fact_Network_Service_Calls[TicketChannel]`; Values [Ticket Count]. Recipes R-BOX + R5. 
- **CSAT by issue**, title `CSAT BY ISSUE`: Clustered bar chart. Position 248 / 528, Size 542 x 260. Y-axis `Fact_Network_Service_Calls[IssueCategory]`; X-axis [Avg CSAT]. Recipes R-BOX + R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending.
- **FCR % by channel**, title `FCR % BY CHANNEL`: Clustered bar chart. Position 804 / 528, Size 542 x 260. Y-axis `Fact_Network_Service_Calls[TicketChannel]`; X-axis [FCR %]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **SLA % by issue**, title `SLA % BY ISSUE`: Clustered bar chart. Position 1360 / 528, Size 542 x 260. Y-axis `Fact_Network_Service_Calls[IssueCategory]`; X-axis [SLA Compliance %]. Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Resolution time (min)**, title `RESOLUTION TIME (MIN)`: Clustered bar chart. Position 248 / 802, Size 1654 x 260. Y-axis `Fact_Network_Service_Calls[IssueCategory]`; X-axis [Avg Ticket Resolution]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 6: Usage & Digital
Page title text: `USAGE & DIGITAL`. Subtitle: `Data, voice and OTT engagement`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[MOU]`, title `VOICE MIN / SUB`: Position 248 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 248 / 152, fill #FFC107.
- Card `[Data per Sub GB]`, title `DATA GB / SUB`: Position 665 / 152, Size 403 x 88. Callout color #FF7A00. Color strip: rectangle 403 x 3 at 665 / 152, fill #FF7A00.
- Card `[Total Data Consumed TB]`, title `STREAMED`: Position 1082 / 152, Size 403 x 88. Callout color #E5262B. Color strip: rectangle 403 x 3 at 1082 / 152, fill #E5262B.
- Card `[Streaming Ad Spend]`, title `OTT AD SPEND`: Position 1499 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 1499 / 152, fill #FFC107.

**Panels**

- **Data per subscriber (GB)**, title `DATA PER SUBSCRIBER (GB)`: Area chart. Position 248 / 254, Size 820 x 260. X-axis `Dim_Date[MonthName]`; Y-axis [Data per Sub GB]. Recipes R-BOX + R3, main color #FFC107. 
- **Voice minutes per subscriber**, title `VOICE MINUTES PER SUBSCRIBER`: Area chart. Position 1082 / 254, Size 820 x 260. X-axis `Dim_Date[MonthName]`; Y-axis [MOU]. Recipes R-BOX + R3, main color #FF7A00. 
- **Network mix**, title `NETWORK MIX`: Donut chart. Position 248 / 528, Size 542 x 260. Legend `Dim_Customers[Network]`; Values [Total Subscribers]. Recipes R-BOX + R5. 
- **Streaming by platform (GB)**, title `STREAMING BY PLATFORM (GB)`: Clustered bar chart. Position 804 / 528, Size 542 x 260. Y-axis `Fact_Digital_Streaming_VAS[Platform]`; X-axis [Streaming GB]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Ad spend per GB (৳)**, title `AD SPEND PER GB (৳)`: Clustered bar chart. Position 1360 / 528, Size 542 x 260. Y-axis `Fact_Digital_Streaming_VAS[Platform]`; X-axis [Ad Cost per GB]. Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Monthly streaming (GB)**, title `MONTHLY STREAMING (GB)`: Clustered column chart. Position 248 / 802, Size 1654 x 260. X-axis `Dim_Date[MonthName]`; Y-axis [Streaming GB]. Recipes R-BOX + R2, main color #FF7A00. 

## Page 7: Billing & Collections
Page title text: `BILLING & COLLECTIONS`. Subtitle: `Postpaid invoicing, collections and bad debt`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[Collection Efficiency %]`, title `COLLECTION EFFICIENCY`: Position 248 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 248 / 152, fill #FFC107.
- Card `[Bad Debt %]`, title `BAD DEBT`: Position 665 / 152, Size 403 x 88. Callout color #FF7A00. Color strip: rectangle 403 x 3 at 665 / 152, fill #FF7A00.
- Card `[Overdue Amount]`, title `OVERDUE`: Position 1082 / 152, Size 403 x 88. Callout color #E5262B. Color strip: rectangle 403 x 3 at 1082 / 152, fill #E5262B.
- Card `[Billed]`, title `BILLED`: Position 1499 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 1499 / 152, fill #FFC107.

**Panels**

- **Collection efficiency (%)**, title `COLLECTION EFFICIENCY (%)`: Area chart. Position 248 / 254, Size 820 x 397. X-axis `Dim_Date[MonthName]`; Y-axis [Collection Efficiency %]. Recipes R-BOX + R3, main color #FFC107. 
- **Overdue aging (৳ M)**, title `OVERDUE AGING (৳ M)`: Clustered column chart. Position 1082 / 254, Size 820 x 397. X-axis `Fact_Billing[Aging Bucket]`; Y-axis [Overdue Amount] (filter out Paid). Recipes R-BOX + R2, main color #E5262B. Filters pane > this visual > `Aging Bucket` > Basic filtering > untick `Paid`. Sort axis > Aging Bucket > Sort ascending (alphabetical order is already 1-30d, 31-60d, 61-90d, 90d+).
- **Collection gauge**, title `COLLECTION GAUGE`: Gauge. Position 248 / 665, Size 542 x 397. Value `[Collection Efficiency %]`; Minimum 0; Maximum 1; Target 0.95. Recipes R-BOX + R7. 
- **Bad debt % by division**, title `BAD DEBT % BY DIVISION`: Clustered bar chart. Position 804 / 665, Size 542 x 397. Y-axis `Dim_Division[Division]`; X-axis [Bad Debt %]. Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Collection % by division**, title `COLLECTION % BY DIVISION`: Clustered bar chart. Position 1360 / 665, Size 542 x 397. Y-axis `Dim_Division[Division]`; X-axis [Collection Efficiency %]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.

## Page 8: Sales & Distribution
Page title text: `SALES & DISTRIBUTION`. Subtitle: `Campaign efficiency, channels and distributors`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[Campaign CAC]`, title `CAC`: Position 248 / 152, Size 542 x 88. Callout color #FFC107. Color strip: rectangle 542 x 3 at 248 / 152, fill #FFC107.
- Card `[Campaign ROI]`, title `CAMPAIGN ROI`: Position 804 / 152, Size 542 x 88. Callout color #FF7A00. Color strip: rectangle 542 x 3 at 804 / 152, fill #FF7A00.
- Card `[LTV to CAC]`, title `LTV : CAC`: Position 1360 / 152, Size 542 x 88. Callout color #E5262B. Color strip: rectangle 542 x 3 at 1360 / 152, fill #E5262B.

**Panels**

- **Campaign spend (৳ M)**, title `CAMPAIGN SPEND (৳ M)`: Clustered column chart. Position 248 / 254, Size 820 x 397. X-axis `Dim_Date[MonthName]`; Y-axis [Campaign Spend]. Recipes R-BOX + R2, main color #FF7A00. 
- **Acquisition channels**, title `ACQUISITION CHANNELS`: Donut chart. Position 1082 / 254, Size 403 x 397. Legend `Fact_Subscriptions[AcquisitionChannel]`; Values [Gross Adds]. Recipes R-BOX + R5. 
- **Top-up by distributor tier**, title `TOP-UP BY DISTRIBUTOR TIER`: Donut chart. Position 1499 / 254, Size 403 x 397. Legend `Dim_Distributors[Tier]`; Values [Recharge Sales]. Recipes R-BOX + R5. 
- **CAC by channel (৳)**, title `CAC BY CHANNEL (৳)`: Clustered bar chart. Position 248 / 665, Size 542 x 397. Y-axis `Fact_Marketing_Campaigns[Channel]`; X-axis [Campaign CAC]. Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **ROI by channel (x)**, title `ROI BY CHANNEL (X)`: Clustered bar chart. Position 804 / 665, Size 542 x 397. Y-axis `Fact_Marketing_Campaigns[Channel]`; X-axis [Campaign ROI]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Top distributors (৳ K)**, title `TOP DISTRIBUTORS (৳ K)`: Clustered bar chart. Position 1360 / 665, Size 542 x 397. Y-axis `Dim_Distributors[Name]`; X-axis [Recharge Sales] (Top N 8). Recipes R-BOX + R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending. Filters pane > this visual > drag the category field in > Filter type Top N > Show items Top 8 > By value: the measure > Apply filter.

## Page 9: Workforce
Page title text: `WORKFORCE`. Subtitle: `Agent productivity, retention and distribution`.

**Slicers** (recipes R-BOX + R1; Title Off for slicers because the header shows the label):

- Slicer `Dim_Division[Division]`, header `DIVISION`: Tile, horizontal. Position 248 / 96, Size 740 x 46.
- Slicer `Dim_Customers[Network]`, header `NETWORK`: Tile, horizontal. Position 1000 / 96, Size 210 x 46.
- Slicer `Dim_Customers[Segment]`, header `SEGMENT`: Tile, horizontal. Position 1222 / 96, Size 210 x 46.
- Slicer `Dim_Date[MonthName]`, header `MONTH`: Dropdown, multi-select. Position 1444 / 96, Size 458 x 46.

**KPI cards** (recipe R0):

- Card `[Headcount]`, title `HEADCOUNT`: Position 248 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 248 / 152, fill #FFC107.
- Card `[Employee Turnover %]`, title `TURNOVER`: Position 665 / 152, Size 403 x 88. Callout color #FF7A00. Color strip: rectangle 403 x 3 at 665 / 152, fill #FF7A00.
- Card `[Avg Performance Rating]`, title `AVG RATING`: Position 1082 / 152, Size 403 x 88. Callout color #E5262B. Color strip: rectangle 403 x 3 at 1082 / 152, fill #E5262B.
- Card `[Tickets per Agent]`, title `TICKETS / AGENT`: Position 1499 / 152, Size 403 x 88. Callout color #FFC107. Color strip: rectangle 403 x 3 at 1499 / 152, fill #FFC107.

**Panels**

- **Resolution by dept (min)**, title `RESOLUTION BY DEPT (MIN)`: Clustered bar chart. Position 248 / 254, Size 542 x 397. Y-axis `Dim_Employees_HR[Department]`; X-axis [Avg Ticket Resolution]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **CSAT by dept**, title `CSAT BY DEPT`: Clustered bar chart. Position 804 / 254, Size 542 x 397. Y-axis `Dim_Employees_HR[Department]`; X-axis [Avg CSAT]. Recipes R-BOX + R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending.
- **Turnover % by dept**, title `TURNOVER % BY DEPT`: Clustered bar chart. Position 1360 / 254, Size 542 x 397. Y-axis `Dim_Employees_HR[Department]`; X-axis [Employee Turnover %]. Recipes R-BOX + R4, main color #E5262B. Sort: ... > Sort axis > the measure > Sort descending.
- **Performance mix**, title `PERFORMANCE MIX`: Donut chart. Position 248 / 665, Size 542 x 397. Legend `Dim_Employees_HR[PerformanceRating]`; Values [Headcount]. Recipes R-BOX + R5. 
- **Headcount by division**, title `HEADCOUNT BY DIVISION`: Clustered bar chart. Position 804 / 665, Size 542 x 397. Y-axis `Dim_Division[Division]`; X-axis [Headcount]. Recipes R-BOX + R4, main color #FF7A00. Sort: ... > Sort axis > the measure > Sort descending.
- **Avg salary by dept (৳ K)**, title `AVG SALARY BY DEPT (৳ K)`: Clustered bar chart. Position 1360 / 665, Size 542 x 397. Y-axis `Dim_Employees_HR[Department]`; X-axis [Avg Salary]. Recipes R-BOX + R4, main color #FFC107. Sort: ... > Sort axis > the measure > Sort descending.

## C-Sync. Make the slicers work on every page
1. On page 1 select the Division slicer > **View > Sync slicers** > in the pane tick every page in BOTH the Sync and Visible columns.
2. Repeat for the Network, Segment and Month slicers.
3. On pages 2 to 9 the four slicers must exist (Visible column). Fastest way: copy the 4 slicers on page 1, paste them on each other page (same position), then check Sync slicers once.


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
| Division = Dhaka: Total Subscribers / Churn | 2,736 / 14.55% |
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
