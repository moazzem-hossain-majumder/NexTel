# NexTel Enterprise Intelligence Hub (Bangladesh)

Black / orange / red / yellow telecom analytics portfolio: a command center plus 8 deep-dive dashboards on a 16-table star schema covering all 8 divisions (Barishal, Chattogram, Dhaka, Khulna, Mymensingh, Rajshahi, Rangpur, Sylhet).

## Start here (Windows)
1. Unzip. 2. Open `dashboard/nextel_dashboard.html` in a browser: this is the **fully interactive** design target. Filter by division / network / segment / month, or click any bar, slice, month column or map division and all pages react.
3. Build it in Power BI with **`powerbi/BUILD_GUIDE.md`** (every click, value and pixel position).

## Folder map
| Path | Purpose |
|---|---|
| `powerbi/BUILD_GUIDE.md` | Step-by-step Power BI build: load, model, DAX, theme, 9 pages with exact X/Y/W/H, test numbers |
| `powerbi/backgrounds/` | 9 page backgrounds, 1920x1080 PNG (cards, titles, slicer strip, glow baked in) |
| `data/` | 16 ready CSVs |
| `dax/measures.dax` | ~60 measures, helper tables, calculated columns |
| `theme/nextel_theme.json` | Power BI theme |
| `geo/` | Division boundaries: `bd_divisions.topojson` (Shape map), GeoJSON, SVG paths |
| `dashboard/` | Interactive HTML dashboard + template |
| `scripts/` | `generate_data.py`, `build_dashboard.py`, `build_powerbi.py` |
| `tests/` | `pytest tests` (10 checks) |
| `screenshots/` | Reference screenshots |

## Notes
- All data is synthetic. Division area and population are approximate (2022 census): verify before publishing.
- LTV assumes a 35% gross margin. Not covered: roaming/interconnect, fraud, spectrum/capex, enterprise (B2B) and IoT.
- Rebuild everything: `python scripts/generate_data.py && python scripts/build_dashboard.py && python scripts/build_powerbi.py`
