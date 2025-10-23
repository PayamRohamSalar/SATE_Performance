"""
فصل اول: مقدمه و کلیات سامانه ساتع
تولید نمودارهای تحلیلی برای فصل اول گزارش
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
print(f"Contract Achievement Rate: {contract_percentage:.1f}%")
print(f"Payment Achievement Rate: {payment_percentage:.1f}%")
print(f"Payment from Contracts: {payment_to_contract_percentage:.1f}%")
print("="*70 + "\n")

# ==============================================================================
# نمودار 1-1: Sankey-Style Flow Chart - جریان اعتبارات
# ==============================================================================
print("\nGenerating Chart 1-1: Flow Diagram...")

fig, ax = plt.subplots(figsize=(16, 10))

# تعریف رنگ‌ها
color_credits = '#3498db'      # آبی
color_contracts = '#2ecc71'    # سبز
color_payments = '#f39c12'     # نارنجی
color_not_contracted = '#e74c3c'  # قرمز
color_not_paid = '#95a5a6'     # خاکستری

# موقعیت‌ها برای نمودار جریان
# ستون 1: اعتبارات (سمت راست)
x1 = 0.85
y1_start = 0.3
y1_height = 0.4

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

# رسم مستطیل‌ها
# مستطیل 1: اعتبارات تکلیفی
rect1 = FancyBboxPatch((x1-0.08, y1_start), 0.08, y1_height,
                         boxstyle="round,pad=0.01", 
                         linewidth=2, edgecolor='black',
                         facecolor=color_credits, alpha=0.7, zorder=3)
ax.add_patch(rect1)

# مستطیل 2: قراردادها
rect2 = FancyBboxPatch((x2-0.04, y2_start), 0.08, y2_height,
                         boxstyle="round,pad=0.01",
                         linewidth=2, edgecolor='black',
                         facecolor=color_contracts, alpha=0.7, zorder=3)
ax.add_patch(rect2)

# مستطیل 3: پرداخت‌ها
rect3 = FancyBboxPatch((x3-0.04, y3_start), 0.08, y3_height,
                         boxstyle="round,pad=0.01",
                         linewidth=2, edgecolor='black',
                         facecolor=color_payments, alpha=0.7, zorder=3)
ax.add_patch(rect3)

# مستطیل 4: اعتبار بدون قرارداد
rect4 = FancyBboxPatch((x2-0.04, not_contracted_start), 0.08, not_contracted_height,
                         boxstyle="round,pad=0.01",
                         linewidth=2, edgecolor='black', linestyle='--',
                         facecolor=color_not_contracted, alpha=0.5, zorder=3)
ax.add_patch(rect4)

# مستطیل 5: قرارداد بدون پرداخت
rect5 = FancyBboxPatch((x3-0.04, not_paid_start), 0.08, not_paid_height,
                         boxstyle="round,pad=0.01",
                         linewidth=2, edgecolor='black', linestyle='--',
                         facecolor=color_not_paid, alpha=0.5, zorder=3)
ax.add_patch(rect5)

# رسم جریان‌ها با خطوط منحنی
from matplotlib.patches import FancyArrowPatch
import matplotlib.patches as mpatches

# جریان 1: اعتبار به قرارداد
arrow1 = FancyArrowPatch((x1-0.08, y1_start + y1_height/2),
                          (x2+0.04, y2_start + y2_height/2),
                          arrowstyle='->', mutation_scale=30, linewidth=3,
                          color=color_contracts, alpha=0.5, zorder=1,
                          connectionstyle="arc3,rad=.2")
ax.add_patch(arrow1)

# جریان 2: اعتبار به "بدون قرارداد"
arrow2 = FancyArrowPatch((x1-0.08, y1_start + y1_height/2),
                          (x2+0.04, not_contracted_start + not_contracted_height/2),
                          arrowstyle='->', mutation_scale=30, linewidth=3,
                          color=color_not_contracted, alpha=0.3, zorder=1,
                          linestyle='--',
                          connectionstyle="arc3,rad=-.2")
ax.add_patch(arrow2)

# جریان 3: قرارداد به پرداخت
arrow3 = FancyArrowPatch((x2-0.04, y2_start + y2_height/2),
                          (x3+0.04, y3_start + y3_height/2),
                          arrowstyle='->', mutation_scale=30, linewidth=3,
                          color=color_payments, alpha=0.5, zorder=1,
                          connectionstyle="arc3,rad=.2")
ax.add_patch(arrow3)

# جریان 4: قرارداد به "بدون پرداخت"
arrow4 = FancyArrowPatch((x2-0.04, y2_start + y2_height/2),
                          (x3+0.04, not_paid_start + not_paid_height/2),
                          arrowstyle='->', mutation_scale=30, linewidth=3,
                          color=color_not_paid, alpha=0.3, zorder=1,
                          linestyle='--',
                          connectionstyle="arc3,rad=-.2")
ax.add_patch(arrow4)

# اضافه کردن برچسب‌ها
# برچسب 1: اعتبارات تکلیفی
ax.text(x1-0.04, y1_start + y1_height + 0.05,
        fix_persian_text('اعتبارات تکلیفی'),
        ha='center', va='bottom', fontsize=16, fontweight='bold',  # سایز فونت عنوان اعتبارات تکلیفی
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color_credits, linewidth=2))

ax.text(x1-0.04, y1_start + y1_height/2,
        format_number_with_separator(total_credits_b, use_persian=True) + '\n' + 
        fix_persian_text('میلیارد ریال'),
        ha='center', va='center', fontsize=13, fontweight='bold',  # سایز فونت مقدار اعتبارات
        color='white')

# برچسب 2: قراردادها
ax.text(x2, y2_start + y2_height + 0.05,
        fix_persian_text('قراردادهای منعقد شده'),
        ha='center', va='bottom', fontsize=16, fontweight='bold',  # سایز فونت عنوان قراردادها
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color_contracts, linewidth=2))

ax.text(x2, y2_start + y2_height/2,
        format_number_with_separator(total_contracts_b, use_persian=True) + '\n' + 
        fix_persian_text('میلیارد ریال') + '\n' +
        fix_persian_text(f'({contract_percentage:.1f}%)'),
        ha='center', va='center', fontsize=12, fontweight='bold',  # سایز فونت مقدار قراردادها
        color='white')

# برچسب 3: پرداخت‌ها
ax.text(x3, y3_start + y3_height + 0.05,
        fix_persian_text('پرداخت‌های انجام شده'),
        ha='center', va='bottom', fontsize=16, fontweight='bold',  # سایز فونت عنوان پرداخت‌ها
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color_payments, linewidth=2))

ax.text(x3, y3_start + y3_height/2,
        format_number_with_separator(total_payments_b, use_persian=True) + '\n' + 
        fix_persian_text('میلیارد ریال') + '\n' +
        fix_persian_text(f'({payment_percentage:.1f}%)'),
        ha='center', va='center', fontsize=12, fontweight='bold',  # سایز فونت مقدار پرداخت‌ها
        color='white')

# برچسب 4: بدون قرارداد
ax.text(x2, not_contracted_start + not_contracted_height/2,
        fix_persian_text('بدون قرارداد') + '\n' +
        format_number_with_separator(not_contracted_b, use_persian=True) + '\n' + 
        fix_persian_text('میلیارد ریال'),
        ha='center', va='center', fontsize=11, fontweight='bold',  # سایز فونت بدون قرارداد
        color='darkred')

# برچسب 5: بدون پرداخت
ax.text(x3, not_paid_start + not_paid_height/2,
        fix_persian_text('بدون پرداخت') + '\n' +
        format_number_with_separator(not_paid_b, use_persian=True) + '\n' + 
        fix_persian_text('میلیارد ریال'),
        ha='center', va='center', fontsize=11, fontweight='bold',  # سایز فونت بدون پرداخت
        color='dimgray')

# تنظیمات محورها
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# عنوان
ax.text(0.5, 0.95, fix_persian_text('جریان اعتبارات از تخصیص تا پرداخت (میلیارد ریال)'),
        ha='center', va='top', fontsize=20, fontweight='bold',  # سایز فونت عنوان اصلی نمودار 1-1
        bbox=dict(boxstyle='round,pad=0.8', facecolor='lightblue', edgecolor='navy', linewidth=2, alpha=0.8))

# پس‌زمینه
fig.patch.set_facecolor('white')
ax.set_facecolor('#f8f9fa')

plt.tight_layout()

# ذخیره
output_path = output_dir / 'chart_1_1.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_1_1.jpg', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"✓ Chart 1-1 saved: {output_path}")

# ==============================================================================
# نمودار 1-2: Gauge Charts - شاخص‌های کلیدی عملکرد
# ==============================================================================
print("\nGenerating Chart 1-2: KPI Gauges...")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# تابع رسم gauge
def draw_gauge(ax, value, threshold, title, color_good, color_bad):
    """رسم نمودار gauge"""
    
    # رسم دایره پس‌زمینه
    theta = np.linspace(0, np.pi, 100)
    x_bg = np.cos(theta)
    y_bg = np.sin(theta)
    
    # رنگ‌های بازه‌ها
    colors_bg = ['#ffcccc', '#fff4cc', '#ccffcc']
    ranges = [[0, 30], [30, 60], [60, 100]]
    
    for i, (range_val, color_bg) in enumerate(zip(ranges, colors_bg)):
        theta_range = np.linspace(np.pi * (100-range_val[1])/100, 
                                   np.pi * (100-range_val[0])/100, 100)
        x_range = np.cos(theta_range)
        y_range = np.sin(theta_range)
        x_range = np.append(x_range, 0)
        y_range = np.append(y_range, 0)
        ax.fill(x_range, y_range, color=color_bg, alpha=0.3, zorder=1)
    
    # رسم دایره اصلی
    ax.plot(x_bg, y_bg, 'k-', linewidth=3, zorder=2)
    ax.plot([-1, 1], [0, 0], 'k-', linewidth=2, zorder=2)
    
    # رسم عقربه
    angle = np.pi * (100 - value) / 100
    x_needle = 0.7 * np.cos(angle)
    y_needle = 0.7 * np.sin(angle)
    
    needle_color = color_good if value >= threshold else color_bad
    ax.arrow(0, 0, x_needle, y_needle, head_width=0.1, head_length=0.1,
             fc=needle_color, ec=needle_color, linewidth=3, zorder=4)
    
    # نقطه مرکزی
    circle = plt.Circle((0, 0), 0.08, color='black', zorder=5)
    ax.add_patch(circle)
    
    # نمایش مقدار
    ax.text(0, -0.3, format_number_with_separator(value, use_persian=True) + '%',
            ha='center', va='center', fontsize=24, fontweight='bold',  # سایز فونت عدد اصلی gauge
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor=needle_color, linewidth=2))
    
    # عنوان
    ax.text(0, -0.55, fix_persian_text(title),
            ha='center', va='center', fontsize=15, fontweight='bold')  # سایز فونت عنوان gauge
    
    # خط آستانه
    threshold_angle = np.pi * (100 - threshold) / 100
    x_threshold = 1.05 * np.cos(threshold_angle)
    y_threshold = 1.05 * np.sin(threshold_angle)
    ax.plot([0, x_threshold], [0, y_threshold], 'r--', linewidth=2, zorder=3, alpha=0.7)
    
    # برچسب آستانه
    ax.text(x_threshold * 1.15, y_threshold * 1.15,
            fix_persian_text(f'هدف: {threshold}%'),
            ha='center', va='center', fontsize=10, color='red',  # سایز فونت برچسب آستانه
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                     edgecolor='red', linewidth=1, alpha=0.8))
    
    # تنظیمات محور
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.7, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')

# Gauge 1: درصد انعقاد قرارداد
draw_gauge(axes[0], contract_percentage, 60, 
           'درصد انعقاد قرارداد', '#2ecc71', '#e74c3c')

# Gauge 2: درصد پرداخت از اعتبار
draw_gauge(axes[1], payment_percentage, 40,
           'درصد پرداخت از کل اعتبار', '#f39c12', '#e74c3c')

# Gauge 3: درصد پرداخت از قرارداد
draw_gauge(axes[2], payment_to_contract_percentage, 50,
           'درصد پرداخت از قرارداد', '#9b59b6', '#e74c3c')

# عنوان کلی
fig.suptitle(fix_persian_text('شاخص‌های کلیدی عملکرد سامانه ساتع - شش ماهه اول ۱۴۰۴'),
             fontsize=22, fontweight='bold', y=0.98)  # سایز فونت عنوان اصلی نمودار 1-2

# پس‌زمینه
fig.patch.set_facecolor('white')

plt.tight_layout()

# ذخیره
output_path = output_dir / 'chart_1_2.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_1_2.jpg', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f"✓ Chart 1-2 saved: {output_path}")

# ==============================================================================
# تولید فایل Markdown با آمار و پرامپت‌ها
# ==============================================================================
print("\nGenerating analysis prompts file...")

markdown_content = f"""# فصل اول: مقدمه و کلیات سامانه ساتع

## 1-4. آمار کلی عملکرد سال 1404

### آمار کلیدی

| شاخص | مقدار |
|------|-------|
| تعداد کل مشمولین | {unique_subjects:,} |
| تعداد مشمولین با قرارداد | {subjects_with_contracts:,} |
| تعداد مشمولین بدون قرارداد | {unique_subjects - subjects_with_contracts:,} |
| تعداد دستگاه‌های اجرایی | {unique_departments:,} |
| تعداد دانشگاه‌های فعال در قرارداد | {unique_universities_contracts:,} |
| تعداد دانشگاه‌های دریافت‌کننده پرداخت | {unique_universities_payments:,} |
| تعداد کل قراردادها | {total_contract_count:,} |
| جمع اعتبارات تکلیفی | {total_credits:,.0f} میلیون ریال ({total_credits_b:,.0f} میلیارد ریال) |
| جمع مبلغ قراردادها | {total_contracts:,.0f} میلیون ریال ({total_contracts_b:,.0f} میلیارد ریال) |
| جمع پرداخت‌ها | {total_payments:,.0f} میلیون ریال ({total_payments_b:,.0f} میلیارد ریال) |
| درصد تحقق قرارداد | {contract_percentage:.1f}% |
| درصد پرداخت از اعتبار | {payment_percentage:.1f}% |
| درصد پرداخت از قرارداد | {payment_to_contract_percentage:.1f}% |

---

## نمودارهای فصل اول

### نمودار 1-1: جریان اعتبارات

**مسیر فایل:** `figs/s1/chart_1_1.png` و `figs/s1/chart_1_1.jpg`

#### A. پرامپت تحلیل (برای Claude):

```
SECTION A - ANALYSIS PROMPT FOR CHART 1-1

Analyze the flow diagram showing the credit flow from allocation to payment in the SATC system for the first half of 1404. Based on the following data:

KEY METRICS:
- Total Mandatory Credits (اعتبارات تکلیفی): {total_credits_b:,.0f} billion Rials
- Total Contracts Signed (قراردادهای منعقد شده): {total_contracts_b:,.0f} billion Rials ({contract_percentage:.1f}% of credits)
- Total Payments Made (پرداخت‌های انجام شده): {total_payments_b:,.0f} billion Rials ({payment_percentage:.1f}% of credits)
- Credits Without Contracts (اعتبار بدون قرارداد): {not_contracted_b:,.0f} billion Rials ({100-contract_percentage:.1f}% of credits)
- Contracts Without Payments (قرارداد بدون پرداخت): {not_paid_b:,.0f} billion Rials ({100-payment_to_contract_percentage:.1f}% of contracts)

ANALYSIS REQUIREMENTS:
1. Provide a comprehensive analysis of the credit flow efficiency
2. Identify bottlenecks in the system (where the largest drops occur)
3. Evaluate the overall performance against the legal requirement (60% of research budget through SATC)
4. Compare contract achievement rate vs payment achievement rate
5. Discuss implications for the second half of the year
6. Highlight critical issues requiring immediate attention
7. Provide 3-4 key insights in Persian

OUTPUT FORMAT:
Write in professional Persian (فارسی رسمی), 3-4 paragraphs, analytical tone.
```

#### B. محل تحلیل (خروجی Claude):

[تحلیل نمودار 1-1 در اینجا قرار می‌گیرد]

---

### نمودار 1-2: شاخص‌های کلیدی عملکرد

**مسیر فایل:** `figs/s1/chart_1_2.png` و `figs/s1/chart_1_2.jpg`

#### A. پرامپت تحلیل (برای Claude):

```
SECTION A - ANALYSIS PROMPT FOR CHART 1-2

Analyze the three gauge charts showing key performance indicators (KPIs) for the SATC system in the first half of 1404:

KPI VALUES:
1. Contract Achievement Rate (درصد انعقاد قرارداد): {contract_percentage:.1f}%
   - Target threshold: 60%
   - Status: {"Above target" if contract_percentage >= 60 else "Below target"}
   
2. Payment from Total Credits (درصد پرداخت از کل اعتبار): {payment_percentage:.1f}%
   - Target threshold: 40%
   - Status: {"Above target" if payment_percentage >= 40 else "Below target"}
   
3. Payment from Contracts (درصد پرداخت از قرارداد): {payment_to_contract_percentage:.1f}%
   - Target threshold: 50%
   - Status: {"Above target" if payment_to_contract_percentage >= 50 else "Below target"}

ANALYSIS REQUIREMENTS:
1. Evaluate each KPI against its target threshold
2. Identify which indicators are performing well and which need improvement
3. Analyze the relationship between the three indicators
4. Discuss whether the 6-month performance trajectory suggests year-end targets will be met
5. Identify the weakest link in the chain (contracting vs payment execution)
6. Provide actionable recommendations for the second half of the year
7. Compare performance expectations for a 6-month period vs actual achievement

OUTPUT FORMAT:
Write in professional Persian (فارسی رسمی), 3-4 paragraphs, analytical and evaluative tone.
Include specific percentages and comparisons to targets.
```

#### B. محل تحلیل (خروجی Claude):

[تحلیل نمودار 1-2 در اینجا قرار می‌گیرد]

---

## نتیجه‌گیری بخش آمار کلی

#### A. پرامپت تحلیل (برای Claude):

```
SECTION A - SYNTHESIS PROMPT FOR CHAPTER 1 STATISTICS

Based on all statistics and charts presented in Chapter 1, provide a comprehensive synthesis:

OVERALL STATISTICS:
- Total subjects: {unique_subjects:,}
- Subjects with contracts: {subjects_with_contracts:,} ({subjects_with_contracts/unique_subjects*100:.1f}%)
- Subjects without contracts: {unique_subjects - subjects_with_contracts:,}
- Active universities in contracts: {unique_universities_contracts:,}
- Universities receiving payments: {unique_universities_payments:,}
- Total number of contracts: {total_contract_count:,}
- Executive departments: {unique_departments:,}

FINANCIAL FLOW:
- Credits → Contracts conversion: {contract_percentage:.1f}%
- Credits → Payments conversion: {payment_percentage:.1f}%
- Contracts → Payments conversion: {payment_to_contract_percentage:.1f}%

ANALYSIS REQUIREMENTS:
1. Summarize the overall health of the SATC system in the first half of 1404
2. Identify the most critical challenge (subject participation, contracting, or payment execution)
3. Evaluate whether the system is on track to meet annual legal requirements
4. Highlight positive achievements worth noting
5. Provide strategic recommendations for stakeholders
6. Set realistic expectations for second-half performance

OUTPUT FORMAT:
Write in professional Persian (فارسی رسمی), 2-3 paragraphs, strategic and forward-looking tone.
This should serve as a bridge to Chapter 2's detailed analysis.
```

#### B. محل تحلیل (خروجی Claude):

[نتیجه‌گیری کلی فصل اول در اینجا قرار می‌گیرد]

---

*تاریخ تولید گزارش: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

# ذخیره فایل markdown
with open(output_dir / 'analysis_prompts_chapter1.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print("✓ Analysis prompts file saved")

# ==============================================================================
# Summary
# ==============================================================================
print("\n" + "="*70)
print("CHAPTER 1 VISUALIZATION COMPLETE")
print("="*70)
print(f"\nGenerated files in: {output_dir}")
print(f"  1. chart_1_1.png/.jpg - Flow Diagram")
print(f"  2. chart_1_2.png/.jpg - KPI Gauges")
print(f"  3. analysis_prompts_chapter1.md - Analysis Template")
print("\n" + "="*70)