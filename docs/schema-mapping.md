# Hugging Face Dataset → Internal Schema Mapping

**Dataset:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)  
**Split used:** `train` (~51,717 rows)

## Source columns

| HF column | Sample | Used |
|-----------|--------|------|
| `url` | Zomato restaurant URL | Yes → stable `id` (hash) |
| `address` | Full address string | Yes → city extraction |
| `name` | Restaurant name | Yes → `name` |
| `location` | Locality (e.g. Banashankari) | Yes → `area` |
| `cuisines` | Comma-separated types | Yes → `cuisine` |
| `approx_cost(for two people)` | e.g. `800` | Yes → `cost`, `cost_numeric`, `budget_tier` |
| `rate` | e.g. `4.1/5`, `NEW`, `None` | Yes → `rating` (invalid → `null`) |
| `rest_type` | Casual Dining | `metadata` |
| `dish_liked` | Dish list | `metadata` |
| `votes`, `phone`, `online_order`, `book_table` | Various | `metadata` |
| `reviews_list`, `menu_item` | Large text | Not loaded (size) |
| `listed_in(type)`, `listed_in(city)` | Listing metadata | `metadata` only |

## Target model: `Restaurant`

| Field | Source / rule |
|-------|----------------|
| `id` | SHA-256 prefix of `url`, else `name` + `address` |
| `name` | `name` (required; skip row if empty) |
| `location` | City parsed from last segment of `address` (required; skip if unknown) |
| `area` | `location` column |
| `cuisine` | `cuisines` or `"Unknown"` |
| `cost` | Display: `₹{n} for two` or raw / `"Not available"` |
| `cost_numeric` | Parsed integer from cost column |
| `budget_tier` | `low` ≤400, `medium` 401–800, `high` >800 INR, else `unknown` |
| `rating` | Parsed from `rate`; `NEW` / missing → `null` (kept in dataset) |
| `metadata` | Raw fields for future soft filters |

## Row skip policy

- Missing `name` → skip (EC-DATA-04)
- Cannot derive city from `address` → skip
- Invalid rating → `rating=null` (row retained; excluded later by min-rating filter)

## City normalization

Aliases map to canonical keys, e.g. `Bengaluru` → `bangalore`. See `domain/normalization.py` → `CITY_ALIASES`.
