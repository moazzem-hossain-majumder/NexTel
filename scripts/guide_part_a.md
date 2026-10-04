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
