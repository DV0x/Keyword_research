"""Actionable keywords lists and recommendations"""
import streamlit as st
import pandas as pd
from datetime import datetime

def render(df: pd.DataFrame, campaign_name: str):
    """Render actionable keywords tab"""
    st.header("🎯 Actionable Keyword Lists")
    
    if df.empty:
        st.warning("No keywords available with current filters")
        return
    
    # Find the keyword column (could have different names)
    keyword_col = None
    possible_keyword_cols = ['keyword', 'keywords', 'term', 'search_term', 'query']
    for col in possible_keyword_cols:
        if col in df.columns:
            keyword_col = col
            break
    
    if keyword_col is None:
        st.warning(f"No keyword column found. Available columns: {df.columns.tolist()}")
        st.info("Expected one of: keyword, keywords, term, search_term, query")
        return
    
    # Quick Wins
    st.subheader("✅ Quick Wins (Easy + High Volume)")
    quick_wins = df[
        (df.get('keyword_difficulty', pd.Series([50]*len(df))) < 30) & 
        (df.get('search_volume', pd.Series([0]*len(df))) > 500)
    ].sort_values('search_volume', ascending=False).head(20)
    
    if not quick_wins.empty:
        display_keyword_table(quick_wins, "quick_wins", campaign_name, keyword_col=keyword_col)
    else:
        st.info("No quick wins found. Try adjusting filters.")
    
    st.markdown("---")
    
    # Two columns for other lists
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💎 High Value Keywords")
        if 'cpc' in df.columns:
            high_value = df[
                (df['cpc'] > df['cpc'].quantile(0.75)) &
                (df.get('search_volume', pd.Series([0]*len(df))) > 100)
            ].sort_values('cpc', ascending=False).head(15)
            
            if not high_value.empty:
                display_keyword_table(high_value, "high_value", campaign_name, compact=True, keyword_col=keyword_col)
    
    with col2:
        st.subheader("🎯 Low Competition")
        if 'keyword_difficulty' in df.columns:
            low_comp = df[
                df['keyword_difficulty'] < 40
            ].sort_values('search_volume', ascending=False).head(15)
            
            if not low_comp.empty:
                display_keyword_table(low_comp, "low_competition", campaign_name, compact=True, keyword_col=keyword_col)
    
    st.markdown("---")
    
    # Commercial Intent
    st.subheader("🛒 High Commercial Intent")
    if 'main_intent' in df.columns:
        commercial = df[
            df['main_intent'].isin(['commercial', 'transactional'])
        ].sort_values(
            'total_score' if 'total_score' in df.columns else 'search_volume',
            ascending=False
        ).head(20)
        
        if not commercial.empty:
            display_keyword_table(commercial, "commercial", campaign_name, keyword_col=keyword_col)

def display_keyword_table(
    df: pd.DataFrame, 
    table_type: str, 
    campaign_name: str,
    compact: bool = False,
    keyword_col: str = 'keyword'
):
    """Display keyword table with export option"""
    # Select columns to display
    display_cols = [keyword_col]
    
    if 'search_volume' in df.columns:
        display_cols.append('search_volume')
    if 'cpc' in df.columns:
        display_cols.append('cpc')
    if 'keyword_difficulty' in df.columns:
        display_cols.append('keyword_difficulty')
    if not compact and 'main_intent' in df.columns:
        display_cols.append('main_intent')
    
    display_df = df[display_cols].copy()
    
    # Rename columns for display
    column_names = {
        keyword_col: 'Keyword',
        'search_volume': 'Volume',
        'cpc': 'CPC ($)',
        'keyword_difficulty': 'Difficulty',
        'main_intent': 'Intent'
    }
    display_df.columns = [column_names.get(col, col) for col in display_df.columns]
    
    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Volume": st.column_config.NumberColumn(format="%d"),
            "CPC ($)": st.column_config.NumberColumn(format="$%.2f"),
            "Difficulty": st.column_config.ProgressColumn(
                min_value=0,
                max_value=100,
                format="%d"
            )
        }
    )
    
    # Export button
    csv = df.to_csv(index=False)
    st.download_button(
        f"📥 Export {table_type.replace('_', ' ').title()}",
        csv,
        f"{campaign_name}_{table_type}_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        key=f"export_{table_type}"
    )