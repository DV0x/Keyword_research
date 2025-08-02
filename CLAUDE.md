# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready keyword research pipeline that uses DataForSEO APIs to discover, analyze, and export keywords for PPC campaigns. The system is designed for the mortgage/finance industry but can be adapted for any vertical.

## Core Architecture

The pipeline follows a modular, step-based architecture:

1. **Configuration Layer** (`config.py`) - Centralized settings for API credentials, target markets, filtering rules, and export preferences
2. **API Abstraction Layer** (`keyword_research.py` lines 176-237) - Rate-limited wrapper functions for DataForSEO endpoints
3. **Data Processing Pipeline** - Nine sequential steps from seed generation to final export
4. **Helper Functions** - Utilities for rate limiting, data flattening, batch processing, and normalization

## Key Components

### API Integration
- Uses DataForSEO Labs API with production-grade rate limiting (30 req/sec)
- Implements exponential backoff retry logic for resilient API calls
- All API functions return flattened pandas DataFrames for consistent data processing

### Data Flow Pipeline
1. **Seed Generation** - Multiple sources: keyword ideas, suggestions, competitor analysis
2. **Enrichment** - Adds search volume, CPC, difficulty scores, and SERP features
3. **Competitor Analysis** - SERP competitor discovery and keyword gap analysis
4. **Filtering** - Pattern-based exclusions, volume/CPC thresholds, intent classification
5. **Seasonality Analysis** - Trend detection and seasonal pattern identification
6. **Clustering** - Semantic and category-based keyword grouping for ad groups
7. **Scoring** - Multi-factor prioritization system with difficulty weighting
8. **Export** - Campaign-ready files with tiered ad groups and negative keywords

### Configuration System
The `CONFIG` dictionary in `config.py` controls all pipeline behavior:
- **API settings**: Rate limits, timeouts, retry logic
- **Target market**: Country, language, provincial analysis
- **Seed keywords**: Business terms and competitor domains
- **Filtering rules**: Volume/CPC ranges, exclusion patterns, word count limits
- **Processing options**: Clustering methods, scoring weights, export formats

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline
```bash
# Test configuration and API credentials
python test_config.py

# Run full keyword research pipeline
python keyword_research.py
```

### Environment Variables Required
Create a `.env` file with:
```
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password
```

## Current Implementation Status

The project is **75% complete** with solid foundations:
- ✅ Steps 1-7: Environment, API connection, and scaffolding
- 🔄 Steps 8-12: Need implementation of core pipeline functions

**Next Implementation Priority:**
1. **Step 8**: Implement actual keyword generation (currently placeholder in `main()`)
2. **Step 9**: Add keyword enrichment with difficulty scoring
3. **Step 10**: Competitor analysis implementation
4. **Step 11**: Smart filtering and clustering algorithms
5. **Step 12**: Export system for campaign-ready files

## Architecture Notes

### Rate Limiting Strategy
Uses a decorator-based approach (`@rate_limited`) that enforces API limits at the function level. The system can handle DataForSEO's 2000 requests/minute limit safely.

### Data Processing Pattern
All API responses are normalized through `flatten_task_result()` which handles nested JSON structures and converts them to flat pandas DataFrames for consistent processing.

### Error Handling
Implements a three-tier error handling strategy:
1. **Network level**: Exponential backoff for connection issues
2. **API level**: Handles DataForSEO-specific error codes
3. **Data level**: Graceful degradation when no data is returned

### Batch Processing
Uses `batch_iterator()` to process large keyword lists in API-appropriate chunks (200-1000 keywords depending on endpoint).

## Customization Points

To adapt for different industries:
1. Update `business_terms` in `config.py` with industry-specific seed keywords
2. Modify `exclude_patterns` to filter out irrelevant terms for your vertical
3. Adjust volume/CPC thresholds based on industry competition levels
4. Update `competitor_domains` as you discover relevant competitors

The pipeline is designed to be industry-agnostic while providing deep customization options through the configuration system.