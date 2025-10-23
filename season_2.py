"""
فصل دوم: تحلیل عملکرد مشمولین
تولید نمودارهای تحلیلی برای فصل دوم گزارش - نسخه اصلاح شده
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
# Font Configuration - Vazirmatn
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
        return str(text)

def format_text_multiline(text, max_chars_per_line=20, max_lines=2):
    """تقسیم متن به چند خط با محدودیت تعداد کاراکتر"""
    if not text or pd.isna(text):
        return ''
    
    text = str(text).strip()
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        if current_length + word_length + len(current_line) <= max_chars_per_line:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(' '.join(current_line))
                if len(lines) >= max_lines:
                    break
            current_line = [word]
            current_length = word_length
    
    if current_line and len(lines) < max_lines:
        lines.append(' '.join(current_line))
    
    # اگر متن بیشتر از حد مجاز بود، سه نقطه اضافه کن
    if len(words) > sum(len(line.split()) for line in lines):
        if lines:
            lines[-1] = lines[-1][:max_chars_per_line-3] + '...'
    
    return '\n'.join(lines)

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

output_dir = Path('./figs/s2')
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
# Data Preparation
# ==============================================================================

# تجمیع داده‌ها بر اساس مشمولین
subjects_summary = df_contracts.groupby('نام مشمول').agg({
    'اعتبار سال 1404': 'first',
    'دستگاه اجرایی مرتبط': 'first',
    'مجموع مبالغ قراردادها': 'sum',
    'دانشگاه': 'count'
}).reset_index()

subjects_summary.columns = ['نام مشمول', 'اعتبار', 'دستگاه', 'مبلغ قرارداد', 'تعداد قرارداد']

# اضافه کردن داده‌های پرداخت
payments_summary = df_payments.groupby('نام مشمول').agg({
    'مجموع مبالغ پرداختی': 'sum'
}).reset_index()
payments_summary.columns = ['نام مشمول', 'مبلغ پرداخت']

subjects_summary = subjects_summary.merge(payments_summary, on='نام مشمول', how='left')
subjects_summary['مبلغ پرداخت'].fillna(0, inplace=True)

# محاسبه درصدها
subjects_summary['درصد قرارداد'] = (subjects_summary['مبلغ قرارداد'] / subjects_summary['اعتبار']) * 100
subjects_summary['درصد پرداخت از اعتبار'] = (subjects_summary['مبلغ پرداخت'] / subjects_summary['اعتبار']) * 100
subjects_summary['درصد پرداخت از قرارداد'] = np.where(
    subjects_summary['مبلغ قرارداد'] > 0,
    (subjects_summary['مبلغ پرداخت'] / subjects_summary['مبلغ قرارداد']) * 100,
    0
)

# تجمیع به تفکیک دستگاه
dept_summary = subjects_summary.groupby('دستگاه').agg({
    'اعتبار': 'sum',
    'مبلغ قرارداد': 'sum',
    'مبلغ پرداخت': 'sum',
    'نام مشمول': 'count'
}).reset_index()
dept_summary.columns = ['دستگاه', 'اعتبار', 'مبلغ قرارداد', 'مبلغ پرداخت', 'تعداد مشمول']

print(f"\nTotal subjects: {len(subjects_summary)}")
print(f"Subjects with contracts: {len(subjects_summary[subjects_summary['مبلغ قرارداد'] > 0])}")
print(f"Subjects with payments: {len(subjects_summary[subjects_summary['مبلغ پرداخت'] > 0])}")

# ==============================================================================
# نمودار 2-1: Treemap - توزیع اعتبارات مشمولین (با متن دو خطی)
# ==============================================================================
print("\nGenerating Chart 2-1: Treemap - Subjects...")

import squarify

fig, ax = plt.subplots(figsize=(20, 12))

# 30 مشمول برتر
top_30 = subjects_summary.nlargest(30, 'اعتبار')

sizes = top_30['اعتبار'].values / 1000
labels = []
for name, val in zip(top_30['نام مشمول'], top_30['اعتبار']):
    name_formatted = format_text_multiline(name, max_chars_per_line=25, max_lines=2)
    value_text = format_number_with_separator(val/1000) + ' میلیارد'
    labels.append(fix_persian_text(name_formatted + '\n' + value_text))

colors = plt.cm.RdYlGn(top_30['درصد قرارداد'] / 100)

squarify.plot(sizes=sizes, label=labels, alpha=0.8, color=colors,
              text_kwargs={'fontsize': 10, 'weight': 'bold'},
              ax=ax, pad=True)

ax.axis('off')

title_text = fix_persian_text('توزیع اعتبارات تکلیفی - ۳۰ مشمول برتر (میلیارد ریال)')
plt.title(title_text, fontsize=24, fontweight='bold', pad=20)

sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=plt.Normalize(vmin=0, vmax=100))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.02, aspect=50)
cbar.set_label(fix_persian_text('درصد تحقق قرارداد (%)'), fontsize=14, weight='bold')
cbar.ax.tick_params(labelsize=12)

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_1.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_1.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-1 saved")

# ==============================================================================
# نمودار 2-1b: Treemap - توزیع اعتبارات دستگاه‌ها
# ==============================================================================
print("\nGenerating Chart 2-1b: Treemap - Departments...")

fig, ax = plt.subplots(figsize=(20, 12))

# همه دستگاه‌ها
dept_sorted = dept_summary.sort_values('اعتبار', ascending=False)

sizes_dept = dept_sorted['اعتبار'].values / 1000
labels_dept = []
for name, val in zip(dept_sorted['دستگاه'], dept_sorted['اعتبار']):
    name_formatted = format_text_multiline(name, max_chars_per_line=30, max_lines=2)
    value_text = format_number_with_separator(val/1000) + ' میلیارد'
    labels_dept.append(fix_persian_text(name_formatted + '\n' + value_text))

dept_sorted['درصد قرارداد'] = (dept_sorted['مبلغ قرارداد'] / dept_sorted['اعتبار']) * 100
colors_dept = plt.cm.RdYlGn(dept_sorted['درصد قرارداد'] / 100)

squarify.plot(sizes=sizes_dept, label=labels_dept, alpha=0.8, color=colors_dept,
              text_kwargs={'fontsize': 11, 'weight': 'bold'},
              ax=ax, pad=True)

ax.axis('off')

title_text = fix_persian_text('توزیع اعتبارات تکلیفی به تفکیک دستگاه اجرایی (میلیارد ریال)')
plt.title(title_text, fontsize=24, fontweight='bold', pad=20)

sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=plt.Normalize(vmin=0, vmax=100))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.02, aspect=50)
cbar.set_label(fix_persian_text('درصد تحقق قرارداد (%)'), fontsize=14, weight='bold')
cbar.ax.tick_params(labelsize=12)

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_1b.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_1b.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-1b saved")

# ==============================================================================
# نمودار 2-2: تعداد و فراوانی قراردادها
# ==============================================================================
print("\nGenerating Chart 2-2: Contract Statistics...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))

# بخش اول: تعداد مشمولین با قرارداد
subjects_with_contract = len(subjects_summary[subjects_summary['مبلغ قرارداد'] > 0])
subjects_without_contract = len(subjects_summary[subjects_summary['مبلغ قرارداد'] == 0])

categories = [
    fix_persian_text('مشمولین با قرارداد'),
    fix_persian_text('مشمولین بدون قرارداد')
]
values = [subjects_with_contract, subjects_without_contract]
colors_pie = ['#4CAF50', '#F44336']

wedges, texts, autotexts = ax1.pie(values, labels=categories, autopct='%1.1f%%',
                                     colors=colors_pie, startangle=90,
                                     textprops={'fontsize': 13, 'weight': 'bold'})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(16)
    autotext.set_fontweight('bold')

ax1.set_title(fix_persian_text('توزیع مشمولین بر اساس انعقاد قرارداد'), 
              fontsize=18, fontweight='bold', pad=15)

# افزودن تعداد
textstr = fix_persian_text(
    f'با قرارداد: {subjects_with_contract} مشمول\n'
    f'بدون قرارداد: {subjects_without_contract} مشمول\n'
    f'جمع: {subjects_with_contract + subjects_without_contract} مشمول'
)
ax1.text(0, -1.4, textstr, ha='center', fontsize=12,
         bbox=dict(boxstyle='round,pad=0.8', facecolor='wheat', alpha=0.8))

# بخش دوم: هیستوگرام مبالغ قراردادها
contracts_values = subjects_summary[subjects_summary['مبلغ قرارداد'] > 0]['مبلغ قرارداد'] / 1000

n, bins, patches = ax2.hist(contracts_values, bins=15, color='#2196F3',
                             alpha=0.7, edgecolor='black', linewidth=1.5)

colors_hist = plt.cm.YlGnBu(n / n.max())
for patch, color in zip(patches, colors_hist):
    patch.set_facecolor(color)

mean_val = contracts_values.mean()
median_val = contracts_values.median()

ax2.axvline(mean_val, color='red', linestyle='--', linewidth=2,
           label=fix_persian_text(f'میانگین: {format_number_with_separator(mean_val)} میلیارد'))
ax2.axvline(median_val, color='green', linestyle='--', linewidth=2,
           label=fix_persian_text(f'میانه: {format_number_with_separator(median_val)} میلیارد'))

ax2.set_xlabel(fix_persian_text('مبلغ قرارداد (میلیارد ریال)'), fontsize=15, fontweight='bold')
ax2.set_ylabel(fix_persian_text('تعداد مشمولین (فراوانی)'), fontsize=15, fontweight='bold')
ax2.set_title(fix_persian_text('توزیع فراوانی مبالغ قراردادهای منعقد شده'), 
              fontsize=18, fontweight='bold', pad=15)
ax2.legend(fontsize=12)
ax2.grid(True, alpha=0.3)
# تبدیل اعداد محورها به فارسی - نمودار 2-2
x_ticks = ax2.get_xticks()
x_labels = [convert_to_persian_number(f'{int(tick):,}') for tick in x_ticks]
ax2.set_xticklabels(x_labels)

y_ticks = ax2.get_yticks()
y_labels = [convert_to_persian_number(f'{int(tick)}') for tick in y_ticks]
ax2.set_yticklabels(y_labels)

ax2.tick_params(labelsize=12)

plt.suptitle(fix_persian_text('آمار قراردادهای منعقد شده - شش ماهه اول ۱۴۰۴'),
             fontsize=22, fontweight='bold', y=0.98)

fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig(output_dir / 'chart_2_2.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_2.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-2 saved")

# ==============================================================================
# نمودار 2-3: درصد تحقق قرارداد - 20 مشمول برتر
# ==============================================================================
print("\nGenerating Chart 2-3: Contract Achievement - Top 20...")

fig, ax = plt.subplots(figsize=(16, 14))

top_20 = subjects_summary.nlargest(20, 'اعتبار').sort_values('درصد قرارداد', ascending=True)

y_pos = np.arange(len(top_20))
percentages = top_20['درصد قرارداد'].values

colors_bar = ['#D32F2F' if p < 10 else '#FF9800' if p < 20 else '#4CAF50' 
              for p in percentages]

bars = ax.barh(y_pos, percentages, color=colors_bar, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.axvline(x=30, color='red', linestyle='--', linewidth=3, alpha=0.7,
          label=fix_persian_text('هدف ۳۰٪'))

labels = [fix_persian_text(format_text_multiline(name, 35, 2)) for name in top_20['نام مشمول']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=11)

for i, (bar, pct) in enumerate(zip(bars, percentages)):
    width = bar.get_width()
    label_text = fix_persian_text(f'{pct:.1f}%')
    ax.text(width + 1, bar.get_y() + bar.get_height()/2,
           label_text, ha='left', va='center', 
           fontsize=11, fontweight='bold')

ax.set_xlabel(fix_persian_text('درصد تحقق قرارداد (%)'), fontsize=16, fontweight='bold')
ax.set_title(fix_persian_text('درصد تحقق قرارداد - ۲۰ مشمول برتر از نظر اعتبار'), 
             fontsize=22, fontweight='bold', pad=20)
ax.set_xlim(0, max(percentages) + 10)
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.legend(fontsize=14, loc='lower right')
# تبدیل اعداد محور X به فارسی - نمودار 2-3
x_ticks = ax.get_xticks()
x_labels = [convert_to_persian_number(f'{int(tick)}') for tick in x_ticks]
ax.set_xticklabels(x_labels)

ax.tick_params(axis='x', labelsize=12)

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_3.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_3.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-3 saved")

# ==============================================================================
# نمودار 2-4: درصد تحقق پرداخت - 20 مشمول دارای قرارداد
# ==============================================================================
print("\nGenerating Chart 2-4: Payment Achievement - Top 20 with contracts...")

fig, ax = plt.subplots(figsize=(16, 14))

# انتخاب مشمولینی که قرارداد دارند
subjects_with_contracts = subjects_summary[subjects_summary['مبلغ قرارداد'] > 0]
top_20_contracts = subjects_with_contracts.nlargest(20, 'مبلغ قرارداد').sort_values('درصد پرداخت از قرارداد', ascending=True)

y_pos = np.arange(len(top_20_contracts))
percentages = top_20_contracts['درصد پرداخت از قرارداد'].values

colors_bar = ['#D32F2F' if p < 50 else '#FF9800' if p < 67 else '#4CAF50' 
              for p in percentages]

bars = ax.barh(y_pos, percentages, color=colors_bar, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.axvline(x=67, color='red', linestyle='--', linewidth=3, alpha=0.7,
          label=fix_persian_text('هدف ۶۷٪'))

labels = [fix_persian_text(format_text_multiline(name, 35, 2)) for name in top_20_contracts['نام مشمول']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=11)

for i, (bar, pct) in enumerate(zip(bars, percentages)):
    width = bar.get_width()
    label_text = fix_persian_text(f'{pct:.1f}%')
    ax.text(width + 2, bar.get_y() + bar.get_height()/2,
           label_text, ha='left', va='center', 
           fontsize=11, fontweight='bold')

ax.set_xlabel(fix_persian_text('درصد پرداخت از قرارداد (%)'), fontsize=16, fontweight='bold')
ax.set_title(fix_persian_text('درصد تحقق پرداخت - ۲۰ مشمول دارای بیشترین قرارداد'), 
             fontsize=22, fontweight='bold', pad=20)
ax.set_xlim(0, min(max(percentages) + 10, 110))
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.legend(fontsize=14, loc='lower right')
# تبدیل اعداد محور X به فارسی - نمودار 2-4
x_ticks = ax.get_xticks()
x_labels = [convert_to_persian_number(f'{int(tick)}') for tick in x_ticks]
ax.set_xticklabels(x_labels)

ax.tick_params(axis='x', labelsize=12)

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_4.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_4.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-4 saved")

# ==============================================================================
# نمودار 2-5: 10 مشمول برتر - اعتبار و قرارداد
# ==============================================================================
print("\nGenerating Chart 2-5: Top 10 - Credit vs Contract...")

fig, ax = plt.subplots(figsize=(16, 12))

top_10 = subjects_summary.nlargest(10, 'اعتبار').sort_values('اعتبار', ascending=True)

y_pos = np.arange(len(top_10))
credits = top_10['اعتبار'].values / 1000
contracts = top_10['مبلغ قرارداد'].values / 1000

# ستون اعتبار
bars1 = ax.barh(y_pos, credits, height=0.35, label=fix_persian_text('اعتبار تکلیفی'),
                color='#2196F3', alpha=0.8, edgecolor='black', linewidth=1.5)

# ستون قرارداد
bars2 = ax.barh(y_pos, contracts, height=0.35, label=fix_persian_text('مبلغ قرارداد'),
                color='#4CAF50', alpha=0.9, edgecolor='black', linewidth=1.5)

# برچسب‌ها
labels = [fix_persian_text(format_text_multiline(name, 40, 2)) for name in top_10['نام مشمول']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=12)

# مقادیر روی میله‌ها
for bar, val in zip(bars1, credits):
    if val > 50:
        ax.text(val/2, bar.get_y() + bar.get_height()/2,
               format_number_with_separator(val),
               ha='center', va='center', fontsize=10, 
               fontweight='bold', color='white')

for bar, val in zip(bars2, contracts):
    if val > 10:
        ax.text(val/2, bar.get_y() + bar.get_height()/2,
               format_number_with_separator(val),
               ha='center', va='center', fontsize=10,
               fontweight='bold', color='white')

ax.set_xlabel(fix_persian_text('مبلغ (میلیارد ریال)'), fontsize=16, fontweight='bold')
ax.set_title(fix_persian_text('مقایسه اعتبار و قرارداد - ۱۰ مشمول دارای بیشترین اعتبار'), 
             fontsize=22, fontweight='bold', pad=20)
ax.legend(fontsize=14, loc='lower right')
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
# تبدیل اعداد محور X به فارسی - نمودار 2-5
x_ticks = ax.get_xticks()
x_labels = [convert_to_persian_number(f'{int(tick):,}') for tick in x_ticks]
ax.set_xticklabels(x_labels)

ax.tick_params(axis='x', labelsize=12)

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_5.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_5.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-5 saved")

# ==============================================================================
# نمودار 2-6: 20 مشمول برتر در پرداخت
# ==============================================================================
print("\nGenerating Chart 2-6: Top 20 - Payments...")

fig, ax = plt.subplots(figsize=(16, 14))

top_20_payments = subjects_summary.nlargest(20, 'مبلغ پرداخت').sort_values('مبلغ پرداخت', ascending=True)

y_pos = np.arange(len(top_20_payments))
payments = top_20_payments['مبلغ پرداخت'].values / 1000

colors_gradient = plt.cm.Greens(np.linspace(0.4, 0.9, len(payments)))

bars = ax.barh(y_pos, payments, color=colors_gradient, alpha=0.8, 
              edgecolor='black', linewidth=1.5)

labels = [fix_persian_text(format_text_multiline(name, 40, 2)) for name in top_20_payments['نام مشمول']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=11)

for bar, val in zip(bars, payments):
    label_text = format_number_with_separator(val) + ' ' + fix_persian_text('میلیارد')
    ax.text(val + max(payments)*0.02, bar.get_y() + bar.get_height()/2,
           label_text, ha='left', va='center',
           fontsize=10, fontweight='bold')

ax.set_xlabel(fix_persian_text('مبلغ پرداخت (میلیارد ریال)'), fontsize=16, fontweight='bold')
ax.set_title(fix_persian_text('۲۰ مشمول دارای بیشترین پرداخت - شش ماهه اول ۱۴۰۴'), 
             fontsize=22, fontweight='bold', pad=20)
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
# تبدیل اعداد محور X به فارسی - نمودار 2-6
x_ticks = ax.get_xticks()
x_labels = [convert_to_persian_number(f'{int(tick):,}') for tick in x_ticks]
ax.set_xticklabels(x_labels)

ax.tick_params(axis='x', labelsize=12)
ax.set_xlim(0, max(payments) * 1.15)

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_6.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_6.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-6 saved")

# ==============================================================================
# نمودار 2-7: نمودار پارتو - تمرکز پرداخت‌ها
# ==============================================================================
print("\nGenerating Chart 2-7: Pareto - Payment Concentration...")

# مرتب‌سازی بر اساس پرداخت
payments_sorted = subjects_summary.sort_values('مبلغ پرداخت', ascending=False).reset_index(drop=True)
payments_sorted = payments_sorted[payments_sorted['مبلغ پرداخت'] > 0]

cumulative_pct = (payments_sorted['مبلغ پرداخت'].cumsum() / payments_sorted['مبلغ پرداخت'].sum()) * 100
subject_pct = (np.arange(1, len(payments_sorted) + 1) / len(payments_sorted)) * 100

fig, ax1 = plt.subplots(figsize=(18, 10))

# ستون‌ها
color1 = '#4CAF50'
ax1.bar(range(len(payments_sorted)), payments_sorted['مبلغ پرداخت']/1000,
       color=color1, alpha=0.7, edgecolor='black', linewidth=0.5)
ax1.set_xlabel(fix_persian_text('رتبه مشمولین (از بالاترین به پایین‌ترین پرداخت)'),
              fontsize=18, fontweight='bold')
ax1.set_ylabel(fix_persian_text('مبلغ پرداخت (میلیارد ریال)'),
              fontsize=18, fontweight='bold', color=color1)
# تبدیل اعداد محورها به فارسی - نمودار 2-7
y1_ticks = ax1.get_yticks()
y1_labels = [convert_to_persian_number(f'{int(tick):,}') for tick in y1_ticks]
ax1.set_yticklabels(y1_labels)

x1_ticks = ax1.get_xticks()
x1_labels = [convert_to_persian_number(f'{int(tick)}') for tick in x1_ticks]
ax1.set_xticklabels(x1_labels)

ax1.tick_params(axis='y', labelcolor=color1, labelsize=14)
ax1.tick_params(axis='x', labelsize=14)

# خط تجمعی
ax2 = ax1.twinx()
color2 = '#D32F2F'
ax2.plot(range(len(cumulative_pct)), cumulative_pct,
        color=color2, linewidth=4, marker='o', markersize=3)
ax2.set_ylabel(fix_persian_text('درصد تجمعی پرداخت‌ها (%)'),
              fontsize=18, fontweight='bold', color=color2)
# تبدیل اعداد محور دوم (درصد تجمعی) به فارسی
y2_ticks = ax2.get_yticks()
y2_labels = [convert_to_persian_number(f'{int(tick)}') for tick in y2_ticks]
ax2.set_yticklabels(y2_labels)

ax2.tick_params(axis='y', labelcolor=color2, labelsize=14)
ax2.set_ylim(0, 105)

# خطوط راهنما
index_20 = int(len(payments_sorted) * 0.2)
payment_at_20 = cumulative_pct.iloc[index_20] if index_20 < len(cumulative_pct) else 0

ax1.axvline(x=index_20, color='green', linestyle='--', linewidth=2, alpha=0.7)
ax1.text(index_20, ax1.get_ylim()[1]*0.9,
        fix_persian_text(f'۲۰٪ مشمولین برتر\n({format_number_with_separator(payment_at_20)}٪ پرداخت)'),
        fontsize=12, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

ax2.axhline(y=80, color='purple', linestyle='--', linewidth=2, alpha=0.7)

# آمار
top_10_pct = (payments_sorted.head(10)['مبلغ پرداخت'].sum() / payments_sorted['مبلغ پرداخت'].sum()) * 100
top_20_pct = (payments_sorted.head(int(len(payments_sorted)*0.2))['مبلغ پرداخت'].sum() / 
              payments_sorted['مبلغ پرداخت'].sum()) * 100

textstr = fix_persian_text(
    f'۱۰ مشمول برتر: {format_number_with_separator(top_10_pct)}٪ از کل پرداخت\n'
    f'۲۰٪ مشمولین برتر: {format_number_with_separator(top_20_pct)}٪ از کل پرداخت\n'
    f'تعداد مشمولین با پرداخت: {len(payments_sorted)}'
)
props = dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.9, edgecolor='black', linewidth=2)
ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=13,
        verticalalignment='top', horizontalalignment='left', bbox=props)

title_text = fix_persian_text('نمودار پارتو: تمرکز پرداخت‌ها - حجم پرداخت در تعداد محدودی از مشمولین متمرکز است')
ax1.set_title(title_text, fontsize=22, fontweight='bold', pad=20)

ax1.grid(True, alpha=0.3)
ax1.set_axisbelow(True)
fig.patch.set_facecolor('white')

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_7.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_7.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-7 saved")

# ==============================================================================
# نمودار 2-8: Pie Charts - توزیع سلسله‌مراتبی (اصلاح شده)
# ==============================================================================
print("\nGenerating Chart 2-8: Pie Charts - Hierarchical Distribution...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# Pie 1: دستگاه‌های اجرایی - 5 برتر + سایر
dept_top_5 = dept_summary.nlargest(5, 'اعتبار')
dept_others = dept_summary.nsmallest(len(dept_summary) - 5, 'اعتبار')

sizes_dept = list(dept_top_5['اعتبار'].values / 1000)
sizes_dept.append(dept_others['اعتبار'].sum() / 1000)

labels_dept = [fix_persian_text(f"{format_text_multiline(d, 20, 2)}\n{format_number_with_separator(s)} میلیارد")
              for d, s in zip(dept_top_5['دستگاه'], sizes_dept[:-1])]
labels_dept.append(fix_persian_text(f"سایر\n{format_number_with_separator(sizes_dept[-1])} میلیارد"))

wedges1, texts1, autotexts1 = ax1.pie(sizes_dept, labels=labels_dept, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 11})

for autotext in autotexts1:
    autotext.set_color('white')
    autotext.set_fontsize(12)
    autotext.set_fontweight('bold')

ax1.set_title(fix_persian_text('توزیع اعتبارات - ۵ دستگاه برتر + سایر'),
             fontsize=18, fontweight='bold', pad=20)

# Pie 2: مشمولین - 10 برتر + سایر
subjects_top_10 = subjects_summary.nlargest(10, 'اعتبار')
subjects_others = subjects_summary.nsmallest(len(subjects_summary) - 10, 'اعتبار')

sizes_subj = list(subjects_top_10['اعتبار'].values / 1000)
sizes_subj.append(subjects_others['اعتبار'].sum() / 1000)

labels_subj = [fix_persian_text(f"{format_text_multiline(s, 15, 2)}\n{format_number_with_separator(sz)} میلیارد")
              for s, sz in zip(subjects_top_10['نام مشمول'], sizes_subj[:-1])]
labels_subj.append(fix_persian_text(f"سایر ({len(subjects_others)} مشمول)\n{format_number_with_separator(sizes_subj[-1])} میلیارد"))

wedges2, texts2, autotexts2 = ax2.pie(sizes_subj, labels=labels_subj, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 10})

for autotext in autotexts2:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

ax2.set_title(fix_persian_text('توزیع اعتبارات - ۱۰ مشمول برتر + سایر'),
             fontsize=18, fontweight='bold', pad=20)

plt.suptitle(fix_persian_text('توزیع سلسله‌مراتبی اعتبارات تکلیفی'),
            fontsize=24, fontweight='bold', y=0.98)

fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig(output_dir / 'chart_2_8.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_8.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-8 saved")

# ==============================================================================
# Summary
# ==============================================================================
print("\n" + "="*70)
print("CHAPTER 2 VISUALIZATION COMPLETE - REVISED VERSION")
print("="*70)
print(f"\nGenerated 8 charts in: {output_dir}")
print(f"  Chart 2-1:  Treemap - توزیع اعتبارات مشمولین")
print(f"  Chart 2-1b: Treemap - توزیع اعتبارات دستگاه‌ها")
print(f"  Chart 2-2:  آمار قراردادها (Pie + Histogram)")
print(f"  Chart 2-3:  درصد تحقق قرارداد - 20 برتر")
print(f"  Chart 2-4:  درصد تحقق پرداخت - 20 با قرارداد")
print(f"  Chart 2-5:  10 برتر - اعتبار vs قرارداد")
print(f"  Chart 2-6:  20 برتر - پرداخت‌ها")
print(f"  Chart 2-7:  پارتو - تمرکز پرداخت‌ها")
print(f"  Chart 2-8:  Pie - توزیع سلسله‌مراتبی")
print("\n" + "="*70)