#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Season 1 Visualizations Generator
Legal Framework and Introduction - Mandatory Research Credits in Iran

This script generates two professional visualizations for Season 1:
1. Chart 1-1: Timeline of Legal Developments (1397-1404)
2. Chart 1-2: Process Flowchart - SATC System Implementation Stages

Output Directory: fig/s1/
Files Generated:
- fig/s1/chart_1_1.png
- fig/s1/chart_1_2.png

Requirements:
- matplotlib
- numpy
- arabic-reshaper
- python-bidi

Install dependencies:
pip install matplotlib numpy arabic-reshaper python-bidi
"""

import matplotlib.pyplot as plt
import numpy as np
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import warnings
import os
warnings.filterwarnings('ignore')

def setup_persian_font():
    """
    Setup Persian font for matplotlib
    Tries multiple font sources for better compatibility
    """
    # Try different font families available on Windows
    font_families = [
        'Tahoma',  # Windows Persian support
        'Arial Unicode MS',  # Windows fallback
        'Segoe UI',  # Windows modern
        'DejaVu Sans',  # Cross-platform
        'Liberation Sans',  # Cross-platform
    ]
    
    font_prop = None
    for family in font_families:
        try:
            font_prop = fm.FontProperties(family=family)
            # Test if font works with a simple figure
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.text(0.5, 0.5, 'test', fontproperties=font_prop)
            plt.close(fig)
            print(f"Using font family: {family}")
            break
        except Exception as e:
            continue
    
    if font_prop is None:
        # Final fallback to default font
        font_prop = fm.FontProperties()
        print("Using default font (Persian text may not display correctly)")
    
    return font_prop

def persian_text(text):
    """
    Convert Persian text to displayable format with proper RTL handling
    """
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    except:
        # Fallback if reshaping fails
        return text

def create_timeline_chart():
    """
    Create Chart 1-1: Timeline of Legal Developments (1397-1404)
    """
    print("Generating Chart 1-1: Timeline of Legal Developments...")
    
    # Setup font
    font_prop = setup_persian_font()
    
    # Timeline data
    timeline_data = [
        {'year': 1397, 'event': 'آغاز اجرای قانون', 'color': '#3498db', 'position': 0},
        {'year': 1398, 'event': 'شروع دوره ۴۰٪', 'color': '#2ecc71', 'position': 1},
        {'year': 1399, 'event': 'ادامه دوره ۴۰٪', 'color': '#2ecc71', 'position': 2},
        {'year': 1400, 'event': 'ادامه دوره ۴۰٪', 'color': '#2ecc71', 'position': 3},
        {'year': 1401, 'event': 'پایان دوره ۴۰٪', 'color': '#2ecc71', 'position': 4},
        {'year': 1402, 'event': 'افزایش به ۶۰٪', 'color': '#e67e22', 'position': 5},
        {'year': 1403, 'event': 'حذف بند قانونی', 'color': '#e74c3c', 'position': 6},
        {'year': 1404, 'event': 'بازگشت با نرخ ۶۰٪', 'color': '#27ae60', 'position': 7}
    ]
    
    # Create figure and axis with larger size for better readability
    fig, ax = plt.subplots(figsize=(18, 12))  # Increased figure size
    
    # Timeline configuration
    y_timeline = 0.5
    x_positions = np.linspace(0.1, 0.9, len(timeline_data))
    
    # Draw main timeline line with increased thickness
    ax.plot([0.05, 0.95], [y_timeline, y_timeline], 'k-', linewidth=4, alpha=0.4)
    
    # Add background periods
    periods = [
        {'start': 0, 'end': 1, 'color': '#3498db', 'alpha': 0.1, 'label': 'آغاز اجرا'},
        {'start': 1, 'end': 5, 'color': '#2ecc71', 'alpha': 0.1, 'label': 'دوره ۴۰٪'},
        {'start': 5, 'end': 6, 'color': '#e67e22', 'alpha': 0.1, 'label': 'دوره ۶۰٪'},
        {'start': 6, 'end': 7, 'color': '#e74c3c', 'alpha': 0.1, 'label': 'حذف قانون'},
        {'start': 7, 'end': 8, 'color': '#27ae60', 'alpha': 0.1, 'label': 'بازگشت ۶۰٪'}
    ]
    
    for period in periods:
        if period['end'] > period['start']:
            start_x = x_positions[period['start']] if period['start'] < len(x_positions) else x_positions[-1]
            end_x = x_positions[period['end']-1] if period['end']-1 < len(x_positions) else x_positions[-1]
            if period['end'] < len(x_positions):
                end_x = x_positions[period['end']]
            ax.axvspan(start_x - 0.03, end_x + 0.03, alpha=period['alpha'], 
                      color=period['color'], zorder=0)
    
    # Plot timeline points and labels
    for i, data in enumerate(timeline_data):
        x_pos = x_positions[i]
        color = data['color']
        
        # Draw timeline marker with larger size
        ax.plot(x_pos, y_timeline, 'o', markersize=20, color=color,  # Increased marker size
                markeredgecolor='white', markeredgewidth=3, zorder=3)
        
        # Add year label below timeline - FONT SIZE COMMENT: Year numbers below timeline
        ax.text(x_pos, y_timeline - 0.15, str(data['year']), 
                ha='center', va='top', fontsize=18, fontweight='bold',  # Increased font size for years
                fontproperties=font_prop)
        
        # Add event label above timeline - FONT SIZE COMMENT: Event text labels above timeline
        y_text = y_timeline + 0.15 + (0.1 if i % 2 == 0 else 0.05)
        ax.text(x_pos, y_text, persian_text(data['event']), 
                ha='center', va='bottom', fontsize=14,  # Increased font size for event labels
                fontproperties=font_prop, bbox=dict(boxstyle="round,pad=0.4", 
                facecolor=color, alpha=0.2, edgecolor=color))
        
        # Draw connection line from marker to text with increased thickness
        ax.plot([x_pos, x_pos], [y_timeline + 0.02, y_text - 0.02], 
                color=color, linewidth=2, alpha=0.7, zorder=1)
    
    # Create legend with larger markers and text
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498db', 
               markersize=15, label=persian_text('آغاز اجرا')),  # Increased legend marker size
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ecc71', 
               markersize=15, label=persian_text('دوره ۴۰٪')),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#e67e22', 
               markersize=15, label=persian_text('افزایش به ۶۰٪')),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', 
               markersize=15, label=persian_text('حذف قانون')),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#27ae60', 
               markersize=15, label=persian_text('بازگشت ۶۰٪'))
    ]
    
    # FONT SIZE COMMENT: Legend text
    ax.legend(handles=legend_elements, loc='upper right', fontsize=14,  # Increased legend font size
              prop=font_prop, frameon=True, fancybox=True, shadow=True)
    
    # FONT SIZE COMMENT: Main chart title
    ax.set_title(persian_text('روند تحولات قانونی اعتبارات پژوهشی اجباری (۱۳۹۷-۱۴۰۴)'), 
                fontsize=22, fontweight='bold', fontproperties=font_prop, pad=25)  # Increased title font size
    
    # FONT SIZE COMMENT: X-axis label
    ax.set_xlabel(persian_text('سال‌های تقویمی'), fontproperties=font_prop, 
                 fontsize=18, fontweight='bold')  # Increased axis label font size
    
    # Configure axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add grid with better visibility
    ax.grid(True, alpha=0.4, linestyle='--', axis='x')
    
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs('fig/s1', exist_ok=True)
    
    # Save to season 1 directory
    plt.savefig('fig/s1/chart_1_1.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("Chart 1-1 saved as 'fig/s1/chart_1_1.png'")

def create_flowchart():
    """
    Create Chart 1-2: Process Flowchart - SATC System Implementation Stages
    """
    print("Generating Chart 1-2: Process Flowchart...")
    
    # Setup font
    font_prop = setup_persian_font()
    
    # Flowchart stages data
    stages = [
        {'step': 1, 'text': 'ثبت نیاز پژوهشی توسط مشمول', 'role': 'entity'},
        {'step': 2, 'text': 'انتشار فراخوان در سامانه ساتع', 'role': 'system'},
        {'step': 3, 'text': 'ارسال پیشنهادات توسط دانشگاه‌ها', 'role': 'university'},
        {'step': 4, 'text': 'داوری و انتخاب مجری', 'role': 'system'},
        {'step': 5, 'text': 'انعقاد قرارداد پژوهشی', 'role': 'system'},
        {'step': 6, 'text': 'اجرای طرح و گزارش پیشرفت', 'role': 'university'},
        {'step': 7, 'text': 'تأیید گزارش توسط مشمول', 'role': 'entity'},
        {'step': 8, 'text': 'پرداخت از طریق سامانه', 'role': 'system'}
    ]
    
    # Role colors
    role_colors = {
        'entity': '#3498db',      # Blue for obligated entities
        'university': '#2ecc71',  # Green for universities
        'system': '#95a5a6'       # Gray for system
    }
    
    role_labels = {
        'entity': 'مراحل مربوط به نهادهای مشمول',
        'university': 'مراحل مربوط به دانشگاه‌ها و مجریان',
        'system': 'مراحل سامانه‌ای'
    }
    
    # Create figure and axis with larger size
    fig, ax = plt.subplots(figsize=(14, 18))  # Increased figure size
    
    # Box dimensions - made larger for better text visibility
    box_width = 0.65  # Increased box width
    box_height = 0.09  # Increased box height
    y_spacing = 0.13  # Increased spacing
    start_y = 0.9
    
    # Draw flowchart boxes and arrows
    for i, stage in enumerate(stages):
        y_pos = start_y - i * y_spacing
        x_pos = 0.5
        
        # Create rounded rectangle for each stage
        box = FancyBboxPatch(
            (x_pos - box_width/2, y_pos - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.015",  # Increased padding
            facecolor=role_colors[stage['role']],
            edgecolor='white',
            linewidth=3,  # Increased border thickness
            alpha=0.85
        )
        ax.add_patch(box)
        
        # FONT SIZE COMMENT: Step numbers inside flowchart boxes
        ax.text(x_pos - box_width/2 + 0.06, y_pos, str(stage['step']), 
                ha='center', va='center', fontsize=18, fontweight='bold',  # Increased step number font size
                color='white', fontproperties=font_prop)
        
        # FONT SIZE COMMENT: Stage description text inside flowchart boxes
        ax.text(x_pos, y_pos, persian_text(stage['text']), 
                ha='center', va='center', fontsize=14, fontweight='bold',  # Increased stage text font size
                color='white', fontproperties=font_prop)
        
        # Add arrow to next stage (except for last stage) with increased thickness
        if i < len(stages) - 1:
            arrow = FancyArrowPatch(
                (x_pos, y_pos - box_height/2 - 0.01),
                (x_pos, y_pos - y_spacing + box_height/2 + 0.01),
                arrowstyle='-|>',
                shrinkA=0, shrinkB=0,
                color='#34495e',
                linewidth=4,  # Increased arrow thickness
                alpha=0.8
            )
            ax.add_patch(arrow)
    
    # Create legend with larger elements
    legend_elements = []
    for role, color in role_colors.items():
        legend_elements.append(
            mpatches.Rectangle((0, 0), 1, 1, facecolor=color, alpha=0.85,
                             label=persian_text(role_labels[role]))
        )
    
    # FONT SIZE COMMENT: Legend text for flowchart
    ax.legend(handles=legend_elements, loc='lower center', fontsize=13,  # Increased legend font size
              prop=font_prop, frameon=True, fancybox=True, shadow=True,
              bbox_to_anchor=(0.5, -0.05), ncol=1)
    
    # FONT SIZE COMMENT: Flowchart main title
    ax.set_title(persian_text('مراحل اجرایی سامانه ساتع (SATC)'), 
                fontsize=22, fontweight='bold', fontproperties=font_prop, pad=25)  # Increased title font size
    
    # Configure axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs('fig/s1', exist_ok=True)
    
    # Save to season 1 directory
    plt.savefig('fig/s1/chart_1_2.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("Chart 1-2 saved as 'fig/s1/chart_1_2.png'")

def main():
    """
    Main function to generate both charts for Season 1
    """
    print("Starting Season 1 Chart Generation...")
    print("=" * 60)
    
    try:
        # Generate Chart 1-1: Timeline
        create_timeline_chart()
        print("* Chart 1-1 completed successfully")
        
        # Generate Chart 1-2: Flowchart
        create_flowchart()
        print("* Chart 1-2 completed successfully")
        
        print("=" * 60)
        print("All Season 1 charts generated successfully!")
        print("Files created in fig/s1/ directory:")
        print("- chart_1_1.png (Timeline of Legal Developments)")
        print("- chart_1_2.png (Process Flowchart)")
        print("\nNote: All fonts have been increased for better readability.")
        print("Check the code comments marked with 'FONT SIZE COMMENT' to adjust specific font sizes.")
        
    except Exception as e:
        print(f"Error generating charts: {e}")
        print("Please ensure all required packages are installed:")
        print("pip install matplotlib numpy arabic-reshaper python-bidi")

if __name__ == "__main__":
    main()