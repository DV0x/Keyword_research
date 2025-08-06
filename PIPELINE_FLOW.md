# DataForSEO Keyword Research Pipeline - ASCII Flow Diagram

## Overview
This document provides a comprehensive visualization of the keyword research pipeline architecture and data flow, including the new campaign management system for organizing multiple keyword research projects.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DataForSEO Keyword Research Pipeline                     │
│                       (Modular + Campaign Management)                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Configuration Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │Campaign Name │  │ API Settings │  │Target Market │  │  Filtering   │   │
│  │  + Metadata  │  │  Rate Limits │  │   Country    │  │    Rules     │   │
│  │   Tracking   │  │   Timeouts   │  │   Language   │  │  Volume/CPC  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API Abstraction Layer                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │           DataForSEOClient (Rate-Limited, Error Handling)            │  │
│  │  • keyword_ideas()  • keyword_suggestions()  • related_keywords()    │  │
│  │  • search_volume()  • keyword_difficulty()   • serp_competitors()    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Pipeline Flow Diagram (V2 Enhanced)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           START: Pipeline Initialization                      │
│                                                                               │
│  • Load environment variables (.env)                                         │
│  • Initialize logging system                                                 │
│  • Create directory structure                                                │
│  • Verify API credentials                                                    │
└────────────────────────────────────────┬─────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     STEP 1: Environment Setup & Validation                    │
│                                                                               │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐                 │
│  │   .env      │───▶│  Credentials │───▶│  API Test Call │                 │
│  │   File      │    │  Validation  │    │  (locations)   │                 │
│  └─────────────┘    └──────────────┘    └────────────────┘                 │
│                                                │                             │
│                                         Success?                             │
│                                    ┌────────┴────────┐                       │
│                                    │ Yes         No  │                       │
│                                    ▼              ▼  │                       │
│                                Continue        Exit  │                       │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        STEP 2: Location Resolution                           │
│                                                                               │
│  ┌────────────────┐        ┌─────────────────┐       ┌─────────────────┐   │
│  │ Target Country │───────▶│  API: Get All   │──────▶│  Country Code   │   │
│  │    "Canada"    │        │   Locations     │       │   Resolution    │   │
│  └────────────────┘        └─────────────────┘       └─────────────────┘   │
│                                                               │              │
│  ┌────────────────┐        ┌─────────────────┐       ┌─────────────────┐   │
│  │   Provincial   │───────▶│  Province Code  │──────▶│  Store Location │   │
│  │   Analysis?    │        │   Resolution    │       │     Mappings    │   │
│  └────────────────┘        └─────────────────┘       └─────────────────┘   │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│              STEP 3: Enhanced Seed Generation (V2 Strategy)                   │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     Seed Generation Strategy Decision                   │ │
│  │  if CONFIG["primary_method"] == "keyword_ideas":                       │ │
│  │      ▶ Use V2 Enhanced Method (Category-Based)                         │ │
│  │  else:                                                                  │ │
│  │      ▶ Use Original Method (Multiple Sources)                          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─── V2 Enhanced Method ─────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Business Terms           Intent-Based Terms        Category Expansion │ │
│  │  ┌─────────────┐         ┌──────────────┐         ┌────────────────┐  │ │
│  │  │"mortgage    │────────▶│"best mortgage"│────────▶│ keyword_ideas  │  │ │
│  │  │ canada"     │         │"apply for..."  │        │ API (3000/seed)│  │ │
│  │  └─────────────┘         └──────────────┘         └────────────────┘  │ │
│  │                                   │                         │           │ │
│  │                                   ▼                         ▼           │ │
│  │                          ┌────────────────┐       ┌─────────────────┐  │ │
│  │                          │ Early Relevance│       │  Deduplicate &  │  │ │
│  │                          │   Filtering    │       │    Normalize    │  │ │
│  │                          └────────────────┘       └─────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Output: seed_keywords_v2.csv (~5,000-10,000 focused keywords)              │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      STEP 4: Keyword Enrichment Pipeline                      │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         Batch Processing (200/batch)                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│     Seed Keywords ──▶ ┌──────────────┐ ──▶ ┌──────────────┐                │
│                       │Search Volume │     │     CPC      │                │
│                       │   & Trends   │     │   & Bids     │                │
│                       └──────────────┘     └──────────────┘                │
│                              │                     │                        │
│                              ▼                     ▼                        │
│                       ┌──────────────┐     ┌──────────────┐                │
│                       │  Difficulty  │     │    Intent    │                │
│                       │    Score     │     │Classification│                │
│                       └──────────────┘     └──────────────┘                │
│                              │                     │                        │
│                              └──────┬──────────────┘                        │
│                                     ▼                                       │
│                           ┌──────────────────┐                              │
│                           │ Enriched Dataset │                              │
│                           │   + Metrics      │                              │
│                           └──────────────────┘                              │
│                                                                               │
│  Output: enriched_keywords_v2.csv (with volume, CPC, difficulty, intent)    │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│               STEP 5: Competitor Analysis & Discovery                         │
│                                                                               │
│  ┌─── Auto-Discovery from SERP ────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Top Keywords ──▶ SERP Analysis ──▶ Extract Domains ──▶ Filter & Rank  │ │
│  │       │                                    │                    │       │ │
│  │       ▼                                    ▼                    ▼       │ │
│  │  ┌──────────┐               ┌───────────────────┐      ┌─────────────┐ │ │
│  │  │Select Top│               │ Frequency Analysis│      │Top 30 Comps │ │ │
│  │  │100 Seeds │               │ (appearances in   │      │by frequency │ │ │
│  │  └──────────┘               │  top 10 SERPs)    │      └─────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─── Competitor Keyword Mining ───────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  For Each Competitor:                                                   │ │
│  │  ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐ │ │
│  │  │   Ranked   │───▶│ Subdomain  │───▶│    Gap     │───▶│   Merge    │ │ │
│  │  │  Keywords  │    │  Analysis  │    │  Analysis  │    │  Results   │ │ │
│  │  └────────────┘    └────────────┘    └────────────┘    └────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Output: competitor_keywords_v2.csv, gap_analysis_v2.csv, serp_competitors.csv│
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  STEP 6: Smart Filtering & Clustering                         │
│                                                                               │
│  ┌─── Multi-Stage Filtering Pipeline ──────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  All Keywords                                                           │ │
│  │       │                                                                 │ │
│  │       ▼                                                                 │ │
│  │  ┌──────────────┐     Filter Criteria:                                 │ │
│  │  │Volume Filter │     • 50 < volume < 50,000                           │ │
│  │  │ (50-50K)     │     • Remove too broad/narrow                        │ │
│  │  └──────┬───────┘                                                      │ │
│  │         ▼                                                               │ │
│  │  ┌──────────────┐     Filter Criteria:                                 │ │
│  │  │ CPC Filter   │     • $0.10 < CPC < $20                              │ │
│  │  │($0.10-$20)   │     • Has commercial value                           │ │
│  │  └──────┬───────┘                                                      │ │
│  │         ▼                                                               │ │
│  │  ┌──────────────┐     Filter Criteria:                                 │ │
│  │  │Pattern Filter│     • Exclude: jobs, training, definition             │ │
│  │  │  (Regex)     │     • Industry-specific exclusions                   │ │
│  │  └──────┬───────┘                                                      │ │
│  │         ▼                                                               │ │
│  │  ┌──────────────┐     Filter Criteria:                                 │ │
│  │  │Intent Filter │     • Keep: commercial, transactional                │ │
│  │  │             │     • Remove: informational (mostly)                  │ │
│  │  └──────┬───────┘                                                      │ │
│  │         ▼                                                               │ │
│  │  ┌──────────────┐     Filter Criteria:                                 │ │
│  │  │Word Count    │     • 2-6 words per keyword                         │ │
│  │  │   Filter     │     • Balance specificity                           │ │
│  │  └──────────────┘                                                      │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─── Semantic Clustering ─────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Filtered Keywords ──▶ TF-IDF Vectorization ──▶ K-Means Clustering     │ │
│  │                              │                         │                │ │
│  │                              ▼                         ▼                │ │
│  │                     ┌─────────────────┐      ┌──────────────────┐      │ │
│  │                     │ Optimal K using │      │ Assign Keywords   │      │ │
│  │                     │ Elbow Method    │      │ to Clusters       │      │ │
│  │                     └─────────────────┘      └──────────────────┘      │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Output: filtered_keywords_v2.csv, negative_keywords_v2.txt, clusters/       │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│               STEP 7: Advanced Scoring & Seasonality Analysis                 │
│                                                                               │
│  ┌─── Multi-Factor Scoring System ─────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  For Each Keyword:                                                      │ │
│  │                                                                         │ │
│  │  ┌────────────┐  Weight: 30%        ┌────────────┐  Weight: 25%       │ │
│  │  │   Volume   │─────────────────────▶│   Intent   │────────────────┐   │ │
│  │  │   Score    │  (normalized)        │   Score    │  (commercial)  │   │ │
│  │  └────────────┘                      └────────────┘                │   │ │
│  │                                                                     ▼   │ │
│  │  ┌────────────┐  Weight: 20%        ┌────────────┐  Weight: 15%  ┌───┐ │ │
│  │  │ Difficulty │─────────────────────▶│    CPC     │──────────────▶│SUM│ │ │
│  │  │  (inverse) │  (easier = better)   │   Score    │  (value proxy)└───┘ │ │
│  │  └────────────┘                      └────────────┘                │   │ │
│  │                                                                     │   │ │
│  │  ┌────────────┐  Weight: 10%                                      ▼   │ │
│  │  │Seasonality │───────────────────────────────────────────▶ Final Score│ │
│  │  │   Score    │  (current relevance)                         (0-100)   │ │
│  │  └────────────┘                                                        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─── Campaign Recommendations ────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Score Range     Recommendation          Priority                       │ │
│  │  ─────────────────────────────────────────────────                     │ │
│  │  80-100         High-priority, launch immediately    ★★★★★             │ │
│  │  60-79          Medium-priority, test campaigns      ★★★★              │ │
│  │  40-59          Low-priority, consider for expansion ★★★               │ │
│  │  <40            Archive for future consideration     ★★                │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Output: scored_keywords_v2.csv, campaign_recommendations_v2.json            │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    STEP 8: Campaign Export System                             │
│                                                                               │
│  ┌─── Campaign Structure Generation ────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Scored Keywords                                                        │ │
│  │       │                                                                 │ │
│  │       ▼                                                                 │ │
│  │  ┌────────────────────────────────────────────────────────────┐        │ │
│  │  │                    Tiered Campaigns                         │        │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │        │ │
│  │  │  │  Tier 1  │  │  Tier 2  │  │  Tier 3  │  │  Tier 4  │  │        │ │
│  │  │  │Score 80+ │  │Score 60+ │  │Score 40+ │  │ Score <40│  │        │ │
│  │  │  │High Vol  │  │ Med Vol  │  │ Low Vol  │  │  Archive │  │        │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │        │ │
│  │  └────────────────────────────────────────────────────────────┘        │ │
│  │                                                                         │ │
│  │       ▼                                                                 │ │
│  │  ┌────────────────────────────────────────────────────────────┐        │ │
│  │  │                    Ad Group Creation                        │        │ │
│  │  │  • Group by semantic clusters                               │        │ │
│  │  │  • Max 20 keywords per ad group                             │        │ │
│  │  │  • Theme-based naming                                       │        │ │
│  │  └────────────────────────────────────────────────────────────┘        │ │
│  │                                                                         │ │
│  │       ▼                                                                 │ │
│  │  ┌────────────────────────────────────────────────────────────┐        │ │
│  │  │                  Export File Generation                     │        │ │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │        │ │
│  │  │  │ Google Ads  │  │Microsoft Ads│  │   Generic   │       │        │ │
│  │  │  │   Editor    │  │   Editor    │  │     CSV     │       │        │ │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘       │        │ │
│  │  └────────────────────────────────────────────────────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Output: exports/[timestamp]/                                                │
│         ├── google_ads_editor.csv                                            │
│         ├── microsoft_ads_editor.csv                                         │
│         ├── campaign_structure.json                                          │
│         └── negative_keywords_master.txt                                     │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    STEP 9: Campaign Organization System                       │
│                                                                               │
│  ┌─── Campaign-Aware Output Management ────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Generated Files ──▶ Create Campaign Dir ──▶ Move to Campaign Storage   │ │
│  │     (data/)                │                        │                   │ │
│  │        │                   ▼                        ▼                   │ │
│  │        │            ┌─────────────────┐    ┌─────────────────┐          │ │
│  │        │            │campaigns/{name}/│    │  Update Latest  │          │ │
│  │        │            │runs/{timestamp}/│    │    Symlink      │          │ │
│  │        │            └─────────────────┘    └─────────────────┘          │ │
│  │        │                   │                        │                   │ │
│  │        ▼                   ▼                        ▼                   │ │
│  │  ┌────────────────────────────────────────────────────────────┐        │ │
│  │  │                  Campaign Structure                        │        │ │
│  │  │  campaigns/{campaign_name}/                                │        │ │
│  │  │  ├── latest -> runs/{timestamp}     # Always current       │        │ │
│  │  │  └── runs/                                                │        │ │
│  │  │      ├── {timestamp_1}/            # Historical run 1     │        │ │
│  │  │      ├── {timestamp_2}/            # Historical run 2     │        │ │
│  │  │      └── {timestamp_n}/            # Latest run           │        │ │
│  │  │          ├── data/                 # Research files       │        │ │
│  │  │          ├── exports/              # Campaign files      │        │ │
│  │  │          └── run_metadata.json     # Run statistics      │        │ │
│  │  └────────────────────────────────────────────────────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Output: Organized campaign structure with metadata tracking                  │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                   STEP 10: Performance Analysis                               │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         Pipeline Metrics                                │ │
│  │                                                                         │ │
│  │  Seeds Generated  ──────▶  Enriched Keywords  ──────▶  Filtered        │ │
│  │     (~10,000)                 (~10,000)                 (~3,000)       │ │
│  │         │                          │                         │          │ │
│  │         ▼                          ▼                         ▼          │ │
│  │  Quality: 100%              Quality: 100%            Quality: 99.8%    │ │
│  │                                                                         │ │
│  │  ┌────────────────────────────────────────────────────────────┐        │ │
│  │  │                    Final Statistics                        │        │ │
│  │  │  • Total Keywords Discovered: ~10,000                      │        │ │
│  │  │  • Campaign-Ready Keywords: ~3,000                         │        │ │
│  │  │  • Quality Retention Rate: 30%                             │        │ │
│  │  │  • Processing Time: ~15-20 minutes                         │        │ │
│  │  │  • API Calls Used: ~500-800                                │        │ │
│  │  └────────────────────────────────────────────────────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Output: export_summary_v2.json + run_metadata.json                          │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
                           ┌──────────────────┐
                           │   END: SUCCESS   │
                           │                  │
                           │ Files Generated: │
                           │ • 15+ CSV files  │
                           │ • 3+ JSON files  │
                           │ • Campaign org   │
                           │ • Metadata track │
                           └──────────────────┘
```

## Data Flow Summary

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Data Flow Overview                            │
└────────────────────────────────────────────────────────────────────────┘

                         Configuration (.env + config.py)
                                      │
                                      ▼
                              [3-5 Seed Keywords]
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
              keyword_ideas API                   Intent Expansion
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                              [5,000-10,000 Keywords]
                                      │
                                      ▼
                            Enrichment (Metrics)
                                      │
                              [+Volume, CPC, KD]
                                      │
                                      ▼
                          Competitor Discovery (SERP)
                                      │
                           [+5,000 Competitor KWs]
                                      │
                                      ▼
                          Smart Filtering (Multi-stage)
                                      │
                             [~3,000 Keywords]
                                      │
                                      ▼
                           Clustering (Semantic)
                                      │
                            [20-30 Ad Groups]
                                      │
                                      ▼
                          Scoring (Multi-factor)
                                      │
                          [Prioritized Keywords]
                                      │
                                      ▼
                          Campaign Export (Tiered)
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
              Google Ads Editor               Microsoft Ads Editor
```

## Campaign Management System

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Campaign Organization Flow                      │
└────────────────────────────────────────────────────────────────────────┘

            User Updates Config                    Pipeline Execution
                    │                                      │
                    ▼                                      ▼
        ┌─────────────────────┐                ┌─────────────────────┐
        │ CONFIG = {          │                │  keyword_research   │
        │   "campaign_name":  │───────────────▶│      .py runs       │
        │     "mortgage",     │                │                     │
        │   "seed": {...}     │                │  • 9-step pipeline  │
        │ }                   │                │  • All processing   │
        └─────────────────────┘                └─────────────────────┘
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │ Campaign Results    │
                                               │ Auto-Organization   │
                                               └─────────────────────┘
                                                          │
                    ┌─────────────────────────────────────┼─────────────────────────────────────┐
                    │                                     │                                     │
                    ▼                                     ▼                                     ▼
        ┌─────────────────────┐                ┌─────────────────────┐                ┌─────────────────────┐
        │   Create Campaign   │                │   Copy Files to     │                │   Update Latest     │
        │    Directory        │                │  Campaign Storage   │                │     Symlink         │
        │                     │                │                     │                │                     │
        │ campaigns/mortgage/ │                │     data/ files     │                │ campaigns/mortgage/ │
        │ runs/2025-08-06_*   │                │     exports/ files  │                │ latest -> runs/...  │
        └─────────────────────┘                └─────────────────────┘                └─────────────────────┘
                    │                                     │                                     │
                    └─────────────────────────────────────┼─────────────────────────────────────┘
                                                          │
                                                          ▼
                                                ┌─────────────────────┐
                                                │  Generate Metadata  │
                                                │                     │
                                                │ run_metadata.json:  │
                                                │ • Campaign name     │
                                                │ • Timestamp         │
                                                │ • Keywords found    │
                                                │ • Average score     │
                                                │ • Seed terms used   │
                                                └─────────────────────┘

Multiple Campaign Structure:

campaigns/
├── mortgage/
│   ├── latest -> runs/2025-08-06_124959    # Always points to latest
│   └── runs/
│       ├── 2024-08-05_existing_data/      # Historical run 1
│       └── 2025-08-06_124959/            # Latest run
│           ├── data/                      # All research files
│           ├── exports/                   # Campaign files
│           └── run_metadata.json          # Run statistics
├── home_equity/
│   ├── latest -> runs/2025-08-06_151022    
│   └── runs/
│       └── 2025-08-06_151022/            # Different campaign
└── refinancing/
    ├── latest -> runs/2025-08-06_160033
    └── runs/
        └── 2025-08-06_160033/            # Another campaign

Benefits:
✅ Same workflow (edit config.py, run pipeline)
✅ Automatic organization by campaign name  
✅ Historical preservation of all runs
✅ Easy switching between campaigns
✅ Metadata tracking for performance analysis
```

## Key Components & Responsibilities

### Core Modules

```
src/
├── core/                      [Infrastructure Layer]
│   ├── api_client.py         → API communication & rate limiting
│   ├── rate_limiter.py       → Request throttling (30 req/sec)
│   └── data_processor.py     → JSON flattening & normalization
│
├── pipeline/                  [Business Logic Layer]
│   ├── seed_generator.py     → Keyword discovery strategies
│   ├── enrichment.py         → Metrics & data augmentation
│   ├── competitor_analyzer.py → SERP analysis & gap discovery
│   ├── filter_cluster.py     → Filtering rules & clustering
│   ├── seasonality_scorer.py → Scoring & trend analysis
│   └── campaign_exporter.py  → Campaign structure generation
│
└── utils/                     [Support Layer]
    ├── logger.py             → Centralized logging
    └── file_handler.py       → I/O operations
```

### API Endpoints Used

```
DataForSEO Labs API Endpoints:
├── /locations_and_languages     → Location code resolution
├── /keyword_ideas               → Category-based expansion (PRIMARY)
├── /keyword_suggestions         → Long-tail variants
├── /related_keywords            → Semantic expansion
├── /ranked_keywords             → Competitor keyword mining
├── /serp_competitors            → SERP-based competitor discovery
├── /keyword_overview            → Bulk metrics enrichment
└── /bulk_keyword_difficulty     → Difficulty scoring
```

### Performance Characteristics

```
┌────────────────────────────────────────────────────────────────┐
│                    Performance Profile                         │
├────────────────────────────────────────────────────────────────┤
│ Metric                    │ V1 Original │ V2 Enhanced        │
├───────────────────────────┼─────────────┼────────────────────┤
│ Processing Time           │ 25-30 min   │ 15-20 min (-35%)   │
│ Keywords Discovered       │ 15,000+     │ 10,000 (focused)   │
│ Quality (Relevance)       │ 85%         │ 99.8%              │
│ API Calls                 │ 1,000+      │ 500-800            │
│ Memory Usage              │ 500MB       │ 300MB              │
│ Campaign-Ready Keywords   │ 2,500       │ 3,000              │
└───────────────────────────┴─────────────┴────────────────────┘
```

## Error Handling & Recovery

```
┌──────────────────────────────────────────────────────────────┐
│                    Error Handling Flow                       │
└──────────────────────────────────────────────────────────────┘

        API Request
             │
             ▼
    ┌─────────────────┐
    │ Try API Call    │
    └────────┬────────┘
             │
        Success? ──────────────────────▶ Return Data
             │
            No
             │
             ▼
    ┌─────────────────┐
    │ Error Type?     │
    └────────┬────────┘
             │
    ┌────────┴────────┬──────────┬──────────┐
    ▼                 ▼          ▼          ▼
Rate Limit (429)   No Data    Network    Other
    │              (40501)     Error      Error
    │                 │          │          │
    ▼                 ▼          ▼          ▼
Exponential      Return Empty  Retry     Log & Raise
Backoff          DataFrame    (3x)        Exception
```

## Configuration Structure

```
CONFIG = {
    campaign_name: "mortgage" → Campaign organization name
    dataforseo: {
        login, password      → API Authentication
        rate_limit: 30       → Requests per second
        timeout: 30          → Request timeout
        retries: 3           → Retry attempts
    },
    target: {
        country: "Canada"    → Target market
        language: "en"       → Content language
        provinces: [...]     → Regional analysis
    },
    seed: {
        business_terms       → Initial keywords
        competitor_domains   → Known competitors
        your_domain         → For gap analysis
        generation_strategy  → V2 enhancement settings
    },
    filters: {
        volume: 50-50,000   → Search volume range
        cpc: $0.10-$20      → Cost per click range
        difficulty: ≤70     → Ranking difficulty
        intents: [...]      → Allowed search intents
    },
    clustering: {
        method: "hybrid"    → Clustering algorithm
        k_range: (8,20)     → Cluster count range
    },
    scoring: {
        weights: {...}      → Multi-factor weights
    },
    export: {
        formats: [...]      → Output file types
        tiers: {...}        → Campaign structure
    }
}
```

## File Outputs

```
Project Root/
├── campaigns/                   [Campaign Organization System]
│   ├── mortgage/
│   │   ├── latest -> runs/2025-08-06_124959    [Always points to latest]
│   │   └── runs/
│   │       ├── 2024-08-05_existing_data/      [Historical run 1]
│   │       │   ├── data/          [Research files: 86 keywords]
│   │       │   ├── exports/       [Campaign files]
│   │       │   └── run_metadata.json  [Run statistics]
│   │       └── 2025-08-06_124959/             [Latest run]
│   │           ├── data/          [All intermediate processing]
│   │           │   ├── seed_keywords_v2.csv
│   │           │   ├── enriched_keywords_v2.csv
│   │           │   ├── competitor_keywords_v2.csv
│   │           │   ├── filtered_keywords_v2.csv
│   │           │   ├── scored_keywords_v2.csv
│   │           │   ├── campaign_recommendations_v2.json
│   │           │   └── export_summary_v2.json
│   │           ├── exports/       [Final campaign files]
│   │           │   ├── google_ads/
│   │           │   │   ├── google_ads_tier_1_easy_wins.csv
│   │           │   │   └── google_ads_tier_2_high_volume.csv
│   │           │   ├── microsoft_ads/
│   │           │   │   ├── microsoft_ads_tier_1_easy_wins.csv
│   │           │   │   └── microsoft_ads_tier_2_high_volume.csv
│   │           │   └── campaign_assets/
│   │           │       ├── campaign_summary.json
│   │           │       └── negative_keywords.txt
│   │           └── run_metadata.json    [Campaign metadata]
│   ├── home_equity/                    [Different campaign]
│   │   ├── latest -> runs/2025-08-06_151022
│   │   └── runs/...
│   └── refinancing/                    [Another campaign]
│       ├── latest -> runs/2025-08-06_160033
│       └── runs/...
│
├── data/                        [Temporary files - copied to campaigns]
├── exports/                     [Temporary files - copied to campaigns]
└── logs/                        [Execution Logs]
    └── keyword_research.log
```

## Success Metrics

The pipeline is considered successful when:
1. ✅ API connection verified
2. ✅ Location codes resolved
3. ✅ >5,000 seed keywords generated
4. ✅ All keywords enriched with metrics
5. ✅ Competitors discovered (auto or manual)
6. ✅ Keywords filtered to high-relevance set
7. ✅ Semantic clusters created
8. ✅ Keywords scored and prioritized
9. ✅ Campaign files exported
10. ✅ 99%+ relevance rate achieved

---

*This document represents the complete data flow and architecture of the DataForSEO Keyword Research Pipeline V2 (Enhanced)*