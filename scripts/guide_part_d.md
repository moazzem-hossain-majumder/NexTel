
---
# PART D: Test it

## D1. Numbers you should see (all slicers cleared)
| Measure | Expected |
|---|---|
__VALID__

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
