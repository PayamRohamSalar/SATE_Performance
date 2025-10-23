"""
فصل سوم (نسخه اصلاح‌شده): تحلیل عملکرد دانشگاه‌ها و مراکز پژوهشی
تولید نمودارهای تحلیلی بدون درصد پرداخت و با تحلیل استانی
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, FancyArrowPatch
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

def extract_province(university_name):
    """استخراج استان از نام دانشگاه"""
    if pd.isna(university_name):
        return 'نامشخص'
    
    name = str(university_name).strip()
    
    # لیست استان‌های ایران
    provinces = {
        'تهران': ['تهران', 'شهید بهشتی', 'علم و صنعت', 'امیرکبیر', 'صنعتی شریف', 'شریف', 'الزهرا', 'خواجه نصیر'],
        'اصفهان': ['اصفهان', 'صنعتی اصفهان'],
        'شیراز': ['شیراز'],
        'فارس': ['شیراز'],
        'تبریز': ['تبریز', 'صنعتی سهند'],
        'آذربایجان شرقی': ['تبریز', 'سهند'],
        'مشهد': ['مشهد', 'فردوسی'],
        'خراسان رضوی': ['مشهد', 'فردوسی'],
        'اهواز': ['اهواز', 'چمران'],
        'خوزستان': ['اهواز', 'چمران', 'جندی شاپور'],
        'کرمان': ['کرمان', 'باهنر', 'شهید باهنر'],
        'گیلان': ['گیلان', 'رشت'],
        'مازندران': ['مازندران', 'بابلسر', 'ساری', 'نوشیروانی', 'بابل'],
        'کرمانشاه': ['کرمانشاه', 'رازی'],
        'همدان': ['همدان', 'بوعلی سینا'],
        'قزوین': ['قزوین', 'امام خمینی'],
        'یزد': ['یزد'],
        'سمنان': ['سمنان'],
        'اردبیل': ['اردبیل', 'محقق اردبیلی'],
        'زنجان': ['زنجان'],
        'کردستان': ['کردستان', 'سنندج'],
        'آذربایجان غربی': ['ارومیه', 'ارمیه'],
        'لرستان': ['لرستان', 'خرم آباد'],
        'ایلام': ['ایلام'],
        'بوشهر': ['بوشهر', 'خلیج فارس'],
        'هرمزگان': ['هرمزگان', 'بندرعباس'],
        'سیستان و بلوچستان': ['سیستان', 'بلوچستان', 'زاهدان'],
        'خراسان شمالی': ['بجنورد'],
        'خراسان جنوبی': ['بیرجند'],
        'البرز': ['البرز', 'کرج'],
        'قم': ['قم'],
        'چهارمحال و بختیاری': ['شهرکرد'],
        'کهگیلویه و بویراحمد': ['یاسوج'],
        'گلستان': ['گلستان', 'گرگان']
    }
    
    # جستجو در نام دانشگاه
    for province, keywords in provinces.items():
        for keyword in keywords:
            if keyword in name:
                return province
    
    # برخی استان‌ها به جای نام شهر
    main_provinces = ['تهران', 'اصفهان', 'فارس', 'خوزستان', 'خراسان رضوی', 
                     'آذربایجان شرقی', 'مازندران', 'کرمان', 'گیلان']
    for prov in main_provinces:
        if prov in name:
            return prov
    
    return 'سایر'

# ==============================================================================
# Setup
# ==============================================================================

output_dir = Path('./figs/s3')
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
# Data Preparation - دانشگاه‌ها
# ==============================================================================

# تجمیع قراردادها به تفکیک دانشگاه
uni_contracts = df_contracts.groupby('دانشگاه').agg({
    'مجموع مبالغ قراردادها': 'sum',
    'نام مشمول': 'count',
    'دستگاه اجرایی مرتبط': lambda x: x.nunique()
}).reset_index()

uni_contracts.columns = ['دانشگاه', 'مبلغ قرارداد', 'تعداد قرارداد', 'تعداد دستگاه']

# تجمیع پرداخت‌ها به تفکیک دانشگاه
uni_payments = df_payments.groupby('دانشگاه').agg({
    'مجموع مبالغ پرداختی': 'sum',
    'نام مشمول': 'count'
}).reset_index()

uni_payments.columns = ['دانشگاه', 'مبلغ پرداخت', 'تعداد پرداخت']

# ادغام داده‌ها
uni_summary = uni_contracts.merge(uni_payments, on='دانشگاه', how='left')
uni_summary['مبلغ پرداخت'].fillna(0, inplace=True)
uni_summary['تعداد پرداخت'].fillna(0, inplace=True)

# میانگین مبلغ قرارداد
uni_summary['میانگین قرارداد'] = uni_summary['مبلغ قرارداد'] / uni_summary['تعداد قرارداد']

# تعداد مشمولین منحصر به فرد
uni_subjects = df_contracts.groupby('دانشگاه')['نام مشمول'].nunique().reset_index()
uni_subjects.columns = ['دانشگاه', 'تعداد مشمول']
uni_summary = uni_summary.merge(uni_subjects, on='دانشگاه', how='left')

# استخراج استان‌ها
uni_summary['استان'] = uni_summary['دانشگاه'].apply(extract_province)
df_contracts['استان'] = df_contracts['دانشگاه'].apply(extract_province)
df_payments['استان'] = df_payments['دانشگاه'].apply(extract_province)

print(f"\nTotal universities: {len(uni_summary)}")
print(f"Universities with contracts: {len(uni_summary[uni_summary['مبلغ قرارداد'] > 0])}")
print(f"Provinces identified: {uni_summary['استان'].nunique()}")

# ==============================================================================
# نمودار 3-1: Box Plot - حجم قراردادهای دانشگاه‌ها
# ==============================================================================
print("\nGenerating Chart 3-1: Box Plot - Contract Volume Distribution...")

fig, ax = plt.subplots(figsize=(14, 10))

# فقط دانشگاه‌هایی که قرارداد دارند
unis_with_contracts = uni_summary[uni_summary['مبلغ قرارداد'] > 0]['مبلغ قرارداد'] / 1000

bp = ax.boxplot([unis_with_contracts], 
                labels=[fix_persian_text('حجم قراردادهای دانشگاه‌ها')],
                patch_artist=True, notch=True, showmeans=True,
                widths=0.5,
                boxprops=dict(facecolor='#2196F3', alpha=0.7, linewidth=2.5),
                whiskerprops=dict(linewidth=2.5, color='#1976D2'),
                capprops=dict(linewidth=2.5, color='#1976D2'),
                medianprops=dict(color='#D32F2F', linewidth=3.5),
                meanprops=dict(marker='D', markerfacecolor='#4CAF50', 
                             markeredgecolor='black', markersize=12, linewidth=1.5),
                flierprops=dict(marker='o', markerfacecolor='red', markersize=8, 
                              alpha=0.6, markeredgecolor='darkred'))

ax.set_ylabel(fix_persian_text('مبلغ قرارداد (میلیارد ریال)'), fontsize=18, fontweight='bold')
ax.set_title(fix_persian_text('توزیع حجم قراردادهای دانشگاه‌ها'),
             fontsize=24, fontweight='bold', pad=20)

ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=1.2)
ax.set_axisbelow(True)
ax.tick_params(axis='both', labelsize=14)

# آمار
median = unis_with_contracts.median()
mean = unis_with_contracts.mean()
q1 = unis_with_contracts.quantile(0.25)
q3 = unis_with_contracts.quantile(0.75)
min_val = unis_with_contracts.min()
max_val = unis_with_contracts.max()

textstr = fix_persian_text(
    f'حداقل: {format_number_with_separator(min_val)} میلیارد\n'
    f'چارک اول: {format_number_with_separator(q1)} میلیارد\n'
    f'میانه: {format_number_with_separator(median)} میلیارد\n'
    f'میانگین: {format_number_with_separator(mean)} میلیارد\n'
    f'چارک سوم: {format_number_with_separator(q3)} میلیارد\n'
    f'حداکثر: {format_number_with_separator(max_val)} میلیارد'
)
props = dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.9, 
            edgecolor='black', linewidth=2.5)
ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=13,
        verticalalignment='top', horizontalalignment='right', bbox=props)

# Legend
legend_elements = [
    plt.Line2D([0], [0], color='#D32F2F', linewidth=3.5, label=fix_persian_text('میانه')),
    plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='#4CAF50', 
              markersize=12, label=fix_persian_text('میانگین'))
]
ax.legend(handles=legend_elements, fontsize=13, loc='upper left')

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_1.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_1.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-1 saved")

# ==============================================================================
# نمودار 3-2: Histogram + Cumulative - توزیع فراوانی مبالغ قراردادها
# ==============================================================================
print("\nGenerating Chart 3-2: Distribution - Contract Amounts...")

fig, ax1 = plt.subplots(figsize=(20, 12))

contract_amounts = uni_summary[uni_summary['مبلغ قرارداد'] > 0].sort_values('مبلغ قرارداد')

# Histogram
n, bins, patches = ax1.hist(contract_amounts['مبلغ قرارداد'] / 1000, 
                            bins=25, color='#1976D2', alpha=0.7, 
                            edgecolor='black', linewidth=1.5,
                            label=fix_persian_text('تعداد دانشگاه‌ها (فراوانی)'))

colors_hist = plt.cm.Blues(n / n.max())
for patch, color in zip(patches, colors_hist):
    patch.set_facecolor(color)

ax1.set_xlabel(fix_persian_text('مبلغ قرارداد (میلیارد ریال)'), fontsize=18, fontweight='bold')
ax1.set_ylabel(fix_persian_text('تعداد دانشگاه‌ها (فراوانی)'), fontsize=18, fontweight='bold', color='blue')
ax1.tick_params(axis='y', labelcolor='blue', labelsize=14)
ax1.tick_params(axis='x', labelsize=14)
ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
ax1.set_axisbelow(True)

# Cumulative curve
ax2 = ax1.twinx()
cumulative_contracts = contract_amounts['مبلغ قرارداد'].cumsum() / 1000
cumulative_percent = (contract_amounts['مبلغ قرارداد'].cumsum() / 
                     contract_amounts['مبلغ قرارداد'].sum()) * 100

ax2.plot(contract_amounts['مبلغ قرارداد'] / 1000, cumulative_percent, 
        color='red', linewidth=4, marker='o', markersize=5,
        label=fix_persian_text('درصد تجمعی مبلغ قراردادها'))

ax2.set_ylabel(fix_persian_text('درصد تجمعی مبلغ قراردادها (٪)'), 
              fontsize=18, fontweight='bold', color='red')
ax2.tick_params(axis='y', labelcolor='red', labelsize=14)
ax2.set_ylim(0, 105)

# خطوط راهنما
threshold_80 = cumulative_percent[cumulative_percent <= 80].index[-1] if len(cumulative_percent[cumulative_percent <= 80]) > 0 else 0
if threshold_80 > 0:
    ax2.axhline(y=80, color='green', linestyle='--', linewidth=2.5, alpha=0.7)
    ax2.axvline(x=contract_amounts.iloc[threshold_80]['مبلغ قرارداد']/1000, 
               color='green', linestyle='--', linewidth=2.5, alpha=0.7)
    
    num_unis_80 = threshold_80 + 1
    percent_unis_80 = (num_unis_80 / len(contract_amounts)) * 100
    
    ax2.text(contract_amounts.iloc[threshold_80]['مبلغ قرارداد']/1000 * 1.1, 82,
            fix_persian_text(f'{format_number_with_separator(percent_unis_80)}٪ دانشگاه‌ها\n' + 
                           f'({int(num_unis_80)} دانشگاه)\n' +
                           f'= ۸۰٪ قراردادها'),
            fontsize=13, bbox=dict(boxstyle='round,pad=0.8', 
                                  facecolor='yellow', alpha=0.8, 
                                  edgecolor='black', linewidth=2),
            fontweight='bold')

ax1.set_title(fix_persian_text('توزیع فراوانی مبالغ قراردادهای دانشگاه‌ها - نمودار پارتو'),
             fontsize=24, fontweight='bold', pad=20)

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=14, loc='upper left')

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_2.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_2.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-2 saved")

# ==============================================================================
# نمودار 3-3: Horizontal Bar - 20 دانشگاه برتر (قرارداد) - بدون تغییر
# ==============================================================================
print("\nGenerating Chart 3-3: Top 20 Universities - Contracts...")

fig, ax = plt.subplots(figsize=(16, 14))

top_20_uni = uni_summary.nlargest(20, 'مبلغ قرارداد').sort_values('مبلغ قرارداد', ascending=True)

y_pos = np.arange(len(top_20_uni))
values = top_20_uni['مبلغ قرارداد'].values / 1000

colors_gradient = plt.cm.Blues(np.linspace(0.4, 0.9, len(values)))

bars = ax.barh(y_pos, values, color=colors_gradient, alpha=0.8,
              edgecolor='black', linewidth=1.5)

labels = [fix_persian_text(format_text_multiline(name, 40, 2)) for name in top_20_uni['دانشگاه']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=11)

for bar, val, count in zip(bars, values, top_20_uni['تعداد قرارداد']):
    label_text = format_number_with_separator(val) + '\n' + fix_persian_text(f'({int(count)} قرارداد)')
    ax.text(val + max(values)*0.02, bar.get_y() + bar.get_height()/2,
           label_text, ha='left', va='center',
           fontsize=10, fontweight='bold')

ax.set_xlabel(fix_persian_text('مبلغ قراردادها (میلیارد ریال)'), fontsize=16, fontweight='bold')
ax.set_title(fix_persian_text('۲۰ دانشگاه برتر از نظر مبلغ قراردادها'),
             fontsize=22, fontweight='bold', pad=20)
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.tick_params(axis='x', labelsize=12)
ax.set_xlim(0, max(values) * 1.2)

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_3.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_3.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-3 saved")

# ==============================================================================
# نمودار 3-4: Horizontal Bar - 20 دانشگاه برتر (پرداخت) - بدون تغییر
# ==============================================================================
print("\nGenerating Chart 3-4: Top 20 Universities - Payments...")

fig, ax = plt.subplots(figsize=(16, 14))

top_20_pay = uni_summary.nlargest(20, 'مبلغ پرداخت').sort_values('مبلغ پرداخت', ascending=True)

y_pos = np.arange(len(top_20_pay))
values = top_20_pay['مبلغ پرداخت'].values / 1000

colors_gradient = plt.cm.Greens(np.linspace(0.4, 0.9, len(values)))

bars = ax.barh(y_pos, values, color=colors_gradient, alpha=0.8,
              edgecolor='black', linewidth=1.5)

labels = [fix_persian_text(format_text_multiline(name, 40, 2)) for name in top_20_pay['دانشگاه']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=11)

for bar, val in zip(bars, values):
    label_text = format_number_with_separator(val) + ' ' + fix_persian_text('میلیارد')
    ax.text(val + max(values)*0.02, bar.get_y() + bar.get_height()/2,
           label_text, ha='left', va='center',
           fontsize=10, fontweight='bold')

ax.set_xlabel(fix_persian_text('مبلغ پرداخت‌ها (میلیارد ریال)'), fontsize=16, fontweight='bold')
ax.set_title(fix_persian_text('۲۰ دانشگاه برتر از نظر مبلغ پرداخت‌ها'),
             fontsize=22, fontweight='bold', pad=20)
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.tick_params(axis='x', labelsize=12)
ax.set_xlim(0, max(values) * 1.2)

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_4.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_4.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-4 saved")

# ==============================================================================
# نمودار 3-5: Grouped Bar - مقایسه قرارداد و پرداخت - بدون تغییر
# ==============================================================================
print("\nGenerating Chart 3-5: Grouped Bar - Contract vs Payment...")

fig, ax = plt.subplots(figsize=(18, 12))

top_15 = uni_summary.nlargest(15, 'مبلغ قرارداد').sort_values('مبلغ قرارداد', ascending=True)

y_pos = np.arange(len(top_15))
contracts = top_15['مبلغ قرارداد'].values / 1000
payments = top_15['مبلغ پرداخت'].values / 1000

bars1 = ax.barh(y_pos + 0.2, contracts, height=0.35, label=fix_persian_text('مبلغ قرارداد'),
                color='#2196F3', alpha=0.8, edgecolor='black', linewidth=1.5)

bars2 = ax.barh(y_pos - 0.2, payments, height=0.35, label=fix_persian_text('مبلغ پرداخت'),
                color='#4CAF50', alpha=0.9, edgecolor='black', linewidth=1.5)

labels = [fix_persian_text(format_text_multiline(name, 35, 2)) for name in top_15['دانشگاه']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=12)

for bar, val in zip(bars1, contracts):
    if val > 5:
        ax.text(val/2, bar.get_y() + bar.get_height()/2,
               format_number_with_separator(val),
               ha='center', va='center', fontsize=9,
               fontweight='bold', color='white')

for bar, val in zip(bars2, payments):
    if val > 5:
        ax.text(val/2, bar.get_y() + bar.get_height()/2,
               format_number_with_separator(val),
               ha='center', va='center', fontsize=9,
               fontweight='bold', color='white')

ax.set_xlabel(fix_persian_text('مبلغ (میلیارد ریال)'), fontsize=16, fontweight='bold')
ax.set_title(fix_persian_text('مقایسه قرارداد و پرداخت - ۱۵ دانشگاه برتر'),
             fontsize=22, fontweight='bold', pad=20)
ax.legend(fontsize=14, loc='lower right')
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.tick_params(axis='x', labelsize=12)

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_5.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_5.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-5 saved")

# ==============================================================================
# نمودار 3-6: Pie Chart - تمرکز قراردادها (رنگ‌های بهتر)
# ==============================================================================
print("\nGenerating Chart 3-6: Pie Chart - Concentration (Better Colors)...")

fig, ax = plt.subplots(figsize=(15, 11))

top_10 = uni_summary.nlargest(10, 'مبلغ قرارداد')
others = uni_summary.nsmallest(len(uni_summary) - 10, 'مبلغ قرارداد')

sizes = list(top_10['مبلغ قرارداد'].values / 1000)
sizes.append(others['مبلغ قرارداد'].sum() / 1000)

labels = [fix_persian_text(f"{format_text_multiline(name, 20, 2)}\n{format_number_with_separator(val)} میلیارد")
         for name, val in zip(top_10['دانشگاه'], sizes[:-1])]
labels.append(fix_persian_text(f"سایر ({len(others)} دانشگاه)\n{format_number_with_separator(sizes[-1])} میلیارد"))

# رنگ‌های زیباتر و متنوع‌تر
colors = [
    '#FF6B6B',  # قرمز مرجانی
    '#4ECDC4',  # فیروزه‌ای
    '#45B7D1',  # آبی روشن
    '#FFA07A',  # نارنجی کمرنگ
    '#98D8C8',  # سبز دریایی
    '#F7DC6F',  # زرد طلایی
    '#BB8FCE',  # بنفش کمرنگ
    '#85C1E2',  # آبی آسمانی
    '#F8B739',  # نارنجی طلایی
    '#52B788',  # سبز یشمی
    '#CCCCCC'   # خاکستری برای سایر
]

# اضافه کردن explode برای برجسته‌تر شدن قسمت‌های بزرگ
explode = [0.05 if i < 3 else 0.02 for i in range(len(sizes))]

wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                    colors=colors, startangle=90, explode=explode,
                                    textprops={'fontsize': 11, 'weight': 'bold'},
                                    wedgeprops={'edgecolor': 'white', 'linewidth': 2.5})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(14)
    autotext.set_fontweight('bold')
    autotext.set_bbox(dict(boxstyle='round,pad=0.3', facecolor='black', 
                          alpha=0.7, edgecolor='none'))

ax.set_title(fix_persian_text('توزیع قراردادها - ۱۰ دانشگاه برتر + سایر'),
             fontsize=24, fontweight='bold', pad=20)

fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig(output_dir / 'chart_3_6.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_6.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-6 saved")

# ==============================================================================
# نمودار 3-7: Box Plot - پراکندگی مبالغ قراردادی
# ==============================================================================
print("\nGenerating Chart 3-7: Box Plot - Contract Amount Distribution...")

fig, ax = plt.subplots(figsize=(14, 10))

# مبالغ قرارداد در سطح قرارداد (نه دانشگاه)
contract_amounts_all = df_contracts['مجموع مبالغ قراردادها'].values / 1000

bp = ax.boxplot([contract_amounts_all], 
                labels=[fix_persian_text('مبالغ قراردادها')],
                patch_artist=True, notch=True, showmeans=True,
                widths=0.5,
                boxprops=dict(facecolor='#4CAF50', alpha=0.7, linewidth=2.5),
                whiskerprops=dict(linewidth=2.5, color='#388E3C'),
                capprops=dict(linewidth=2.5, color='#388E3C'),
                medianprops=dict(color='#D32F2F', linewidth=3.5),
                meanprops=dict(marker='D', markerfacecolor='#FFA726', 
                             markeredgecolor='black', markersize=12, linewidth=1.5),
                flierprops=dict(marker='o', markerfacecolor='red', markersize=8, 
                              alpha=0.6, markeredgecolor='darkred'))

ax.set_ylabel(fix_persian_text('مبلغ قرارداد (میلیارد ریال)'), fontsize=18, fontweight='bold')
ax.set_title(fix_persian_text('پراکندگی مبالغ قراردادهای منعقد شده'),
             fontsize=24, fontweight='bold', pad=20)

ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=1.2)
ax.set_axisbelow(True)
ax.tick_params(axis='both', labelsize=14)

# آمار
median = np.median(contract_amounts_all)
mean = np.mean(contract_amounts_all)
q1 = np.percentile(contract_amounts_all, 25)
q3 = np.percentile(contract_amounts_all, 75)
min_val = np.min(contract_amounts_all)
max_val = np.max(contract_amounts_all)

textstr = fix_persian_text(
    f'تعداد کل قراردادها: {format_number_with_separator(len(contract_amounts_all))}\n'
    f'حداقل: {format_number_with_separator(min_val)} میلیارد\n'
    f'چارک اول: {format_number_with_separator(q1)} میلیارد\n'
    f'میانه: {format_number_with_separator(median)} میلیارد\n'
    f'میانگین: {format_number_with_separator(mean)} میلیارد\n'
    f'چارک سوم: {format_number_with_separator(q3)} میلیارد\n'
    f'حداکثر: {format_number_with_separator(max_val)} میلیارد'
)
props = dict(boxstyle='round,pad=1', facecolor='lightgreen', alpha=0.9, 
            edgecolor='black', linewidth=2.5)
ax.text(0.98, 0.97, textstr, transform=ax.transAxes, fontsize=13,
        verticalalignment='top', horizontalalignment='right', bbox=props)

# Legend
legend_elements = [
    plt.Line2D([0], [0], color='#D32F2F', linewidth=3.5, label=fix_persian_text('میانه')),
    plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='#FFA726', 
              markersize=12, label=fix_persian_text('میانگین'))
]
ax.legend(handles=legend_elements, fontsize=13, loc='upper left')

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_7.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_7.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-7 saved")

# ==============================================================================
# نمودار 3-8: Scatter - تعداد مشمولین vs مجموع قراردادها
# ==============================================================================
print("\nGenerating Chart 3-8: Scatter - Subjects vs Total Contracts...")

fig, ax = plt.subplots(figsize=(18, 12))

# تمام دانشگاه‌های دارای قرارداد
unis_with_contracts_df = uni_summary[uni_summary['مبلغ قرارداد'] > 0].copy()

x = unis_with_contracts_df['تعداد مشمول']
y = unis_with_contracts_df['مبلغ قرارداد'] / 1000
sizes = unis_with_contracts_df['تعداد قرارداد'] * 30 + 100

scatter = ax.scatter(x, y, s=sizes, alpha=0.6, 
                    c=y, cmap='viridis',
                    edgecolors='black', linewidth=1.5)

# برچسب برای همه دانشگاه‌ها
for _, row in unis_with_contracts_df.iterrows():
    ax.annotate(fix_persian_text(format_text_multiline(row['دانشگاه'], 18, 1)),
               xy=(row['تعداد مشمول'], row['مبلغ قرارداد']/1000),
               xytext=(8, 8), textcoords='offset points',
               fontsize=8, alpha=0.7,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', 
                        alpha=0.4, edgecolor='gray', linewidth=0.8))

ax.set_xlabel(fix_persian_text('تعداد مشمولین طرف قرارداد'), fontsize=18, fontweight='bold')
ax.set_ylabel(fix_persian_text('مجموع مبالغ قراردادها (میلیارد ریال)'), fontsize=18, fontweight='bold')
ax.set_title(fix_persian_text('رابطه تعداد مشمولین و مجموع قراردادهای دانشگاه‌ها\n(اندازه نقاط = تعداد قراردادها)'),
             fontsize=22, fontweight='bold', pad=20)

ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
ax.set_axisbelow(True)

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label(fix_persian_text('مبلغ قرارداد (میلیارد)'), fontsize=15, weight='bold')
cbar.ax.tick_params(labelsize=12)

ax.tick_params(axis='both', labelsize=13)

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_8.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_8.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-8 saved")

# ==============================================================================
# نمودار 3-9: Histogram - توزیع میانگین قرارداد - بدون تغییر
# ==============================================================================
print("\nGenerating Chart 3-9: Histogram - Average Contract Size...")

fig, ax = plt.subplots(figsize=(16, 10))

avg_contracts = uni_summary[uni_summary['میانگین قرارداد'] > 0]['میانگین قرارداد'] / 1000

n, bins, patches = ax.hist(avg_contracts, bins=20, color='#2196F3',
                           alpha=0.7, edgecolor='black', linewidth=1.5)

colors_hist = plt.cm.Blues(n / n.max())
for patch, color in zip(patches, colors_hist):
    patch.set_facecolor(color)

mean_val = avg_contracts.mean()
median_val = avg_contracts.median()

ax.axvline(mean_val, color='red', linestyle='--', linewidth=2.5,
          label=fix_persian_text(f'میانگین: {format_number_with_separator(mean_val)} میلیارد'))
ax.axvline(median_val, color='green', linestyle='--', linewidth=2.5,
          label=fix_persian_text(f'میانه: {format_number_with_separator(median_val)} میلیارد'))

ax.set_xlabel(fix_persian_text('میانگین مبلغ قرارداد (میلیارد ریال)'), fontsize=16, fontweight='bold')
ax.set_ylabel(fix_persian_text('تعداد دانشگاه‌ها (فراوانی)'), fontsize=16, fontweight='bold')
ax.set_title(fix_persian_text('توزیع میانگین مبلغ قرارداد دانشگاه‌ها'),
             fontsize=22, fontweight='bold', pad=20)

ax.legend(fontsize=14)
ax.grid(True, alpha=0.3)
ax.tick_params(labelsize=12)

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_9.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_9.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-9 saved")

# ==============================================================================
# نمودار 3-10: پراکندگی استانی - قراردادها و پرداخت‌ها
# ==============================================================================
print("\nGenerating Chart 3-10: Provincial Distribution...")

# تجمیع به تفکیک استان
province_contracts = df_contracts.groupby('استان')['مجموع مبالغ قراردادها'].sum() / 1000
province_payments = df_payments.groupby('استان')['مجموع مبالغ پرداختی'].sum() / 1000

province_summary = pd.DataFrame({
    'استان': province_contracts.index,
    'مبلغ قرارداد': province_contracts.values
})

province_summary = province_summary.merge(
    pd.DataFrame({'استان': province_payments.index, 'مبلغ پرداخت': province_payments.values}),
    on='استان', how='left'
)
province_summary['مبلغ پرداخت'].fillna(0, inplace=True)

# مرتب‌سازی و انتخاب 15 استان برتر
province_summary = province_summary.sort_values('مبلغ قرارداد', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(18, 12))

x = np.arange(len(province_summary))
width = 0.35

bars1 = ax.bar(x - width/2, province_summary['مبلغ قرارداد'], width, 
              label=fix_persian_text('مبلغ قرارداد'),
              color='#2196F3', alpha=0.8, edgecolor='black', linewidth=1.5)

bars2 = ax.bar(x + width/2, province_summary['مبلغ پرداخت'], width,
              label=fix_persian_text('مبلغ پرداخت'),
              color='#4CAF50', alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_xlabel(fix_persian_text('استان'), fontsize=18, fontweight='bold')
ax.set_ylabel(fix_persian_text('مبلغ (میلیارد ریال)'), fontsize=18, fontweight='bold')
ax.set_title(fix_persian_text('پراکندگی استانی قراردادها و پرداخت‌ها - ۱۵ استان برتر'),
            fontsize=24, fontweight='bold', pad=20)

ax.set_xticks(x)
ax.set_xticklabels([fix_persian_text(prov) for prov in province_summary['استان']],
                   rotation=45, ha='right', fontsize=12)

# اضافه کردن مقادیر روی میله‌ها
for bar in bars1:
    height = bar.get_height()
    if height > 5:
        ax.text(bar.get_x() + bar.get_width()/2., height/2,
               format_number_with_separator(height),
               ha='center', va='center', fontsize=9, 
               fontweight='bold', color='white')

for bar in bars2:
    height = bar.get_height()
    if height > 5:
        ax.text(bar.get_x() + bar.get_width()/2., height/2,
               format_number_with_separator(height),
               ha='center', va='center', fontsize=9, 
               fontweight='bold', color='white')

ax.legend(fontsize=15, loc='upper right')
ax.grid(True, axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.tick_params(axis='y', labelsize=13)

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_10.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_10.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-10 saved")



# ==============================================================================
# Summary Statistics
# ==============================================================================

stats = {
    'تعداد کل دانشگاه‌ها': len(uni_summary),
    'دانشگاه‌های دارای قرارداد': len(uni_summary[uni_summary['مبلغ قرارداد'] > 0]),
    'دانشگاه‌های دارای پرداخت': len(uni_summary[uni_summary['مبلغ پرداخت'] > 0]),
    'تعداد استان‌ها': uni_summary['استان'].nunique(),
    'مجموع قراردادها (میلیارد)': uni_summary['مبلغ قرارداد'].sum() / 1000,
    'مجموع پرداخت‌ها (میلیارد)': uni_summary['مبلغ پرداخت'].sum() / 1000,
    'میانگین قرارداد هر دانشگاه (میلیارد)': uni_summary['مبلغ قرارداد'].mean() / 1000,
    'میانه قرارداد (میلیارد)': uni_summary['مبلغ قرارداد'].median() / 1000,
    'سهم 10 دانشگاه برتر از کل (%)': (uni_summary.nlargest(10, 'مبلغ قرارداد')['مبلغ قرارداد'].sum() / 
                                          uni_summary['مبلغ قرارداد'].sum()) * 100
}

stats_df = pd.DataFrame(list(stats.items()), columns=['شاخص', 'مقدار'])
stats_df.to_excel(output_dir / 'chapter3_statistics_revised.xlsx', index=False)

# Provincial statistics
province_stats = pd.DataFrame({
    'استان': province_summary['استان'],
    'مبلغ قرارداد (میلیارد)': province_summary['مبلغ قرارداد'],
    'مبلغ پرداخت (میلیارد)': province_summary['مبلغ پرداخت']
})
province_stats.to_excel(output_dir / 'provincial_statistics.xlsx', index=False)

print(f"✓ Statistics saved")

# ==============================================================================
# Summary
# ==============================================================================
print("\n" + "="*70)
print("CHAPTER 3 VISUALIZATION COMPLETE (REVISED VERSION)")
print("="*70)
print(f"\nGenerated 10 charts in: {output_dir}")
print(f"  Chart 3-1:  Box Plot - حجم قراردادهای دانشگاه‌ها")
print(f"  Chart 3-2:  Histogram+Cumulative - توزیع مبالغ قراردادها")
print(f"  Chart 3-3:  Horizontal Bar - 20 برتر (قرارداد)")
print(f"  Chart 3-4:  Horizontal Bar - 20 برتر (پرداخت)")
print(f"  Chart 3-5:  Grouped Bar - مقایسه قرارداد و پرداخت")
print(f"  Chart 3-6:  Pie Chart - تمرکز قراردادها (رنگ‌های زیبا)")
print(f"  Chart 3-7:  Box Plot - پراکندگی مبالغ قراردادی")
print(f"  Chart 3-8:  Scatter - مشمولین vs قراردادها")
print(f"  Chart 3-9:  Histogram - میانگین قرارداد")
print(f"  Chart 3-10: Bar Chart - پراکندگی استانی")
print(f"\nKey findings:")
print(f"  - Total universities: {len(uni_summary)}")
print(f"  - With contracts: {len(uni_summary[uni_summary['مبلغ قرارداد'] > 0])}")
print(f"  - Provinces: {uni_summary['استان'].nunique()}")
print(f"  - Top 10 share: {stats['سهم 10 دانشگاه برتر از کل (%)']:.1f}%")
print("\n" + "="*70)