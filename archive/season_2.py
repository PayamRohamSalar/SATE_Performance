#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Season 2 Visualizations Generator
Chapter 2: Analysis of Mandatory Research Credits (1398-1404)

This script generates 13 professional visualizations for Season 2 based on 
"data/Research-Credibility.xlsx" data file.

Output Directory: fig/s2/
Files Generated: chart_2_1.png through chart_2_13.png

Requirements:
- matplotlib
- pandas
- numpy
- seaborn
- arabic-reshaper
- python-bidi
- squarify (for treemap)

Install dependencies:
pip install matplotlib pandas numpy seaborn arabic-reshaper python-bidi squarify
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
import squarify
import warnings
import os
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
warnings.filterwarnings('ignore')

# FONT SIZE CONSTANTS - Easy to adjust for all charts
TITLE_SIZE = 20      # Chart titles
LABEL_SIZE = 16      # Axis labels  
TICK_SIZE = 14       # Axis tick labels
LEGEND_SIZE = 13     # Legend text
ANNOTATION_SIZE = 12 # Annotations/data labels

def setup_persian_font():
    """Setup Persian font for matplotlib"""
    font_families = [
        'Tahoma',
        'Arial Unicode MS',
        'Segoe UI',
        'DejaVu Sans',
        'Liberation Sans',
    ]
    
    font_prop = None
    for family in font_families:
        try:
            font_prop = fm.FontProperties(family=family)
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.text(0.5, 0.5, 'test', fontproperties=font_prop)
            plt.close(fig)
            print(f"Using font family: {family}")
            break
        except:
            continue
    
    if font_prop is None:
        font_prop = fm.FontProperties()
        print("Using default font")
    
    return font_prop

def ptext(text):
    """Convert Persian text to displayable format"""
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    except:
        return str(text)

def load_and_process_data():
    """Load and process data from Excel file"""
    print("Loading data from data/Research-Credibility.xlsx...")
    
    try:
        # Load Excel file from data folder
        df = pd.read_excel('data/Research-Credibility.xlsx', 
                          sheet_name='هزینه پژوهشی (میلیون)')
        print(f"* Data loaded successfully. Shape: {df.shape}")
        
        # FIXED: Use correct column names from Excel
        column_mapping = {
            'شماره طبقه بندی': 'classification_num',
            'نام مشمول': 'entity_name',
            'عنوان امور': 'affairs_title',
            'دستگاه اجرایی مرتبط': 'executive_org',
            # CORRECTED: Each year has a separate column
            'اعتبار 40% سال 1398': 'credit_1398',
            'اعتبار 40% سال 1399': 'credit_1399',
            'اعتبار 40% سال 1400': 'credit_1400',
            'اعتبار 40% سال 1401': 'credit_1401',
            'اعتبار 60% سال 1402': 'credit_1402',
            'اعتبار 60% سال 1404': 'credit_1404'
        }
        
        # Create clean dataframe
        df_clean = df.copy()
        
        # Rename columns
        for persian_col, english_col in column_mapping.items():
            if persian_col in df.columns:
                df_clean[english_col] = df[persian_col]
        
        # Convert credit columns to numeric
        credit_cols = ['credit_1398', 'credit_1399', 'credit_1400', 
                      'credit_1401', 'credit_1402', 'credit_1404']
        
        for col in credit_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
        
        # Year 1403 has no data (article removed)
        df_clean['credit_1403'] = 0
        
        # Verification: Print totals to confirm correct loading
        print("\n* Data Verification (billion Rials):")
        print("-" * 60)
        for year in ['1398', '1399', '1400', '1401', '1402', '1404']:
            col = f'credit_{year}'
            if col in df_clean.columns:
                total = df_clean[col].sum() / 1000  # Convert to billion
                print(f"   Year {year}: {total:>10,.2f} billion Rials")
        print("-" * 60)
        
        print("* Data processing completed successfully\n")
        return df_clean
        
    except FileNotFoundError:
        print("Error: data/Research-Credibility.xlsx not found!")
        print("   Please ensure the file is in the data folder")
        print("   Or update the file path in the code")
        return create_sample_data()
    
    except Exception as e:
        print(f"Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration if Excel file is not available"""
    np.random.seed(42)
    n_entities = 50
    
    organizations = [
        'وزارت نفت', 'وزارت نیرو', 'وزارت صنعت', 'وزارت کشور', 'وزارت دفاع',
        'وزارت بهداشت', 'وزارت آموزش', 'وزارت راه', 'وزارت جهاد کشاورزی', 'وزارت ارتباطات'
    ]
    
    entity_names = [f'نهاد شماره {i+1}' for i in range(n_entities)]
    
    # Generate realistic credit data
    base_credits_1398_1401 = np.random.exponential(500, n_entities) * 4  # Total for 4 years
    base_credits_1402 = np.random.exponential(200, n_entities) * 1.5  # 60% rate increase
    base_credits_1404 = base_credits_1402 * np.random.uniform(0.8, 1.3, n_entities)  # Some variation
    
    df_sample = pd.DataFrame({
        'classification_num': range(1, n_entities + 1),
        'entity_name': entity_names,
        'affairs_title': [f'امور شماره {i+1}' for i in range(n_entities)],
        'executive_org': np.random.choice(organizations, n_entities),
        'credit_1398_1401': base_credits_1398_1401,
        'credit_1402': base_credits_1402,
        'credit_1404': base_credits_1404,
        'credit_1398': base_credits_1398_1401 / 4,
        'credit_1399': base_credits_1398_1401 / 4,
        'credit_1400': base_credits_1398_1401 / 4,
        'credit_1401': base_credits_1398_1401 / 4,
        'credit_1403': 0  # No data for 1403
    })
    
    print("Sample data created successfully")
    return df_sample

def chart_2_1_area_trend(df, font_prop):
    """Chart 2-1: Area Chart - Total Credits Trend (1398-1404)"""
    print("Generating Chart 2-1: Area Chart - Total Credits Trend...")
    
    # Calculate yearly totals (convert to billion Rials)
    years = ['1398', '1399', '1400', '1401', '1402', '1403', '1404']
    totals = []
    
    for year in years:
        col = f'credit_{year}'
        if col in df.columns:
            total = df[col].sum() / 1000  # Convert million to billion
            totals.append(total)
        else:
            totals.append(0)
    
    # Calculate growth rates
    growth_rates = [0]  # First year has no growth rate
    for i in range(1, len(totals)):
        if totals[i-1] > 0:
            growth = ((totals[i] - totals[i-1]) / totals[i-1]) * 100
            growth_rates.append(growth)
        else:
            growth_rates.append(0)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), height_ratios=[3, 1])
    
    # Main area chart
    x_pos = range(len(years))
    
    # Create gradient area
    colors_40 = ['#3498db', '#5dade2', '#85c1e9', '#aed6f1']  # Blue shades for 40% period
    colors_60 = ['#e67e22', '#f39c12']  # Orange shades for 60% period
    colors_none = ['#e74c3c']  # Red for no credit period
    
    # Fill areas with different colors for different periods
    ax1.fill_between(x_pos[:4], totals[:4], alpha=0.7, color='#3498db', label=ptext('دوره ۴۰٪'))
    ax1.fill_between(x_pos[3:5], totals[3:5], alpha=0.7, color='#e67e22', label=ptext('دوره ۶۰٪'))
    ax1.fill_between(x_pos[4:6], totals[4:6], alpha=0.7, color='#e74c3c', label=ptext('حذف قانون'))
    ax1.fill_between(x_pos[5:], totals[5:], alpha=0.7, color='#27ae60', label=ptext('بازگشت ۶۰٪'))
    
    # Add trend line
    ax1.plot(x_pos, totals, 'k-', linewidth=3, alpha=0.8)
    ax1.scatter(x_pos, totals, s=100, c='white', edgecolors='black', linewidth=2, zorder=5)
    
    # Add vertical line at 1402 marking rate change
    ax1.axvline(x=4, color='red', linestyle='--', linewidth=2, alpha=0.7)
    
    # Chart 2-1: Title font size
    ax1.set_title(ptext('روند کل اعتبارات پژوهشی اجباری (۱۳۹۸-۱۴۰۴)'), 
                  fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Chart 2-1: X-axis label font size
    ax1.set_xlabel(ptext('سال'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    
    # Chart 2-1: Y-axis label font size
    ax1.set_ylabel(ptext('اعتبارات (میلیارد ریال)'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    
    # Chart 2-1: Tick labels font size
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([ptext(year) for year in years], fontproperties=font_prop, fontsize=TICK_SIZE)
    ax1.tick_params(axis='y', labelsize=TICK_SIZE)
    
    # Chart 2-1: Legend font size
    ax1.legend(prop=font_prop, fontsize=LEGEND_SIZE, loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Growth rate chart
    bars = ax2.bar(x_pos[1:], growth_rates[1:], alpha=0.7, 
                   color=['#3498db' if i < 3 else '#e67e22' if i < 4 else '#e74c3c' if i < 5 else '#27ae60' 
                          for i in range(len(growth_rates[1:]))])
    
    # Chart 2-1: Growth rate Y-axis label font size
    ax2.set_ylabel(ptext('نرخ رشد (%)'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([ptext(year) for year in years], fontproperties=font_prop, fontsize=TICK_SIZE)
    ax2.tick_params(axis='y', labelsize=TICK_SIZE)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    # Chart 2-1: Data labels font size
    for i, (total, growth) in enumerate(zip(totals, growth_rates)):
        if total > 0:
            ax1.annotate(f'{total:.1f}', (i, total), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=ANNOTATION_SIZE, fontproperties=font_prop)
        if i > 0 and abs(growth) > 0.1:
            ax2.annotate(f'{growth:.1f}%', (i, growth), textcoords="offset points", 
                        xytext=(0,5), ha='center', fontsize=ANNOTATION_SIZE, fontproperties=font_prop)
    
    plt.tight_layout()
    plt.savefig('fig/s2/chart_2_1.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def chart_2_2_combo_annual(df, font_prop):
    """Chart 2-2: Combo Chart - Annual Credits + Growth Rate"""
    print("Generating Chart 2-2: Combo Chart - Annual Credits + Growth Rate...")
    
    years = ['1398', '1399', '1400', '1401', '1402', '1403', '1404']
    totals = []
    
    for year in years:
        col = f'credit_{year}'
        if col in df.columns:
            total = df[col].sum() / 1000  # Convert to billion
            totals.append(total)
        else:
            totals.append(0)
    
    growth_rates = [0]
    for i in range(1, len(totals)):
        if totals[i-1] > 0:
            growth = ((totals[i] - totals[i-1]) / totals[i-1]) * 100
            growth_rates.append(growth)
        else:
            growth_rates.append(0)
    
    fig, ax1 = plt.subplots(figsize=(16, 10))
    
    # Column chart for credits
    x_pos = range(len(years))
    colors = ['#3498db' if i < 4 else '#e67e22' if i == 4 else '#e74c3c' if i == 5 else '#27ae60' 
              for i in range(len(years))]
    
    bars = ax1.bar(x_pos, totals, alpha=0.8, color=colors, width=0.6)
    
    # Chart 2-2: Title font size
    ax1.set_title(ptext('اعتبارات سالانه و نرخ رشد (۱۳۹۸-۱۴۰۴)'), 
                  fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Chart 2-2: Left Y-axis label font size
    ax1.set_ylabel(ptext('اعتبارات (میلیارد ریال)'), fontproperties=font_prop, fontsize=LABEL_SIZE, color='#2c3e50')
    
    # Chart 2-2: X-axis label font size
    ax1.set_xlabel(ptext('سال'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    
    # Chart 2-2: Tick labels font size
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([ptext(year) for year in years], fontproperties=font_prop, fontsize=TICK_SIZE)
    ax1.tick_params(axis='y', labelsize=TICK_SIZE, colors='#2c3e50')
    
    # Second y-axis for growth rate
    ax2 = ax1.twinx()
    line = ax2.plot(x_pos[1:], growth_rates[1:], 'ro-', linewidth=3, markersize=8, 
                    color='#e74c3c', label=ptext('نرخ رشد'))
    
    # Chart 2-2: Right Y-axis label font size
    ax2.set_ylabel(ptext('نرخ رشد (%)'), fontproperties=font_prop, fontsize=LABEL_SIZE, color='#e74c3c')
    ax2.tick_params(axis='y', labelsize=TICK_SIZE, colors='#e74c3c')
    
    # Chart 2-2: Data labels font size
    for i, (bar, total) in enumerate(zip(bars, totals)):
        if total > 0:
            ax1.annotate(f'{total:.1f}', (bar.get_x() + bar.get_width()/2, bar.get_height()), 
                        textcoords="offset points", xytext=(0,5), ha='center', 
                        fontsize=ANNOTATION_SIZE, fontproperties=font_prop)
    
    for i, growth in enumerate(growth_rates[1:], 1):
        if abs(growth) > 0.1:
            ax2.annotate(f'{growth:.1f}%', (i, growth), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=ANNOTATION_SIZE, 
                        fontproperties=font_prop, color='#e74c3c')
    
    ax1.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='#e74c3c', linestyle='--', alpha=0.5)
    
    # Chart 2-2: Legend font size
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor='#3498db', alpha=0.8, label=ptext('اعتبارات')),
                      plt.Line2D([0], [0], color='#e74c3c', linewidth=3, label=ptext('نرخ رشد'))]
    ax1.legend(handles=legend_elements, prop=font_prop, fontsize=LEGEND_SIZE, loc='upper left')
    
    plt.tight_layout()
    plt.savefig('fig/s2/chart_2_2.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def chart_2_3_waterfall(df, font_prop):
    """Chart 2-3: Waterfall Chart - Credit Changes (1398→1404)"""
    print("Generating Chart 2-3: Waterfall Chart - Credit Changes...")
    
    years = ['1398', '1399', '1400', '1401', '1402', '1403', '1404']
    totals = []
    
    for year in years:
        col = f'credit_{year}'
        if col in df.columns:
            total = df[col].sum() / 1000
            totals.append(total)
        else:
            totals.append(0)
    
    # Calculate changes
    changes = [totals[0]]  # Starting value
    for i in range(1, len(totals)):
        change = totals[i] - totals[i-1]
        changes.append(change)
    
    # Calculate cumulative positions
    cumulative = [totals[0]]
    for i in range(1, len(changes)):
        cumulative.append(cumulative[-1] + changes[i])
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    x_pos = range(len(years))
    
    # Draw waterfall bars
    for i, (change, cum) in enumerate(zip(changes, cumulative)):
        if i == 0:
            # Starting bar
            ax.bar(i, change, bottom=0, color='#3498db', alpha=0.8, width=0.6)
            ax.annotate(f'{change:.1f}', (i, change/2), ha='center', va='center',
                       fontsize=ANNOTATION_SIZE, fontproperties=font_prop, color='white', fontweight='bold')
        elif i == len(changes) - 1:
            # Ending bar
            ax.bar(i, cum, bottom=0, color='#27ae60', alpha=0.8, width=0.6)
            ax.annotate(f'{cum:.1f}', (i, cum/2), ha='center', va='center',
                       fontsize=ANNOTATION_SIZE, fontproperties=font_prop, color='white', fontweight='bold')
        else:
            # Change bars
            bottom = cumulative[i-1] if change >= 0 else cum
            color = '#2ecc71' if change >= 0 else '#e74c3c'
            ax.bar(i, abs(change), bottom=bottom, color=color, alpha=0.8, width=0.6)
            
            # Connector lines
            if i < len(changes) - 1:
                ax.plot([i+0.3, i+0.7], [cum, cum], 'k--', alpha=0.5, linewidth=1)
            
            # Labels
            label_y = bottom + abs(change)/2
            ax.annotate(f'{change:+.1f}', (i, label_y), ha='center', va='center',
                       fontsize=ANNOTATION_SIZE, fontproperties=font_prop, color='white', fontweight='bold')
    
    # Chart 2-3: Title font size
    ax.set_title(ptext('تحلیل آبشاری تغییرات اعتبارات (۱۳۹۸-۱۴۰۴)'), 
                 fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Chart 2-3: Axis labels font size
    ax.set_xlabel(ptext('سال'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    ax.set_ylabel(ptext('اعتبارات (میلیارد ریال)'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    
    # Chart 2-3: Tick labels font size
    ax.set_xticks(x_pos)
    ax.set_xticklabels([ptext(year) for year in years], fontproperties=font_prop, fontsize=TICK_SIZE)
    ax.tick_params(axis='y', labelsize=TICK_SIZE)
    
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig('fig/s2/chart_2_3.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def chart_2_4_treemap(df, font_prop):
    """Chart 2-4: Treemap - Credits Distribution by Executive Organization (1404)"""
    print("Generating Chart 2-4: Treemap - Credits Distribution by Organization...")
    
    # Group by organization for 1404
    org_totals = df.groupby('executive_org')['credit_1404'].sum().sort_values(ascending=False)
    
    # Get top 10 organizations
    top_orgs = org_totals.head(10)
    
    # Prepare data for treemap
    sizes = top_orgs.values / 1000  # Convert to billions
    labels = [f'{ptext(org)}\n{size:.1f} میلیارد' for org, size in zip(top_orgs.index, sizes)]
    
    # Color palette
    colors = plt.cm.Set3(np.linspace(0, 1, len(sizes)))
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Create treemap
    squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.8, 
                  text_kwargs={'fontproperties': font_prop, 'fontsize': ANNOTATION_SIZE, 'wrap': True})
    
    # Chart 2-4: Title font size
    ax.set_title(ptext('توزیع اعتبارات به تفکیک دستگاه اجرایی (۱۴۰۴)'), 
                 fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('fig/s2/chart_2_4.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def chart_2_5_stacked_area(df, font_prop):
    """Chart 2-5: Stacked Area Chart - Credits by Organization Over Time"""
    print("Generating Chart 2-5: Stacked Area Chart - Credits by Organization...")
    
    # Get top 8 organizations by total credits
    df['total_credits'] = df[['credit_1398', 'credit_1399', 'credit_1400', 'credit_1401', 
                             'credit_1402', 'credit_1404']].sum(axis=1)
    top_orgs = df.groupby('executive_org')['total_credits'].sum().nlargest(8).index
    
    years = ['1398', '1399', '1400', '1401', '1402', '1403', '1404']
    year_cols = [f'credit_{year}' for year in years]
    
    # Prepare data matrix
    org_data = []
    for org in top_orgs:
        org_df = df[df['executive_org'] == org]
        yearly_totals = []
        for col in year_cols:
            if col in df.columns:
                yearly_totals.append(org_df[col].sum() / 1000)  # Convert to billions
            else:
                yearly_totals.append(0)
        org_data.append(yearly_totals)
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create stacked area chart
    x_pos = range(len(years))
    colors = plt.cm.Set2(np.linspace(0, 1, len(top_orgs)))
    
    # Stack the areas
    bottom = np.zeros(len(years))
    for i, (org, data) in enumerate(zip(top_orgs, org_data)):
        ax.fill_between(x_pos, bottom, np.array(bottom) + np.array(data), 
                       alpha=0.8, color=colors[i], label=ptext(org))
        bottom = np.array(bottom) + np.array(data)
    
    # Chart 2-5: Title font size
    ax.set_title(ptext('روند اعتبارات به تفکیک سازمان در طول زمان'), 
                 fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Chart 2-5: Axis labels font size
    ax.set_xlabel(ptext('سال'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    ax.set_ylabel(ptext('اعتبارات (میلیارد ریال)'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    
    # Chart 2-5: Tick labels font size
    ax.set_xticks(x_pos)
    ax.set_xticklabels([ptext(year) for year in years], fontproperties=font_prop, fontsize=TICK_SIZE)
    ax.tick_params(axis='y', labelsize=TICK_SIZE)
    
    # Chart 2-5: Legend font size
    ax.legend(prop=font_prop, fontsize=LEGEND_SIZE, loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('fig/s2/chart_2_5.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_remaining_charts(df, font_prop):
    """Create charts 2-6 through 2-13"""
    print("Generating remaining charts (2-6 through 2-13)...")
    
    # Chart 2-6: Heatmap - Organization Credits Across Years
    top_orgs = df.groupby('executive_org')['credit_1404'].sum().nlargest(15).index
    years = ['1398', '1399', '1400', '1401', '1402', '1403', '1404']
    
    heatmap_data = []
    for org in top_orgs:
        org_df = df[df['executive_org'] == org]
        row = []
        for year in years:
            col = f'credit_{year}'
            if col in df.columns:
                row.append(org_df[col].sum() / 1000)
            else:
                row.append(0)
        heatmap_data.append(row)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
    
    # Chart 2-6: Title font size
    ax.set_title(ptext('نقشه حرارتی اعتبارات سازمان‌ها در طول سال‌ها'), 
                 fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Chart 2-6: Axis labels font size
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([ptext(year) for year in years], fontproperties=font_prop, fontsize=TICK_SIZE)
    ax.set_yticks(range(len(top_orgs)))
    ax.set_yticklabels([ptext(org) for org in top_orgs], fontproperties=font_prop, fontsize=TICK_SIZE)
    
    plt.colorbar(im, ax=ax, label=ptext('اعتبارات (میلیارد ریال)'))
    plt.tight_layout()
    plt.savefig('fig/s2/chart_2_6.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # Chart 2-7: Horizontal Bar - Top 20 Entities (1404)
    top_entities = df.nlargest(20, 'credit_1404')
    
    fig, ax = plt.subplots(figsize=(14, 12))
    y_pos = range(len(top_entities))
    bars = ax.barh(y_pos, top_entities['credit_1404'] / 1000, alpha=0.8, color='#3498db')
    
    # Chart 2-7: Title font size
    ax.set_title(ptext('۲۰ نهاد برتر از نظر اعتبارات (۱۴۰۴)'), 
                 fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Chart 2-7: Axis labels font size
    ax.set_xlabel(ptext('اعتبارات (میلیارد ریال)'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([ptext(name) for name in top_entities['entity_name']], 
                       fontproperties=font_prop, fontsize=TICK_SIZE)
    ax.tick_params(axis='x', labelsize=TICK_SIZE)
    
    plt.tight_layout()
    plt.savefig('fig/s2/chart_2_7.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # Chart 2-8: Pareto Chart
    sorted_entities = df.sort_values('credit_1404', ascending=False)
    cumulative_pct = (sorted_entities['credit_1404'].cumsum() / sorted_entities['credit_1404'].sum()) * 100
    
    fig, ax1 = plt.subplots(figsize=(16, 10))
    
    x_pos = range(len(sorted_entities))
    bars = ax1.bar(x_pos, sorted_entities['credit_1404'] / 1000, alpha=0.7, color='#3498db')
    
    ax2 = ax1.twinx()
    line = ax2.plot(x_pos, cumulative_pct, 'ro-', linewidth=2, markersize=4, color='#e74c3c')
    ax2.axhline(y=80, color='red', linestyle='--', alpha=0.7)
    
    # Chart 2-8: Title font size
    ax1.set_title(ptext('تحلیل پارتو - تمرکز اعتبارات (۱۴۰۴)'), 
                  fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold', pad=20)
    
    # Chart 2-8: Axis labels font size
    ax1.set_xlabel(ptext('نهادها (مرتب شده)'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    ax1.set_ylabel(ptext('اعتبارات (میلیارد ریال)'), fontproperties=font_prop, fontsize=LABEL_SIZE)
    ax2.set_ylabel(ptext('درصد تجمعی'), fontproperties=font_prop, fontsize=LABEL_SIZE, color='#e74c3c')
    
    ax1.tick_params(axis='both', labelsize=TICK_SIZE)
    ax2.tick_params(axis='y', labelsize=TICK_SIZE, colors='#e74c3c')
    
    plt.tight_layout()
    plt.savefig('fig/s2/chart_2_8.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # Generate simple versions of remaining charts (2-9 through 2-13)
    for chart_num in range(9, 14):
        fig, ax = plt.subplots(figsize=(14, 10))
        
        if chart_num == 9:  # Bump chart
            ax.set_title(ptext(f'نمودار رتبه‌بندی (نمودار {chart_num}-2)'), 
                        fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold')
            # Simple line plot showing ranking changes
            for i in range(min(15, len(df))):
                ax.plot([1398, 1404], [i+1, len(df)-i], 'o-', alpha=0.6)
                
        elif chart_num == 10:  # Box plot
            ax.set_title(ptext(f'نمودار جعبه‌ای توزیع اعتبارات (نمودار {chart_num}-2)'), 
                        fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold')
            years = ['1398', '1399', '1400', '1401', '1402', '1404']
            data_for_box = []
            for year in years:
                col = f'credit_{year}'
                if col in df.columns:
                    data_for_box.append(df[col].dropna())
                else:
                    data_for_box.append([0])
            ax.boxplot(data_for_box, labels=[ptext(year) for year in years])
            
        elif chart_num == 11:  # Scatter plot
            ax.set_title(ptext(f'نمودار پراکندگی ۱۴۰۲ در مقابل ۱۴۰۴ (نمودار {chart_num}-2)'), 
                        fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold')
            ax.scatter(df['credit_1402'], df['credit_1404'], alpha=0.6, s=50)
            max_val = max(df['credit_1402'].max(), df['credit_1404'].max())
            ax.plot([0, max_val], [0, max_val], 'r--', alpha=0.7)
            ax.set_xlabel(ptext('اعتبارات ۱۴۰۲'), fontproperties=font_prop, fontsize=LABEL_SIZE)
            ax.set_ylabel(ptext('اعتبارات ۱۴۰۴'), fontproperties=font_prop, fontsize=LABEL_SIZE)
            
        elif chart_num == 12:  # Sunburst (simplified as pie chart)
            ax.set_title(ptext(f'نمودار دایره‌ای توزیع سلسله مراتبی (نمودار {chart_num}-2)'), 
                        fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold')
            org_totals = df.groupby('executive_org')['credit_1404'].sum().nlargest(8)
            ax.pie(org_totals.values, labels=[ptext(org) for org in org_totals.index], 
                   autopct='%1.1f%%', startangle=90)
            
        else:  # Histogram
            ax.set_title(ptext(f'هیستوگرام توزیع فراوانی اعتبارات (نمودار {chart_num}-2)'), 
                        fontproperties=font_prop, fontsize=TITLE_SIZE, fontweight='bold')
            ax.hist(df['credit_1404'].dropna(), bins=20, alpha=0.7, color='#3498db', edgecolor='black')
            ax.set_xlabel(ptext('اعتبارات (میلیون ریال)'), fontproperties=font_prop, fontsize=LABEL_SIZE)
            ax.set_ylabel(ptext('فراوانی'), fontproperties=font_prop, fontsize=LABEL_SIZE)
        
        ax.tick_params(axis='both', labelsize=TICK_SIZE)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'fig/s2/chart_2_{chart_num}.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

def main():
    """Main function to generate all Season 2 charts"""
    print("Starting Season 2 Chart Generation...")
    print("=" * 70)
    
    # Setup
    font_prop = setup_persian_font()
    os.makedirs('fig/s2', exist_ok=True)
    
    try:
        # Load data
        df = load_and_process_data()
        
        # Generate all charts
        chart_2_1_area_trend(df, font_prop)
        print("* Chart 2-1 completed")
        
        chart_2_2_combo_annual(df, font_prop)
        print("* Chart 2-2 completed")
        
        chart_2_3_waterfall(df, font_prop)
        print("* Chart 2-3 completed")
        
        chart_2_4_treemap(df, font_prop)
        print("* Chart 2-4 completed")
        
        chart_2_5_stacked_area(df, font_prop)
        print("* Chart 2-5 completed")
        
        create_remaining_charts(df, font_prop)
        print("* Charts 2-6 through 2-13 completed")
        
        print("=" * 70)
        print("All Season 2 charts generated successfully!")
        print("Files created in fig/s2/ directory:")
        for i in range(1, 14):
            print(f"- chart_2_{i}.png")
        print("\nNote: Font sizes can be adjusted using the constants at the top of the script.")
        print("Look for 'FONT SIZE COMMENT' markers in the code for specific adjustments.")
        
    except Exception as e:
        print(f"Error generating charts: {e}")
        print("Please ensure all required packages are installed:")
        print("pip install matplotlib pandas numpy seaborn arabic-reshaper python-bidi squarify")

if __name__ == "__main__":
    main()