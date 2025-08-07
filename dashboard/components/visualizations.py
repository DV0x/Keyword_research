"""Reusable visualization components"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

def create_opportunity_scatter(
    df: pd.DataFrame,
    color_by: Optional[str] = 'priority_tier',
    keyword_col: str = 'keyword'
) -> go.Figure:
    """Create opportunity map scatter plot"""
    if 'keyword_difficulty' not in df.columns or 'search_volume' not in df.columns:
        return go.Figure()
    
    # Build hover data dynamically
    hover_cols = []
    if keyword_col in df.columns:
        hover_cols.append(keyword_col)
    if 'cpc' in df.columns:
        hover_cols.append('cpc')
    
    fig = px.scatter(
        df,
        x='keyword_difficulty',
        y='search_volume',
        size='cpc' if 'cpc' in df.columns else None,
        color=color_by if color_by in df.columns else None,
        hover_data=hover_cols,
        title='Keyword Opportunity Map',
        labels={
            'keyword_difficulty': 'Difficulty Score',
            'search_volume': 'Monthly Searches'
        },
        height=400
    )
    
    # Add quadrant lines
    fig.add_hline(y=1000, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=25, y=5000, text="Quick Wins", showarrow=False)
    fig.add_annotation(x=75, y=5000, text="Competitive", showarrow=False)
    
    return fig

def create_distribution_pie(
    df: pd.DataFrame,
    column: str,
    title: str = "Distribution"
) -> go.Figure:
    """Create distribution pie chart"""
    if column not in df.columns:
        return go.Figure()
    
    value_counts = df[column].value_counts()
    
    fig = px.pie(
        values=value_counts.values,
        names=value_counts.index,
        title=title,
        height=400
    )
    
    return fig

def create_difficulty_histogram(df: pd.DataFrame) -> go.Figure:
    """Create difficulty distribution histogram"""
    if 'keyword_difficulty' not in df.columns:
        return go.Figure()
    
    # Create bins
    bins = [0, 30, 50, 70, 100]
    labels = ['Easy (0-30)', 'Medium (30-50)', 'Hard (50-70)', 'Very Hard (70+)']
    
    df['difficulty_bin'] = pd.cut(df['keyword_difficulty'], bins=bins, labels=labels)
    bin_counts = df['difficulty_bin'].value_counts()
    
    fig = px.bar(
        x=bin_counts.index,
        y=bin_counts.values,
        title='Keywords by Difficulty Level',
        labels={'x': 'Difficulty Level', 'y': 'Number of Keywords'},
        color=bin_counts.index,
        color_discrete_map={
            'Easy (0-30)': '#28a745',
            'Medium (30-50)': '#17a2b8',
            'Hard (50-70)': '#ffc107',
            'Very Hard (70+)': '#dc3545'
        },
        height=350
    )
    
    return fig