"""
فصل اول: مقدمه و کلیات سامانه ساتع
تولید نمودارهای تحلیلی برای فصل اول گزارش
نسخه بهبود یافته با کیفیت بالا - DPI 400
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.sankey import Sankey
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# To show Farsi Font
import arabic_reshaper
from bidi.algorithm import get_display

# ==============================================================================
# Font Configuration for Persian (Farsi) Text
# ==============================================================================

# تنظیم فونت پیش‌فرض
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.autolayout'] = True

# ==============================================================================
# Helper function to convert Persian text to a displayable format
# ==============================================================================

def fix_persian_text(text):
    """
    تبدیل متن فارسی/عربی به فرمت قابل نمایش در matplotlib
    """
    if text is None or str(text).strip() == '':
        return ''
    
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"Warning: Could not reshape text '{text}': {e}")
        return str(text)

# ==============================================================================
# Helper function to convert English numbers to Persian
# ==============================================================================

def convert_to_persian_number(number):
    """تبدیل اعداد انگلیسی به اعداد فارسی"""
    english_digits = '0123456789.,%'
    persian_digits = '۰۱۲۳۴۵۶۷۸۹.،٪'
    translation_table = str.maketrans(english_digits, persian_digits)
    return str(number).translate(translation_table)

def format_number_with_separator(number, use_persian=True):
    """قالب‌بندی اعداد با جداکننده هزارگان"""
    formatted = f'{number:,.0f}' if isinstance(number, (int, float)) else str(number)
    if use_persian:
        return convert_to_persian_number(formatted)
    return formatted

# ==============================================================================
# Setup Output Directory
# ==============================================================================

output_dir = Path('./figs/s1')
output_dir.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory: {output_dir}")

# ==============================================================================
# Load Data
# ==============================================================================

print("\nLoading data...")
df_contracts = pd.read_excel('./data/Credits_Contracts.xlsx')
df_payments = pd.read_excel('./data/Credits_Payments.xlsx')

print(f"Contracts shape: {df_contracts.shape}")
print(f"Payments shape: {df_payments.shape}")

# محاسبات آماری
total_credits = df_contracts.groupby('نام مشمول')['اعتبار سال 1404'].first().sum()
total_contracts = df_contracts['مجموع مبالغ قراردادها'].sum()
total_payments = df_payments['مجموع مبالغ پرداختی'].sum()

# تبدیل به میلیارد ریال
total_credits_b = total_credits / 1000
total_contracts_b = total_contracts / 1000
total_payments_b = total_payments / 1000
not_contracted_b = total_credits_b - total_contracts_b
not_paid_b = total_contracts_b - total_payments_b

# محاسبه درصدها
contract_percentage = (total_contracts / total_credits) * 100
payment_percentage = (total_payments / total_credits) * 100
payment_to_contract_percentage = (total_payments / total_contracts) * 100

# هدف‌گذاری برای 6 ماهه (نصف اعتبار تکلیفی)
target_contract_percentage = 30.0  # 30% از کل اعتبار برای قرارداد در 6 ماه
target_payment_percentage = 20.0   # 20% از کل اعتبار برای پرداخت در 6 ماه
target_payment_from_contract = 67.0  # 67% از قراردادها باید پرداخت شود (20/30)

# آمار تکمیلی
unique_subjects = df_contracts.groupby('نام مشمول')['اعتبار سال 1404'].first().shape[0]
subjects_with_contracts = df_contracts['نام مشمول'].nunique()
unique_universities_contracts = df_contracts['دانشگاه'].nunique()
unique_universities_payments = df_payments['دانشگاه'].nunique()
total_contract_count = df_contracts.shape[0]
unique_departments = df_contracts['دستگاه اجرایی مرتبط'].nunique()

print("\n" + "="*70)
print("KEY STATISTICS")
print("="*70)
print(f"Total Credits: {total_credits_b:,.0f} billion Rials")
print(f"Total Contracts: {total_contracts_b:,.0f} billion Rials ({contract_percentage:.1f}%)")
print(f"Total Payments: {total_payments_b:,.0f} billion Rials ({payment_percentage:.1f}%)")
print(f"Contract Achievement Rate: {contract_percentage:.1f}% (Target: {target_contract_percentage}%)")
print(f"Payment Achievement Rate: {payment_percentage:.1f}% (Target: {target_payment_percentage}%)")
print(f"Payment from Contracts: {payment_to_contract_percentage:.1f}% (Target: {target_payment_from_contract:.0f}%)")
print("="*70 + "\n")

# ==============================================================================
# نمودار 1-1: Sankey-Style Flow Chart - جریان اعتبارات
# ==============================================================================
print("\nGenerating Chart 1-1: Flow Diagram...")

# افزایش سایز figure برای کیفیت بهتر
fig, ax = plt.subplots(figsize=(20, 12))

# تعریف رنگ‌ها با کیفیت بالاتر
color_credits = '#2E86AB'       # آبی تیره
color_contracts = '#06A77D'     # سبز نعنایی
color_payments = '#F77F00'      # نارنجی
color_not_contracted = '#D62828'  # قرمز
color_not_paid = '#6C757D'      # خاکستری

# موقعیت‌ها برای نمودار جریان
# ستون 1: اعتبارات (سمت راست)
x1 = 0.85
y1_start = 0.25
y1_height = 0.5

# ستون 2: قراردادها (وسط)
x2 = 0.5
contract_ratio = total_contracts_b / total_credits_b
y2_height = y1_height * contract_ratio
y2_start = 0.5 - y2_height / 2

not_contracted_height = y1_height - y2_height
not_contracted_start = y2_start + y2_height

# ستون 3: پرداخت‌ها (سمت چپ)
x3 = 0.15
payment_ratio = total_payments_b / total_contracts_b
y3_height = y2_height * payment_ratio
y3_start = 0.5 - y3_height / 2

not_paid_height = y2_height - y3_height
not_paid_start = y3_start + y3_height

# رسم مستطیل‌ها با کیفیت بالا
box_width = 0.1
# مستطیل 1: اعتبارات تکلیفی
rect1 = FancyBboxPatch((x1-box_width, y1_start), box_width, y1_height,
                         boxstyle="round,pad=0.015", 
                         linewidth=3, edgecolor='#1a1a1a',
                         facecolor=color_credits, alpha=0.85, zorder=3)
ax.add_patch(rect1)

# مستطیل 2: قراردادها
rect2 = FancyBboxPatch((x2-box_width/2, y2_start), box_width, y2_height,
                         boxstyle="round,pad=0.015",
                         linewidth=3, edgecolor='#1a1a1a',
                         facecolor=color_contracts, alpha=0.85, zorder=3)
ax.add_patch(rect2)

# مستطیل 3: پرداخت‌ها
rect3 = FancyBboxPatch((x3-box_width/2, y3_start), box_width, y3_height,
                         boxstyle="round,pad=0.015",
                         linewidth=3, edgecolor='#1a1a1a',
                         facecolor=color_payments, alpha=0.85, zorder=3)
ax.add_patch(rect3)

# مستطیل 4: اعتبار بدون قرارداد
if not_contracted_height > 0.01:
    rect4 = FancyBboxPatch((x2-box_width/2, not_contracted_start), box_width, not_contracted_height,
                             boxstyle="round,pad=0.015",
                             linewidth=3, edgecolor='#1a1a1a', linestyle='--',
                             facecolor=color_not_contracted, alpha=0.6, zorder=3)
    ax.add_patch(rect4)

# مستطیل 5: قرارداد بدون پرداخت
if not_paid_height > 0.01:
    rect5 = FancyBboxPatch((x3-box_width/2, not_paid_start), box_width, not_paid_height,
                             boxstyle="round,pad=0.015",
                             linewidth=3, edgecolor='#1a1a1a', linestyle='--',
                             facecolor=color_not_paid, alpha=0.6, zorder=3)
    ax.add_patch(rect5)

# رسم جریان‌ها با خطوط منحنی
from matplotlib.patches import FancyArrowPatch

# جریان 1: اعتبار به قرارداد
arrow1 = FancyArrowPatch((x1-box_width, y1_start + y1_height/2),
                          (x2+box_width/2, y2_start + y2_height/2),
                          arrowstyle='->', mutation_scale=40, linewidth=4,
                          color=color_contracts, alpha=0.6, zorder=1,
                          connectionstyle="arc3,rad=.15")
ax.add_patch(arrow1)

# جریان 2: اعتبار به "بدون قرارداد"
if not_contracted_height > 0.01:
    arrow2 = FancyArrowPatch((x1-box_width, y1_start + y1_height/2),
                              (x2+box_width/2, not_contracted_start + not_contracted_height/2),
                              arrowstyle='->', mutation_scale=40, linewidth=4,
                              color=color_not_contracted, alpha=0.4, zorder=1,
                              linestyle='--',
                              connectionstyle="arc3,rad=-.15")
    ax.add_patch(arrow2)

# جریان 3: قرارداد به پرداخت
arrow3 = FancyArrowPatch((x2-box_width/2, y2_start + y2_height/2),
                          (x3+box_width/2, y3_start + y3_height/2),
                          arrowstyle='->', mutation_scale=40, linewidth=4,
                          color=color_payments, alpha=0.6, zorder=1,
                          connectionstyle="arc3,rad=.15")
ax.add_patch(arrow3)

# جریان 4: قرارداد به "بدون پرداخت"
if not_paid_height > 0.01:
    arrow4 = FancyArrowPatch((x2-box_width/2, y2_start + y2_height/2),
                              (x3+box_width/2, not_paid_start + not_paid_height/2),
                              arrowstyle='->', mutation_scale=40, linewidth=4,
                              color=color_not_paid, alpha=0.4, zorder=1,
                              linestyle='--',
                              connectionstyle="arc3,rad=-.15")
    ax.add_patch(arrow4)

# اضافه کردن برچسب‌ها با فونت بزرگ‌تر
# برچسب 1: اعتبارات تکلیفی
ax.text(x1-box_width/2, y1_start + y1_height + 0.06,
        fix_persian_text('اعتبارات تکلیفی'),
        ha='center', va='bottom', fontsize=22, fontweight='bold',  # سایز فونت عنوان اعتبارات تکلیفی
        bbox=dict(boxstyle='round,pad=0.7', facecolor='white', edgecolor=color_credits, linewidth=3))

ax.text(x1-box_width/2, y1_start + y1_height/2,
        format_number_with_separator(total_credits_b, use_persian=True) + '\n' + 
        fix_persian_text('میلیارد ریال'),
        ha='center', va='center', fontsize=18, fontweight='bold',  # سایز فونت مقدار اعتبارات
        color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=color_credits, alpha=0.3, edgecolor='none'))

# برچسب 2: قراردادها
ax.text(x2, y2_start + y2_height + 0.06,
        fix_persian_text('قراردادهای منعقد شده'),
        ha='center', va='bottom', fontsize=22, fontweight='bold',  # سایز فونت عنوان قراردادها
        bbox=dict(boxstyle='round,pad=0.7', facecolor='white', edgecolor=color_contracts, linewidth=3))

ax.text(x2, y2_start + y2_height/2,
        format_number_with_separator(total_contracts_b, use_persian=True) + '\n' + 
        fix_persian_text('میلیارد ریال') + '\n' +
        fix_persian_text(f'({contract_percentage:.1f}%)'),
        ha='center', va='center', fontsize=17, fontweight='bold',  # سایز فونت مقدار قراردادها
        color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=color_contracts, alpha=0.3, edgecolor='none'))

# برچسب 3: پرداخت‌ها
ax.text(x3, y3_start + y3_height + 0.06,
        fix_persian_text('پرداخت‌های انجام شده'),
        ha='center', va='bottom', fontsize=22, fontweight='bold',  # سایز فونت عنوان پرداخت‌ها
        bbox=dict(boxstyle='round,pad=0.7', facecolor='white', edgecolor=color_payments, linewidth=3))

ax.text(x3, y3_start + y3_height/2,
        format_number_with_separator(total_payments_b, use_persian=True) + '\n' + 
        fix_persian_text('میلیارد ریال') + '\n' +
        fix_persian_text(f'({payment_percentage:.1f}%)'),
        ha='center', va='center', fontsize=17, fontweight='bold',  # سایز فونت مقدار پرداخت‌ها
        color='white',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=color_payments, alpha=0.3, edgecolor='none'))

# برچسب 4: بدون قرارداد
if not_contracted_height > 0.05:
    ax.text(x2, not_contracted_start + not_contracted_height/2,
            fix_persian_text('بدون قرارداد') + '\n' +
            format_number_with_separator(not_contracted_b, use_persian=True) + '\n' + 
            fix_persian_text('میلیارد ریال'),
            ha='center', va='center', fontsize=15, fontweight='bold',  # سایز فونت بدون قرارداد
            color='white',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=color_not_contracted, alpha=0.7, edgecolor='white', linewidth=2))

# برچسب 5: بدون پرداخت
if not_paid_height > 0.05:
    ax.text(x3, not_paid_start + not_paid_height/2,
            fix_persian_text('بدون پرداخت') + '\n' +
            format_number_with_separator(not_paid_b, use_persian=True) + '\n' + 
            fix_persian_text('میلیارد ریال'),
            ha='center', va='center', fontsize=15, fontweight='bold',  # سایز فونت بدون پرداخت
            color='white',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=color_not_paid, alpha=0.7, edgecolor='white', linewidth=2))

# تنظیمات محورها
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# عنوان
title_text = fix_persian_text('جریان اعتبارات از تخصیص تا پرداخت (میلیارد ریال)')
ax.text(0.5, 0.96, title_text,
        ha='center', va='top', fontsize=26, fontweight='bold',  # سایز فونت عنوان اصلی نمودار 1-1
        bbox=dict(boxstyle='round,pad=1.0', facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=3, alpha=0.9))

# پس‌زمینه
fig.patch.set_facecolor('white')
ax.set_facecolor('#FAFAFA')

plt.tight_layout()

# ذخیره با کیفیت بسیار بالا
output_path = output_dir / 'chart_1_1.png'
plt.savefig(output_path, dpi=400, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_dir / 'chart_1_1.jpg', dpi=400, bbox_inches='tight', facecolor='white', edgecolor='none', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 1-1 saved: {output_path}")

# ==============================================================================
# نمودار 1-2: Gauge Charts - شاخص‌های کلیدی عملکرد
# ==============================================================================
print("\nGenerating Chart 1-2: KPI Gauges...")

# افزایش سایز figure
fig, axes = plt.subplots(1, 3, figsize=(22, 8))

# تابع رسم gauge با کیفیت بالا
def draw_gauge(ax, value, threshold, title, color_good, color_bad):
    """رسم نمودار gauge با کیفیت بالا"""
    
    # رسم دایره پس‌زمینه
    theta = np.linspace(0, np.pi, 200)
    x_bg = np.cos(theta)
    y_bg = np.sin(theta)
    
    # رنگ‌های بازه‌ها
    colors_bg = ['#FFCDD2', '#FFF9C4', '#C8E6C9']
    ranges = [[0, 30], [30, 60], [60, 100]]
    
    for i, (range_val, color_bg) in enumerate(zip(ranges, colors_bg)):
        theta_range = np.linspace(np.pi * (100-range_val[1])/100, 
                                   np.pi * (100-range_val[0])/100, 200)
        x_range = np.cos(theta_range)
        y_range = np.sin(theta_range)
        x_range = np.append(x_range, 0)
        y_range = np.append(y_range, 0)
        ax.fill(x_range, y_range, color=color_bg, alpha=0.4, zorder=1, edgecolor='none')
    
    # رسم دایره اصلی
    ax.plot(x_bg, y_bg, 'k-', linewidth=4, zorder=2)
    ax.plot([-1, 1], [0, 0], 'k-', linewidth=3, zorder=2)
    
    # رسم عقربه
    angle = np.pi * (100 - value) / 100
    x_needle = 0.75 * np.cos(angle)
    y_needle = 0.75 * np.sin(angle)
    
    needle_color = color_good if value >= threshold else color_bad
    
    # عقربه با سایه
    ax.arrow(0, 0, x_needle, y_needle, 
             head_width=0.12, head_length=0.12,
             fc=needle_color, ec='black', linewidth=3, zorder=4,
             length_includes_head=True)
    
    # نقطه مرکزی
    circle = plt.Circle((0, 0), 0.1, color='black', zorder=5)
    ax.add_patch(circle)
    circle_white = plt.Circle((0, 0), 0.08, color='white', zorder=6)
    ax.add_patch(circle_white)
    
    # نمایش مقدار با باکس بزرگتر
    value_text = format_number_with_separator(value, use_persian=True) + '%'
    ax.text(0, -0.35, value_text,
            ha='center', va='center', fontsize=32, fontweight='bold',  # سایز فونت عدد اصلی gauge
            bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                     edgecolor=needle_color, linewidth=3, alpha=0.95))
    
    # عنوان
    ax.text(0, -0.65, fix_persian_text(title),
            ha='center', va='center', fontsize=19, fontweight='bold')  # سایز فونت عنوان gauge
    
    # خط آستانه
    threshold_angle = np.pi * (100 - threshold) / 100
    x_threshold = 1.1 * np.cos(threshold_angle)
    y_threshold = 1.1 * np.sin(threshold_angle)
    ax.plot([0, x_threshold], [0, y_threshold], 'r--', linewidth=3, zorder=3, alpha=0.8)
    
    # برچسب آستانه
    target_text = fix_persian_text(f'هدف: {threshold:.0f}%')
    ax.text(x_threshold * 1.2, y_threshold * 1.2,
            target_text,
            ha='center', va='center', fontsize=13, color='red', fontweight='bold',  # سایز فونت برچسب آستانه
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='red', linewidth=2, alpha=0.9))
    
    # تنظیمات محور
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-0.8, 1.3)
    ax.set_aspect('equal')
    ax.axis('off')

# Gauge 1: درصد انعقاد قرارداد
draw_gauge(axes[0], contract_percentage, target_contract_percentage, 
           'درصد انعقاد قرارداد', '#06A77D', '#D62828')

# Gauge 2: درصد پرداخت از اعتبار
draw_gauge(axes[1], payment_percentage, target_payment_percentage,
           'درصد پرداخت از کل اعتبار', '#F77F00', '#D62828')

# Gauge 3: درصد پرداخت از قرارداد
draw_gauge(axes[2], payment_to_contract_percentage, target_payment_from_contract,
           'درصد پرداخت از قرارداد', '#7B2CBF', '#D62828')

# عنوان کلی
title_text = fix_persian_text('شاخص‌های کلیدی عملکرد سامانه ساتع - شش ماهه اول ۱۴۰۴')
fig.suptitle(title_text,
             fontsize=28, fontweight='bold', y=0.98)  # سایز فونت عنوان اصلی نمودار 1-2

# پس‌زمینه
fig.patch.set_facecolor('white')

plt.tight_layout()

# ذخیره با کیفیت بسیار بالا
output_path = output_dir / 'chart_1_2.png'
plt.savefig(output_path, dpi=400, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_dir / 'chart_1_2.jpg', dpi=400, bbox_inches='tight', facecolor='white', edgecolor='none', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 1-2 saved: {output_path}")

print("\n" + "="*70)
print("CHAPTER 1 VISUALIZATION COMPLETE - HIGH QUALITY VERSION")
print("="*70)
print(f"\nGenerated files in: {output_dir}")
print(f"  1. chart_1_1.png/.jpg - Flow Diagram (DPI: 400)")
print(f"  2. chart_1_2.png/.jpg - KPI Gauges (DPI: 400)")
print(f"\nKey improvements:")
print(f"  ✓ Increased DPI to 400 for superior quality")
print(f"  ✓ Larger figure sizes (20x12 and 22x8)")
print(f"  ✓ Bigger fonts throughout (18-32pt)")
print(f"  ✓ Corrected 6-month targets (30% contract, 20% payment)")
print(f"  ✓ Enhanced visual quality with better colors and spacing")
print("\n" + "="*70)