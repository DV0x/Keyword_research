"""
Data Table Page - Complete keyword data view
Shows all scored keywords with essential columns for campaign management
"""
import streamlit as st
import pandas as pd


def render(filtered_df, selected_campaign):
    """Render the data table page"""
    st.header("📋 Complete Keyword Data")
    
    if filtered_df.empty:
        st.warning("No keyword data available.")
        return
    
    # Essential columns to display
    essential_columns = [
        'keyword', 'search_volume', 'keyword_difficulty', 'main_intent', 'cpc',
        'total_score', 'priority_tier', 'difficulty_tier', 'recommended_match_type',
        'competition_level', 'cluster_name', 'source'
    ]
    
    # Filter to only include columns that exist in the dataframe
    available_columns = [col for col in essential_columns if col in filtered_df.columns]
    
    # Display available columns info
    st.info(f"Showing {len(available_columns)} essential columns out of {len(filtered_df.columns)} total columns")
    
    # Create filtered dataframe with essential columns
    display_df = filtered_df[available_columns].copy()
    
    # Create filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Search box
        search_term = st.text_input("🔍 Search keywords", placeholder="Type to filter...")
    
    with col2:
        # Intent filter
        if 'main_intent' in display_df.columns:
            intents = ['All'] + sorted(display_df['main_intent'].dropna().unique().tolist())
            selected_intent = st.selectbox("Intent", intents)
    
    with col3:
        # Priority tier filter
        if 'priority_tier' in display_df.columns:
            tiers = ['All'] + sorted(display_df['priority_tier'].dropna().unique().tolist())
            selected_tier = st.selectbox("Priority Tier", tiers)
    
    # Apply filters
    filtered_display_df = display_df.copy()
    
    # Search filter
    if search_term:
        filtered_display_df = filtered_display_df[
            filtered_display_df['keyword'].str.contains(search_term, case=False, na=False)
        ]
    
    # Intent filter
    if 'main_intent' in display_df.columns and selected_intent != 'All':
        filtered_display_df = filtered_display_df[
            filtered_display_df['main_intent'] == selected_intent
        ]
    
    # Priority tier filter
    if 'priority_tier' in display_df.columns and selected_tier != 'All':
        filtered_display_df = filtered_display_df[
            filtered_display_df['priority_tier'] == selected_tier
        ]
    
    # Display row count
    st.write(f"**Displaying {len(filtered_display_df):,} of {len(display_df):,} keywords**")
    
    # Style the dataframe with color coding
    def style_dataframe(df):
        """Apply color coding to the dataframe"""
        def highlight_difficulty_tier(val):
            if pd.isna(val):
                return ''
            val = str(val).lower()
            if val == 'easy':
                return 'background-color: #d4edda'  # Green
            elif val == 'medium':
                return 'background-color: #fff3cd'  # Yellow
            elif val == 'hard':
                return 'background-color: #f8d7da'  # Red
            return ''
        
        def highlight_priority_tier(val):
            if pd.isna(val):
                return ''
            val = str(val).lower()
            if val == 'high':
                return 'background-color: #cce5ff'  # Light blue
            elif val == 'medium':
                return 'background-color: #e6f3ff'  # Very light blue
            return ''
        
        styled_df = df.style
        
        if 'difficulty_tier' in df.columns:
            styled_df = styled_df.applymap(highlight_difficulty_tier, subset=['difficulty_tier'])
        
        if 'priority_tier' in df.columns:
            styled_df = styled_df.applymap(highlight_priority_tier, subset=['priority_tier'])
        
        # Format numeric columns
        if 'search_volume' in df.columns:
            styled_df = styled_df.format({'search_volume': '{:,.0f}'})
        
        if 'cpc' in df.columns:
            styled_df = styled_df.format({'cpc': '${:.2f}'})
        
        if 'total_score' in df.columns:
            styled_df = styled_df.format({'total_score': '{:.1f}'})
        
        if 'keyword_difficulty' in df.columns:
            styled_df = styled_df.format({'keyword_difficulty': '{:.0f}'})
        
        return styled_df
    
    # Display the styled dataframe
    if not filtered_display_df.empty:
        st.dataframe(
            style_dataframe(filtered_display_df),
            use_container_width=True,
            height=600
        )
        
        # Export functionality
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Download button
            csv = filtered_display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"{selected_campaign}_keywords_data.csv",
                mime="text/csv"
            )
        
        with col2:
            st.write(f"**Total keywords:** {len(filtered_display_df):,}")
    
    else:
        st.warning("No keywords match your filter criteria.")
    
    # Column legend
    with st.expander("📖 Column Descriptions"):
        st.markdown("""
        **Essential Columns:**
        - **keyword**: The search term
        - **search_volume**: Monthly search volume
        - **keyword_difficulty**: SEO ranking difficulty (0-100, lower is easier)
        - **main_intent**: Search intent (commercial/navigational/transactional)
        - **cpc**: Cost per click in CAD
        - **total_score**: Overall priority score from algorithm
        - **priority_tier**: High/Medium/Low priority classification
        - **difficulty_tier**: Easy/Medium/Hard difficulty classification
        - **recommended_match_type**: Suggested match type for ads
        - **competition_level**: Google Ads competition level
        - **cluster_name**: Ad group clustering assignment
        - **source**: How the keyword was discovered
        
        **Color Coding:**
        - 🟢 Easy difficulty tier
        - 🟡 Medium difficulty tier  
        - 🔴 Hard difficulty tier
        - 🔵 High priority tier
        - 💙 Medium priority tier
        """)