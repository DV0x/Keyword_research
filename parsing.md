Below is the simplest repeat-able recipe I use in agencies when someone drops a **huge “ranked \_keywords” CSV** on my desk and says, *“Just give me the bid-worthy terms by tomorrow.”*
Copy-paste each numbered code block into **one Jupyter notebook** (or run it line-by-line in a Python REPL) and you’ll end up with a **clean, sortable sheet** of keywords + the few metrics you really need.

> **You only edit two things:**
>
> 1. the **`RAW`** filename in Step 1
> 2. the freshness windows in Step 5 (default: metrics ≤ 90 days, ranks ≤ 30 days)

Everything else is automatic.

---

### 0 — Install once

```bash
pip install pandas numpy python-dateutil
```

---

### 1 — Load the file & pick the useful columns

```python
import pandas as pd, ast, json, numpy as np
from pathlib import Path

RAW = Path("data/competitors_ranked_2025-08-05.csv")   # <-- your file
df = pd.read_csv(RAW, engine="python")                 # engine=python tolerates commas in JSON

# --- choose ONLY the columns you care about ---
cols = [
    "keyword",                              # query
    "keyword_search_volume",                # last-month volume
    "keyword_cpc",                          # avg CPC
    "keyword_competition",                  # 0-100 index
    "keyword_low_top_of_page_bid",          # low-range bid
    "keyword_high_top_of_page_bid",         # high-range bid
    "keyword_difficulty",                   # SEO KD
    "keyword_search_intent_info",           # intent JSON
    "keyword_last_updated_time",            # when volume/CPC were refreshed
    "ranked_serp_element"                   # blob that holds competitor rank + timestamp
]
df = df[cols]
```

---

### 2 — Flatten the two JSON blobs

```python
# --- Intent ---
df["intent"] = df["keyword_search_intent_info"].apply(
    lambda s: ast.literal_eval(s)["main_intent"] if pd.notna(s) else "unknown"
)

# --- Competitor rank & rank timestamp ---
serp = df["ranked_serp_element"].apply(ast.literal_eval)
df["competitor_rank"] = serp.map(lambda j: j["serp_item"]["rank_absolute"])
df["rank_date"]       = pd.to_datetime(
    serp.map(lambda j: j["last_updated_time"]), errors="coerce"
)
```

*(No need to keep the original JSON columns once you’ve extracted what you need.)*

```python
df.drop(columns=["keyword_search_intent_info","ranked_serp_element"], inplace=True)
```

---

### 3 — Light cleanup

```python
# numeric cast
num_cols = ["keyword_search_volume","keyword_cpc","keyword_competition",
            "keyword_low_top_of_page_bid","keyword_high_top_of_page_bid","keyword_difficulty"]
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

# fix volumes if they look tiny (older exports store 8.3 instead of 830)
if df["keyword_search_volume"].max() < 50:
    df["keyword_search_volume"] = (df["keyword_search_volume"] * 100).round(0)
```

---

### 4 — Drop obvious junk

```python
junk = ["calculator","meaning","definition","job","salary"]
mask = ~df["keyword"].str.contains("|".join(junk), case=False, na=False)
df = df[mask]
```

---

### 5 — Keep only *fresh* rows

```python
from datetime import datetime, timedelta
now = datetime.utcnow()

df["kw_date"] = pd.to_datetime(df["keyword_last_updated_time"], errors="coerce")

df = df[
    (df.kw_date >= now - timedelta(days=90)) &     # metrics ≤ 3 months old
    (df.rank_date >= now - timedelta(days=30))     # ranking snapshot ≤ 1 month old
]
```

---

### 6 — Rename to friendly headers & reorder

```python
df = df.rename(columns={
    "keyword_search_volume":"vol",
    "keyword_cpc":"cpc",
    "keyword_competition":"competition",
    "keyword_low_top_of_page_bid":"low_bid",
    "keyword_high_top_of_page_bid":"high_bid",
    "keyword_difficulty":"kd"
})[["keyword","vol","cpc","competition","low_bid","high_bid",
    "kd","intent","competitor_rank","kw_date","rank_date"]]
```

---

### 7 — Export for bidding / sorting

```python
OUT = Path("bidding_ready_2025-08-05.csv")
df.sort_values(["vol","competitor_rank"], ascending=[False,True]).to_csv(OUT, index=False)
print("✅  Saved", OUT.resolve(), "with", len(df), "rows")
```

---

## How to read the sheet tomorrow morning

| Column                    | Why you care                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------------- |
| **keyword**               | Copy into Ads Editor.                                                                                   |
| **vol**                   | Anything 20+ searches/month deserves its own ad group; consolidate smaller ones.                        |
| **cpc**                   | Multiply × 1.2 for your initial Max CPC bid.                                                            |
| **competition**           | 0-100; > 70 means a crowded auction—double-check lander quality & budget.                               |
| **low\_bid / high\_bid**  | Google’s bid range for top-of-page. Stay near the low end while you test.                               |
| **kd**                    | < 40 → publish an SEO page later; 40-60 = build links; > 60 ignore for SEO.                             |
| **intent**                | Keep **commercial / transactional** on day 1; everything else can wait or become a negative.            |
| **competitor\_rank**      | If the rival is already #1 organically, your ad may need extra punch (call-out, 24 h approval, etc.).   |
| **kw\_date / rank\_date** | Sanity check freshness—if something slipped through older than the window, refresh in DataForSEO first. |

That’s it. This single notebook cell chain turns the unwieldy 10 000-row export into a **ready-to-sort CSV** you can act on immediately—no automation overhead, no extra tooling.
