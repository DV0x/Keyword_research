# Keyword Research Dashboard Guide

This comprehensive guide explains the Streamlit dashboard implementation, data sources, and how each component helps with keyword research analysis.

## Table of Contents
- [Overview](#overview)
- [Data Sources & Pipeline](#data-sources--pipeline)
- [Dashboard Tabs Explained](#dashboard-tabs-explained)
- [Filters & Configuration](#filters--configuration)
- [Export Functionality](#export-functionality)

## Overview

The dashboard is a modular Streamlit application that visualizes keyword research data from the DataForSEO pipeline. It provides actionable insights through interactive visualizations, strategic keyword lists, and advanced clustering analysis.

### Architecture
```
dashboard/
├── dashboard.py          # Main orchestrator
├── components/           # UI components
│   ├── sidebar.py       # Filters and controls
│   ├── metrics.py       # KPI metrics row
│   └── visualizations.py # Reusable charts
├── pages/               # Dashboard tabs
│   ├── overview.py      # Overview charts
│   ├── actionable.py    # Keyword lists
│   └── clustering.py    # Clustering analysis
└── utils/               # Core utilities
    ├── data_loader.py   # Campaign data loading
    ├── clustering_engine.py # Clustering algorithms
    └── export_utils.py  # Export formatting
```

## Data Sources & Pipeline

All dashboard data originates from **DataForSEO APIs** processed through a 9-step pipeline:

### Data Flow
1. **Source**: DataForSEO Labs API endpoints
   - Keyword Ideas API
   - Keyword Suggestions API  
   - SERP Competitors API
   - Domain Rank Overview API
   - Bulk Keyword Difficulty API

2. **Processing**: `keyword_research.py` 9-step pipeline
   - Seed generation → Enrichment → Competitor analysis → Filtering → Scoring

3. **Output Files**: Dashboard reads from `campaigns/[campaign]/latest/data/`

### Pipeline Output Files

#### **Core Data Files**

1. **`seed_keywords_v2.csv`** *(Step 1-2)*
   - **Content**: Initial keyword ideas from DataForSEO sources
   - **Key Data**: Basic keyword, search volume, CPC, competition, search intent
   - **Source APIs**: Keyword Ideas, Suggestions, Competitor Analysis

2. **`enriched_keywords_v2.csv`** *(Step 2)*
   - **Content**: Seeds enhanced with full DataForSEO metrics  
   - **Added Data**: Difficulty scores, backlink requirements, trends, seasonality

3. **`filtered_keywords_v2.csv`** *(Step 4)*
   - **Content**: Keywords after smart filtering (99.8% relevance)
   - **Removed**: Irrelevant terms, wrong intent, volume/CPC outliers

4. **`competitor_keywords_v2.csv`** *(Step 3)*
   - **Content**: SERP competitor analysis data
   - **Source**: SERP Competitors API analyzing top-ranking domains

5. **`scored_keywords_v2.csv`** *(Step 8 - MAIN DASHBOARD DATA)*
   - **Content**: Final scored keywords with campaign-ready metrics
   - **Key Columns**: `total_score`, `priority_tier`, `difficulty_tier`, `recommended_match_type`
   - **Used By**: All dashboard tabs for visualizations and analysis

#### **Supporting Files**

6. **`negative_keywords_v2.txt`** *(Step 9)*
   - **Content**: Campaign negative keyword list for filtering irrelevant traffic

7. **`campaign_recommendations_v2.json`** *(Step 9)*
   - **Content**: Strategic recommendations and campaign structure

8. **`export_summary_v2.json`** *(Pipeline End)*
   - **Content**: Pipeline statistics and performance metrics

### Key Metrics Origins

- **Search Volume**: DataForSEO keyword data
- **CPC**: Google Ads historical data via DataForSEO
- **Keyword Difficulty**: DataForSEO's proprietary 0-100 difficulty score
- **Priority Tiers**: Pipeline's scoring algorithm
- **Search Intent**: DataForSEO's intent classification
- **Competitor Data**: SERP analysis from DataForSEO

## Dashboard Tabs Explained

### 📊 Overview Tab

Provides high-level campaign insights through 4 key visualizations:

#### **1. Opportunity Map (Scatter Plot)**
- **X-axis**: Keyword Difficulty (0-100)
- **Y-axis**: Search Volume (monthly searches)
- **Bubble Size**: CPC value (larger = more valuable)
- **Color**: Priority tiers or search intent
- **Quadrants**: 
  - **Quick Wins** (low difficulty + high volume)
  - **Competitive** (high difficulty + high volume)
- **Value**: Identifies strategy opportunities and investment priorities

#### **2. Keyword Distribution (Pie Chart)**
- **Shows**: Breakdown by priority tiers OR search intent
- **Options**: Priority levels, Commercial/Informational balance
- **Value**: Campaign structure insights and budget allocation guidance

#### **3. CPC Distribution (Histogram)**  
- **Shows**: Cost-per-click frequency distribution
- **Bins**: 30 automatic ranges
- **Value**: Budget planning and bid strategy insights

#### **4. Competition Landscape (Difficulty Histogram)**
- **Shows**: Keywords grouped by difficulty levels
- **Categories**: Easy (0-30), Medium (30-50), Hard (50-70), Very Hard (70+)
- **Color Coding**: Green to Red difficulty progression
- **Value**: Resource allocation and timeline planning

#### **Summary Statistics**
- **Volume Stats**: Total, average, median search volume
- **CPC Stats**: Average, median, range of costs
- **Difficulty Stats**: Average difficulty, easy/hard keyword counts

### 🎯 Actionable Keywords Tab

Provides 4 strategic keyword lists for immediate campaign implementation:

#### **1. ✅ Quick Wins** *(Priority Focus)*
- **Criteria**: Difficulty < 30 AND Volume > 500
- **Purpose**: Easy-to-rank keywords with substantial traffic
- **Strategy**: Start campaigns here for fastest ROI
- **Display**: Top 20 keywords, sorted by volume

#### **2. 💎 High Value Keywords**
- **Criteria**: CPC > 75th percentile AND Volume > 100
- **Purpose**: Most profitable keywords worth higher investment
- **Strategy**: Premium bid strategy for high-converting terms
- **Display**: Top 15 keywords, sorted by CPC

#### **3. 🎯 Low Competition**
- **Criteria**: Difficulty < 40
- **Purpose**: Easier ranking opportunities across volume ranges  
- **Strategy**: Broader content/SEO strategy opportunities
- **Display**: Top 15 keywords, sorted by volume

#### **4. 🛒 High Commercial Intent**
- **Criteria**: Intent = `commercial` OR `transactional`
- **Purpose**: Keywords most likely to convert to leads/sales
- **Strategy**: High-priority for conversion-focused campaigns
- **Display**: Top 20 keywords, sorted by total score

#### **Table Features**
- **Dynamic columns**: Keyword, Volume, CPC, Difficulty, Intent
- **Progress bars**: Visual difficulty indicators
- **Export buttons**: Individual CSV downloads per list
- **Responsive design**: Compact view for smaller lists

### 🧩 Clustering Tab

Advanced keyword grouping for campaign structure optimization:

#### **Clustering Methods**
- **K-Means**: TF-IDF vector similarity grouping (current)
- **Hierarchical**: Tree-based grouping (planned)
- **Semantic**: AI-based understanding (planned)
- **Dynamic clusters**: 2-20 groups based on dataset size

#### **Clustering Controls**
- **Method Selection**: Algorithm choice
- **Cluster Count**: Slider (2 to max clusters)
- **Visualization Type**: 4 different views

#### **Visualization Types**

##### **1. Network Graph**
- **Nodes**: Keywords (size = volume, color = cluster)
- **Edges**: Similarity connections (>30% threshold)
- **Layout**: Spring-force algorithm
- **Interactivity**: Hover for keyword details
- **Use Case**: Understanding keyword relationships

##### **2. Scatter Plot (2D PCA)**
- **Axes**: Principal components of TF-IDF space
- **Points**: Keywords (size = volume, color = cluster)
- **Purpose**: Visual cluster separation
- **Use Case**: Outlier detection and cluster quality assessment

##### **3. Bubble Chart**
- **X-axis**: Average cluster difficulty
- **Y-axis**: Average cluster CPC
- **Bubble size**: Total cluster volume
- **Color**: Number of keywords per cluster
- **Quadrants**: Strategic priority identification
- **Use Case**: Cluster prioritization (easy + valuable = priority)

##### **4. Dendrogram** *(Coming Soon)*
- **Structure**: Hierarchical clustering tree
- **Use Case**: Understanding clustering decisions

#### **Cluster Intelligence**
- **Auto-naming**: Based on most frequent terms
- **Summaries**: Volume, CPC, difficulty, intent analysis
- **Statistics**: Per-cluster metrics and comparisons
- **Export options**: Individual clusters, Google Ads format, summaries

#### **Clustering Algorithm Details**
1. **TF-IDF Vectorization**: Convert keywords to numerical features
2. **Similarity Matrix**: Cosine similarity between keyword vectors  
3. **K-Means Clustering**: Group similar keywords
4. **PCA Reduction**: 2D visualization of high-dimensional data
5. **Network Analysis**: Connect similar keywords (NetworkX)

## Filters & Configuration

Dashboard filtering uses the pipeline's smart filtering system from `config.py`:

### **Applied Filters** *(from scored keywords)*

#### **Volume Filters**
- **Min Search Volume**: 50 searches/month 
- **Max Search Volume**: 50,000 searches/month
- **Purpose**: Avoid low-traffic and overly broad terms

#### **CPC Filters (Canadian Dollars)**
- **Min CPC**: $0.10 CAD
- **Max CPC**: $50.00 CAD  
- **Purpose**: Focus on monetizable keywords within budget

#### **Difficulty Filters**
- **Max Keyword Difficulty**: 70/100
- **Purpose**: Exclude ultra-competitive terms

#### **Search Intent Filters**
- **Allowed**: `["commercial", "transactional", "navigational"]`
- **Excluded**: Informational (low conversion potential)
- **Purpose**: High-conversion intent focus

#### **Word Count Filters**
- **Min Words**: 2 words
- **Max Words**: 6 words
- **Purpose**: Optimal phrase length

#### **Pattern Exclusion** *(Regex-based)*
- **Job-related**: `jobs`, `careers`, `salary`, `hiring`
- **Educational**: `definition`, `what is`, `training`, `school`
- **Free/DIY**: `free`, `diy`, `yourself`
- **Purpose**: Remove non-commercial queries

### **Filter Application Order**
1. Volume filter → Remove low/high outliers
2. CPC filter → Remove unprofitable keywords  
3. Difficulty filter → Remove ultra-competitive
4. Intent filter → Keep only commercial
5. Word count filter → Optimal length
6. Pattern exclusion → Remove irrelevant

**Result**: 99.8% relevance rate through multi-stage filtering

### **Sidebar Controls**
- **Campaign Selection**: Choose active campaign
- **Volume Range**: Interactive sliders
- **CPC Range**: Budget-based filtering
- **Difficulty Range**: Competition level selection
- **Intent Selection**: Multi-select commercial types
- **Real-time Updates**: All tabs update instantly

## Export Functionality

### **Overview Tab Exports**
- **Chart Data**: Underlying data for each visualization
- **Summary Stats**: Downloadable metrics tables

### **Actionable Tab Exports**
- **Quick Wins CSV**: `{campaign}_quick_wins_{date}.csv`
- **High Value CSV**: `{campaign}_high_value_{date}.csv`  
- **Low Competition CSV**: `{campaign}_low_competition_{date}.csv`
- **Commercial Intent CSV**: `{campaign}_commercial_{date}.csv`
- **Format**: Campaign-ready with all relevant metrics

### **Clustering Tab Exports**

#### **Individual Clusters**
- **Format**: `{campaign}_cluster_{id}.csv`
- **Content**: All keywords in specific cluster
- **Use Case**: Creating targeted ad groups

#### **Complete Dataset**
- **Format**: `{campaign}_clustered_keywords.csv`
- **Content**: All keywords + cluster assignments
- **Additional**: Cluster names and IDs

#### **Google Ads Format**
- **Format**: `{campaign}_google_ads_clusters.csv`
- **Structure**: Campaign/Ad Group hierarchy
- **Columns**: Campaign, Ad Group, Keyword, Match Type, Bid

#### **Cluster Summary**
- **Format**: `{campaign}_cluster_summary.csv`  
- **Content**: Strategic overview per cluster
- **Metrics**: Volume, CPC, difficulty, keyword counts

### **Export Features**
- **Instant Download**: Browser-based CSV generation
- **Timestamped Files**: Automatic date/time naming
- **Campaign Context**: Includes campaign name in filename
- **Ready Format**: Direct import to ad platforms

## Technical Implementation

### **Data Loading**
- **Auto-discovery**: Scans `campaigns/` directory
- **Latest Data**: Always uses most recent pipeline run
- **Error Handling**: Graceful fallbacks for missing data
- **Performance**: Cached loading for large datasets

### **Real-time Processing**
- **Filtering**: Client-side pandas operations
- **Clustering**: On-demand sklearn processing
- **Visualizations**: Plotly interactive charts
- **State Management**: Streamlit session state

### **Dependencies**
- **Core**: `streamlit >= 1.28.0`, `pandas >= 2.0.0`
- **Visualization**: `plotly >= 5.17.0`
- **ML**: `scikit-learn >= 1.3.0`
- **Network**: `networkx >= 3.0`
- **Processing**: `numpy >= 1.24.0`

### **Performance Considerations**
- **Lazy Loading**: Components load data on demand
- **Chunk Processing**: Large datasets processed in batches
- **Memory Management**: Efficient pandas operations
- **Caching**: Streamlit native caching for expensive operations

## Usage Best Practices

### **Campaign Analysis Workflow**
1. **Start with Overview**: Get high-level campaign insights
2. **Identify Opportunities**: Use opportunity map quadrants
3. **Extract Actionables**: Download quick wins and high-value lists
4. **Structure Campaigns**: Use clustering for ad group organization
5. **Export for Implementation**: Get platform-ready files

### **Strategic Decision Making**
- **Budget Allocation**: Use CPC distribution and high-value lists
- **Timeline Planning**: Easy keywords for quick wins, hard ones for long-term
- **Content Strategy**: Use clusters to identify topic areas
- **Competitive Analysis**: Compare difficulty vs. opportunity

### **Export Strategy**
- **Quick Implementation**: Start with actionable lists
- **Structured Campaigns**: Use clustering exports for organization
- **Ongoing Analysis**: Regular dashboard reviews with updated pipeline data
- **Performance Tracking**: Compare dashboard insights with campaign results

This documentation serves as a comprehensive reference for understanding and using the keyword research dashboard effectively.