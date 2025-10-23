"""
فصل اول: مقدمه و کلیات سامانه ساتع
تولید نمودارهای تحلیلی برای فصل اول گزارش
نسخه اصلاح شده - 3 نمودار اصلی
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.patches import Rectangle, FancyBboxPatch
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# To show Farsi Font
import arabic_reshaper
from bidi.algorithm import get_display

# ==============================================================================
# Font Configuration
# ==============================================================================

font_path = Path(r"D:\OneDrive\AI-Project\SATE_Performance_1404\fonts\Vazirmatn-Regular.ttf")
if font_path.exists():
    font_manager.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Vazirmatn'
else:
    print(f"Warning: Font not found at {font_path}")
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.autolayout'] = True

# ==============================================================================
# Helper Functions
# ==============================================================================

def fix_persian_text(text):
    """تبدیل متن فارسی به فرمت قابل نمایش"""
    if text is None or str(text).strip() == '':
        return ''
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"Warning: Could not reshape text '{text}': {e}")
        return str(text)

def convert_to_persian_number(number):
    """تبدیل اعداد انگلیسی به فارسی"""
    english_digits = '0123456789.,%'
    persian_digits = '۰۱۲۳۴۵۶۷۸۹.،٪'
    translation_table = str.maketrans(english_digits, persian_digits)
    return str(number).translate(translation_table)

def format_number_with_separator(number, use_persian=True):
    """قالب‌بندی اعداد با جداکننده هزارگان"""
    if pd.isna(number):
        return convert_to_persian_number('0') if use_persian else '0'
    formatted = f'{number:,.0f}' if isinstance(number, (int, float)) else str(number)
    if use_persian:
        return convert_to_persian_number(formatted)
    return formatted

# ==============================================================================
# Setup
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

# ==============================================================================
# محاسبات آماری
# ==============================================================================

# اعتبار تکلیفی کل
total_credits = df_contracts.groupby('نام مشمول')['اعتبار سال 1404'].first().sum()

# اعتبار واریز شده به صندوق عتف (داده مستقیم)
deposited_to_atf = 4228781  # میلیون ریال

# مجموع قراردادها
total_contracts = df_contracts['مجموع مبالغ قراردادها'].sum()

# مجموع پرداخت‌ها
total_payments = df_payments['مجموع مبالغ پرداختی'].sum()

# تبدیل به میلیارد ریال
total_credits_b = total_credits / 1000
deposited_to_atf_b = deposited_to_atf / 1000
total_contracts_b = total_contracts / 1000
total_payments_b = total_payments / 1000

print("\n" + "="*70)
print("KEY STATISTICS")
print("="*70)
print(f"Total Mandatory Credits: {total_credits_b:,.0f} billion Rials")
print(f"Deposited to ATF Fund: {deposited_to_atf_b:,.0f} billion Rials ({(deposited_to_atf/total_credits)*100:.1f}%)")
print(f"Total Contracts: {total_contracts_b:,.0f} billion Rials ({(total_contracts/total_credits)*100:.1f}%)")
print(f"Total Payments: {total_payments_b:,.0f} billion Rials ({(total_payments/total_credits)*100:.1f}%)")
print("="*70 + "\n")

# ==============================================================================
# نمودار 1-1: نمودار ستونی - مقایسه اعتبارات
# ==============================================================================
print("\nGenerating Chart 1-1: Column Chart - Comparison...")

fig, ax = plt.subplots(figsize=(16, 10))

# داده‌ها
categories = [
    fix_persian_text('اعتبار تکلیفی کل\nسال ۱۴۰۴'),
    fix_persian_text('واریز شده به\nصندوق عتف'),
    fix_persian_text('مجموع قراردادهای\nمنعقد شده'),
    fix_persian_text('مجموع مبالغ\nپرداختی')
]

values = [total_credits_b, deposited_to_atf_b, total_contracts_b, total_payments_b]
percentages = [100, (deposited_to_atf/total_credits)*100, 
               (total_contracts/total_credits)*100, (total_payments/total_credits)*100]

# رنگ‌ها
colors = ['#1976D2', '#7B1FA2', '#388E3C', '#F57C00']

# رسم ستون‌ها
bars = ax.bar(range(len(categories)), values, color=colors, alpha=0.85, 
              edgecolor='black', linewidth=2, width=0.6)

# اضافه کردن مقادیر روی ستون‌ها
for i, (bar, value, pct) in enumerate(zip(bars, values, percentages)):
    height = bar.get_height()
    
    # مقدار به میلیارد
    value_text = format_number_with_separator(value) + '\n' + fix_persian_text('میلیارد ریال')
    ax.text(bar.get_x() + bar.get_width()/2, height + 150,
           value_text,
           ha='center', va='bottom', fontsize=16, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='white', 
                    edgecolor=colors[i], linewidth=2, alpha=0.9))
    
    # درصد
    if i > 0:  # برای غیر از ستون اول
        pct_text = fix_persian_text(f'({pct:.1f}%)')
        ax.text(bar.get_x() + bar.get_width()/2, height/2,
               pct_text,
               ha='center', va='center', fontsize=18, fontweight='bold',
               color='white',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.5))

# تنظیمات محورها
ax.set_xticks(range(len(categories)))
ax.set_xticklabels(categories, fontsize=15, fontweight='bold')
ax.set_ylabel(fix_persian_text('مبلغ (میلیارد ریال)'), fontsize=18, fontweight='bold')
ax.set_title(fix_persian_text('مقایسه اعتبار تکلیفی، واریز به صندوق، قراردادها و پرداخت‌ها - شش ماهه اول ۱۴۰۴'), 
             fontsize=22, fontweight='bold', pad=20)

# Grid
ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=1)
ax.set_axisbelow(True)

# محدوده محور Y
ax.set_ylim(0, max(values) * 1.2)

# تیک‌های محور Y - تبدیل اعداد به فارسی
y_ticks = ax.get_yticks()
y_labels = [convert_to_persian_number(f'{int(tick):,}') for tick in y_ticks]
ax.set_yticklabels(y_labels)
ax.tick_params(axis='y', labelsize=14)

# پس‌زمینه
fig.patch.set_facecolor('white')
ax.set_facecolor('#F5F5F5')

plt.tight_layout()
plt.savefig(output_dir / 'chart_1_1.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_1_1.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 1-1 saved")

# ==============================================================================
# نمودار 1-2: هیستوگرام - توزیع فراوانی اعتبارات
# ==============================================================================
print("\nGenerating Chart 1-2: Histogram - Credit Distribution...")

# استخراج اعتبار هر شرکت و فیلتر کردن کمتر از 100 میلیون ریال
credits_per_subject_raw = df_contracts.groupby('نام مشمول')['اعتبار سال 1404'].first()
# فیلتر: فقط مشمولین با اعتبار بیشتر از 100 میلیون ریال
credits_per_subject = credits_per_subject_raw[credits_per_subject_raw > 100] / 1000  # میلیارد

fig, ax = plt.subplots(figsize=(16, 10))

# رسم هیستوگرام
n, bins, patches = ax.hist(credits_per_subject, bins=20, color='#1976D2', 
                            alpha=0.7, edgecolor='black', linewidth=1.5)

# رنگ‌بندی بر اساس فراوانی
colors_hist = plt.cm.YlOrRd(n / n.max())
for patch, color in zip(patches, colors_hist):
    patch.set_facecolor(color)

# خط میانگین
mean_credit = credits_per_subject.mean()
ax.axvline(mean_credit, color='red', linestyle='--', linewidth=3, 
          label=fix_persian_text(f'میانگین: {format_number_with_separator(mean_credit)} میلیارد'))

# خط میانه
median_credit = credits_per_subject.median()
ax.axvline(median_credit, color='green', linestyle='--', linewidth=3,
          label=fix_persian_text(f'میانه: {format_number_with_separator(median_credit)} میلیارد'))

# تنظیمات
ax.set_xlabel(fix_persian_text('اعتبار تکلیفی (میلیارد ریال)'), fontsize=18, fontweight='bold')
ax.set_ylabel(fix_persian_text('تعداد مشمولین (فراوانی)'), fontsize=18, fontweight='bold')
ax.set_title(fix_persian_text('توزیع فراوانی اعتبارات تکلیفی مشمولین (بالای 100 میلیون ریال) - سال ۱۴۰۴'), 
             fontsize=22, fontweight='bold', pad=20)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)
ax.set_axisbelow(True)

# Legend
ax.legend(fontsize=14, loc='upper right')

# تیک‌ها - تبدیل اعداد محورها به فارسی
x_ticks = ax.get_xticks()
x_labels = [convert_to_persian_number(f'{int(tick):,}') for tick in x_ticks]
ax.set_xticklabels(x_labels)

y_ticks = ax.get_yticks()
y_labels = [convert_to_persian_number(f'{int(tick)}') for tick in y_ticks]
ax.set_yticklabels(y_labels)

ax.tick_params(axis='both', labelsize=14)

# افزودن آمار
textstr = fix_persian_text(
    f'تعداد مشمولین (بالای 100 میلیون ریال): {len(credits_per_subject)}\n'
    f'حداقل: {format_number_with_separator(credits_per_subject.min())} میلیارد\n'
    f'حداکثر: {format_number_with_separator(credits_per_subject.max())} میلیارد\n'
    f'انحراف معیار: {format_number_with_separator(credits_per_subject.std())} میلیارد'
)
props = dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.8, edgecolor='black', linewidth=2)
ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=13,
        verticalalignment='top', horizontalalignment='right', bbox=props)

fig.patch.set_facecolor('white')
ax.set_facecolor('#F5F5F5')

plt.tight_layout()
plt.savefig(output_dir / 'chart_1_2.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_1_2.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 1-2 saved")

# ==============================================================================
# تابع محاسبه ضریب جینی
# ==============================================================================

def calculate_gini(values):
    """محاسبه ضریب جینی برای نابرابری"""
    sorted_values = np.sort(values)
    n = len(values)
    cumsum = np.cumsum(sorted_values)
    return (2 * np.sum((n - np.arange(1, n + 1) + 1) * sorted_values)) / (n * cumsum[-1]) - (n + 1) / n

# ==============================================================================
# نمودار 1-3: نمودار پارتو - تمرکز اعتبارات
# ==============================================================================
print("\nGenerating Chart 1-3: Pareto Chart - Credit Concentration...")

# مرتب‌سازی نزولی
credits_sorted = credits_per_subject.sort_values(ascending=False).reset_index(drop=True)

# محاسبه درصد تجمعی
cumulative_percentage = (credits_sorted.cumsum() / credits_sorted.sum()) * 100
subject_percentage = (np.arange(1, len(credits_sorted) + 1) / len(credits_sorted)) * 100

fig, ax1 = plt.subplots(figsize=(18, 10))

# محور اول: مبالغ اعتبار
color1 = '#1976D2'
ax1.bar(range(len(credits_sorted)), credits_sorted, color=color1, alpha=0.7, 
        edgecolor='black', linewidth=0.5)
ax1.set_xlabel(fix_persian_text('رتبه مشمولین (از بالاترین به پایین‌ترین اعتبار)'), 
               fontsize=18, fontweight='bold')
ax1.set_ylabel(fix_persian_text('اعتبار تکلیفی (میلیارد ریال)'), 
               fontsize=18, fontweight='bold', color=color1)
# تبدیل اعداد محورها به فارسی برای نمودار پارتو
y1_ticks = ax1.get_yticks()
y1_labels = [convert_to_persian_number(f'{int(tick):,}') for tick in y1_ticks]
ax1.set_yticklabels(y1_labels)

x1_ticks = ax1.get_xticks()
x1_labels = [convert_to_persian_number(f'{int(tick)}') for tick in x1_ticks]
ax1.set_xticklabels(x1_labels)

ax1.tick_params(axis='y', labelcolor=color1, labelsize=14)
ax1.tick_params(axis='x', labelsize=14)

# محور دوم: درصد تجمعی
ax2 = ax1.twinx()
color2 = '#D32F2F'
ax2.plot(range(len(cumulative_percentage)), cumulative_percentage, 
         color=color2, linewidth=4, marker='o', markersize=3, label=fix_persian_text('درصد تجمعی'))
ax2.set_ylabel(fix_persian_text('درصد تجمعی اعتبارات (%)'), 
               fontsize=18, fontweight='bold', color=color2)
# تبدیل اعداد محور دوم (درصد تجمعی) به فارسی
y2_ticks = ax2.get_yticks()
y2_labels = [convert_to_persian_number(f'{int(tick)}') for tick in y2_ticks]
ax2.set_yticklabels(y2_labels)

ax2.tick_params(axis='y', labelcolor=color2, labelsize=14)
ax2.set_ylim(0, 105)

# خطوط راهنما - قانون پارتو
# 20% مشمولین = چند درصد اعتبار؟
index_20 = int(len(credits_sorted) * 0.2)
credit_at_20 = cumulative_percentage.iloc[index_20]

# 80% اعتبار = چند درصد مشمولین؟
index_80 = cumulative_percentage[cumulative_percentage <= 80].index[-1] if any(cumulative_percentage <= 80) else 0
subject_at_80 = (index_80 + 1) / len(credits_sorted) * 100

# خط عمودی 20%
ax1.axvline(x=index_20, color='green', linestyle='--', linewidth=2, alpha=0.7)
ax1.text(index_20, ax1.get_ylim()[1]*0.9, 
         fix_persian_text(f'۲۰٪ مشمولین برتر\n({format_number_with_separator(credit_at_20)}٪ اعتبار)'),
         fontsize=12, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

# خط افقی 80%
ax2.axhline(y=80, color='purple', linestyle='--', linewidth=2, alpha=0.7)
ax2.text(len(credits_sorted)*0.7, 82, 
         fix_persian_text(f'۸۰٪ اعتبارات\nدر {format_number_with_separator(subject_at_80)}٪ مشمولین'),
         fontsize=12, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))

# عنوان
title_text = fix_persian_text('نمودار پارتو: تمرکز اعتبارات تکلیفی (بالای 100 میلیون ریال) - تعداد کمی از مشمولین سهم بزرگی از اعتبارات دارند')
ax1.set_title(title_text, fontsize=22, fontweight='bold', pad=20)

# Grid
ax1.grid(True, alpha=0.3, linestyle='--', linewidth=1)
ax1.set_axisbelow(True)

# آمار کلیدی
top_10_pct = (credits_sorted.head(10).sum() / credits_sorted.sum()) * 100
top_20_pct = (credits_sorted.head(int(len(credits_sorted)*0.2)).sum() / credits_sorted.sum()) * 100
top_50_pct = (credits_sorted.head(int(len(credits_sorted)*0.5)).sum() / credits_sorted.sum()) * 100

textstr = fix_persian_text(
    f'۱۰ مشمول برتر: {format_number_with_separator(top_10_pct)}٪ از کل اعتبار\n'
    f'۲۰٪ مشمولین برتر: {format_number_with_separator(top_20_pct)}٪ از کل اعتبار\n'
    f'۵۰٪ مشمولین برتر: {format_number_with_separator(top_50_pct)}٪ از کل اعتبار\n'
    f'\n'
    f'ضریب جینی: {format_number_with_separator(calculate_gini(credits_sorted.values))}'
)

props = dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.9, edgecolor='black', linewidth=2)
ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=13,
        verticalalignment='top', horizontalalignment='left', bbox=props)

fig.patch.set_facecolor('white')

plt.tight_layout()
plt.savefig(output_dir / 'chart_1_3.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_1_3.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 1-3 saved")

# ==============================================================================
# ذخیره آمار
# ==============================================================================

# محاسبه آمار کلیدی
stats = {
    'اعتبار کل (میلیارد ریال)': total_credits_b,
    'واریز به صندوق عتف (میلیارد ریال)': deposited_to_atf_b,
    'درصد واریز به صندوق': (deposited_to_atf/total_credits)*100,
    'مجموع قراردادها (میلیارد ریال)': total_contracts_b,
    'درصد قراردادها از اعتبار': (total_contracts/total_credits)*100,
    'مجموع پرداخت‌ها (میلیارد ریال)': total_payments_b,
    'درصد پرداخت‌ها از اعتبار': (total_payments/total_credits)*100,
    'درصد پرداخت از قرارداد': (total_payments/total_contracts)*100,
    'تعداد مشمولین (بالای 100 میلیون ریال)': len(credits_per_subject),
    'میانگین اعتبار (میلیارد ریال)': credits_per_subject.mean(),
    'میانه اعتبار (میلیارد ریال)': credits_per_subject.median(),
    'انحراف معیار اعتبار': credits_per_subject.std(),
    '10 مشمول برتر - درصد از کل': top_10_pct,
    '20% مشمولین برتر - درصد از کل': top_20_pct,
    'ضریب جینی': calculate_gini(credits_sorted.values)
}

# ذخیره در فایل
stats_df = pd.DataFrame(list(stats.items()), columns=['شاخص', 'مقدار'])
stats_df.to_excel(output_dir / 'chapter1_statistics.xlsx', index=False)

print(f"✓ Statistics saved to: {output_dir / 'chapter1_statistics.xlsx'}")

# ==============================================================================
# Summary
# ==============================================================================
print("\n" + "="*70)
print("CHAPTER 1 VISUALIZATION COMPLETE - REVISED VERSION")
print("="*70)
print(f"\nGenerated 3 charts in: {output_dir}")
print(f"  Chart 1-1: Column Chart - مقایسه اعتبارات")
print(f"  Chart 1-2: Histogram - توزیع فراوانی اعتبارات")
print(f"  Chart 1-3: Pareto Chart - تمرکز اعتبارات")
print(f"\nKey findings:")
print(f"  - Total Credits: {total_credits_b:,.0f} billion Rials")
print(f"  - Deposited to ATF: {deposited_to_atf_b:,.0f} billion ({(deposited_to_atf/total_credits)*100:.1f}%)")
print(f"  - Contracts: {total_contracts_b:,.0f} billion ({(total_contracts/total_credits)*100:.1f}%)")
print(f"  - Payments: {total_payments_b:,.0f} billion ({(total_payments/total_credits)*100:.1f}%)")
print(f"  - Top 10 subjects hold: {top_10_pct:.1f}% of total credits")
print(f"  - Top 20% subjects hold: {top_20_pct:.1f}% of total credits")
print(f"  - Gini coefficient: {calculate_gini(credits_sorted.values):.3f}")
print("\n" + "="*70)