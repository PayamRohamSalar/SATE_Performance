"""
فصل دوم: تحلیل عملکرد مشمولین
تولید نمودارهای تحلیلی برای فصل دوم گزارش
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# To show Farsi Font
import arabic_reshaper
from bidi.algorithm import get_display

# ==============================================================================
# Font Configuration
# ==============================================================================

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
    'دانشگاه': 'count'  # تعداد قراردادها
}).reset_index()

subjects_summary.columns = ['نام مشمول', 'اعتبار', 'دستگاه', 'مبلغ قرارداد', 'تعداد قرارداد']

# اضافه کردن داده‌های پرداخت
payments_summary = df_payments.groupby('نام مشمول').agg({
    'مجموع مبالغ پرداختی': 'sum'
}).reset_index()
payments_summary.columns = ['نام مشمول', 'مبلغ پرداخت']

# ادغام داده‌ها
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

# تعداد دانشگاه‌های همکار
uni_count = df_contracts.groupby('نام مشمول')['دانشگاه'].nunique().reset_index()
uni_count.columns = ['نام مشمول', 'تعداد دانشگاه']
subjects_summary = subjects_summary.merge(uni_count, on='نام مشمول', how='left')

print(f"\nTotal subjects: {len(subjects_summary)}")
print(f"Subjects with contracts: {len(subjects_summary[subjects_summary['مبلغ قرارداد'] > 0])}")
print(f"Subjects with payments: {len(subjects_summary[subjects_summary['مبلغ پرداخت'] > 0])}")

# ==============================================================================
# نمودار 2-1: Treemap - توزیع اعتبارات تکلیفی
# ==============================================================================
print("\nGenerating Chart 2-1: Treemap...")

import squarify

fig, ax = plt.subplots(figsize=(20, 12))

# مرتب‌سازی و انتخاب 30 مشمول برتر
top_30 = subjects_summary.nlargest(30, 'اعتبار')

# محاسبه اندازه‌ها
sizes = top_30['اعتبار'].values / 1000  # به میلیارد
labels = [fix_persian_text(f"{name[:40]}...\n{format_number_with_separator(val/1000)} میلیارد") 
          for name, val in zip(top_30['نام مشمول'], top_30['اعتبار'])]

# رنگ‌بندی بر اساس درصد قرارداد
colors = plt.cm.RdYlGn(top_30['درصد قرارداد'] / 100)

# رسم treemap
squarify.plot(sizes=sizes, label=labels, alpha=0.8, color=colors,
              text_kwargs={'fontsize': 11, 'weight': 'bold'},  # سایز فونت برچسب‌های treemap
              ax=ax, pad=True)

ax.axis('off')

# عنوان
title_text = fix_persian_text('توزیع اعتبارات تکلیفی بین ۳۰ مشمول برتر (میلیارد ریال)')
plt.title(title_text, fontsize=24, fontweight='bold', pad=20)  # سایز فونت عنوان نمودار 2-1

# Colorbar
sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=plt.Normalize(vmin=0, vmax=100))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.02, aspect=50)
cbar.set_label(fix_persian_text('درصد تحقق قرارداد (%)'), fontsize=14, weight='bold')  # سایز فونت برچسب colorbar
cbar.ax.tick_params(labelsize=12)  # سایز اعداد colorbar

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_1.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_1.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-1 saved")

# ==============================================================================
# نمودار 2-2: Scatter Plot - رابطه اعتبار و قرارداد
# ==============================================================================
print("\nGenerating Chart 2-2: Scatter Plot...")

fig, ax = plt.subplots(figsize=(18, 12))

# داده‌ها بر حسب میلیارد
x = subjects_summary['اعتبار'] / 1000
y = subjects_summary['مبلغ قرارداد'] / 1000
colors_scatter = subjects_summary['درصد قرارداد']
sizes_scatter = subjects_summary['تعداد دانشگاه'] * 100 + 100

# رسم scatter
scatter = ax.scatter(x, y, c=colors_scatter, s=sizes_scatter, 
                     alpha=0.6, cmap='RdYlGn', edgecolors='black', linewidth=1.5)

# خط هدف 30%
x_line = np.linspace(0, x.max(), 100)
y_line = x_line * 0.30
ax.plot(x_line, y_line, 'r--', linewidth=3, alpha=0.7, 
        label=fix_persian_text('خط هدف ۳۰٪'))

# برچسب‌گذاری مشمولین برتر
top_10_credits = subjects_summary.nlargest(10, 'اعتبار')
for _, row in top_10_credits.iterrows():
    if row['مبلغ قرارداد'] > 0:
        ax.annotate(fix_persian_text(row['نام مشمول'][:25]),
                   xy=(row['اعتبار']/1000, row['مبلغ قرارداد']/1000),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=9, alpha=0.7,  # سایز فونت برچسب‌های نقاط
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))

# تنظیمات محورها
ax.set_xlabel(fix_persian_text('اعتبار تکلیفی (میلیارد ریال)'), 
              fontsize=16, fontweight='bold')  # سایز فونت برچسب محور X
ax.set_ylabel(fix_persian_text('مبلغ قراردادها (میلیارد ریال)'), 
              fontsize=16, fontweight='bold')  # سایز فونت برچسب محور Y
ax.set_title(fix_persian_text('رابطه بین اعتبار تکلیفی و مبلغ قراردادهای منعقد شده'), 
             fontsize=22, fontweight='bold', pad=20)  # سایز فونت عنوان نمودار 2-2

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
ax.set_axisbelow(True)

# Colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label(fix_persian_text('درصد تحقق قرارداد (%)'), 
               fontsize=14, weight='bold')  # سایز فونت برچسب colorbar
cbar.ax.tick_params(labelsize=12)  # سایز اعداد colorbar

# Legend
ax.legend(fontsize=14, loc='upper left')  # سایز فونت legend

# محورها
ax.tick_params(axis='both', labelsize=12)  # سایز اعداد محورها

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_2.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_2.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-2 saved")

# ==============================================================================
# نمودار 2-3: Horizontal Bar - درصد تحقق قرارداد (20 برتر)
# ==============================================================================
print("\nGenerating Chart 2-3: Horizontal Bar...")

fig, ax = plt.subplots(figsize=(16, 14))

# انتخاب 20 مشمول با بالاترین اعتبار
top_20 = subjects_summary.nlargest(20, 'اعتبار').sort_values('درصد قرارداد', ascending=True)

y_pos = np.arange(len(top_20))
percentages = top_20['درصد قرارداد'].values

# رنگ‌بندی
colors_bar = ['#D32F2F' if p < 10 else '#FF9800' if p < 20 else '#4CAF50' 
              for p in percentages]

# رسم نمودار
bars = ax.barh(y_pos, percentages, color=colors_bar, alpha=0.8, edgecolor='black', linewidth=1.5)

# خط هدف 30%
ax.axvline(x=30, color='red', linestyle='--', linewidth=3, alpha=0.7,
          label=fix_persian_text('هدف ۳۰٪'))

# برچسب‌ها
labels = [fix_persian_text(name[:40]) for name in top_20['نام مشمول']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=12)  # سایز فونت نام مشمولین

# نمایش درصد روی میله‌ها
for i, (bar, pct, credit) in enumerate(zip(bars, percentages, top_20['اعتبار']/1000)):
    width = bar.get_width()
    label_text = fix_persian_text(f'{pct:.1f}%')
    ax.text(width + 1, bar.get_y() + bar.get_height()/2,
           label_text, ha='left', va='center', 
           fontsize=11, fontweight='bold')  # سایز فونت درصدها روی میله‌ها

# تنظیمات
ax.set_xlabel(fix_persian_text('درصد تحقق قرارداد (%)'), 
              fontsize=16, fontweight='bold')  # سایز فونت برچسب محور X
ax.set_title(fix_persian_text('درصد تحقق قرارداد - ۲۰ مشمول برتر از نظر اعتبار'), 
             fontsize=22, fontweight='bold', pad=20)  # سایز فونت عنوان نمودار 2-3
ax.set_xlim(0, max(percentages) + 10)

# Grid
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Legend
ax.legend(fontsize=14, loc='lower right')  # سایز فونت legend

ax.tick_params(axis='x', labelsize=12)  # سایز اعداد محور X

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_3.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_3.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-3 saved")

# ==============================================================================
# نمودار 2-4: Heatmap - تعداد قراردادها (مشمول × دانشگاه)
# ==============================================================================
print("\nGenerating Chart 2-4: Heatmap...")

# ایجاد ماتریس تعداد قراردادها
contract_matrix = df_contracts.groupby(['نام مشمول', 'دانشگاه']).size().reset_index(name='تعداد')

# انتخاب 15 مشمول و 15 دانشگاه برتر
top_subjects = subjects_summary.nlargest(15, 'اعتبار')['نام مشمول'].values
top_unis = df_contracts.groupby('دانشگاه').size().nlargest(15).index.values

contract_matrix_filtered = contract_matrix[
    (contract_matrix['نام مشمول'].isin(top_subjects)) & 
    (contract_matrix['دانشگاه'].isin(top_unis))
]

# Pivot
pivot_matrix = contract_matrix_filtered.pivot(
    index='نام مشمول', 
    columns='دانشگاه', 
    values='تعداد'
).fillna(0)

fig, ax = plt.subplots(figsize=(20, 12))

# رسم heatmap
sns.heatmap(pivot_matrix, annot=True, fmt='.0f', cmap='YlOrRd', 
            linewidths=0.5, cbar_kws={'label': fix_persian_text('تعداد قرارداد')},
            ax=ax, annot_kws={'fontsize': 10})  # سایز فونت اعداد داخل heatmap

# تنظیمات
ax.set_xlabel(fix_persian_text('دانشگاه'), fontsize=16, fontweight='bold')  # سایز فونت برچسب محور X
ax.set_ylabel(fix_persian_text('مشمول'), fontsize=16, fontweight='bold')  # سایز فونت برچسب محور Y
ax.set_title(fix_persian_text('ماتریس تعداد قراردادها - ۱۵ مشمول برتر × ۱۵ دانشگاه برتر'), 
             fontsize=22, fontweight='bold', pad=20)  # سایز فونت عنوان نمودار 2-4

# برچسب‌ها
ax.set_xticklabels([fix_persian_text(str(label.get_text())[:30]) 
                    for label in ax.get_xticklabels()], 
                   rotation=45, ha='right', fontsize=11)  # سایز فونت نام دانشگاه‌ها
ax.set_yticklabels([fix_persian_text(str(label.get_text())[:40]) 
                    for label in ax.get_yticklabels()], 
                   rotation=0, fontsize=11)  # سایز فونت نام مشمولین

# Colorbar
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=12)  # سایز اعداد colorbar

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_4.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_4.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-4 saved")

# ==============================================================================
# نمودار 2-5: Waterfall - مقایسه اعتبار، قرارداد، پرداخت
# ==============================================================================
print("\nGenerating Chart 2-5: Waterfall...")

fig, ax = plt.subplots(figsize=(18, 10))

# محاسبه مقادیر کل
total_credit = subjects_summary['اعتبار'].sum() / 1000
total_contract = subjects_summary['مبلغ قرارداد'].sum() / 1000
total_payment = subjects_summary['مبلغ پرداخت'].sum() / 1000

# داده‌های waterfall
categories = [
    fix_persian_text('اعتبار تکلیفی'),
    fix_persian_text('کاهش: بدون قرارداد'),
    fix_persian_text('قراردادهای منعقد شده'),
    fix_persian_text('کاهش: بدون پرداخت'),
    fix_persian_text('پرداخت‌های انجام شده')
]

values = [
    total_credit,
    -(total_credit - total_contract),
    total_contract,
    -(total_contract - total_payment),
    total_payment
]

# محاسبه موقعیت‌ها
positions = [0, 0, 0, 0, 0]
positions[0] = 0
positions[1] = positions[0] + values[0]
positions[2] = positions[1] + values[1]
positions[3] = positions[2] + values[2]
positions[4] = positions[3] + values[3]

heights = [values[0], values[1], values[2], values[3], values[4]]
bottoms = [0, positions[0], positions[1], positions[2], positions[3]]

colors_waterfall = ['#2196F3', '#F44336', '#4CAF50', '#FF9800', '#9C27B0']

# رسم میله‌ها
bars = ax.bar(range(len(categories)), 
              [abs(h) for h in heights], 
              bottom=bottoms,
              color=colors_waterfall, 
              alpha=0.8, 
              edgecolor='black', 
              linewidth=2)

# خطوط اتصال
for i in range(len(categories)-1):
    if i in [0, 2]:  # خطوط افقی
        y = bottoms[i+1]
        ax.plot([i+0.4, i+1-0.4], [y, y], 'k--', linewidth=2, alpha=0.5)

# برچسب‌ها
for i, (bar, val) in enumerate(zip(bars, heights)):
    height = bar.get_height()
    label_text = format_number_with_separator(abs(val))
    ax.text(bar.get_x() + bar.get_width()/2, 
           bar.get_y() + height/2,
           label_text, 
           ha='center', va='center',
           fontsize=14, fontweight='bold', color='white',  # سایز فونت اعداد روی میله‌ها
           bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.3))

# تنظیمات
ax.set_xticks(range(len(categories)))
ax.set_xticklabels(categories, fontsize=14, fontweight='bold')  # سایز فونت برچسب‌های محور X
ax.set_ylabel(fix_persian_text('مبلغ (میلیارد ریال)'), 
              fontsize=16, fontweight='bold')  # سایز فونت برچسب محور Y
ax.set_title(fix_persian_text('جریان اعتبارات: از تخصیص تا پرداخت (آبشاری)'), 
             fontsize=22, fontweight='bold', pad=20)  # سایز فونت عنوان نمودار 2-5

ax.grid(True, axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.tick_params(axis='y', labelsize=12)  # سایز اعداد محور Y

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_5.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_5.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-5 saved")

# ==============================================================================
# نمودار 2-6: Bullet Chart - پیشرفت پرداخت (15 برتر)
# ==============================================================================
print("\nGenerating Chart 2-6: Bullet Chart...")

fig, ax = plt.subplots(figsize=(16, 14))

# انتخاب 15 مشمول برتر
top_15 = subjects_summary.nlargest(15, 'اعتبار').sort_values('درصد پرداخت از قرارداد', ascending=True)

y_pos = np.arange(len(top_15))

# رسم پس‌زمینه (هدف)
ax.barh(y_pos, [100]*len(top_15), height=0.6, 
        color='#E0E0E0', alpha=0.5, label=fix_persian_text('سقف ۱۰۰٪'))

# رسم قرارداد
contract_pct = (top_15['مبلغ قرارداد'] / top_15['اعتبار'] * 100).values
ax.barh(y_pos, contract_pct, height=0.5, 
        color='#2196F3', alpha=0.7, label=fix_persian_text('درصد قرارداد'))

# رسم پرداخت
payment_pct = top_15['درصد پرداخت از قرارداد'].values
bars_payment = ax.barh(y_pos, payment_pct, height=0.3, 
                       color='#4CAF50', alpha=0.9, label=fix_persian_text('درصد پرداخت از قرارداد'))

# خط هدف
ax.axvline(x=67, color='red', linestyle='--', linewidth=3, alpha=0.7,
          label=fix_persian_text('هدف ۶۷٪'))

# برچسب‌ها
labels = [fix_persian_text(name[:35]) for name in top_15['نام مشمول']]
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=11)  # سایز فونت نام مشمولین

# نمایش درصد
for i, (bar, pct) in enumerate(zip(bars_payment, payment_pct)):
    if pct > 5:
        label_text = fix_persian_text(f'{pct:.1f}%')
        ax.text(pct/2, bar.get_y() + bar.get_height()/2,
               label_text, ha='center', va='center',
               fontsize=10, fontweight='bold', color='white')  # سایز فونت درصدها داخل میله

# تنظیمات
ax.set_xlabel(fix_persian_text('درصد (%)'), fontsize=16, fontweight='bold')  # سایز فونت برچسب محور X
ax.set_title(fix_persian_text('پیشرفت پرداخت نسبت به قرارداد - ۱۵ مشمول برتر'), 
             fontsize=22, fontweight='bold', pad=20)  # سایز فونت عنوان نمودار 2-6
ax.set_xlim(0, 110)

ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.legend(fontsize=12, loc='lower right')  # سایز فونت legend
ax.tick_params(axis='x', labelsize=12)  # سایز اعداد محور X

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_6.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_6.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-6 saved")

# ==============================================================================
# نمودار 2-7: Funnel - قیف تبدیل
# ==============================================================================
print("\nGenerating Chart 2-7: Funnel...")

fig, ax = plt.subplots(figsize=(14, 10))

# محاسبه مراحل قیف
stages = [
    fix_persian_text('اعتبارات تکلیفی'),
    fix_persian_text('قراردادهای منعقد شده'),
    fix_persian_text('پرداخت‌های انجام شده')
]

values_funnel = [
    total_credit,
    total_contract,
    total_payment
]

percentages_funnel = [100, (total_contract/total_credit)*100, (total_payment/total_credit)*100]

colors_funnel = ['#2196F3', '#4CAF50', '#FF9800']

# رسم قیف
y_pos_funnel = np.arange(len(stages))
widths = [p/100 * 2 for p in percentages_funnel]

for i, (stage, width, color, value, pct) in enumerate(zip(stages, widths, colors_funnel, values_funnel, percentages_funnel)):
    # مستطیل
    left = 1 - width/2
    rect = plt.Rectangle((left, i-0.3), width, 0.6, 
                         facecolor=color, edgecolor='black', linewidth=2, alpha=0.8)
    ax.add_patch(rect)
    
    # متن مرحله
    ax.text(1, i, stage, 
           ha='center', va='center', fontsize=16, fontweight='bold',  # سایز فونت نام مراحل
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='black', linewidth=2))
    
    # مقدار و درصد
    value_text = format_number_with_separator(value) + '\n' + \
                 fix_persian_text(f'میلیارد ریال') + '\n' + \
                 fix_persian_text(f'({pct:.1f}%)')
    ax.text(1, i-0.6, value_text,
           ha='center', va='top', fontsize=13, fontweight='bold')  # سایز فونت مقادیر

# خطوط اتصال
for i in range(len(stages)-1):
    ax.plot([1, 1], [i+0.3, i+0.7], 'k--', linewidth=2, alpha=0.5)

# تنظیمات
ax.set_xlim(0, 2)
ax.set_ylim(-1, len(stages))
ax.axis('off')

title_text = fix_persian_text('قیف تبدیل اعتبارات در سامانه ساتع')
ax.text(1, len(stages)+0.3, title_text,
       ha='center', va='bottom', fontsize=24, fontweight='bold')  # سایز فونت عنوان نمودار 2-7

fig.patch.set_facecolor('white')

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_7.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_7.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-7 saved")

# ==============================================================================
# تحلیل به تفکیک دستگاه‌های اجرایی
# ==============================================================================

# تجمیع به تفکیک دستگاه
dept_summary = subjects_summary.groupby('دستگاه').agg({
    'اعتبار': 'sum',
    'مبلغ قرارداد': 'sum',
    'مبلغ پرداخت': 'sum',
    'نام مشمول': 'count'
}).reset_index()

dept_summary.columns = ['دستگاه', 'اعتبار', 'مبلغ قرارداد', 'مبلغ پرداخت', 'تعداد مشمول']

dept_summary['درصد قرارداد'] = (dept_summary['مبلغ قرارداد'] / dept_summary['اعتبار']) * 100
dept_summary['درصد پرداخت'] = (dept_summary['مبلغ پرداخت'] / dept_summary['اعتبار']) * 100
dept_summary['درصد پرداخت از قرارداد'] = np.where(
    dept_summary['مبلغ قرارداد'] > 0,
    (dept_summary['مبلغ پرداخت'] / dept_summary['مبلغ قرارداد']) * 100,
    0
)

# ==============================================================================
# نمودار 2-8: Sunburst - توزیع سلسله‌مراتبی
# ==============================================================================
print("\nGenerating Chart 2-8: Sunburst...")

# این نمودار با plotly بهتر است، اما برای matplotlib از pie استفاده می‌کنیم
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# Pie 1: دستگاه‌های اجرایی
dept_top = dept_summary.nlargest(10, 'اعتبار')
sizes_dept = dept_top['اعتبار'].values / 1000
labels_dept = [fix_persian_text(f"{d[:20]}\n{format_number_with_separator(s)} میلیارد") 
               for d, s in zip(dept_top['دستگاه'], sizes_dept)]

wedges1, texts1, autotexts1 = ax1.pie(sizes_dept, labels=labels_dept, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 11})  # سایز فونت برچسب‌های pie

for autotext in autotexts1:
    autotext.set_color('white')
    autotext.set_fontsize(12)  # سایز فونت درصدها داخل pie
    autotext.set_fontweight('bold')

ax1.set_title(fix_persian_text('توزیع اعتبارات به تفکیک دستگاه اجرایی'), 
              fontsize=18, fontweight='bold', pad=20)  # سایز فونت عنوان pie اول

# Pie 2: مشمولین برتر
subjects_top = subjects_summary.nlargest(15, 'اعتبار')
sizes_subj = subjects_top['اعتبار'].values / 1000
labels_subj = [fix_persian_text(f"{s[:15]}\n{format_number_with_separator(sz)} میلیارد") 
               for s, sz in zip(subjects_top['نام مشمول'], sizes_subj)]

wedges2, texts2, autotexts2 = ax2.pie(sizes_subj, labels=labels_subj, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 10})  # سایز فونت برچسب‌های pie

for autotext in autotexts2:
    autotext.set_color('white')
    autotext.set_fontsize(11)  # سایز فونت درصدها داخل pie
    autotext.set_fontweight('bold')

ax2.set_title(fix_persian_text('توزیع اعتبارات - ۱۵ مشمول برتر'), 
              fontsize=18, fontweight='bold', pad=20)  # سایز فونت عنوان pie دوم

plt.suptitle(fix_persian_text('توزیع سلسله‌مراتبی اعتبارات'), 
             fontsize=24, fontweight='bold', y=0.98)  # سایز فونت عنوان اصلی نمودار 2-8

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_8.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_8.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-8 saved")

# ==============================================================================
# نمودار 2-9: Radar Chart - مقایسه دستگاه‌ها
# ==============================================================================
print("\nGenerating Chart 2-9: Radar Chart...")

from math import pi

fig, ax = plt.subplots(figsize=(14, 14), subplot_kw=dict(projection='polar'))

# انتخاب 6 دستگاه برتر
top_6_depts = dept_summary.nlargest(6, 'اعتبار')

# معیارها
categories = [
    fix_persian_text('درصد قرارداد'),
    fix_persian_text('درصد پرداخت'),
    fix_persian_text('پرداخت از قرارداد'),
    fix_persian_text('تعداد مشمول'),
    fix_persian_text('تنوع دانشگاه')
]

# نرمال‌سازی تعداد مشمول و تنوع دانشگاه به درصد
dept_uni_diversity = []
for _, dept_row in top_6_depts.iterrows():
    dept_unis = df_contracts[df_contracts['دستگاه اجرایی مرتبط'] == dept_row['دستگاه']]['دانشگاه'].nunique()
    dept_uni_diversity.append(dept_unis)

max_subject = top_6_depts['تعداد مشمول'].max()
max_uni = max(dept_uni_diversity)

# رسم برای هر دستگاه
angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
angles += angles[:1]

colors_radar = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336', '#00BCD4']

for i, (_, row) in enumerate(top_6_depts.iterrows()):
    values = [
        row['درصد قرارداد'],
        row['درصد پرداخت'],
        row['درصد پرداخت از قرارداد'],
        (row['تعداد مشمول'] / max_subject) * 100,
        (dept_uni_diversity[i] / max_uni) * 100
    ]
    values += values[:1]
    
    ax.plot(angles, values, 'o-', linewidth=2, color=colors_radar[i], 
           label=fix_persian_text(row['دستگاه'][:25]))
    ax.fill(angles, values, alpha=0.15, color=colors_radar[i])

# تنظیمات
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=13, fontweight='bold')  # سایز فونت برچسب‌های محورها
ax.set_ylim(0, 100)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['۲۰', '۴۰', '۶۰', '۸۰', '۱۰۰'], fontsize=11)  # سایز فونت اعداد شعاعی
ax.grid(True, linestyle='--', alpha=0.7)

ax.set_title(fix_persian_text('مقایسه چند بعدی دستگاه‌های اجرایی'), 
             fontsize=22, fontweight='bold', pad=30, y=1.08)  # سایز فونت عنوان نمودار 2-9

ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)  # سایز فونت legend

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_9.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_9.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-9 saved")

# ==============================================================================
# نمودار 2-10: Grouped Bar - مقایسه اعتبار، قرارداد، پرداخت (دستگاه‌ها)
# ==============================================================================
print("\nGenerating Chart 2-10: Grouped Bar...")

fig, ax = plt.subplots(figsize=(18, 10))

# انتخاب 10 دستگاه برتر
top_10_depts = dept_summary.nlargest(10, 'اعتبار').sort_values('اعتبار', ascending=True)

y_pos_grouped = np.arange(len(top_10_depts))
bar_height = 0.25

# رسم میله‌ها
bars1 = ax.barh(y_pos_grouped - bar_height, top_10_depts['اعتبار']/1000, 
                bar_height, label=fix_persian_text('اعتبار تکلیفی'), 
                color='#2196F3', alpha=0.8, edgecolor='black', linewidth=1)

bars2 = ax.barh(y_pos_grouped, top_10_depts['مبلغ قرارداد']/1000, 
                bar_height, label=fix_persian_text('مبلغ قراردادها'), 
                color='#4CAF50', alpha=0.8, edgecolor='black', linewidth=1)

bars3 = ax.barh(y_pos_grouped + bar_height, top_10_depts['مبلغ پرداخت']/1000, 
                bar_height, label=fix_persian_text('مبلغ پرداخت‌ها'), 
                color='#FF9800', alpha=0.8, edgecolor='black', linewidth=1)

# برچسب‌ها
labels_grouped = [fix_persian_text(d[:40]) for d in top_10_depts['دستگاه']]
ax.set_yticks(y_pos_grouped)
ax.set_yticklabels(labels_grouped, fontsize=12)  # سایز فونت نام دستگاه‌ها

# تنظیمات
ax.set_xlabel(fix_persian_text('مبلغ (میلیارد ریال)'), fontsize=16, fontweight='bold')  # سایز فونت برچسب محور X
ax.set_title(fix_persian_text('مقایسه اعتبار، قرارداد و پرداخت به تفکیک دستگاه اجرایی'), 
             fontsize=22, fontweight='bold', pad=20)  # سایز فونت عنوان نمودار 2-10

ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.legend(fontsize=14, loc='lower right')  # سایز فونت legend
ax.tick_params(axis='x', labelsize=12)  # سایز اعداد محور X

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_10.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_10.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-10 saved")

# ==============================================================================
# نمودار 2-11: Box Plot - توزیع نرخ‌ها
# ==============================================================================
print("\nGenerating Chart 2-11: Box Plot...")

fig, ax = plt.subplots(figsize=(14, 10))

# داده‌ها
data_box = [
    subjects_summary['درصد قرارداد'].dropna(),
    subjects_summary['درصد پرداخت از اعتبار'].dropna(),
    subjects_summary['درصد پرداخت از قرارداد'].dropna()
]

labels_box = [
    fix_persian_text('نرخ تحقق\nقرارداد'),
    fix_persian_text('نرخ پرداخت\nاز اعتبار'),
    fix_persian_text('نرخ پرداخت\nاز قرارداد')
]

# رسم box plot
bp = ax.boxplot(data_box, labels=labels_box, patch_artist=True,
                notch=True, showmeans=True,
                boxprops=dict(facecolor='lightblue', alpha=0.7, linewidth=2),
                whiskerprops=dict(linewidth=2),
                capprops=dict(linewidth=2),
                medianprops=dict(color='red', linewidth=3),
                meanprops=dict(marker='D', markerfacecolor='green', markersize=8))

# رنگ‌آمیزی
colors_box = ['#2196F3', '#4CAF50', '#FF9800']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)

# خطوط هدف
ax.axhline(y=30, color='red', linestyle='--', linewidth=2, alpha=0.7,
          label=fix_persian_text('هدف قرارداد: ۳۰٪'))
ax.axhline(y=20, color='orange', linestyle='--', linewidth=2, alpha=0.7,
          label=fix_persian_text('هدف پرداخت: ۲۰٪'))
ax.axhline(y=67, color='purple', linestyle='--', linewidth=2, alpha=0.7,
          label=fix_persian_text('هدف پرداخت از قرارداد: ۶۷٪'))

# تنظیمات
ax.set_ylabel(fix_persian_text('درصد (%)'), fontsize=16, fontweight='bold')  # سایز فونت برچسب محور Y
ax.set_title(fix_persian_text('توزیع نرخ تحقق و پرداخت در بین مشمولین'), 
             fontsize=22, fontweight='bold', pad=20)  # سایز فونت عنوان نمودار 2-11
ax.set_ylim(-5, 105)

ax.grid(True, axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.legend(fontsize=12, loc='upper right')  # سایز فونت legend
ax.tick_params(axis='both', labelsize=13)  # سایز فونت برچسب‌ها و اعداد

plt.tight_layout()
plt.savefig(output_dir / 'chart_2_11.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_2_11.jpg', dpi=400, bbox_inches='tight', facecolor='white', pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 2-11 saved")

# ==============================================================================
# Summary
# ==============================================================================
print("\n" + "="*70)
print("CHAPTER 2 VISUALIZATION COMPLETE")
print("="*70)
print(f"\nGenerated {11} charts in: {output_dir}")
print(f"  Chart 2-1:  Treemap - توزیع اعتبارات")
print(f"  Chart 2-2:  Scatter - رابطه اعتبار و قرارداد")
print(f"  Chart 2-3:  Horizontal Bar - درصد تحقق قرارداد")
print(f"  Chart 2-4:  Heatmap - ماتریس قراردادها")
print(f"  Chart 2-5:  Waterfall - جریان اعتبارات")
print(f"  Chart 2-6:  Bullet - پیشرفت پرداخت")
print(f"  Chart 2-7:  Funnel - قیف تبدیل")
print(f"  Chart 2-8:  Sunburst/Pie - توزیع سلسله‌مراتبی")
print(f"  Chart 2-9:  Radar - مقایسه دستگاه‌ها")
print(f"  Chart 2-10: Grouped Bar - مقایسه دستگاه‌ها")
print(f"  Chart 2-11: Box Plot - توزیع نرخ‌ها")
print("\n" + "="*70)