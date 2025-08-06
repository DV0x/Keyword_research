# Campaign-Based Keyword Research Implementation Guide

## Overview
This guide implements a simple campaign-based keyword research system using your existing config.py and keyword_research.py workflow. No complex templates or new runners needed - just organized output!

## Prerequisites
- [x] Existing keyword research pipeline working
- [x] Python environment with dependencies installed
- [x] DataForSEO API credentials configured

---

## Phase 1: Organize Existing Data (3 minutes) ✅ COMPLETED

### Step 1.1: Preserve Your Current Data ✅
Your existing research data has been organized:
- enriched_keywords_v2.csv (86 keywords)
- scored_keywords_v2.csv (prioritized keywords) 
- clusters/ directory (17 semantic groupings)
- exports/ directory (campaign files)
- tiers/ directory (difficulty-based groupings)

### Step 1.2: Create Initial Campaign Structure ✅
Your first campaign and existing data migration:
```bash
# ✅ COMPLETED: Initial mortgage campaign created
campaigns/mortgage/runs/2024-08-05_existing_data/
├── data/           # All your research files (86 keywords)
├── exports/        # Campaign-ready Google/Microsoft Ads files  
└── run_metadata.json  # Run details (avg score: 45.9)

# ✅ COMPLETED: Latest symlink created
campaigns/mortgage/latest -> runs/2024-08-05_existing_data
```

---

## Phase 2: Campaign-Aware Output System (5 minutes) ✅ COMPLETED

### Step 2.1: Add Campaign Name to Config ✅
**Simple approach**: Just add a campaign name field to your existing config.py

**Edit config.py - Add this line after line 8:**
```python
CONFIG = {
    "campaign_name": "mortgage",  # ← Add this line for campaign organization
    "dataforseo": {
        # ... rest of your existing config unchanged
    }
}
```

### Step 2.2: Modify keyword_research.py for Campaign Output ✅
**Add campaign-aware output to your existing pipeline**

**At the top of keyword_research.py, after imports:**
```python
import os
from pathlib import Path
from datetime import datetime
import shutil
import json

def get_campaign_output_dir():
    """Create campaign-specific output directory"""
    campaign_name = CONFIG.get("campaign_name", "default_campaign")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    # Create campaign run directory
    run_dir = Path(f"campaigns/{campaign_name}/runs/{timestamp}")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Create data and exports subdirectories
    (run_dir / "data").mkdir(exist_ok=True)
    (run_dir / "exports").mkdir(exist_ok=True)
    
    return run_dir, timestamp, campaign_name

def save_campaign_results(run_dir, timestamp, campaign_name):
    """Move results to campaign directory and create metadata"""
    files_moved = 0
    
    # Move data files
    if Path("data").exists():
        for item in Path("data").iterdir():
            if item.is_file():
                shutil.copy2(item, run_dir / "data" / item.name)
                files_moved += 1
            elif item.is_dir():
                shutil.copytree(item, run_dir / "data" / item.name, dirs_exist_ok=True)
                files_moved += len(list(item.glob("*")))
    
    # Move exports
    if Path("exports").exists():
        for item in Path("exports").iterdir():
            if item.is_dir():
                shutil.copytree(item, run_dir / "exports" / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, run_dir / "exports" / item.name)
            files_moved += 1
    
    # Create run metadata
    metadata = {
        "campaign": campaign_name,
        "timestamp": timestamp,
        "run_date": datetime.now().isoformat(),
        "seeds": CONFIG["seed"]["business_terms"],
        "files_generated": [f.name for f in (run_dir / "data").glob("*") if f.is_file()]
    }
    
    # Add keyword stats if available
    scored_file = run_dir / "data" / "scored_keywords_v2.csv"
    if scored_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(scored_file)
            metadata["keywords_found"] = len(df)
            if 'total_score' in df.columns:
                metadata["avg_score"] = float(df['total_score'].mean())
        except Exception:
            metadata["keywords_found"] = 0
            metadata["avg_score"] = 0
    
    # Save metadata
    with open(run_dir / "run_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Update latest symlink
    latest_link = Path(f"campaigns/{campaign_name}/latest")
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(Path("runs") / run_dir.name)
    
    print(f"📁 Campaign results saved to: {run_dir}")
    print(f"🔗 Updated latest symlink: campaigns/{campaign_name}/latest")
    return metadata
```

**At the end of main_improved() function, before the final return True:**
```python
        # Step 9: Save to campaign structure
        logger.info("📋 Step 9: Organizing Campaign Results...")
        run_dir, timestamp, campaign_name = get_campaign_output_dir()
        metadata = save_campaign_results(run_dir, timestamp, campaign_name)
        
        logger.info(f"✅ Campaign '{campaign_name}' completed!")
        logger.info(f"📊 Keywords: {metadata.get('keywords_found', 'N/A')}")
        logger.info(f"📁 Results: {run_dir}")
```

**✅ PHASE 2 COMPLETED SUCCESSFULLY!**

Test run completed with results:
- Campaign: 'mortgage' 
- Keywords discovered: 611 → 86 high-quality keywords
- Results saved to: `campaigns/mortgage/runs/2025-08-06_124959/`
- Latest symlink updated: `campaigns/mortgage/latest`

Current campaign structure:
```bash
campaigns/mortgage/
├── latest -> runs/2025-08-06_124959    # Updated to latest run
└── runs/
    ├── 2024-08-05_existing_data/      # Original data preserved
    └── 2025-08-06_124959/            # Fresh test run (same config)
```

---

## Phase 3: Usage Workflow (Simple!) ✅ READY TO USE

### Step 3.1: Running Different Campaigns

**For Mortgage Campaign:**
```bash
# 1. Edit config.py
CONFIG = {
    "campaign_name": "mortgage",
    "seed": {
        "business_terms": ["mortgage canada", "home mortgage canada"]
    }
}

# 2. Run pipeline
python keyword_research.py

# 3. Results automatically saved to:
# campaigns/mortgage/runs/2024-08-06_143022/
```

**For Home Equity Campaign:**
```bash
# 1. Edit config.py  
CONFIG = {
    "campaign_name": "home_equity",
    "seed": {
        "business_terms": ["heloc canada", "equity loan"]
    }
}

# 2. Run pipeline
python keyword_research.py

# 3. Results automatically saved to:
# campaigns/home_equity/runs/2024-08-06_150245/
```

### Step 3.2: Final Structure
After running multiple campaigns, your organized structure will be:
```
campaigns/
├── mortgage/
│   ├── latest -> runs/2024-08-06_143022
│   └── runs/
│       ├── 2024-08-05_existing_data/  # Your original data
│       └── 2024-08-06_143022/         # New run
└── home_equity/
    ├── latest -> runs/2024-08-06_150245  
    └── runs/
        └── 2024-08-06_150245/         # Different campaign
```

---

## Benefits of This Simple Approach

✅ **Same Workflow** - Edit config.py, run keyword_research.py  
✅ **No Data Loss** - Each campaign preserved separately  
✅ **No Templates** - Just one config file to manage  
✅ **Auto Organization** - Results organized by campaign name  
✅ **Multiple Runs** - Same campaign, different runs preserved  
✅ **Easy Switching** - Change campaign_name and seeds, run again  

---

## Phase 4: Dashboard (Optional)

If you want to visualize your campaign portfolio, you can add the dashboard from the original Phase 3 in the full implementation guide. The dashboard will automatically discover all your campaigns and provide analysis tools.

---

## Implementation Status

1. ✅ **Phase 1**: Existing data organized (complete)
2. ✅ **Phase 2**: Campaign-aware system implemented and tested  
3. ✅ **Phase 3**: Ready to use - change campaign_name and run different campaigns
4. 📊 **Phase 4**: Optional dashboard for portfolio analysis

## Success Summary

**✅ Campaign System Active!**
- ✅ Config.py updated with campaign_name field
- ✅ Pipeline automatically organizes results by campaign
- ✅ Each run preserved with timestamp
- ✅ Latest symlinks always point to most recent run
- ✅ Tested successfully with mortgage campaign

**✅ Ready for Multi-Campaign Workflow:**
- Change `campaign_name` in config.py
- Update `business_terms` for new keyword focus
- Run `python keyword_research.py`
- Results automatically organized in `campaigns/{name}/runs/`

**The system now perfectly matches your preferred workflow while providing organized campaign management!**
