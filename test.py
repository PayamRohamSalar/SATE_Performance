"""
نمودار 3-11: نقشه جغرافیایی ایران - Heatmap مبالغ پرداختی به تفکیک استان
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# To show Farsi Font
import arabic_reshaper
from bidi.algorithm import get_display

# ==============================================================================
# Font Configuration
# ==============================================================================

try:
    from matplotlib import font_manager
    vazir_font = font_manager.FontProperties(family='Vazirmatn')
    plt.rcParams['font.family'] = 'Vazirmatn'
    print("✓ Using Vazirmatn font")
except:
    plt.rcParams['font.family'] = 'DejaVu Sans'
    print("⚠ Vazirmatn not found, using DejaVu Sans")

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
    
    # لیست استان‌های ایران با نام‌های استاندارد
    provinces = {
        'تهران': ['تهران', 'شهید بهشتی', 'علم و صنعت', 'امیرکبیر', 'صنعتی شریف', 'شریف', 'الزهرا', 'خواجه نصیر'],
        'اصفهان': ['اصفهان', 'صنعتی اصفهان'],
        'فارس': ['شیراز'],
        'آذربایجان شرقی': ['تبریز', 'سهند'],
        'خراسان رضوی': ['مشهد', 'فردوسی'],
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
    
    return 'سایر'

def normalize_province_name(name):
    """نرمال‌سازی نام استان برای تطبیق با GeoJSON"""
    # دیکشنری تطبیق نام‌ها
    name_mapping = {
        'آذربایجان شرقی': 'آذربایجان شرقی',
        'آذربایجان غربی': 'آذربایجان غربی',
        'اردبیل': 'اردبیل',
        'اصفهان': 'اصفهان',
        'البرز': 'البرز',
        'ایلام': 'ایلام',
        'بوشهر': 'بوشهر',
        'تهران': 'تهران',
        'چهارمحال و بختیاری': 'چهارمحال و بختیاری',
        'خراسان جنوبی': 'خراسان جنوبی',
        'خراسان رضوی': 'خراسان رضوی',
        'خراسان شمالی': 'خراسان شمالی',
        'خوزستان': 'خوزستان',
        'زنجان': 'زنجان',
        'سمنان': 'سمنان',
        'سیستان و بلوچستان': 'سیستان و بلوچستان',
        'فارس': 'فارس',
        'قزوین': 'قزوین',
        'قم': 'قم',
        'کردستان': 'کردستان',
        'کرمان': 'کرمان',
        'کرمانشاه': 'کرمانشاه',
        'کهگیلویه و بویراحمد': 'کهگیلویه و بویراحمد',
        'گلستان': 'گلستان',
        'گیلان': 'گیلان',
        'لرستان': 'لرستان',
        'مازندران': 'مازندران',
        'مرکزی': 'مرکزی',
        'هرمزگان': 'هرمزگان',
        'همدان': 'همدان',
        'یزد': 'یزد'
    }
    
    return name_mapping.get(name, name)

# ==============================================================================
# Setup
# ==============================================================================

output_dir = Path('./figs/s3_revised')
output_dir.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# Load Data
# ==============================================================================

print("\nLoading data...")
df_payments = pd.read_excel('./data/Credits_Payments.xlsx')

# استخراج استان‌ها
df_payments['استان'] = df_payments['دانشگاه'].apply(extract_province)

# تجمیع پرداخت‌ها به تفکیک استان
province_payments = df_payments.groupby('استان')['مجموع مبالغ پرداختی'].sum() / 1000  # میلیارد

province_data = pd.DataFrame({
    'استان': province_payments.index,
    'مبلغ_پرداخت': province_payments.values
})

# نرمال‌سازی نام استان‌ها
province_data['استان_نرمال'] = province_data['استان'].apply(normalize_province_name)

print(f"Total provinces with payments: {len(province_data)}")
print(f"Total payment amount: {province_data['مبلغ_پرداخت'].sum():.0f} billion")

# ==============================================================================
# Load GeoJSON
# ==============================================================================

print("\nLoading GeoJSON...")

# مسیرهای ممکن برای فایل GeoJSON
possible_paths = [
    './iran-geojson/iran_geo.json',
    './iran-geojson/iran.json',
    './iran_geo.json',
    './data/iran_geo.json',
    '../iran-geojson/iran_geo.json'
]

geojson_path = None
for path in possible_paths:
    if Path(path).exists():
        geojson_path = path
        break

if geojson_path is None:
    print("ERROR: iran_geo.json not found!")
    print("Please make sure the file exists in one of these locations:")
    for path in possible_paths:
        print(f"  - {path}")
    print("\nCreating a placeholder map instead...")
    
    # ایجاد یک نقشه ساده با دیتای فعلی
    fig, ax = plt.subplots(figsize=(16, 14))
    
    # مرتب‌سازی بر اساس مبلغ
    province_data_sorted = province_data.sort_values('مبلغ_پرداخت', ascending=True)
    
    y_pos = np.arange(len(province_data_sorted))
    values = province_data_sorted['مبلغ_پرداخت'].values
    
    colors = plt.cm.YlOrRd(values / values.max())
    
    bars = ax.barh(y_pos, values, color=colors, edgecolor='black', linewidth=1.5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([fix_persian_text(p) for p in province_data_sorted['استان']], fontsize=12)
    
    for bar, val in zip(bars, values):
        ax.text(val + max(values)*0.02, bar.get_y() + bar.get_height()/2,
               format_number_with_separator(val) + ' میلیارد',
               ha='left', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel(fix_persian_text('مبلغ پرداخت (میلیارد ریال)'), fontsize=16, fontweight='bold')
    ax.set_title(fix_persian_text('توزیع استانی پرداخت‌ها\n(نقشه جغرافیایی در دسترس نیست)'),
                fontsize=22, fontweight='bold', pad=20)
    ax.grid(True, axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'chart_3_11.png', dpi=400, bbox_inches='tight', facecolor='white')
    plt.savefig(output_dir / 'chart_3_11.jpg', dpi=400, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("\n✓ Placeholder chart saved as chart_3_11")
    exit()

print(f"✓ Found GeoJSON at: {geojson_path}")

# خواندن فایل GeoJSON
try:
    iran_geo = gpd.read_file(geojson_path)
    print(f"✓ Loaded {len(iran_geo)} provinces from GeoJSON")
    
    # بررسی ستون‌های موجود
    print(f"Available columns: {iran_geo.columns.tolist()}")
    
    # تشخیص ستون نام استان
    name_column = None
    for col in ['name', 'NAME', 'province', 'PROVINCE', 'استان', 'نام']:
        if col in iran_geo.columns:
            name_column = col
            break
    
    if name_column is None:
        print("Warning: Could not find province name column. Using first string column.")
        for col in iran_geo.columns:
            if iran_geo[col].dtype == 'object' and col != 'geometry':
                name_column = col
                break
    
    print(f"Using column '{name_column}' as province name")
    
    # نرمال‌سازی نام‌ها در GeoJSON
    iran_geo['استان_نرمال'] = iran_geo[name_column].apply(normalize_province_name)
    
    # Merge data with geo
    iran_merged = iran_geo.merge(province_data, on='استان_نرمال', how='left')
    iran_merged['مبلغ_پرداخت'].fillna(0, inplace=True)
    
    print(f"✓ Merged data: {iran_merged['مبلغ_پرداخت'].notna().sum()} provinces with payment data")

except Exception as e:
    print(f"ERROR loading GeoJSON: {e}")
    exit()

# ==============================================================================
# نمودار 3-11: نقشه جغرافیایی Heatmap
# ==============================================================================
print("\nGenerating Chart 3-11: Geographic Heatmap...")

fig, ax = plt.subplots(figsize=(20, 16))

# ترسیم نقشه با colormap
iran_merged.plot(column='مبلغ_پرداخت', 
                 cmap='YlOrRd',  # Yellow-Orange-Red
                 linewidth=1.5,
                 edgecolor='black',
                 legend=False,
                 ax=ax,
                 missing_kwds={'color': 'lightgrey', 'label': 'بدون داده'})

# حذف محورها
ax.set_axis_off()

# عنوان
title_text = fix_persian_text('نقشه توزیع جغرافیایی پرداخت‌ها به دانشگاه‌ها\n(میلیارد ریال)')
ax.set_title(title_text, fontsize=28, fontweight='bold', pad=30)

# اضافه کردن نام و مقدار روی هر استان
for idx, row in iran_merged.iterrows():
    try:
        # مرکز هر استان
        centroid = row.geometry.centroid
        x, y = centroid.x, centroid.y
        
        # نام استان
        province_name = fix_persian_text(row['استان'] if pd.notna(row['استان']) else row['استان_نرمال'])
        
        # مقدار
        amount = row['مبلغ_پرداخت']
        
        if amount > 0:
            # نمایش نام و مقدار
            text = f"{province_name}\n{format_number_with_separator(amount)}"
            fontsize = 9 if amount < 10 else (11 if amount < 50 else 13)
            
            ax.annotate(text, xy=(x, y), ha='center', va='center',
                       fontsize=fontsize, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', 
                               facecolor='white', 
                               alpha=0.85,
                               edgecolor='black',
                               linewidth=1.5),
                       zorder=10)
        else:
            # فقط نام برای استان‌های بدون داده
            ax.annotate(province_name, xy=(x, y), ha='center', va='center',
                       fontsize=8, alpha=0.6, style='italic')
    except:
        continue

# Colorbar دستی
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

# محدوده رنگ‌ها
vmin = 0
vmax = iran_merged['مبلغ_پرداخت'].max()

norm = Normalize(vmin=vmin, vmax=vmax)
sm = ScalarMappable(cmap='YlOrRd', norm=norm)
sm.set_array([])

# اضافه کردن colorbar
cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', 
                   pad=0.02, aspect=50, shrink=0.6)
cbar.set_label(fix_persian_text('مبلغ پرداخت (میلیارد ریال)'), 
              fontsize=18, fontweight='bold')
cbar.ax.tick_params(labelsize=14)

# تبدیل تیک‌ها به فارسی
ticks = cbar.get_ticks()
cbar.ax.set_xticklabels([format_number_with_separator(tick) for tick in ticks])

# اضافه کردن جعبه آمار
stats_text = fix_persian_text(
    f'تعداد استان‌های فعال: {(iran_merged["مبلغ_پرداخت"] > 0).sum()}\n'
    f'مجموع پرداخت‌ها: {format_number_with_separator(iran_merged["مبلغ_پرداخت"].sum())} میلیارد\n'
    f'میانگین: {format_number_with_separator(iran_merged[iran_merged["مبلغ_پرداخت"] > 0]["مبلغ_پرداخت"].mean())} میلیارد\n'
    f'بیشترین: {format_number_with_separator(vmax)} میلیارد'
)

props = dict(boxstyle='round,pad=1.2', facecolor='wheat', alpha=0.95, 
            edgecolor='black', linewidth=2.5)
ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
        fontsize=14, verticalalignment='top',
        bbox=props, zorder=10)

plt.tight_layout()
plt.savefig(output_dir / 'chart_3_11.png', dpi=400, bbox_inches='tight', facecolor='white')
plt.savefig(output_dir / 'chart_3_11.jpg', dpi=400, bbox_inches='tight', facecolor='white', 
           pil_kwargs={'quality': 95})
plt.close()

print(f"✓ Chart 3-11 saved")

# ذخیره داده‌های استانی
iran_merged[['استان_نرمال', 'مبلغ_پرداخت']].to_excel(
    output_dir / 'geographic_payments.xlsx', index=False
)

print("\n" + "="*70)
print("GEOGRAPHIC HEATMAP COMPLETE")
print("="*70)
print(f"Chart saved: {output_dir}/chart_3_11.png")
print(f"Active provinces: {(iran_merged['مبلغ_پرداخت'] > 0).sum()}")
print(f"Total payments: {iran_merged['مبلغ_پرداخت'].sum():.0f} billion IRR")
print("="*70)