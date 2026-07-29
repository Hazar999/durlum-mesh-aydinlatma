
from __future__ import annotations

import math
import base64
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ROOM_TARGETS = {
    "Ofis / çalışma alanı": 500.0,
    "Toplantı odası": 500.0,
    "Teknik çizim / hassas çalışma": 750.0,
    "Üretim alanı / genel çalışma": 300.0,
    "Koridor": 100.0,
    "Resepsiyon / lobi": 200.0,
    "Depo": 200.0,
    "Özel / elle gir": 500.0,
}


PRODUCT_FAMILIES = [
    "Expanded Metal / RHOMBOS",
    "Open Cell / Raster Tavan",
    "Baffle / Dikey Lamel",
    "Character Özel Sistemler",
    "Akustik Çözümler",
]

# Aşağıdaki tablolar yüklenen durlum kataloglarında açıkça verilen bilgilerden
# oluşturulmuştur. Katalogda doğrulanmayan hücreler özellikle boş bırakılmıştır.
OPEN_CELL_CATALOG = [
    {
        "system": "STARLAM 4", "category": "Lineer Raster", "panel_size": "1200×600 / 1250×625 mm; maks. boy 1800 mm",
        "blade_width_mm": "4", "blade_height_mm": "42", "grid_spacing_mm": "30–75",
        "material": "Alüminyum", "thickness_mm": "", "installation": "U94 / T15 / T24 / entegre taşıyıcı",
        "lighting": "OMEGA 40", "visual_character": "Açık, dekoratif ve lineer", "notes": "Yatay veya düşey uygulamalar mümkündür.",
    },
    {
        "system": "STARLAM 9", "category": "Lineer Raster", "panel_size": "1200×600 / 1250×625 mm; maks. boy 1800 mm",
        "blade_width_mm": "9", "blade_height_mm": "40", "grid_spacing_mm": "30–100",
        "material": "Alüminyum", "thickness_mm": "", "installation": "U94 / T15 / T24 / entegre taşıyıcı",
        "lighting": "OMEGA 40", "visual_character": "Açık, dekoratif ve lineer", "notes": "Yatay veya düşey uygulamalar mümkündür.",
    },
    {
        "system": "STARLAM 15", "category": "Lineer Raster", "panel_size": "1200×600 / 1250×625 mm; maks. boy 1800 mm",
        "blade_width_mm": "15", "blade_height_mm": "37", "grid_spacing_mm": "40–100",
        "material": "Alüminyum", "thickness_mm": "", "installation": "U94 / T15 / T24 / entegre taşıyıcı",
        "lighting": "OMEGA 40", "visual_character": "Açık, dekoratif ve lineer", "notes": "Yatay veya düşey uygulamalar mümkündür.",
    },
    {"system": "STAR 3", "category": "Lineer Raster", "panel_size": "Projeye göre", "blade_width_mm": "3", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Katalog/proje detayına göre", "lighting": "Projeye göre", "visual_character": "Hafif ve zarif lineer görünüm", "notes": "Yatay ve düşey uygulanabilir."},
    {"system": "STAR 9", "category": "Lineer Raster", "panel_size": "Projeye göre", "blade_width_mm": "9", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Katalog/proje detayına göre", "lighting": "Projeye göre", "visual_character": "Hafif ve zarif lineer görünüm", "notes": "Yatay ve düşey uygulanabilir."},
    {"system": "STAR 15", "category": "Lineer Raster", "panel_size": "Projeye göre", "blade_width_mm": "15", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Katalog/proje detayına göre", "lighting": "Projeye göre", "visual_character": "Hafif ve zarif lineer görünüm", "notes": "Yatay ve düşey uygulanabilir."},
    {"system": "VARIO 3", "category": "Lineer Raster", "panel_size": "Projeye göre", "blade_width_mm": "3", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Katalog/proje detayına göre", "lighting": "Projeye göre", "visual_character": "Lineer", "notes": "Kesin ölçüler proje verisiyle doğrulanmalıdır."},
    {"system": "TICELL-N", "category": "Çok Yönlü Raster", "panel_size": "Projeye göre", "blade_width_mm": "", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Projeye göre", "lighting": "Entegre çözümler mümkün", "visual_character": "Çok yönlü hücresel", "notes": "Kesin ölçüler katalog/proje detayıyla doğrulanmalıdır."},
    {"system": "QUADRA-DECOR", "category": "Çok Yönlü Raster", "panel_size": "Projeye göre", "blade_width_mm": "", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Projeye göre", "lighting": "Perforasyonla ışık yayılımını destekler", "visual_character": "Dalgalı, modern ve havadar", "notes": "Düzensiz perforasyon heterojen bir tavan görüntüsü oluşturur."},
    {"system": "LIVA", "category": "Çok Yönlü Raster", "panel_size": "1200 mm modül uzunluğu", "blade_width_mm": "98", "blade_height_mm": "100 / 150 / 200", "grid_spacing_mm": "100 / 120", "material": "Alüminyum", "thickness_mm": "0,8", "installation": "U94", "lighting": "Projeye göre", "visual_character": "Derin, çok yönlü lamel", "notes": "Taşıyıcı aralığı en çok 1200 mm olarak gösterilir."},
    {"system": "PYTHA", "category": "Çok Yönlü Raster", "panel_size": "1385,64×600 mm (0,831 m²)", "blade_width_mm": "9", "blade_height_mm": "40", "grid_spacing_mm": "86 / 100 / 120 / 150", "material": "Alüminyum", "thickness_mm": "0,4", "installation": "Entegre taşıyıcı", "lighting": "PYTHA-LIGHT C150", "visual_character": "Paralelkenar, çok yönlü", "notes": "Taşıyıcılar arası mesafe 1200 mm."},
    {"system": "QUADRA", "category": "Tek Lamelli Hücre", "panel_size": "Projeye göre", "blade_width_mm": "Değişken", "blade_height_mm": "Değişken", "grid_spacing_mm": "Değişken", "material": "Ön boyalı alüminyum", "thickness_mm": "", "installation": "Projeye göre", "lighting": "Leuchtenraster ve ışıklık kapaması için uygun", "visual_character": "Hafif ve havadar", "notes": "Hücre ölçüsü, yüksekliği ve biçimi projeye göre değişebilir."},
    {"system": "ETINCELL", "category": "Tek Lamelli Hücre", "panel_size": "Projeye göre", "blade_width_mm": "", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Projeye göre", "lighting": "Projeye göre", "visual_character": "Tek lamelli hücresel", "notes": "Kesin ölçüler katalog/proje detayıyla doğrulanmalıdır."},
    {"system": "TICELL", "category": "Tek Lamelli Hücre", "panel_size": "1200×600 mm", "blade_width_mm": "", "blade_height_mm": "40", "grid_spacing_mm": "33,33×33,33 / 54,55×54,55 hücre", "material": "Alüminyum", "thickness_mm": "0,6 / 0,95", "installation": "U94 / T15 / T24", "lighting": "LUMEO-R ile korona etkisi", "visual_character": "Hücresel ve geçirgen", "notes": "Başka formatlar talep üzerine mümkündür."},
    {"system": "GEO", "category": "Çift Lamelli Hücre", "panel_size": "Projeye göre", "blade_width_mm": "", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Projeye göre", "lighting": "Projeye göre", "visual_character": "Modern, dekoratif ve keskin kenarlı", "notes": "Çok sayıda renk seçeneğiyle projeye uyarlanabilir."},
    {"system": "GEOTE", "category": "Çift Lamelli Hücre", "panel_size": "Projeye göre", "blade_width_mm": "", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Projeye göre", "lighting": "Projeye göre", "visual_character": "Prestijli ve homojen", "notes": "AVM, showroom, havalimanı ve kamusal yapılar için katalogda öne çıkarılır."},
    {"system": "GETINCELL", "category": "Çift Lamelli Hücre", "panel_size": "Projeye göre", "blade_width_mm": "", "blade_height_mm": "", "grid_spacing_mm": "", "material": "Alüminyum", "thickness_mm": "", "installation": "Projeye göre", "lighting": "Projeye göre", "visual_character": "Çift lamelli hücresel", "notes": "Kesin ölçüler katalog/proje detayıyla doğrulanmalıdır."},
]

BAFFLE_CATALOG = [
    {"system": "POLYLAM", "category": "Dikey Lamel", "width_min_mm": None, "width_max_mm": None, "width_options": "40 / 63 / 100", "length_min_mm": None, "length_max_mm": None, "height_min_mm": 40, "height_max_mm": 360, "module_rule": "Projeye göre", "build_height_extra_mm": None, "access": "Standart", "lighting": "OMEGA 40 / OMEGA 63 / PUNTEO-S", "acoustic": "Opsiyonel", "cooling": "Opsiyonel", "notes": "Açık tavan, mekânı sınırlayan güçlü lineer karakter ve akustik seçenekler."},
    {"system": "POLYLAM-KS", "category": "Açılır / Kayar Dikey Lamel", "width_min_mm": 30, "width_max_mm": 100, "width_options": "Standart 40 / 63 / 100", "length_min_mm": 300, "length_max_mm": 2000, "height_min_mm": 100, "height_max_mm": 360, "module_rule": "Minimum aralık = lamel genişliği + 20 mm", "build_height_extra_mm": 89, "access": "Açılır ve kayar; aletsiz tavan boşluğu erişimi", "lighting": "OMEGA / PUNTEO", "acoustic": "Opsiyonel", "cooling": "Hayır", "notes": "Sık revizyon gereken alanlar için uygundur."},
    {"system": "POLYLAM-S", "category": "Kayar Dikey Lamel", "width_min_mm": 30, "width_max_mm": 100, "width_options": "Standart 40 / 63 / 100", "length_min_mm": 300, "length_max_mm": 2000, "height_min_mm": 100, "height_max_mm": 360, "module_rule": "Minimum aralık = lamel genişliği + 20 mm", "build_height_extra_mm": 89, "access": "Kayar", "lighting": "OMEGA / PUNTEO", "acoustic": "Opsiyonel", "cooling": "Hayır", "notes": "POLYLAM'ın tamamen kayar varyantıdır."},
    {"system": "POLYLAM KREUZRASTER", "category": "Çapraz Grid Dikey Lamel", "width_min_mm": 25, "width_max_mm": 100, "width_options": "25–100", "length_min_mm": None, "length_max_mm": None, "height_min_mm": 40, "height_max_mm": 360, "module_rule": "Modül serbest seçilebilir", "build_height_extra_mm": None, "access": "Projeye göre", "lighting": "Kesintisiz entegre aydınlatma", "acoustic": "Opsiyonel", "cooling": "Opsiyonel", "notes": "Foyer, konferans, galeri ve resepsiyon alanları için güçlü geometrik etki."},
    {"system": "POLYLAM dur-COOLTEC", "category": "Soğutmalı Dikey Lamel", "width_min_mm": None, "width_max_mm": None, "width_options": "Projeye göre", "length_min_mm": None, "length_max_mm": None, "height_min_mm": None, "height_max_mm": None, "module_rule": "Projeye göre", "build_height_extra_mm": None, "access": "Projeye göre", "lighting": "Entegre çözümler", "acoustic": "Opsiyonel", "cooling": "Evet", "notes": "Kesin kapasite ve ölçüler proje mühendisliğiyle doğrulanmalıdır."},
    {"system": "POLYLAM dur-SONIC", "category": "Akustik Dikey Lamel Tamamlayıcısı", "width_min_mm": 600, "width_max_mm": 600, "width_options": "Standart 600", "length_min_mm": None, "length_max_mm": None, "height_min_mm": 100, "height_max_mm": 300, "module_rule": "Standart 600×245 mm", "build_height_extra_mm": None, "access": "Sabit", "lighting": "Yok / çevresel", "acoustic": "Düşük frekans; αw=1,00 [L]", "cooling": "Hayır", "notes": "Standart yükseklik 245 mm; ağırlık yaklaşık 10 kg/lfm; perforasyon Rv L6."},
]

CHARACTER_CATALOG = [
    {"system": "LOOP TYP 2", "category": "Açık Tasarım Tavanı", "main_function": "Organik formlara uyarlanabilen açık metal tavan", "standard_dimension": "Panel 1124,23×1004,25 mm; modül 1115,44×966 mm; derz 2 mm", "lighting": "PUNTEO-J60", "acoustic": "dur-SONIC TUBE ile opsiyonel", "cooling": "Projeye göre", "access": "Alt konstrüksiyona vidalı", "calculation_mode": "Serbest kesit + proje geometrisi", "notes": "Serbest kesit %50'den fazladır; OA tabanlı RHOMBOS hesabı kullanılmaz."},
    {"system": "LOOP TYP 3", "category": "Mıknatıslı Açık Tasarım Tavanı", "main_function": "Açık tavan, aydınlatma ve tesisat entegrasyonu", "standard_dimension": "Projeye göre", "lighting": "PUNTEO-J60", "acoustic": "Perfore S7-KS arka tavanla standart akustik etki", "cooling": "dur-COOLTEC TYP 1.1 ile mümkün", "access": "Mıknatıslı, güvenlik halatlı ve aletsiz erişim", "calculation_mode": "Proje geometrisi + entegre tesisatlar", "notes": "Havalandırma, sprinkler ve kablo hatları entegre edilebilir."},
    {"system": "OPEN SKY", "category": "Translüsent Cam Işıklı Tavan", "main_function": "Homojen geniş yüzey aydınlatması", "standard_dimension": "500×500–1200×1200 mm; önerilen modül yaklaşık 1 m²; çevresel derz 8 mm", "lighting": "Geniş açılı reflektörlerle tavan üstü aydınlatma", "acoustic": "Hayır", "cooling": "Hayır", "access": "Aletsiz açılır cam elemanlar", "calculation_mode": "Ölçülmüş cam geçirgenliği + armatür fotometrisi", "notes": "Minimum sistem yüksekliği 363 mm; çapraz reflektörlü çözümde genellikle 510 mm."},
    {"system": "TOMEO-R", "category": "Tavan–Aydınlatma Kombinasyonu", "main_function": "Yuvarlak metal tavan elemanları ve LUMEO-R ışık yüzeyleri", "standard_dimension": "Tavan elemanları Ø293 / 593 / 893 / 1200 mm; yükseklik 60 mm", "lighting": "LUMEO-R LED / LIGHT PIPE", "acoustic": "Dolgu ile mümkün", "cooling": "Standartta opsiyonel", "access": "Kablo veya M6/M8 tij ile montaj", "calculation_mode": "Armatür bazlı fotometrik hesap + yerleşim", "notes": "Sprinkler ve havalandırma elemanları tavan kompozisyonuna entegre edilebilir."},
    {"system": "TOMEO-R ACTIVE", "category": "Termal Tavan Adası", "main_function": "Beton çekirdek aktivasyonlu yapılarda akustik ve iklimsel tavan adası", "standard_dimension": "Ø1200 mm örneği; yükseklik 60 mm", "lighting": "LUMEO-R ile birlikte", "acoustic": "Evet", "cooling": "Evet", "access": "Projeye göre", "calculation_mode": "Termal kapasite + akustik + fotometri", "notes": "Kesin performans için mekanik proje verileri gerekir."},
    {"system": "FLUID", "category": "Serbest Formlu Metal Tavan", "main_function": "Yaratıcı, eğrisel metal tavan ve aydınlatma", "standard_dimension": "Projeye özel", "lighting": "Entegre / projeye özel", "acoustic": "Perfore panel ve akustik dolgu ile mümkün", "cooling": "Projeye göre", "access": "Mıknatıslı ve güvenlik halatlı; aletsiz erişim", "calculation_mode": "Proje geometrisi", "notes": "Elemanlar 10 mm derzle yerleştirilebilir; havalandırma, sprinkler ve kablolar entegre edilebilir."},
    {"system": "DOMUS S-OMEGA", "category": "Kavisli Işık Kanalı", "main_function": "Kavisli lineer aydınlatma kanalı", "standard_dimension": "Projeye özel", "lighting": "S-OMEGA kavisli ışık kanalı", "acoustic": "Projeye göre", "cooling": "Projeye göre", "access": "Projeye göre", "calculation_mode": "Kavis geometrisi + armatür fotometrisi", "notes": "Özellikle alçak hacimlerde açık mekân hissini destekler."},
    {"system": "DOMUS", "category": "Kavisli Tavan–Aydınlatma Sistemi", "main_function": "Kavisli tavanla mimari mekân etkisi", "standard_dimension": "Projeye özel", "lighting": "Entegre", "acoustic": "Projeye göre", "cooling": "Projeye göre", "access": "Projeye göre", "calculation_mode": "Proje geometrisi + fotometri", "notes": "Standart bir OA veya hücre hesabıyla değerlendirilemez."},
]

ACOUSTIC_CATALOG = [
    {"system": "POLYLAM dur-SONIC", "category": "Düşük Frekans Absorberi", "standard_dimension": "600×245 mm", "special_dimension": "Yükseklik 100–300 mm; genişlik standart 600 mm", "material": "Galvanizli sac", "perforation": "Rv L6", "absorption": "αw=1,00 [L]", "weight": "Yaklaşık 10 kg/lfm", "mounting": "POLYLAM sistemiyle birlikte", "notes": "POLYLAM'ın orta ve yüksek frekanstaki etkisini düşük frekansta tamamlar."},
    {"system": "dur-SONIC QUAD", "category": "Düşük Frekans Duvar Absorberi", "standard_dimension": "800×800 / 1200×1100 / 1800×800 mm; kalınlık 120 mm", "special_dimension": "Maks. yükseklik 2800 mm; maks. genişlik 1100 mm; derinlik 100 mm", "material": "Galvanizli sac", "perforation": "Yan yüzler Qg L17", "absorption": "αw=0,45 [LM]", "weight": "Yaklaşık 25 kg/m²", "mounting": "Duvara doğrudan veya boşluklu", "notes": "Boşluklu kurulum yüksek frekanslardaki absorpsiyonu da artırabilir."},
]

LIGHTING_INTEGRATIONS = [
    {"ceiling_system": "POLYLAM 40", "lighting_system": "OMEGA 40", "integration_type": "Lineer entegre", "compatibility": "40 mm lamel ile uyumlu", "notes": "Kesintisiz ışık çizgisi."},
    {"ceiling_system": "POLYLAM 63", "lighting_system": "OMEGA 63", "integration_type": "Lineer entegre", "compatibility": "63 mm lamel ile uyumlu", "notes": "Renk uyumlu lineer kanal."},
    {"ceiling_system": "POLYLAM 40", "lighting_system": "PUNTEO-S", "integration_type": "Noktasal entegre", "compatibility": "40 mm lamel ile uyumlu", "notes": "Minimal armatür; Tunable White seçeneği bulunabilir."},
    {"ceiling_system": "STARLAM", "lighting_system": "OMEGA 40", "integration_type": "Lineer entegre", "compatibility": "STARLAM ailesi", "notes": "Katalogda uygun ışık kanalı olarak belirtilir."},
    {"ceiling_system": "PYTHA", "lighting_system": "PYTHA-LIGHT C150", "integration_type": "Sisteme özel LED insert", "compatibility": "PYTHA", "notes": "Entegre taşıyıcıyla birlikte değerlendirilir."},
    {"ceiling_system": "TICELL", "lighting_system": "LUMEO-R", "integration_type": "Arkadan ışıklı yüzey", "compatibility": "TICELL", "notes": "Hücre ve perforasyonlardan korona etkisi oluşturur."},
    {"ceiling_system": "LOOP TYP 2 / 3", "lighting_system": "PUNTEO-J60", "integration_type": "Noktasal entegre", "compatibility": "LOOP açıklıkları", "notes": "Karakteristik yuvarlak açıklıklara uyumlu."},
    {"ceiling_system": "OPEN SKY", "lighting_system": "Geniş açılı reflektör", "integration_type": "Tavan üstü dolaylı", "compatibility": "Cam tavan", "notes": "Homojen yüzey aydınlatması için çapraz ışınım önerilir."},
    {"ceiling_system": "TOMEO-R", "lighting_system": "LUMEO-R LED", "integration_type": "Yuvarlak ışık yüzeyi", "compatibility": "TOMEO-R", "notes": "Homojen DUROSATIN kapaklı ışık yüzeyi."},
]

LOGO_B64 = "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"

st.set_page_config(
    page_title="Durlum Tavan Sistemleri ve Aydınlatma",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root {
    --brand:#1898d4;
    --brand-dark:#123a5a;
    --brand-soft:#edf7fc;
    --ink:#1f2a37;
    --muted:#6b7280;
    --line:#dbe6ee;
    --card:#ffffff;
    --bg:#f4f7fb;
    --success:#2f9e44;
    --warn:#f59f00;
    --shadow:0 10px 28px rgba(18,58,90,.08);
}
html, body, [class*="css"]  { font-family: Inter, Segoe UI, Arial, sans-serif; }
.stApp { background: linear-gradient(180deg,#f8fbfd 0%, #f2f6fa 100%); color: var(--ink); }
.block-container { padding-top: 1rem; max-width: 1540px; }
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; }

.app-shell {
    background: rgba(255,255,255,.72);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(220,231,239,.85);
    border-radius: 24px;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
    overflow: hidden;
}
.app-topbar {
    display:flex; align-items:center; justify-content:space-between;
    padding: 18px 22px 10px 22px; border-bottom:1px solid var(--line);
}
.brand-wrap { display:flex; align-items:center; gap:16px; }
.logo-box {
    width:74px; height:74px; border-radius:0; overflow:hidden;
    border:1px solid #d7e7f1; background:white; flex-shrink:0;
    box-shadow: 0 6px 18px rgba(24,152,212,.15);
}
.logo-box img { width:100%; height:100%; object-fit:cover; display:block; }
.brand-title { font-size:1.85rem; font-weight:800; color:var(--brand-dark); line-height:1.1; }
.brand-subtitle { color:var(--muted); font-size:.96rem; margin-top:4px; }
.chip-row { display:flex; gap:10px; flex-wrap:wrap; }
.chip {
    background:var(--brand-soft); color:var(--brand-dark); border:1px solid #cfe8f7;
    padding:8px 12px; border-radius:999px; font-size:.86rem; font-weight:600;
}

[data-baseweb="tab-list"] { gap:10px; padding: 8px 18px 0 18px; }
button[data-baseweb="tab"] {
    height:46px; border-radius:14px 14px 0 0; padding:0 16px;
    background:transparent; color:var(--muted); font-weight:700;
}
button[data-baseweb="tab"] p { font-size:0.96rem; }
button[data-baseweb="tab"][aria-selected="true"] { color:var(--brand); background:white; border-bottom:3px solid var(--brand); }

.section-title { font-size:1.2rem; font-weight:800; color:var(--brand-dark); margin:0 0 8px 0; }
.section-subtitle { font-size:.92rem; color:var(--muted); margin:0 0 16px 0; }

.input-panel {
    background:rgba(255,255,255,.92); border:1px solid var(--line); border-radius:22px;
    padding:18px 18px 14px 18px; box-shadow: var(--shadow);
}
.input-group-title {
    margin:18px 0 10px 0; font-size:.92rem; letter-spacing:.03em; font-weight:800;
    color:var(--brand-dark); text-transform:uppercase;
}
.hero-card {
    background: linear-gradient(135deg,#ffffff 0%, #fbfdff 55%, #f0f7fb 100%);
    border:1px solid var(--line); border-radius:22px; box-shadow: var(--shadow);
    padding:18px; min-height:146px;
}
.hero-inner { display:flex; gap:18px; align-items:stretch; }
.hero-visual {
    width:260px; min-width:260px; border-radius:18px;
    background: linear-gradient(135deg,#e9f2f8 0%, #f7fbff 60%, #ddeaf3 100%);
    border:1px solid #dce7ee; display:flex; align-items:center; justify-content:center;
    color:#99a8b6; font-weight:700; overflow:hidden; position:relative;
}
.hero-visual::before {
    content:""; position:absolute; inset:0;
    background:
      linear-gradient(135deg, rgba(24,152,212,.10), rgba(24,152,212,0) 60%),
      repeating-linear-gradient(0deg, transparent 0 18px, rgba(24,58,90,.045) 18px 19px),
      repeating-linear-gradient(90deg, transparent 0 18px, rgba(24,58,90,.045) 18px 19px);
}
.hero-visual span { position:relative; z-index:1; text-align:center; padding:10px; }
.hero-content h2 { margin:4px 0 8px 0; color:var(--brand-dark); font-size:2rem; line-height:1.15; }
.hero-content p { margin:0; color:var(--muted); font-size:1rem; line-height:1.55; max-width:860px; }

.notice-bar {
    margin-top:14px; background:#eef5fb; border:1px solid #d9e7f3; color:#39566f;
    border-radius:14px; padding:12px 14px; font-size:.96rem;
}

.metric-card {
    background: white; border:1px solid var(--line); border-radius:18px; padding:14px 16px;
    box-shadow: var(--shadow); min-height:108px;
}
.metric-label { color:var(--muted); font-size:.9rem; font-weight:600; margin-bottom:8px; }
.metric-value { color:var(--brand-dark); font-size:2rem; font-weight:800; line-height:1.1; }
.metric-sub { color:#8293a1; font-size:.88rem; margin-top:6px; }
.badge { display:inline-block; margin-top:10px; padding:5px 10px; border-radius:999px; font-size:.8rem; font-weight:700; }
.badge-blue { background:#e8f4fb; color:#1572a6; }
.badge-green { background:#eaf8ee; color:#2f9e44; }
.badge-amber { background:#fff4df; color:#c57d00; }

.compare-box {
    background:white; border:1px solid var(--line); border-radius:18px; box-shadow: var(--shadow);
    padding:16px;
}
.performance-grid { display:grid; grid-template-columns: 1.2fr .9fr; gap:18px; }
.simple-chart { position:relative; height:230px; padding:10px 16px 8px 16px; }
.chart-area {
    height:160px; display:flex; align-items:flex-end; justify-content:space-around; gap:18px;
    border-bottom:2px solid #d5e1eb; border-left:2px solid #d5e1eb; padding:0 10px 0 16px; margin-top:10px;
}
.bar-wrap { display:flex; flex-direction:column; align-items:center; gap:8px; width:30%; }
.bar { width:58px; border-radius:10px 10px 0 0; position:relative; }
.bar-grey { background:linear-gradient(180deg,#dfe4ea 0%, #c7d0db 100%); }
.bar-slate { background:linear-gradient(180deg,#9db0c2 0%, #7f92a5 100%); }
.bar-blue { background:linear-gradient(180deg,#1ca4df 0%, #1688c0 100%); }
.bar-label { font-size:.85rem; color:#5d6d7c; text-align:center; }
.bar-value { font-weight:800; color:var(--brand-dark); }
.target-line {
    position:absolute; left:14px; right:8px; border-top:2px dashed #7b8a99;
}
.target-pill {
    position:absolute; right:18px; transform:translateY(-14px);
    background:white; border:1px solid #dbe5ee; border-radius:999px; padding:2px 9px;
    font-size:.8rem; color:#536371; font-weight:700;
}
.mini-list { display:grid; gap:10px; margin-top:8px; }
.mini-row { display:flex; justify-content:space-between; gap:10px; border-bottom:1px dashed #e1eaf0; padding-bottom:8px; }
.mini-row span:first-child { color:#6a7784; }
.mini-row span:last-child { color:var(--brand-dark); font-weight:700; text-align:right; }
.dot-green::before, .dot-amber::before { content:"●"; margin-right:7px; }
.dot-green::before { color:#2f9e44; }
.dot-amber::before { color:#f59f00; }

.layout-card {
    background:white; border:1px solid var(--line); border-radius:18px; padding:16px; box-shadow: var(--shadow);
}
.recommendation-card {
    background:white; border:1px solid var(--line); border-left:6px solid var(--brand);
    border-radius:18px; padding:16px; box-shadow: var(--shadow); margin-bottom:12px;
}
.recommendation-card h4 { margin:0 0 6px 0; color:var(--brand-dark); font-size:1.12rem; }
.recommendation-meta { color:#6b7785; font-size:.92rem; margin-bottom:12px; line-height:1.5; }
.recommendation-card ul { margin:6px 0 10px 20px; }
.recommendation-card li { margin-bottom:4px; }
.callout {
    background:#fffdfa; border:1px solid #f3e7c1; color:#7b6320; border-radius:16px;
    padding:13px 15px; margin: 12px 0;
}
.info-callout {
    background:#f2f8fc; border:1px solid #d9e8f4; color:#476177; border-radius:16px;
    padding:13px 15px; margin: 12px 0;
}

.stDataFrame, div[data-testid="stMetric"] { border-radius:18px; overflow:hidden; }
[data-testid="stMetric"] {
    border:1px solid var(--line); box-shadow: var(--shadow); background:white; padding:12px;
}
[data-testid="stMetricLabel"] { color:#6b7280; }
[data-testid="stMetricValue"] { color:var(--brand-dark); }

.stButton button, .stDownloadButton button {
    background: linear-gradient(135deg,#1798d4 0%, #147cb0 100%) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    padding:.7rem 1rem !important; font-weight:700 !important;
    box-shadow: 0 10px 24px rgba(23,152,212,.18);
}
.stSelectbox label, .stNumberInput label, .stRadio label, .stSlider label, .stCheckbox label {
    font-weight:600 !important; color:#51606e !important;
}
div[data-baseweb="select"] > div, .stNumberInput > div > div > input { border-radius:12px !important; }

.footer-note { color:#6f7f8f; font-size:.88rem; margin-top:12px; }

.family-shell {
    background:white; border:1px solid var(--line); border-radius:20px; padding:14px 16px;
    box-shadow:var(--shadow); margin:14px 0 16px 0;
}
.family-kicker { color:var(--muted); font-size:.86rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; }
.family-title { color:var(--brand-dark); font-weight:800; font-size:1.18rem; margin-top:3px; }
.fact-card { background:white; border:1px solid var(--line); border-radius:17px; padding:14px; box-shadow:var(--shadow); min-height:120px; }
.fact-card .fact-name { color:var(--muted); font-size:.85rem; font-weight:700; margin-bottom:7px; }
.fact-card .fact-value { color:var(--brand-dark); font-size:1.1rem; line-height:1.35; font-weight:800; }
.fact-card .fact-note { color:#7a8996; font-size:.84rem; margin-top:7px; line-height:1.45; }
.product-summary { background:linear-gradient(135deg,#f7fbfe,#eef7fc); border:1px solid #d8e9f4; border-radius:18px; padding:15px 17px; margin:10px 0; }
@media (max-width: 1200px) {
  .hero-inner { flex-direction:column; }
  .hero-visual { width:100%; min-width:100%; height:180px; }
  .performance-grid { grid-template-columns: 1fr; }
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    meshes = pd.read_csv(DATA_DIR / "meshes.csv")
    systems = pd.read_csv(DATA_DIR / "systems.csv")
    return meshes, systems


def tr_number(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def lighting_values(room_area_m2: float, fixture_count: int, lumens_per_fixture: float,
                    utilization_factor: float, maintenance_factor: float,
                    transmission: float, light_position: str, target_lux: float) -> dict[str, float]:
    base_flux = fixture_count * lumens_per_fixture * utilization_factor * maintenance_factor
    no_mesh_lux = base_flux / room_area_m2 if room_area_m2 > 0 else 0.0
    effective_t = transmission if light_position == "Mesh üstünde" else 1.0
    with_mesh_lux = no_mesh_lux * effective_t
    denominator = lumens_per_fixture * utilization_factor * maintenance_factor * effective_t
    required = math.ceil((target_lux * room_area_m2) / denominator) if denominator > 0 else 0
    return {
        "no_mesh_lux": no_mesh_lux,
        "with_mesh_lux": with_mesh_lux,
        "loss_pct": max(0.0, (1.0 - effective_t) * 100.0),
        "required_count": required,
        "effective_t": effective_t,
    }


def grid_options(required_count: int, room_length: float, room_width: float, limit: int = 3) -> list[dict[str, float]]:
    if required_count <= 0 or room_length <= 0 or room_width <= 0:
        return []
    aspect = room_length / room_width
    max_axis = max(2, math.ceil(math.sqrt(required_count)) * 3)
    candidates = []
    for rows in range(1, max_axis + 1):
        for columns in range(1, max_axis + 1):
            total = rows * columns
            if total < required_count:
                continue
            extra = total - required_count
            grid_aspect = columns / rows
            aspect_penalty = abs(math.log(max(grid_aspect, 1e-9) / aspect))
            score = extra * 0.25 + aspect_penalty
            candidates.append({
                "rows": rows,
                "columns": columns,
                "total": total,
                "extra": extra,
                "length_spacing": room_length / columns,
                "width_spacing": room_width / rows,
                "length_edge": room_length / (2 * columns),
                "width_edge": room_width / (2 * rows),
                "score": score,
            })
    candidates.sort(key=lambda item: (item["score"], item["extra"], item["total"]))
    unique, seen = [], set()
    for item in candidates:
        key = (int(item["rows"]), int(item["columns"]))
        if key not in seen:
            unique.append(item)
            seen.add(key)
        if len(unique) >= limit:
            break
    return unique


def score_higher(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    if valid.empty:
        return pd.Series(50.0, index=series.index)
    low, high = valid.min(), valid.max()
    if math.isclose(float(low), float(high)):
        result = pd.Series(100.0, index=series.index)
        return result.where(numeric.notna(), 0.0)
    return ((numeric - low) / (high - low) * 100).fillna(0.0)


def score_lower(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    if valid.empty:
        return pd.Series(50.0, index=series.index)
    low, high = valid.min(), valid.max()
    if math.isclose(float(low), float(high)):
        result = pd.Series(100.0, index=series.index)
        return result.where(numeric.notna(), 0.0)
    return ((high - numeric) / (high - low) * 100).fillna(0.0)


def visual_preference_score(open_area: pd.Series, preference: str) -> pd.Series:
    if preference == "Daha açık tavan":
        return score_higher(open_area)
    if preference == "Daha kapalı görünüm":
        return score_lower(open_area)
    return pd.Series(50.0, index=open_area.index)


def describe_candidate(row: pd.Series, eligible: pd.DataFrame) -> tuple[list[str], list[str]]:
    adv, risk = [], []
    min_additional = int(eligible["İlave gerekli"].min()) if not eligible.empty else 0
    max_current_lux = float(eligible["Mevcut düzende lux"].max()) if not eligible.empty else 0.0
    min_energy = float(eligible["Hedefte güç (kW)"].min()) if not eligible.empty else 0.0

    if int(row["İlave gerekli"]) == min_additional:
        adv.append("Uygun alternatifler içinde en az ilave armatür ihtiyacı")
    if math.isclose(float(row["Mevcut düzende lux"]), max_current_lux, abs_tol=0.5):
        adv.append("Mevcut armatür sayısıyla en yüksek tahmini aydınlık")
    if math.isclose(float(row["Hedefte güç (kW)"]), min_energy, abs_tol=0.01):
        adv.append("Hedef lux için en düşük kurulu güç grubu")
    if bool(row["Standart"]):
        adv.append("Katalogda standart mesh olarak işaretli")
    if float(row["OA (%)"]) >= 75:
        adv.append("Yüksek açık alan; mesh üstü aydınlatmada daha düşük tahmini ışık kaybı")
    if float(row["OA (%)"]) <= 55:
        adv.append("Daha kapalı tavan görünümü isteyen projeler için güçlü aday")
    if pd.notna(row.get("Fire (%)")) and eligible["Fire (%)"].notna().any() and math.isclose(
        float(row["Fire (%)"]), float(eligible["Fire (%)"].dropna().min()), abs_tol=0.05
    ):
        adv.append("Girilen proje verileri içinde en düşük fire değerlerinden biri")

    if int(row["İlave gerekli"]) > min_additional:
        risk.append(f"En iyi alternatife göre {int(row['İlave gerekli']) - min_additional} fazla ilave armatür gerektiriyor")
    if float(row["OA (%)"]) >= 75:
        risk.append("Yüksek açık alan nedeniyle tavan üstü tesisat daha görünür olabilir")
    if float(row["OA (%)"]) <= 55:
        risk.append("Mesh üstü armatürde ışık kaybı ve enerji ihtiyacı daha yüksek olabilir")
    if not bool(row["Standart"]):
        risk.append("Katalogda standart mesh olarak işaretli değil")
    if pd.isna(row.get("Fire (%)")):
        risk.append("Bu mesh için proje bazlı fire verisi girilmedi")

    return adv[:4], risk[:4]


def metric_card(title: str, value: str, subtitle: str = "", badge: str | None = None, badge_class: str = "badge-blue") -> str:
    badge_html = f"<span class='badge {badge_class}'>{badge}</span>" if badge else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{subtitle}</div>
        {badge_html}
    </div>
    """


def draw_comparison_chart(no_mesh: float, current: float, target: float) -> str:
    """Markdown'un girintili HTML'yi kod bloğu sanmaması için tek satırlı HTML üretir."""
    ymax = max(no_mesh, current, target, 1)
    scale = 150 / ymax
    bars = [
        ("Mesh olmadan", no_mesh, "bar-grey"),
        ("Seçili düzen", current, "bar-slate"),
        ("Hedef", target, "bar-blue"),
    ]
    bar_parts: list[str] = []
    for label, value, css in bars:
        h = max(8, value * scale)
        bar_parts.append(
            f"<div class='bar-wrap'>"
            f"<div class='bar-value'>{int(round(value))}</div>"
            f"<div class='bar {css}' style='height:{h:.1f}px;'></div>"
            f"<div class='bar-label'>{label}</div>"
            f"</div>"
        )
    target_top = max(10, 170 - target * scale)
    return (
        "<div class='compare-box simple-chart'>"
        "<div class='section-title' style='font-size:1rem;margin-bottom:4px;'>Aydınlık Karşılaştırma (lux)</div>"
        f"<div class='target-line' style='top:{target_top:.1f}px;'></div>"
        f"<div class='target-pill' style='top:{target_top:.1f}px;'>Hedef {int(round(target))}</div>"
        f"<div class='chart-area'>{''.join(bar_parts)}</div>"
        "</div>"
    )


def grid_preview(rows: int, cols: int) -> str:
    dots = []
    for r in range(rows):
        row_dots = []
        for c in range(cols):
            row_dots.append("<span style='display:inline-block;width:8px;height:8px;border-radius:50%;background:#1a8ed0;margin:4px;'></span>")
        dots.append("<div style='line-height:0;'>" + "".join(row_dots) + "</div>")
    return "".join(dots)



def get_optional_secret(name: str, default: str = "") -> str:
    """Streamlit secret tanımlı değilse uygulamayı durdurmadan boş değer döndürür."""
    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


def build_free_gpt_prompt(
    output_type: str,
    custom_request: str,
    system_name: str,
    panel_length: int,
    panel_width: int,
    panel_version: str,
    room_type: str,
    room_area: float,
    room_height: float,
    target_lux: float,
    light_position: str,
    current_mesh: str,
    open_area_pct: float,
    effective_transmission_pct: float,
    current_lux: float,
    no_mesh_lux: float,
    current_fixture_count: int,
    required_fixture_count: int,
    additional_fixture_count: int,
    power_w: float,
    current_power_kw: float,
    current_power_density: float,
    recommended_count: int,
    recommended_grid: str,
    alternatives: list[dict[str, object]],
) -> str:
    task_map = {
        "Mimari yorum": (
            "Sonucu bir mimarın hızlı okuyacağı şekilde yorumla. Mimari görünüm, tesisat görünürlüğü, "
            "aydınlatma ve enerji dengesini ayrı başlıklarla açıkla."
        ),
        "Müşteri sunum metni": (
            "Teknik ayrıntıyı azaltarak müşteri toplantısında kullanılabilecek 120-180 kelimelik profesyonel bir açıklama yaz. "
            "Kesinlik iddiası kurma ve ön hesap olduğunu belirt."
        ),
        "Teknik ofis raporu": (
            "Teknik ofis için maddeli bir değerlendirme hazırla: girdiler, hesap sonucu, hedef farkı, armatür ihtiyacı, "
            "enerji etkisi, alternatifler, riskler ve doğrulama için gereken veriler."
        ),
        "Alternatif mesh karşılaştırması": (
            "Mevcut mesh ile verilen uygun alternatifleri karşılaştır. En iyi aydınlatma, dengeli çözüm ve daha kapalı görünüm "
            "başlıklarında karar gerekçesi sun. Teknik olarak uygun olmayan yeni bir mesh önerme."
        ),
        "Eksik veri ve doğrulama listesi": (
            "Bu ön hesabı kesin projeye dönüştürmek için eksik veya doğrulanması gereken bilgileri önem sırasıyla listele. "
            "IES/LDT, gerçek optik geçirgenlik, renk, mesh yönü, armatür-mesh mesafesi, düzgünlük ve kamaşma konularını değerlendir."
        ),
    }
    task = task_map.get(output_type, task_map["Mimari yorum"])
    alt_lines = []
    for idx, alt in enumerate(alternatives[:5], start=1):
        alt_lines.append(
            f"{idx}. {alt['mesh']} | OA %{alt['oa_pct']:.1f} | tahmini {alt['lux']:.0f} lux | "
            f"toplam {alt['required']} armatür | ilave {alt['additional']} | "
            f"hedef güç {alt['power_kw']:.2f} kW | standart: {'evet' if alt['standard'] else 'hayır'}"
        )
    alternatives_text = "\n".join(alt_lines) if alt_lines else "Uygun alternatif listesi oluşturulamadı."
    custom = custom_request.strip() or "Ek kullanıcı talebi yok."

    return f"""DURLUM MESH VE AYDINLATMA TASARIM ASİSTANI İÇİN PROJE ÖZETİ

GÖREV
{task}

ZORUNLU KURALLAR
- Yalnızca aşağıda verilen proje ve hesap değerlerini kullan.
- Lux, armatür, güç, OA ve teknik uyumluluk değerlerini yeniden hesaplama veya değiştirme.
- Listede olmayan ya da teknik olarak elenmiş bir meshi önerme.
- Katalog OA değerinin gerçek optik ışık geçirgenliği olmadığını; geçici bir ön hesap yaklaşımı olduğunu açıkça belirt.
- Kesin fotometrik sonuç için IES/LDT tabanlı simülasyon veya yerinde ölçüm gerektiğini söyle.
- Yanıt Türkçe, profesyonel, açık ve mimarlara uygun olsun.
- Avantajlar ve riskleri birbirinden ayır.

PROJE VE SİSTEM
- Mekân türü: {room_type}
- Mekân alanı: {room_area:.1f} m²
- Mekân yüksekliği: {room_height:.1f} m
- Tavan sistemi: {system_name}
- Panel ölçüsü: {panel_length} × {panel_width} mm
- Panel versiyonu: {panel_version}
- Armatür konumu: {light_position}

MEVCUT SEÇİM
- Mesh: {current_mesh}
- Açık alan (OA): %{open_area_pct:.1f}
- Ön hesapta kullanılan etkin geçirgenlik: %{effective_transmission_pct:.1f}
- Hedef ortalama aydınlık: {target_lux:.0f} lux
- Mesh olmadan tahmini aydınlık: {no_mesh_lux:.0f} lux
- Seçili düzende tahmini aydınlık: {current_lux:.0f} lux
- Mevcut armatür: {current_fixture_count} adet
- Matematiksel toplam ihtiyaç: {required_fixture_count} adet
- İlave ihtiyaç: {additional_fixture_count} adet
- Bir armatür gücü: {power_w:.1f} W
- Mevcut toplam güç: {current_power_kw:.2f} kW
- Mevcut güç yoğunluğu: {current_power_density:.2f} W/m²
- Yerleşime uygun önerilen toplam: {recommended_count} adet
- Önerilen yaklaşık grid: {recommended_grid}

TEKNİK OLARAK UYGUN ALTERNATİFLER
{alternatives_text}

KULLANICININ EK TALEBİ
{custom}

YANIT BİÇİMİ
1. Kısa karar özeti
2. Mevcut seçimin güçlü yönleri
3. Riskler ve sınırlamalar
4. Uygun alternatifler ve hangi durumda seçilecekleri
5. Kesin proje için gereken doğrulamalar
"""



def safe_catalog_text(value: object, fallback: str = "Projeye özel / katalog doğrulaması gerekli") -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return fallback
    value_text = str(value).strip()
    return value_text if value_text and value_text.lower() != "nan" else fallback


def fact_card(name: str, value: object, note: str = "") -> str:
    return (
        "<div class='fact-card'>"
        f"<div class='fact-name'>{name}</div>"
        f"<div class='fact-value'>{safe_catalog_text(value)}</div>"
        f"<div class='fact-note'>{note}</div>"
        "</div>"
    )


def matching_lighting_rows(lighting_df: pd.DataFrame, system_name: str) -> pd.DataFrame:
    system_lower = system_name.lower()
    system_token = system_lower.split()[0]
    mask = lighting_df["ceiling_system"].astype(str).str.lower().apply(
        lambda value: value in system_lower or system_lower in value or value.split()[0] == system_token
    )
    return lighting_df.loc[mask].copy()


def build_family_gpt_prompt(
    product_family: str,
    system_name: str,
    output_type: str,
    custom_request: str,
    summary_lines: list[str],
    warning_lines: list[str],
) -> str:
    task_map = {
        "Mimari yorum": "Sistemi mimari görünüm, mekânsal etki, aydınlatma entegrasyonu ve kullanım açısından yorumla.",
        "Müşteri sunum metni": "Müşteri toplantısında kullanılabilecek 120–180 kelimelik profesyonel ve anlaşılır bir metin yaz.",
        "Teknik ofis raporu": "Girdiler, katalog uygunluğu, avantajlar, riskler, eksik veriler ve doğrulama adımlarını maddeli teknik rapor halinde yaz.",
        "Alternatif sistem karşılaştırması": "Yalnızca verilen ürün ailesi içinde olası sistem yaklaşımını karşılaştır; katalogda olmayan ölçü veya performans uydurma.",
        "Eksik veri ve doğrulama listesi": "Kesin tasarım için eksik olan fotometrik, geometrik, akustik, mekanik ve üretim verilerini önem sırasına göre listele.",
    }
    task = task_map.get(output_type, task_map["Mimari yorum"])
    custom = custom_request.strip() or "Ek kullanıcı talebi yok."
    summary_text = "\n".join(f"- {line}" for line in summary_lines)
    warning_text = "\n".join(f"- {line}" for line in warning_lines) if warning_lines else "- Katalog dışı ek uyarı yok."
    return f"""DURLUM TAVAN SİSTEMLERİ VE AYDINLATMA TASARIM ASİSTANI İÇİN PROJE ÖZETİ

GÖREV
{task}

ZORUNLU KURALLAR
- Yalnızca aşağıda verilen proje ve katalog verilerini kullan.
- Farklı ürün ailelerinin hesap mantığını birbirine karıştırma.
- Katalogda bulunmayan ölçü, ışık geçirgenliği, lux, akustik performans veya üretim değeri uydurma.
- Expanded Metal için OA yaklaşımını yalnızca RHOMBOS bölümünde kullan.
- Open Cell için hücre/lamel geometrisini; Baffle için lamel genişliği, yüksekliği, uzunluğu ve aralığını esas al.
- Character ürünlerinde ürün özel fotometri ve proje geometrisi gerektiğini açıkça belirt.
- Yanıt Türkçe, profesyonel ve mimarlara uygun olsun.

ÜRÜN AİLESİ VE SİSTEM
- Ürün ailesi: {product_family}
- Seçilen sistem: {system_name}

PROJE ÖZETİ
{summary_text}

UYARILAR VE SINIRLAMALAR
{warning_text}

KULLANICININ EK TALEBİ
{custom}

YANIT BİÇİMİ
1. Kısa karar özeti
2. Mimari ve teknik güçlü yönler
3. Aydınlatma / akustik / mekanik entegrasyon
4. Riskler ve sınırlamalar
5. Kesin proje için gereken veriler
"""


def render_family_gpt_bridge(
    product_family: str,
    system_name: str,
    summary_lines: list[str],
    warning_lines: list[str],
    key_prefix: str,
) -> None:
    left, right = st.columns([0.9, 1.5], gap="large")
    with left:
        with st.container(border=True):
            output_type = st.selectbox(
                "Hazırlanacak çıktı",
                ["Mimari yorum", "Müşteri sunum metni", "Teknik ofis raporu", "Alternatif sistem karşılaştırması", "Eksik veri ve doğrulama listesi"],
                key=f"{key_prefix}_gpt_output",
            )
            custom_request = st.text_area(
                "Ek talep",
                placeholder="Örnek: Aydınlatma çizgisi tavanın mimari ritmini bozmasın ve bakım erişimi kolay olsun.",
                height=120,
                key=f"{key_prefix}_gpt_request",
            )
            configured_gpt_url = get_optional_secret("DURLUM_GPT_URL")
            temporary_gpt_url = st.text_input(
                "Durlum GPT bağlantısı",
                value=configured_gpt_url,
                placeholder="https://chatgpt.com/g/g-...",
                key=f"{key_prefix}_gpt_url",
            )
            if temporary_gpt_url.startswith("https://"):
                st.link_button("DURLUM GPT'Yİ AÇ", temporary_gpt_url, use_container_width=True)
            else:
                st.link_button("ÖNCE ÖZEL GPT OLUŞTUR", "https://chatgpt.com/gpts/editor", use_container_width=True)
            st.markdown("<div class='info-callout'><b>Ücretsiz:</b> API kullanılmaz. Uygulama proje özetini hazırlar; metin özel GPT’ye kopyalanır.</div>", unsafe_allow_html=True)

    prompt = build_family_gpt_prompt(product_family, system_name, output_type, custom_request, summary_lines, warning_lines)
    with right:
        st.markdown("<div class='hero-card'><div class='hero-content'><h2>Projeyi GPT’ye Hazırla</h2><p>Metni kopyalayıp özel Durlum GPT’ye yapıştırın. Müşteri PDF’si veya gizli çizim otomatik gönderilmez.</p></div></div>", unsafe_allow_html=True)
        st.code(prompt, language=None, wrap_lines=True)
        st.download_button(
            "GPT proje özetini TXT indir",
            prompt.encode("utf-8"),
            file_name=f"durlum_{key_prefix}_gpt_ozeti.txt",
            mime="text/plain",
            use_container_width=True,
        )


def render_open_cell_module(open_cell_df: pd.DataFrame, lighting_df: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Open Cell / Raster Tavan Karar Ekranı</div><div class='section-subtitle'>Hücre, lamel, modül, montaj ve aydınlatma entegrasyonunu ürün ailesine özel olarak değerlendirin.</div>", unsafe_allow_html=True)
    tab_system, tab_lighting, tab_gpt, tab_catalog = st.tabs(["▦ Sistem / Teknik", "✦ Aydınlatma Entegrasyonu", "✦ GPT Tasarım Asistanı", "⌘ Katalog Verisi"])

    with tab_system:
        left, right = st.columns([1, 1.55], gap="large")
        with left:
            with st.container(border=True):
                category = st.selectbox("Raster sistemi türü", open_cell_df["category"].drop_duplicates().tolist(), key="oc_category")
                filtered = open_cell_df.loc[open_cell_df["category"] == category]
                system_name = st.selectbox("Sistem", filtered["system"].tolist(), key="oc_system")
                selected = filtered.loc[filtered["system"] == system_name].iloc[0]
                project_area = st.number_input("Uygulama alanı (m²)", min_value=1.0, value=100.0, step=1.0, key="oc_area")
                ceiling_height = st.number_input("Mekân yüksekliği (m)", min_value=1.0, value=3.2, step=0.1, key="oc_height")
                color = st.selectbox("Renk / yüzey", ["Beyaz", "Siyah", "RAL 9006", "Doğal eloksal", "Projeye özel"], key="oc_color")
                design_priority = st.selectbox("Tasarım önceliği", ["Dengeli çözüm", "Lineer görünüm", "Havadar görünüm", "Tesisatı gizleme", "Aydınlatma entegrasyonu", "Bakım erişimi"], key="oc_priority")
                integrated_light = st.checkbox("Entegre aydınlatma istiyorum", value=True, key="oc_integrated")

        with right:
            st.markdown("<div class='hero-card'><div class='hero-content'><h2>Open Cell Sistem Seçimi</h2><p>Bu ailede RHOMBOS OA hesabı kullanılmaz. Karar; hücre/lamel geometrisi, modül, taşıyıcı, görünüm ve sisteme özel aydınlatma üzerinden verilir.</p></div></div>", unsafe_allow_html=True)
            cols = st.columns(3)
            cards = [
                ("Panel / Modül", selected["panel_size"], "Katalogda verilen format"),
                ("Lamel W × H", f"{safe_catalog_text(selected['blade_width_mm'])} × {safe_catalog_text(selected['blade_height_mm'])} mm", "Boş değerler proje özelidir"),
                ("Hücre / Adım", selected["grid_spacing_mm"], "Raster geometrisi"),
            ]
            for col, (name, value, note) in zip(cols, cards):
                with col:
                    st.markdown(fact_card(name, value, note), unsafe_allow_html=True)
            cols2 = st.columns(3)
            cards2 = [
                ("Montaj", selected["installation"], "Taşıyıcı yaklaşımı"),
                ("Aydınlatma", selected["lighting"], "Katalog uyumlu çözüm"),
                ("Mimari karakter", selected["visual_character"], "Görsel karar"),
            ]
            for col, (name, value, note) in zip(cols2, cards2):
                with col:
                    st.markdown(fact_card(name, value, note), unsafe_allow_html=True)
            st.markdown(f"<div class='product-summary'><b>{system_name}</b><br>{safe_catalog_text(selected['notes'])}<br><br><b>Proje:</b> {project_area:.1f} m² · {ceiling_height:.1f} m · {color} · öncelik: {design_priority}</div>", unsafe_allow_html=True)
            if "Projeye göre" in safe_catalog_text(selected["panel_size"]):
                st.warning("Bu sistem için kesin panel/hücre ölçülerini proje veya ürün özel teknik sayfasından doğrulayın.")
            if integrated_light and safe_catalog_text(selected["lighting"]).startswith("Projeye göre"):
                st.warning("Entegre aydınlatma seçildi; ancak katalog tablosunda sistem özel bir armatür adı doğrulanmadı.")

    selected = open_cell_df.loc[open_cell_df["system"] == st.session_state.get("oc_system", open_cell_df.iloc[0]["system"])].iloc[0]
    system_name = str(selected["system"])
    project_area = float(st.session_state.get("oc_area", 100.0))
    ceiling_height = float(st.session_state.get("oc_height", 3.2))
    color = str(st.session_state.get("oc_color", "Beyaz"))
    design_priority = str(st.session_state.get("oc_priority", "Dengeli çözüm"))

    with tab_lighting:
        st.markdown("<div class='section-title'>Sisteme Uygun Aydınlatma Yaklaşımı</div>", unsafe_allow_html=True)
        matches = matching_lighting_rows(lighting_df, system_name)
        if not matches.empty:
            st.dataframe(matches.rename(columns={"ceiling_system": "Tavan sistemi", "lighting_system": "Aydınlatma", "integration_type": "Entegrasyon", "compatibility": "Uyumluluk", "notes": "Not"}), use_container_width=True, hide_index=True)
        else:
            st.info("Bu sistem için katalogdan doğrulanmış özel bir armatür eşleşmesi henüz eklenmedi. Proje fotometrisi ve entegrasyon detayı gerekir.")
        st.markdown("<div class='callout'><b>Hesap sınırı:</b> Open Cell ürünlerinde yalnız hücre boşluğundan otomatik lux hesabı yapılmaz. Lamel yüksekliği, bakış açısı, armatür konumu ve IES/LDT dağılımı sonucu belirgin biçimde etkiler.</div>", unsafe_allow_html=True)

    summary_lines = [
        f"Uygulama alanı: {project_area:.1f} m²", f"Mekân yüksekliği: {ceiling_height:.1f} m", f"Kategori: {selected['category']}",
        f"Panel/modül: {safe_catalog_text(selected['panel_size'])}", f"Lamel genişliği/yüksekliği: {safe_catalog_text(selected['blade_width_mm'])} / {safe_catalog_text(selected['blade_height_mm'])} mm",
        f"Hücre/adım: {safe_catalog_text(selected['grid_spacing_mm'])}", f"Montaj: {safe_catalog_text(selected['installation'])}", f"Aydınlatma: {safe_catalog_text(selected['lighting'])}",
        f"Renk/yüzey: {color}", f"Tasarım önceliği: {design_priority}",
    ]
    warnings = ["OA değeri üzerinden RHOMBOS tipi ışık geçirgenliği hesabı uygulanmamalıdır."]
    if "Projeye göre" in safe_catalog_text(selected["panel_size"]):
        warnings.append("Kesin modül ve panel ölçüleri proje özel teknik verisiyle doğrulanmalıdır.")
    with tab_gpt:
        render_family_gpt_bridge("Open Cell / Raster Tavan", system_name, summary_lines, warnings, "open_cell")
    with tab_catalog:
        st.dataframe(open_cell_df, use_container_width=True, hide_index=True)


def render_baffle_module(baffle_df: pd.DataFrame, lighting_df: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Baffle / Dikey Lamel Karar Ekranı</div><div class='section-subtitle'>POLYLAM ailesini lamel geometrisi, erişim, aydınlatma, akustik ve soğutma seçenekleriyle değerlendirin.</div>", unsafe_allow_html=True)
    tab_system, tab_lighting, tab_gpt, tab_catalog = st.tabs(["▦ Sistem / Teknik", "✦ Aydınlatma Entegrasyonu", "✦ GPT Tasarım Asistanı", "⌘ Katalog Verisi"])

    with tab_system:
        left, right = st.columns([1, 1.55], gap="large")
        with left:
            with st.container(border=True):
                system_name = st.selectbox("Baffle sistemi", baffle_df["system"].tolist(), key="bf_system")
                selected = baffle_df.loc[baffle_df["system"] == system_name].iloc[0]
                width_min = selected["width_min_mm"]
                width_max = selected["width_max_mm"]
                height_min = selected["height_min_mm"]
                height_max = selected["height_max_mm"]
                length_min = selected["length_min_mm"]
                length_max = selected["length_max_mm"]
                default_width = float(width_min) if pd.notna(width_min) else 40.0
                default_height = float(height_min) if pd.notna(height_min) else 100.0
                default_length = float(length_min) if pd.notna(length_min) else 1200.0
                blade_width = st.number_input("Lamel genişliği (mm)", min_value=10.0, value=default_width, step=1.0, key="bf_width")
                blade_height = st.number_input("Lamel yüksekliği (mm)", min_value=20.0, value=default_height, step=5.0, key="bf_height")
                blade_length = st.number_input("Lamel uzunluğu (mm)", min_value=100.0, value=default_length, step=50.0, key="bf_length")
                suggested_spacing = blade_width + 20 if system_name in ["POLYLAM-KS", "POLYLAM-S"] else max(100.0, blade_width + 20)
                blade_spacing = st.number_input("Lamel eksen aralığı (mm)", min_value=20.0, value=float(suggested_spacing), step=5.0, key="bf_spacing")
                project_area = st.number_input("Uygulama alanı (m²)", min_value=1.0, value=100.0, step=1.0, key="bf_area")
                color = st.selectbox("Renk / yüzey", ["RAL 9016 mat", "Beyaz", "Siyah", "Eloksal", "Ahşap görünümlü baskı", "Projeye özel"], key="bf_color")

        width_ok = (pd.isna(width_min) or blade_width >= float(width_min)) and (pd.isna(width_max) or blade_width <= float(width_max))
        height_ok = (pd.isna(height_min) or blade_height >= float(height_min)) and (pd.isna(height_max) or blade_height <= float(height_max))
        length_ok = (pd.isna(length_min) or blade_length >= float(length_min)) and (pd.isna(length_max) or blade_length <= float(length_max))
        spacing_ok = blade_spacing >= blade_width + 20 if system_name in ["POLYLAM-KS", "POLYLAM-S"] else True
        build_extra = selected["build_height_extra_mm"]

        with right:
            st.markdown("<div class='hero-card'><div class='hero-content'><h2>POLYLAM Geometri ve Sistem Uygunluğu</h2><p>Baffle ailesinde karar; lamel genişliği, yüksekliği, uzunluğu, aks aralığı, bakım erişimi ve entegre ışık çizgisi üzerinden verilir.</p></div></div>", unsafe_allow_html=True)
            cols = st.columns(3)
            with cols[0]: st.markdown(fact_card("Katalog genişliği", selected["width_options"], "Standart / doğrulanmış aralık"), unsafe_allow_html=True)
            with cols[1]: st.markdown(fact_card("Yükseklik aralığı", f"{safe_catalog_text(height_min)}–{safe_catalog_text(height_max)} mm", "Boşsa proje özeldir"), unsafe_allow_html=True)
            with cols[2]: st.markdown(fact_card("Uzunluk aralığı", f"{safe_catalog_text(length_min)}–{safe_catalog_text(length_max)} mm", "Boşsa proje özeldir"), unsafe_allow_html=True)
            cols2 = st.columns(3)
            with cols2[0]: st.markdown(fact_card("Erişim", selected["access"], "Bakım yaklaşımı"), unsafe_allow_html=True)
            with cols2[1]: st.markdown(fact_card("Aydınlatma", selected["lighting"], "Entegre çözüm"), unsafe_allow_html=True)
            with cols2[2]: st.markdown(fact_card("Akustik / soğutma", f"{selected['acoustic']} / {selected['cooling']}", "Ek işlevler"), unsafe_allow_html=True)
            status = []
            status.append("✅ Lamel genişliği katalog aralığında." if width_ok else "⚠️ Lamel genişliği doğrulanmış katalog aralığı dışında.")
            status.append("✅ Lamel yüksekliği katalog aralığında." if height_ok else "⚠️ Lamel yüksekliği doğrulanmış katalog aralığı dışında.")
            status.append("✅ Lamel uzunluğu katalog aralığında." if length_ok else "⚠️ Lamel uzunluğu doğrulanmış katalog aralığı dışında.")
            status.append("✅ Modül aralığı minimum kurala uyuyor." if spacing_ok else f"⚠️ Minimum modül aralığı en az {blade_width + 20:.0f} mm olmalıdır.")
            st.markdown("".join(f"<div class='{'info-callout' if item.startswith('✅') else 'callout'}'>{item}</div>" for item in status), unsafe_allow_html=True)
            if pd.notna(build_extra):
                st.metric("Yaklaşık toplam sistem yüksekliği", f"{blade_height + float(build_extra):.0f} mm", help="Katalogdaki lamel yüksekliği + taşıyıcı ilavesi yaklaşımı.")
            st.markdown(f"<div class='product-summary'><b>{system_name}</b><br>{selected['notes']}<br><br><b>Proje:</b> {project_area:.1f} m² · {blade_width:.0f}×{blade_height:.0f} mm lamel · {blade_length:.0f} mm uzunluk · {blade_spacing:.0f} mm aks · {color}</div>", unsafe_allow_html=True)

    selected = baffle_df.loc[baffle_df["system"] == st.session_state.get("bf_system", baffle_df.iloc[0]["system"])].iloc[0]
    system_name = str(selected["system"])
    blade_width = float(st.session_state.get("bf_width", 40.0))
    blade_height = float(st.session_state.get("bf_height", 100.0))
    blade_length = float(st.session_state.get("bf_length", 1200.0))
    blade_spacing = float(st.session_state.get("bf_spacing", 100.0))
    project_area = float(st.session_state.get("bf_area", 100.0))
    color = str(st.session_state.get("bf_color", "RAL 9016 mat"))

    with tab_lighting:
        matches = matching_lighting_rows(lighting_df, system_name)
        st.markdown("<div class='section-title'>Entegre Aydınlatma Seçenekleri</div>", unsafe_allow_html=True)
        if not matches.empty:
            st.dataframe(matches.rename(columns={"ceiling_system": "Tavan sistemi", "lighting_system": "Aydınlatma", "integration_type": "Entegrasyon", "compatibility": "Uyumluluk", "notes": "Not"}), use_container_width=True, hide_index=True)
        else:
            st.info(f"Katalog özeti: {safe_catalog_text(selected['lighting'])}. Kesin armatür kodu ve elektrik/fotometri verisi proje bazında doğrulanmalıdır.")
        if blade_width == 40:
            st.success("40 mm lamel için OMEGA 40 veya PUNTEO-S yaklaşımı katalogda öne çıkıyor.")
        elif blade_width == 63:
            st.success("63 mm lamel için OMEGA 63 yaklaşımı katalogda öne çıkıyor.")
        else:
            st.warning("Girilen lamel genişliği için katalogdaki standart OMEGA 40/63 eşleşmesi doğrudan uygulanamaz; proje özel entegrasyon gerekir.")

    summary_lines = [
        f"Uygulama alanı: {project_area:.1f} m²", f"Sistem kategorisi: {selected['category']}", f"Lamel genişliği: {blade_width:.0f} mm",
        f"Lamel yüksekliği: {blade_height:.0f} mm", f"Lamel uzunluğu: {blade_length:.0f} mm", f"Lamel eksen aralığı: {blade_spacing:.0f} mm",
        f"Modül kuralı: {selected['module_rule']}", f"Erişim: {selected['access']}", f"Aydınlatma: {selected['lighting']}", f"Akustik: {selected['acoustic']}", f"Soğutma: {selected['cooling']}", f"Renk/yüzey: {color}",
    ]
    warnings = ["RHOMBOS OA katsayısı bu ürün ailesine uygulanmamalıdır."]
    if system_name in ["POLYLAM-KS", "POLYLAM-S"] and blade_spacing < blade_width + 20:
        warnings.append(f"Minimum modül aralığı {blade_width + 20:.0f} mm olmalıdır.")
    with tab_gpt:
        render_family_gpt_bridge("Baffle / Dikey Lamel", system_name, summary_lines, warnings, "baffle")
    with tab_catalog:
        st.dataframe(baffle_df, use_container_width=True, hide_index=True)


def render_character_module(character_df: pd.DataFrame, lighting_df: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Character Özel Sistemler</div><div class='section-subtitle'>LOOP, OPEN SKY, TOMEO, FLUID ve DOMUS ürünlerini proje mantığına uygun teknik kartlarla değerlendirin.</div>", unsafe_allow_html=True)
    tab_system, tab_lighting, tab_gpt, tab_catalog = st.tabs(["▦ Sistem / Proje", "✦ Aydınlatma ve Entegrasyon", "✦ GPT Tasarım Asistanı", "⌘ Katalog Verisi"])
    with tab_system:
        left, right = st.columns([1, 1.55], gap="large")
        with left:
            with st.container(border=True):
                system_name = st.selectbox("Özel tavan sistemi", character_df["system"].tolist(), key="ch_system")
                selected = character_df.loc[character_df["system"] == system_name].iloc[0]
                project_area = st.number_input("Uygulama alanı (m²)", min_value=1.0, value=100.0, step=1.0, key="ch_area")
                ceiling_height = st.number_input("Mekân yüksekliği (m)", min_value=1.0, value=3.2, step=0.1, key="ch_height")
                needs_acoustic = st.checkbox("Akustik özellik gerekli", value=False, key="ch_acoustic")
                needs_cooling = st.checkbox("Soğutma / iklim entegrasyonu gerekli", value=False, key="ch_cooling")
                needs_services = st.multiselect("Entegre tesisatlar", ["Aydınlatma", "Sprinkler", "Havalandırma", "Kablo hatları", "Duman tahliyesi"], default=["Aydınlatma"], key="ch_services")
                specific_value = ""
                specific_warning = ""
                if system_name == "OPEN SKY":
                    module_w = st.number_input("Cam modül genişliği (mm)", min_value=500, max_value=1200, value=1000, step=50, key="ch_os_w")
                    module_l = st.number_input("Cam modül uzunluğu (mm)", min_value=500, max_value=1200, value=1000, step=50, key="ch_os_l")
                    reflector = st.checkbox("Çapraz reflektörlü çözüm", value=True, key="ch_os_reflector")
                    specific_value = f"Cam modül {module_w}×{module_l} mm; derz 8 mm; gerekli yükseklik yaklaşık {'510' if reflector else '363'} mm"
                elif system_name.startswith("TOMEO-R"):
                    diameter = st.selectbox("Eleman çapı", [293, 593, 893, 1200], index=3, key="ch_tomeo_d")
                    specific_value = f"Seçilen yuvarlak eleman Ø{diameter} mm; katalog yüksekliği 60 mm"
                elif system_name == "LOOP TYP 2":
                    specific_value = "Serbest kesit >%50; panel 1124,23×1004,25 mm; modül 1115,44×966 mm"
                else:
                    specific_warning = "Bu sistem projeye özel geometrik modelleme ve üretici teknik detayı gerektirir."

        with right:
            st.markdown("<div class='hero-card'><div class='hero-content'><h2>Özel Tavan–Işık Çözümü</h2><p>Character ailesinde tek bir genel formül kullanılmaz. Her ürünün geometrisi, erişimi, akustik/iklim işlevi ve aydınlatma tipi ayrı ele alınır.</p></div></div>", unsafe_allow_html=True)
            cols = st.columns(3)
            with cols[0]: st.markdown(fact_card("Kategori", selected["category"], "Ürün ailesi"), unsafe_allow_html=True)
            with cols[1]: st.markdown(fact_card("Standart / referans ölçü", selected["standard_dimension"], "Katalog özeti"), unsafe_allow_html=True)
            with cols[2]: st.markdown(fact_card("Hesap yaklaşımı", selected["calculation_mode"], "RHOMBOS'tan farklıdır"), unsafe_allow_html=True)
            cols2 = st.columns(3)
            with cols2[0]: st.markdown(fact_card("Aydınlatma", selected["lighting"], "Entegrasyon"), unsafe_allow_html=True)
            with cols2[1]: st.markdown(fact_card("Akustik", selected["acoustic"], "Opsiyon / işlev"), unsafe_allow_html=True)
            with cols2[2]: st.markdown(fact_card("Soğutma", selected["cooling"], "İklim işlevi"), unsafe_allow_html=True)
            st.markdown(f"<div class='product-summary'><b>{system_name}</b><br>{selected['main_function']}<br><br>{selected['notes']}<br><br><b>Proje:</b> {project_area:.1f} m² · {ceiling_height:.1f} m · tesisatlar: {', '.join(needs_services) if needs_services else 'yok'}<br>{specific_value}</div>", unsafe_allow_html=True)
            if specific_warning:
                st.warning(specific_warning)
            if needs_acoustic and str(selected["acoustic"]).lower() in ["hayır", "no"]:
                st.warning("Seçilen sistemde katalog özeti akustik işlev göstermiyor; ayrı absorber veya farklı sistem düşünülmelidir.")
            if needs_cooling and "Hayır" in str(selected["cooling"]):
                st.warning("Seçilen sistemde katalog özeti soğutma işlevi göstermiyor.")

    selected = character_df.loc[character_df["system"] == st.session_state.get("ch_system", character_df.iloc[0]["system"])].iloc[0]
    system_name = str(selected["system"])
    project_area = float(st.session_state.get("ch_area", 100.0))
    ceiling_height = float(st.session_state.get("ch_height", 3.2))
    needs_services = st.session_state.get("ch_services", ["Aydınlatma"])

    with tab_lighting:
        matches = matching_lighting_rows(lighting_df, system_name)
        if not matches.empty:
            st.dataframe(matches.rename(columns={"ceiling_system": "Tavan sistemi", "lighting_system": "Aydınlatma", "integration_type": "Entegrasyon", "compatibility": "Uyumluluk", "notes": "Not"}), use_container_width=True, hide_index=True)
        else:
            st.info(f"Katalog özeti: {selected['lighting']}. Kesin lux hesabı için armatür kodu, IES/LDT, yerleşim ve ürün özel optik/geometrik veri gerekir.")
        st.markdown(f"<div class='callout'><b>Hesap yaklaşımı:</b> {selected['calculation_mode']}. Bu ürün için yalnızca açık alan oranından otomatik lux sonucu üretilmez.</div>", unsafe_allow_html=True)

    summary_lines = [
        f"Uygulama alanı: {project_area:.1f} m²", f"Mekân yüksekliği: {ceiling_height:.1f} m", f"Kategori: {selected['category']}", f"Ana işlev: {selected['main_function']}",
        f"Standart/referans ölçü: {selected['standard_dimension']}", f"Aydınlatma: {selected['lighting']}", f"Akustik: {selected['acoustic']}", f"Soğutma: {selected['cooling']}", f"Erişim: {selected['access']}", f"Entegre tesisatlar: {', '.join(needs_services) if needs_services else 'yok'}",
    ]
    warnings = ["Bu sistem RHOMBOS OA formülüyle hesaplanamaz.", "Kesin sonuç için ürün özel fotometri ve proje geometrisi gerekir."]
    with tab_gpt:
        render_family_gpt_bridge("Character Özel Sistemler", system_name, summary_lines, warnings, "character")
    with tab_catalog:
        st.dataframe(character_df, use_container_width=True, hide_index=True)


def render_acoustic_module(acoustic_df: pd.DataFrame) -> None:
    st.markdown("<div class='section-title'>Akustik Çözümler</div><div class='section-subtitle'>Düşük frekans absorberlerini ürün verisiyle seçin; kesin oda akustiği hesabından ayrı tutun.</div>", unsafe_allow_html=True)
    tab_system, tab_gpt, tab_catalog = st.tabs(["▦ Ürün / Ön Değerlendirme", "✦ GPT Tasarım Asistanı", "⌘ Katalog Verisi"])
    with tab_system:
        left, right = st.columns([1, 1.55], gap="large")
        with left:
            with st.container(border=True):
                system_name = st.selectbox("Akustik ürün", acoustic_df["system"].tolist(), key="ac_system")
                selected = acoustic_df.loc[acoustic_df["system"] == system_name].iloc[0]
                room_use = st.selectbox("Mekân kullanımı", ["Ofis", "Toplantı odası", "Lobi", "Konferans salonu", "Restoran", "Diğer"], key="ac_use")
                room_area = st.number_input("Mekân alanı (m²)", min_value=1.0, value=100.0, step=1.0, key="ac_area")
                room_height = st.number_input("Mekân yüksekliği (m)", min_value=1.0, value=3.2, step=0.1, key="ac_height")
                acoustic_issue = st.multiselect("Öncelikli problem", ["Düşük frekans birikimi", "Konuşma anlaşılabilirliği", "Yüksek yankı", "Mekanik tesisat gürültüsü", "Genel konfor"], default=["Düşük frekans birikimi"], key="ac_issue")
        with right:
            st.markdown("<div class='hero-card'><div class='hero-content'><h2>Akustik Ürün Ön Seçimi</h2><p>Bu ekran katalogdaki absorber verisini düzenler. Hedef yankılanma süresi veya oda akustiği sonucu için hacim, yüzeyler ve mevcut absorpsiyon ayrıca modellenmelidir.</p></div></div>", unsafe_allow_html=True)
            cols = st.columns(3)
            with cols[0]: st.markdown(fact_card("Standart ölçü", selected["standard_dimension"], "Katalog"), unsafe_allow_html=True)
            with cols[1]: st.markdown(fact_card("Absorpsiyon", selected["absorption"], "Katalog sınıflandırması"), unsafe_allow_html=True)
            with cols[2]: st.markdown(fact_card("Ağırlık", selected["weight"], "Yaklaşık"), unsafe_allow_html=True)
            cols2 = st.columns(3)
            with cols2[0]: st.markdown(fact_card("Malzeme", selected["material"], "Ürün yapısı"), unsafe_allow_html=True)
            with cols2[1]: st.markdown(fact_card("Perforasyon", selected["perforation"], "Katalog"), unsafe_allow_html=True)
            with cols2[2]: st.markdown(fact_card("Montaj", selected["mounting"], "Uygulama"), unsafe_allow_html=True)
            volume = room_area * room_height
            st.markdown(f"<div class='product-summary'><b>{system_name}</b><br>{selected['notes']}<br><br><b>Mekân:</b> {room_use} · {room_area:.1f} m² · yaklaşık {volume:.1f} m³ · sorun: {', '.join(acoustic_issue) if acoustic_issue else 'belirtilmedi'}</div>", unsafe_allow_html=True)
            st.warning("Bu ekran ürün seçimine yardımcı olur; kaç adet absorber gerektiğini otomatik ve kesin biçimde hesaplamaz.")

    selected = acoustic_df.loc[acoustic_df["system"] == st.session_state.get("ac_system", acoustic_df.iloc[0]["system"])].iloc[0]
    system_name = str(selected["system"])
    room_area = float(st.session_state.get("ac_area", 100.0))
    room_height = float(st.session_state.get("ac_height", 3.2))
    room_use = str(st.session_state.get("ac_use", "Ofis"))
    acoustic_issue = st.session_state.get("ac_issue", ["Düşük frekans birikimi"])
    summary_lines = [
        f"Mekân: {room_use}", f"Alan: {room_area:.1f} m²", f"Yükseklik: {room_height:.1f} m", f"Yaklaşık hacim: {room_area * room_height:.1f} m³",
        f"Öncelikli problem: {', '.join(acoustic_issue) if acoustic_issue else 'belirtilmedi'}", f"Standart ölçü: {selected['standard_dimension']}", f"Özel ölçü: {selected['special_dimension']}", f"Absorpsiyon: {selected['absorption']}", f"Montaj: {selected['mounting']}",
    ]
    warnings = ["Kesin adet ve yerleşim için hedef RT, mevcut yüzeylerin absorpsiyonu ve frekans bazlı oda modeli gerekir."]
    with tab_gpt:
        render_family_gpt_bridge("Akustik Çözümler", system_name, summary_lines, warnings, "acoustic")
    with tab_catalog:
        st.dataframe(acoustic_df, use_container_width=True, hide_index=True)

def apply_room_preset() -> None:
    room_type = st.session_state.get("room_type", "Ofis / çalışma alanı")
    if room_type != "Özel / elle gir":
        st.session_state["target_lux"] = ROOM_TARGETS[room_type]


meshes, systems = load_data()
open_cell_df = pd.DataFrame(OPEN_CELL_CATALOG)
baffle_df = pd.DataFrame(BAFFLE_CATALOG)
character_df = pd.DataFrame(CHARACTER_CATALOG)
acoustic_df = pd.DataFrame(ACOUSTIC_CATALOG)
lighting_df = pd.DataFrame(LIGHTING_INTEGRATIONS)

if "room_type" not in st.session_state:
    st.session_state["room_type"] = "Ofis / çalışma alanı"
if "target_lux" not in st.session_state:
    st.session_state["target_lux"] = ROOM_TARGETS[st.session_state["room_type"]]

st.markdown(
    (
        "<div class='app-shell'>"
        "<div class='app-topbar'>"
        "<div class='brand-wrap'>"
        f"<div class='logo-box'><img src='data:image/jpeg;base64,{LOGO_B64}' alt='durlum' /></div>"
        "<div>"
        "<div class='brand-title'>Durlum Tavan Sistemleri ve Aydınlatma</div>"
        "<div class='brand-subtitle'>Mimarlar ve teknik ekipler için ürün ailesine özel teknik seçim, aydınlatma entegrasyonu ve açıklanabilir karar desteği</div>"
        "</div></div>"
        "<div class='chip-row'>"
        "<div class='chip'>Architect Edition</div>"
        "<div class='chip'>Tüm Tavan Sistemleri</div>"
        "<div class='chip'>Ücretsiz GPT Köprüsü</div>"
        "</div></div></div>"
    ),
    unsafe_allow_html=True,
)


st.markdown(
    "<div class='family-shell'><div class='family-kicker'>Ana seçim</div>"
    "<div class='family-title'>Projenizde kullanılacak ürün ailesini seçin</div></div>",
    unsafe_allow_html=True,
)
product_family = st.selectbox(
    "Ürün ailesi",
    PRODUCT_FAMILIES,
    key="product_family",
    help="Her ürün ailesi kendi geometrisi ve teknik mantığıyla değerlendirilir.",
)

if product_family == "Open Cell / Raster Tavan":
    render_open_cell_module(open_cell_df, lighting_df)
    st.caption("Kaynak: durlum Open Cell Ceilings kataloğu. Katalogda doğrulanmayan değerler projeye özel olarak işaretlenmiştir.")
    st.stop()
elif product_family == "Baffle / Dikey Lamel":
    render_baffle_module(baffle_df, lighting_df)
    st.caption("Kaynak: durlum CHARACTER kataloğu POLYLAM bölümü. Kesin üretim ve performans değerleri proje onayıyla doğrulanmalıdır.")
    st.stop()
elif product_family == "Character Özel Sistemler":
    render_character_module(character_df, lighting_df)
    st.caption("Kaynak: durlum CHARACTER kataloğu. LOOP, OPEN SKY, TOMEO, FLUID ve DOMUS ürünleri ürün özel proje mantığıyla değerlendirilir.")
    st.stop()
elif product_family == "Akustik Çözümler":
    render_acoustic_module(acoustic_df)
    st.caption("Kaynak: durlum CHARACTER kataloğu dur-SONIC bölümü. Kesin oda akustiği hesabı değildir.")
    st.stop()

tab_project, tab_light, tab_compare, tab_gpt, tab_catalog = st.tabs([
    "▦ Panel / Mesh", "✦ Aydınlatma", "≋ Alternatif Karşılaştırma",
    "✦ GPT Tasarım Asistanı", "⌘ Katalog Verisi"
])

with tab_project:
    st.markdown("<div class='section-title'>Panel, sistem ve mesh uygunluğu</div><div class='section-subtitle'>Üretilebilirlik sınırlarını hızlıca doğrulayın ve proje alanını tek ekranda görün.</div>", unsafe_allow_html=True)
    left, right = st.columns([1.02, 1.38], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("<div class='input-group-title'>Proje girdileri</div>", unsafe_allow_html=True)
            system_name = st.selectbox("Tavan sistemi", systems["system"].tolist())
            panel_length = st.number_input("Panel boyu (mm)", min_value=100, max_value=6000, value=2200, step=10)
            panel_width = st.number_input("Panel eni (mm)", min_value=100, max_value=3000, value=595, step=5)
            panel_count = st.number_input("Panel adedi", min_value=1, max_value=100000, value=23, step=1)
            default_mesh_index = int(meshes.index[meshes["mesh_code"] == "M600"][0]) if "M600" in meshes["mesh_code"].values else 0
            mesh_code = st.selectbox("Mesh kodu", meshes["mesh_code"].tolist(), index=default_mesh_index)
            panel_version = st.selectbox("Panel versiyonu", ["V1", "V2", "V3_BASIC", "V4", "V5", "V6"])
            unit_weight = st.number_input("Birim ağırlık (kg/m²)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

    selected_system = systems.loc[systems["system"] == system_name].iloc[0]
    selected_mesh = meshes.loc[meshes["mesh_code"] == mesh_code].iloc[0]
    area_each = panel_length * panel_width / 1_000_000
    total_area = area_each * panel_count
    dimensions_ok = (
        panel_length <= selected_system["max_panel_length_mm"]
        and panel_width <= selected_system["max_panel_width_mm"]
        and area_each <= selected_system["recommended_max_area_m2"]
    )
    version_ok = bool(selected_mesh[panel_version])

    with right:
        st.markdown(
            f"""
            <div class='hero-card'>
              <div class='hero-inner'>
                <div class='hero-visual'><span>Panel geometri, açık alan ve sistem uyumluluğu<br/>tek bakışta</span></div>
                <div class='hero-content'>
                  <h2>Proje Geometrisi ve Katalog Uygunluğu</h2>
                  <p>Seçilen sistem, panel ölçüsü ve mesh tipine göre üretilebilirlik sınırlarını anında görün. Bu ekran; teklif öncesi doğrulama, tasarım sunumu ve teknik ofis kontrolü için sadeleştirilmiş bir karar yüzüdür.</p>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(metric_card("Tek panel", f"{tr_number(area_each, 3)} m²", "Bir panel alanı", "Geometri", "badge-blue"), unsafe_allow_html=True)
        with r2:
            st.markdown(metric_card("Toplam alan", f"{tr_number(total_area, 2)} m²", "Panel adedine göre", "Proje", "badge-green"), unsafe_allow_html=True)
        with r3:
            st.markdown(metric_card("Açık alan (OA)", f"%{tr_number(selected_mesh['open_area_pct'], 1)}", "Seçilen mesh", "Mesh", "badge-amber"), unsafe_allow_html=True)

        r4, r5, r6 = st.columns(3)
        with r4:
            st.markdown(metric_card("Maks. panel boyu", f"{int(selected_system['max_panel_length_mm'])} mm", "Sistem sınırı"), unsafe_allow_html=True)
        with r5:
            st.markdown(metric_card("Maks. panel eni", f"{int(selected_system['max_panel_width_mm'])} mm", "Sistem sınırı"), unsafe_allow_html=True)
        with r6:
            st.markdown(metric_card("Önerilen maks. alan", f"{tr_number(selected_system['recommended_max_area_m2'], 1)} m²", "Katalog rehberi"), unsafe_allow_html=True)

        status_html = ""
        if dimensions_ok:
            status_html += "<div class='info-callout'>✅ Panel ölçüleri seçilen sistemin katalog sınırları içinde.</div>"
        else:
            status_html += "<div class='callout'>⚠️ Panel ölçülerinden en az biri seçilen sistemin katalog sınırını aşıyor.</div>"
        if version_ok:
            status_html += f"<div class='info-callout'>✅ {mesh_code}, {panel_version} panel versiyonu için katalogda teknik olarak mümkün görünüyor.</div>"
        else:
            status_html += f"<div class='callout'>⚠️ {mesh_code}, {panel_version} panel versiyonu için katalog tablosunda uygun gösterilmiyor.</div>"
        if unit_weight > 0:
            status_html += f"<div class='info-callout'>ℹ️ Tahmini toplam ağırlık: <b>{tr_number(total_area * unit_weight, 1)} kg</b></div>"
        else:
            status_html += "<div class='info-callout'>ℹ️ Toplam ağırlık için doğrulanmış kg/m² değeri girildiğinde sonuç hesaplanır.</div>"
        st.markdown(status_html, unsafe_allow_html=True)

with tab_light:
    st.markdown("<div class='section-title'>Aydınlatma karar ekranı</div><div class='section-subtitle'>Mimari mesh seçimlerini lux, armatür ihtiyacı ve yerleşim etkisiyle birlikte değerlendirin.</div>", unsafe_allow_html=True)
    left, right = st.columns([1.02, 2.05], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("<div class='input-group-title'>Sistem ve geometri</div>", unsafe_allow_html=True)
            room_type = st.selectbox("Mekân türü", list(ROOM_TARGETS.keys()), key="room_type", on_change=apply_room_preset)
            room_length = st.number_input("Mekân uzunluğu (m)", min_value=1.0, max_value=500.0, value=12.0, step=0.5)
            room_width = st.number_input("Mekân genişliği (m)", min_value=1.0, max_value=500.0, value=10.0, step=0.5)
            room_height = st.number_input("Mekân yüksekliği (m)", min_value=1.0, max_value=20.0, value=3.2, step=0.1)
            st.markdown("<div class='input-group-title'>Mesh seçimi</div>", unsafe_allow_html=True)
            transmission_mode = st.radio("Mesh ışık geçirgenliği kaynağı", ["Katalog OA değerini geçici tahmin olarak kullan", "Ölçülmüş geçirgenlik değerini kullan"])
            lighting_mesh = st.selectbox("Aydınlatma için mesh", meshes["mesh_code"].tolist(), key="lighting_mesh")
            lighting_mesh_row = meshes.loc[meshes["mesh_code"] == lighting_mesh].iloc[0]
            correction = 0.90
            if transmission_mode.startswith("Katalog"):
                correction = st.slider("Yön / renk / mesafe düzeltme katsayısı", 0.50, 1.10, 0.90, 0.01)
                transmission = min(1.0, lighting_mesh_row["open_area_pct"] / 100 * correction)
            else:
                measured_t = st.number_input("Ölçülmüş ışık geçirgenliği (%)", min_value=1.0, max_value=100.0, value=75.0, step=0.5)
                transmission = measured_t / 100
            st.text_input("Etkin geçirgenlik katsayısı", value=f"{transmission:.2f}", disabled=True)

            st.markdown("<div class='input-group-title'>Armatür bilgileri</div>", unsafe_allow_html=True)
            fixture_count = st.number_input("Mevcut armatür sayısı", min_value=1, max_value=10000, value=18, step=1)
            lumens = st.number_input("Bir armatürün ışık akısı (lm)", min_value=100.0, max_value=200000.0, value=4000.0, step=100.0)
            power_w = st.number_input("Bir armatürün gücü (W)", min_value=0.0, max_value=5000.0, value=35.0, step=1.0)
            utilization = st.slider("Kullanım faktörü (UF)", 0.10, 1.00, 0.60, 0.01)
            maintenance = st.slider("Bakım faktörü (MF)", 0.10, 1.00, 0.80, 0.01)

            st.markdown("<div class='input-group-title'>Hedef ve konum</div>", unsafe_allow_html=True)
            target_lux = st.number_input("Hedef ortalama aydınlık (lux)", min_value=1.0, max_value=5000.0, step=25.0, key="target_lux")
            light_position = st.radio("Armatür konumu", ["Mesh üstünde", "Mesh altında / entegre OMEGA kanalda"], index=0)
            st.markdown("<div class='input-group-title'>Öncelik ve ölçüm tercihi</div>", unsafe_allow_html=True)
            priority_view = st.select_slider("Öncelik", options=["Işık geçirgenliği (OA)", "Dengeli çözüm", "Maksimum aydınlık"], value="Işık geçirgenliği (OA)")
            st.selectbox("Ölçüm tercihi", ["Kesin vertikal düzlemde aydınlık (yüzey düzeltilmeli)", "Yatay düzlem ön hesap", "Sadece hızlı karşılaştırma"], index=0)
            st.button("HESAPLA", use_container_width=True)

    room_area = room_length * room_width
    calc_position = "Mesh üstünde" if light_position.startswith("Mesh üstünde") else "Mesh altında"
    vals = lighting_values(room_area, int(fixture_count), lumens, utilization, maintenance, transmission, calc_position, target_lux)
    required_count = int(vals["required_count"])
    grids = grid_options(required_count, room_length, room_width)
    primary_grid = grids[0] if grids else None
    recommended_count = int(primary_grid["total"]) if primary_grid else required_count
    recommended_vals = lighting_values(room_area, recommended_count, lumens, utilization, maintenance, transmission, calc_position, target_lux)
    minimum_additional_count = max(0, required_count - int(fixture_count))
    recommended_additional_count = max(0, recommended_count - int(fixture_count))
    current_power_kw = fixture_count * power_w / 1000
    current_power_density = (fixture_count * power_w) / room_area if room_area > 0 else 0.0
    recommended_power_kw = recommended_count * power_w / 1000
    recommended_power_density = (recommended_count * power_w) / room_area if room_area > 0 else 0.0

    with right:
        st.markdown(
            """
            <div class='hero-card'>
              <div class='hero-inner'>
                <div class='hero-visual'><span>Mesh Seçim ve Aydınlatma<br/>Karar Destek Sistemi</span></div>
                <div class='hero-content'>
                  <h2>Mesh Seçim ve Aydınlatma Karar Destek Sistemi</h2>
                  <p>Mimari mesh sistemleri için aydınlatma performansı analizi, armatür ihtiyacı, yerleşim etkisi ve alternatif değerlendirmeyi tek ekranda toplayan sade fakat şık bir karar yüzü.</p>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if vals["with_mesh_lux"] >= target_lux:
            notice = f"Seçilen ayarlarla yapılan hesaplamaya göre mevcut düzen {int(round(vals['with_mesh_lux']))} lux sağlar. Hedef değer karşılanıyor."
        else:
            notice = f"Seçilen ayarlar ile yapılan hesaplamaya göre mevcut düzen {int(round(vals['with_mesh_lux']))} lux sağlar. Hedef {int(round(target_lux))} lux'a ulaşmak için ilave {recommended_additional_count} armatür gereklidir."
        st.markdown(f"<div class='notice-bar'>ℹ️ {notice}</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top:14px;'>Sonuç Özeti</div>", unsafe_allow_html=True)
        row1 = st.columns([1,1,1,1.3])
        with row1[0]:
            st.markdown(metric_card("Mesh olmadan", f"{int(round(vals['no_mesh_lux']))} lux", "Referans aydınlık", "Referans", "badge-green"), unsafe_allow_html=True)
        with row1[1]:
            st.markdown(metric_card("Seçili düzen", f"{int(round(vals['with_mesh_lux']))} lux", "Mevcut düzen sonucu", "Dengeli", "badge-amber"), unsafe_allow_html=True)
        with row1[2]:
            st.markdown(metric_card("Hedef (ort. aydınlık)", f"{int(round(target_lux))} lux", "Tasarım hedefi", "Hedef", "badge-blue"), unsafe_allow_html=True)
        with row1[3]:
            st.markdown(draw_comparison_chart(vals['no_mesh_lux'], vals['with_mesh_lux'], target_lux), unsafe_allow_html=True)

        row2 = st.columns(4)
        cards2 = [
            ("Mevcut armatür", f"{int(fixture_count)} adet", "Kurulu"),
            ("Toplam gerekli", f"{required_count} adet", "Hedefe ulaşmak için"),
            ("İlave gerekli", f"{minimum_additional_count} adet", "Ek ihtiyaç"),
            ("Önerilen yerleşim grid", f"{int(primary_grid['rows'])} × {int(primary_grid['columns'])}" if primary_grid else "—", "Sıra × boy"),
        ]
        for col, (t, v, s) in zip(row2, cards2):
            with col:
                st.markdown(metric_card(t, v, s), unsafe_allow_html=True)

        row3 = st.columns(4)
        cards3 = [
            ("Işık kaybı", f"%{tr_number(vals['loss_pct'], 1)}", "Mesh etkisi"),
            ("Mevcut toplam güç", f"{tr_number(current_power_kw, 2)} kW", "Toplam kurulu güç"),
            ("Kurulu güç yoğunluğu", f"{tr_number(current_power_density, 2)} W/m²", "Güç yoğunluğu"),
            ("Önerilen güç", f"{tr_number(recommended_power_kw, 2)} kW", "Önerilen düzen"),
        ]
        for col, (t, v, s) in zip(row3, cards3):
            with col:
                st.markdown(metric_card(t, v, s), unsafe_allow_html=True)

        compare_left, compare_right = st.columns([1.2, .95], gap="large")
        with compare_left:
            st.markdown("<div class='section-title' style='margin-top:14px;'>Yaklaşık armatür yerleşim önerisi</div>", unsafe_allow_html=True)
            if primary_grid:
                st.markdown(
                    f"""
                    <div class='layout-card'>
                        <div style='display:flex; gap:18px; align-items:flex-start; justify-content:space-between;'>
                          <div style='flex:1;'>
                            <div style='color:#1a69a1; font-weight:800; margin-bottom:8px;'>Birinci öneri: En yönünde {int(primary_grid['rows'])} sıra × boy yönünde {int(primary_grid['columns'])} armatür = {int(primary_grid['total'])} adet.</div>
                            <div style='color:#5b6977; line-height:1.65;'>
                              Boy yönünde yaklaşık merkez aralığı: <b>{tr_number(primary_grid['length_spacing'], 2)} m</b><br/>
                              En yönünde yaklaşık merkez aralığı: <b>{tr_number(primary_grid['width_spacing'], 2)} m</b><br/>
                              Duvarlardan yaklaşık ilk merkez mesafesi: boy yönünde <b>{tr_number(primary_grid['length_edge'], 2)} m</b>, en yönünde <b>{tr_number(primary_grid['width_edge'], 2)} m</b>
                            </div>
                          </div>
                          <div style='min-width:170px; text-align:center;'>
                             <div style='font-size:.88rem; color:#6b7785; margin-bottom:6px;'>Önerilen grid</div>
                             <div style='display:inline-block; background:#f5faff; border:1px solid #dbe8f1; border-radius:14px; padding:12px 14px;'>
                                {grid_preview(int(primary_grid['rows']), int(primary_grid['columns']))}
                             </div>
                             <div style='font-size:.83rem; color:#6c7b89; margin-top:6px;'>{tr_number(room_length,1)} m × {tr_number(room_width,1)} m</div>
                          </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            layout_rows = []
            for idx, option in enumerate(grids, start=1):
                layout_rows.append({
                    "Öneri": idx,
                    "Sıra × Boy": f"{int(option['rows'])} × {int(option['columns'])}",
                    "Toplam Armatür": int(option["total"]),
                    "OA Geçirgenliği": f"%{tr_number(transmission*100, 0)}",
                    "Tahmini Aydınlık (lux)": lighting_values(room_area, int(option['total']), lumens, utilization, maintenance, transmission, calc_position, target_lux)["with_mesh_lux"],
                    "İlave Armatür": max(0, int(option['total']) - int(fixture_count)),
                    "Toplam Güç (kW)": int(option['total']) * power_w / 1000,
                    "Güç Yoğunluğu (W/m²)": (int(option['total']) * power_w) / room_area if room_area > 0 else 0.0,
                })
            if layout_rows:
                st.dataframe(pd.DataFrame(layout_rows), use_container_width=True, hide_index=True,
                             column_config={
                                 "Tahmini Aydınlık (lux)": st.column_config.NumberColumn(format="%.0f"),
                                 "Toplam Güç (kW)": st.column_config.NumberColumn(format="%.2f"),
                                 "Güç Yoğunluğu (W/m²)": st.column_config.NumberColumn(format="%.2f"),
                             })
        with compare_right:
            st.markdown("<div class='section-title' style='margin-top:14px;'>Performans Özeti</div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class='compare-box'>
                    <div class='mini-list'>
                       <div class='mini-row'><span>Işık geçirgenliği (OA)</span><span class='dot-green'>%{tr_number(transmission*100, 1)}</span></div>
                       <div class='mini-row'><span>Aydınlık seviyesi</span><span class='dot-amber'>{int(round(vals['with_mesh_lux']))} / {int(round(target_lux))} lux</span></div>
                       <div class='mini-row'><span>Güç yoğunluğu</span><span class='dot-green'>{tr_number(current_power_density,2)} W/m²</span></div>
                       <div class='mini-row'><span>Mekân yüksekliği</span><span>{tr_number(room_height,1)} m</span></div>
                       <div class='mini-row'><span>Armatür konumu</span><span>{light_position}</span></div>
                       <div class='mini-row'><span>Mesh</span><span>{lighting_mesh}</span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if vals["with_mesh_lux"] >= target_lux:
            st.markdown(f"<div class='info-callout'>✅ Ön hesaba göre hedef karşılanıyor. Mevcut düzen yaklaşık <b>{int(round(vals['with_mesh_lux']))} lux</b> sağlıyor.</div>", unsafe_allow_html=True)
        else:
            diff = max(0, target_lux - vals["with_mesh_lux"])
            st.markdown(f"<div class='callout'>⚠️ Ön hesaba göre hedefin yaklaşık <b>{int(round(diff))} lux</b> altındasınız. Toplam <b>{recommended_count}</b> armatür, yani mevcut düzene ek olarak yaklaşık <b>{recommended_additional_count}</b> armatür gerekir.</div>", unsafe_allow_html=True)

with tab_compare:
    st.markdown("<div class='section-title'>Alternatif Karşılaştırma ve Öneri Motoru</div><div class='section-subtitle'>Teknik olarak uygun meshleri filtreleyin, tasarım önceliğine göre sıralayın ve en iyi üç alternatifi açıklamalarıyla görün.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-callout'><b>Aktif proje koşulu:</b> {system_name} · {int(panel_length)} × {int(panel_width)} mm panel · {panel_version} · mevcut seçim <b>{mesh_code}</b> · {tr_number(room_area,1)} m² · hedef {int(round(target_lux))} lux</div>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        priority = st.selectbox("Öneri önceliği", ["Dengeli seçim", "En iyi aydınlatma", "En az ilave armatür", "En düşük enerji tüketimi", "En düşük fire"])
        visual_preference = st.selectbox("Görsel tercih", ["Nötr", "Daha açık tavan", "Daha kapalı görünüm"])
        only_standard = st.checkbox("Yalnızca standart meshleri öner", value=False)
    with f2:
        oa_min = st.number_input("Minimum OA (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        oa_max = st.number_input("Maksimum OA (%)", min_value=0.0, max_value=100.0, value=100.0, step=1.0)
        use_max_additional = st.checkbox("İlave armatür üst sınırı", value=False)
        max_additional = st.number_input("En fazla ilave armatür", min_value=0, max_value=10000, value=40, step=1, disabled=not use_max_additional)
    with f3:
        use_max_power_density = st.checkbox("Güç yoğunluğu üst sınırı", value=False)
        max_power_density = st.number_input("Maksimum güç yoğunluğu (W/m²)", min_value=0.0, max_value=500.0, value=20.0, step=0.5, disabled=not use_max_power_density)
        compare_correction = st.slider("Alternatifler için OA düzeltme katsayısı", 0.50, 1.10, 0.90, 0.01)

    with st.expander("İsteğe bağlı proje bazlı fire verisi"):
        fire_seed = pd.DataFrame({"Mesh": meshes["mesh_code"].tolist(), "Fire (%)": [None] * len(meshes)})
        fire_editor = st.data_editor(
            fire_seed,
            use_container_width=True,
            hide_index=True,
            disabled=["Mesh"],
            key="mesh_fire_editor_v6",
            column_config={"Fire (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.1, format="%.1f")},
        )
        fire_map = {str(row["Mesh"]): float(row["Fire (%)"]) for _, row in fire_editor.iterrows() if pd.notna(row["Fire (%)"])}

    candidate_rows, eliminated_rows = [], []
    panel_area = panel_length * panel_width / 1_000_000
    for _, mesh_row in meshes.iterrows():
        code = str(mesh_row["mesh_code"])
        reasons = []
        if panel_length > selected_system["max_panel_length_mm"]:
            reasons.append(f"Panel boyu sistem sınırını aşıyor ({int(selected_system['max_panel_length_mm'])} mm)")
        if panel_width > selected_system["max_panel_width_mm"]:
            reasons.append(f"Panel eni sistem sınırını aşıyor ({int(selected_system['max_panel_width_mm'])} mm)")
        if panel_area > selected_system["recommended_max_area_m2"]:
            reasons.append(f"Panel alanı önerilen sınırı aşıyor ({selected_system['recommended_max_area_m2']:.1f} m²)")
        if not bool(mesh_row[panel_version]):
            reasons.append(f"{panel_version} panel versiyonu ile katalogda uyumlu değil")
        if float(mesh_row["open_area_pct"]) < oa_min or float(mesh_row["open_area_pct"]) > oa_max:
            reasons.append(f"OA kullanıcı sınırı dışında (%{oa_min:.0f}–%{oa_max:.0f})")
        if only_standard and not bool(mesh_row["is_standard"]):
            reasons.append("Katalogda standart mesh olarak işaretli değil")

        estimated_t = min(1.0, float(mesh_row["open_area_pct"]) / 100 * compare_correction)
        result = lighting_values(room_area, int(fixture_count), lumens, utilization, maintenance, estimated_t, calc_position, target_lux)
        required_total = int(result["required_count"])
        additional = max(0, required_total - int(fixture_count))
        power_kw_target = required_total * power_w / 1000
        power_density_target = required_total * power_w / room_area if room_area > 0 else 0.0

        if use_max_additional and additional > int(max_additional):
            reasons.append(f"İlave armatür sınırını aşıyor ({additional} > {int(max_additional)})")
        if use_max_power_density and power_density_target > float(max_power_density):
            reasons.append(f"Güç yoğunluğu sınırını aşıyor ({power_density_target:.1f} > {float(max_power_density):.1f} W/m²)")
        if priority == "En düşük fire" and code not in fire_map:
            reasons.append("En düşük fire sıralaması için fire değeri girilmedi")

        if reasons:
            eliminated_rows.append({"Mesh": code, "Neden": " · ".join(reasons)})
            continue

        candidate_rows.append({
            "Mesh": code,
            "ML × MW (mm)": f"{mesh_row['mesh_length_mm']} × {mesh_row['mesh_width_mm']}",
            "OA (%)": float(mesh_row["open_area_pct"]),
            "Geçici T (%)": estimated_t * 100,
            "Mevcut düzende lux": result["with_mesh_lux"],
            "Işık kaybı (%)": result["loss_pct"],
            "Toplam gerekli": required_total,
            "İlave gerekli": additional,
            "Hedefte güç (kW)": power_kw_target,
            "Hedefte W/m²": power_density_target,
            "Standart": bool(mesh_row["is_standard"]),
            "Fire (%)": fire_map.get(code),
        })

    if not candidate_rows:
        st.markdown("<div class='callout'>⚠️ Seçilen filtrelerle uygun mesh bulunamadı. OA sınırlarını veya ilave armatür kısıtlarını gevşetmeyi deneyin.</div>", unsafe_allow_html=True)
        if eliminated_rows:
            st.dataframe(pd.DataFrame(eliminated_rows), use_container_width=True, hide_index=True)
    else:
        eligible = pd.DataFrame(candidate_rows)
        eligible["Aydınlatma puanı"] = score_higher(eligible["Mevcut düzende lux"])
        eligible["İlave puanı"] = score_lower(eligible["İlave gerekli"])
        eligible["Enerji puanı"] = score_lower(eligible["Hedefte güç (kW)"])
        eligible["Görsel puan"] = visual_preference_score(eligible["OA (%)"], visual_preference)
        eligible["Standart puanı"] = eligible["Standart"].map({True:100.0, False:50.0})
        if eligible["Fire (%)"].notna().any():
            eligible["Fire puanı"] = score_lower(eligible["Fire (%)"])
        else:
            eligible["Fire puanı"] = 50.0

        if priority == "En iyi aydınlatma":
            eligible["Öneri puanı"] = eligible["Aydınlatma puanı"] * 0.5 + eligible["İlave puanı"] * 0.2 + eligible["Enerji puanı"] * 0.15 + eligible["Görsel puan"] * 0.1 + eligible["Standart puanı"] * 0.05
        elif priority == "En az ilave armatür":
            eligible["Öneri puanı"] = eligible["İlave puanı"] * 0.5 + eligible["Aydınlatma puanı"] * 0.2 + eligible["Enerji puanı"] * 0.15 + eligible["Görsel puan"] * 0.1 + eligible["Standart puanı"] * 0.05
        elif priority == "En düşük enerji tüketimi":
            eligible["Öneri puanı"] = eligible["Enerji puanı"] * 0.5 + eligible["İlave puanı"] * 0.2 + eligible["Aydınlatma puanı"] * 0.15 + eligible["Görsel puan"] * 0.1 + eligible["Standart puanı"] * 0.05
        elif priority == "En düşük fire":
            eligible["Öneri puanı"] = eligible["Fire puanı"] * 0.45 + eligible["İlave puanı"] * 0.2 + eligible["Enerji puanı"] * 0.15 + eligible["Aydınlatma puanı"] * 0.1 + eligible["Standart puanı"] * 0.1
        else:
            eligible["Öneri puanı"] = eligible["İlave puanı"] * 0.3 + eligible["Enerji puanı"] * 0.2 + eligible["Aydınlatma puanı"] * 0.2 + eligible["Görsel puan"] * 0.15 + eligible["Fire puanı"] * 0.1 + eligible["Standart puanı"] * 0.05

        eligible = eligible.sort_values(["Öneri puanı", "İlave gerekli", "Hedefte güç (kW)", "OA (%)"], ascending=[False, True, True, False]).reset_index(drop=True)
        eligible.insert(0, "Sıra", range(1, len(eligible)+1))

        summary_cols = st.columns(4)
        with summary_cols[0]:
            st.markdown(metric_card("Uygun alternatif", str(len(eligible)), "Filtreleri geçen mesh sayısı"), unsafe_allow_html=True)
        with summary_cols[1]:
            st.markdown(metric_card("Birinci öneri", str(eligible.iloc[0]["Mesh"]), "En yüksek puanlı mesh", "Öneri", "badge-blue"), unsafe_allow_html=True)
        with summary_cols[2]:
            st.markdown(metric_card("En düşük ilave", f"{int(eligible['İlave gerekli'].min())} adet", "Uygun seçenekler içinde"), unsafe_allow_html=True)
        with summary_cols[3]:
            st.markdown(metric_card("En düşük hedef güç", f"{tr_number(eligible['Hedefte güç (kW)'].min(),2)} kW", "Enerji açısından"), unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top:12px;'>İlk üç öneri</div>", unsafe_allow_html=True)
        for _, candidate in eligible.head(3).iterrows():
            advantages, risks = describe_candidate(candidate, eligible)
            fire_text = "—" if pd.isna(candidate["Fire (%)"]) else f"%{tr_number(candidate['Fire (%)'], 1)}"
            adv_html = "".join([f"<li>{x}</li>" for x in advantages]) if advantages else "<li>—</li>"
            risk_html = "".join([f"<li>{x}</li>" for x in risks]) if risks else "<li>—</li>"
            st.markdown(
                f"""
                <div class='recommendation-card'>
                    <h4>{int(candidate['Sıra'])}. öneri · {candidate['Mesh']}</h4>
                    <div class='recommendation-meta'>
                        Öneri puanı: <b>{tr_number(candidate['Öneri puanı'],1)}/100</b> ·
                        OA %{tr_number(candidate['OA (%)'],1)} · mevcut düzende {int(round(candidate['Mevcut düzende lux']))} lux ·
                        hedef için {int(candidate['Toplam gerekli'])} armatür · ilave {int(candidate['İlave gerekli'])} ·
                        {tr_number(candidate['Hedefte güç (kW)'],2)} kW · fire {fire_text}
                    </div>
                    <div style='display:grid; grid-template-columns:1fr 1fr; gap:14px;'>
                      <div><div style='font-weight:800;color:#2f9e44;margin-bottom:4px;'>Avantajlar</div><ul>{adv_html}</ul></div>
                      <div><div style='font-weight:800;color:#c57d00;margin-bottom:4px;'>Dikkat edilmesi gerekenler</div><ul>{risk_html}</ul></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        best = eligible.iloc[0]
        current_mesh_row = meshes.loc[meshes["mesh_code"] == mesh_code].iloc[0]
        current_t = min(1.0, float(current_mesh_row["open_area_pct"]) / 100 * compare_correction)
        current_result = lighting_values(room_area, int(fixture_count), lumens, utilization, maintenance, current_t, calc_position, target_lux)
        current_required = int(current_result["required_count"])
        current_additional = max(0, current_required - int(fixture_count))
        current_power = current_required * power_w / 1000

        st.markdown("<div class='section-title' style='margin-top:12px;'>Mevcut seçim ile birinci öneri</div>", unsafe_allow_html=True)
        compare_df = pd.DataFrame([
            {"Seçenek": f"Mevcut · {mesh_code}", "OA (%)": float(current_mesh_row["open_area_pct"]), "Mevcut düzende lux": float(current_result["with_mesh_lux"]), "Toplam gerekli": current_required, "İlave gerekli": current_additional, "Hedefte güç (kW)": current_power},
            {"Seçenek": f"Önerilen · {best['Mesh']}", "OA (%)": float(best["OA (%)"]), "Mevcut düzende lux": float(best["Mevcut düzende lux"]), "Toplam gerekli": int(best["Toplam gerekli"]), "İlave gerekli": int(best["İlave gerekli"]), "Hedefte güç (kW)": float(best["Hedefte güç (kW)"])},
        ])
        st.dataframe(compare_df, use_container_width=True, hide_index=True,
                     column_config={
                         "OA (%)": st.column_config.NumberColumn(format="%.1f"),
                         "Mevcut düzende lux": st.column_config.NumberColumn(format="%.0f"),
                         "Hedefte güç (kW)": st.column_config.NumberColumn(format="%.2f"),
                     })

        delta_additional = current_additional - int(best["İlave gerekli"])
        delta_power = current_power - float(best["Hedefte güç (kW)"])
        delta_lux = float(best["Mevcut düzende lux"]) - float(current_result["with_mesh_lux"])
        delta_oa = float(best["OA (%)"]) - float(current_mesh_row["open_area_pct"])
        notes = []
        if delta_additional > 0:
            notes.append(f"yaklaşık {delta_additional} daha az ilave armatür")
        elif delta_additional < 0:
            notes.append(f"yaklaşık {abs(delta_additional)} daha fazla ilave armatür")
        if abs(delta_power) > 0.005:
            notes.append(f"{tr_number(abs(delta_power),2)} kW {'daha düşük' if delta_power > 0 else 'daha yüksek'} hedef kurulu gücü")
        if abs(delta_lux) >= 1:
            notes.append(f"mevcut armatürlerle {int(round(abs(delta_lux)))} lux {'daha fazla' if delta_lux > 0 else 'daha az'}")
        if abs(delta_oa) >= 0.1:
            notes.append(f"OA farkı {delta_oa:+.1f} puan")
        if str(best["Mesh"]) == mesh_code:
            st.markdown("<div class='info-callout'>✅ Mevcut mesh seçimi, girilen kriterlere göre birinci sırada kaldı.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='info-callout'>ℹ️ <b>{best['Mesh']}</b>, <b>{mesh_code}</b> seçimine göre {', '.join(notes) if notes else 'benzer bir teknik sonuç'} sunuyor. Nihai karar; görsel beklenti, gerçek geçirgenlik, maliyet ve üretim verisiyle doğrulanmalıdır.</div>", unsafe_allow_html=True)

        display_cols = ["Sıra", "Mesh", "ML × MW (mm)", "OA (%)", "Geçici T (%)", "Mevcut düzende lux", "Işık kaybı (%)", "Toplam gerekli", "İlave gerekli", "Hedefte güç (kW)", "Hedefte W/m²", "Fire (%)", "Standart", "Öneri puanı"]
        st.markdown("<div class='section-title' style='margin-top:12px;'>Tüm uygun alternatifler</div>", unsafe_allow_html=True)
        st.dataframe(eligible[display_cols], use_container_width=True, hide_index=True,
                     column_config={
                         "OA (%)": st.column_config.NumberColumn(format="%.1f"),
                         "Geçici T (%)": st.column_config.NumberColumn(format="%.1f"),
                         "Mevcut düzende lux": st.column_config.NumberColumn(format="%.0f"),
                         "Işık kaybı (%)": st.column_config.NumberColumn(format="%.1f"),
                         "Hedefte güç (kW)": st.column_config.NumberColumn(format="%.2f"),
                         "Hedefte W/m²": st.column_config.NumberColumn(format="%.2f"),
                         "Fire (%)": st.column_config.NumberColumn(format="%.1f"),
                         "Öneri puanı": st.column_config.ProgressColumn(format="%.1f", min_value=0, max_value=100),
                     })
        st.download_button("Öneri tablosunu CSV indir", eligible[display_cols].to_csv(index=False).encode("utf-8-sig"), file_name="mesh_alternatif_onerileri_v6.csv", mime="text/csv")
        if eliminated_rows:
            with st.expander(f"Elenen meshler ve nedenleri ({len(eliminated_rows)} adet)"):
                st.dataframe(pd.DataFrame(eliminated_rows), use_container_width=True, hide_index=True)


with tab_gpt:
    st.markdown(
        "<div class='section-title'>Ücretsiz GPT Tasarım Asistanı Köprüsü</div>"
        "<div class='section-subtitle'>Uygulama teknik hesabı hazırlar; bu sekme sonucu özel Durlum GPT’ye aktarılabilecek güvenli bir proje metnine dönüştürür. API kullanılmaz.</div>",
        unsafe_allow_html=True,
    )

    # Alternatif listesi, yalnızca seçili sistem ve panel versiyonuna teknik olarak uygun meshlerden oluşturulur.
    gpt_alternatives = []
    for _, gpt_mesh_row in meshes.iterrows():
        gpt_panel_area = panel_length * panel_width / 1_000_000
        technically_ok = (
            panel_length <= selected_system["max_panel_length_mm"]
            and panel_width <= selected_system["max_panel_width_mm"]
            and gpt_panel_area <= selected_system["recommended_max_area_m2"]
            and bool(gpt_mesh_row[panel_version])
        )
        if not technically_ok:
            continue
        gpt_t = min(1.0, float(gpt_mesh_row["open_area_pct"]) / 100 * 0.90)
        gpt_result = lighting_values(
            room_area,
            int(fixture_count),
            lumens,
            utilization,
            maintenance,
            gpt_t,
            calc_position,
            target_lux,
        )
        gpt_required = int(gpt_result["required_count"])
        gpt_alternatives.append({
            "mesh": str(gpt_mesh_row["mesh_code"]),
            "oa_pct": float(gpt_mesh_row["open_area_pct"]),
            "lux": float(gpt_result["with_mesh_lux"]),
            "required": gpt_required,
            "additional": max(0, gpt_required - int(fixture_count)),
            "power_kw": gpt_required * power_w / 1000,
            "standard": bool(gpt_mesh_row["is_standard"]),
        })
    gpt_alternatives.sort(key=lambda item: (item["additional"], item["power_kw"], -item["lux"]))

    left_ai, right_ai = st.columns([1.0, 1.45], gap="large")
    with left_ai:
        with st.container(border=True):
            st.markdown("<div class='input-group-title'>GPT çıktısı</div>", unsafe_allow_html=True)
            gpt_output_type = st.selectbox(
                "Hazırlanacak çalışma",
                [
                    "Mimari yorum",
                    "Müşteri sunum metni",
                    "Teknik ofis raporu",
                    "Alternatif mesh karşılaştırması",
                    "Eksik veri ve doğrulama listesi",
                ],
            )
            gpt_custom_request = st.text_area(
                "Ek talep",
                placeholder="Örnek: Daha kapalı bir görünüm istiyoruz fakat ilave armatür sayısı mümkün olduğunca düşük olsun.",
                height=120,
            )
            st.markdown(
                "<div class='info-callout'><b>Ücretsiz çalışma:</b> Burada API bağlantısı yoktur. "
                "Uygulama yalnızca hesap özetini ve GPT’ye verilecek hazır komutu oluşturur.</div>",
                unsafe_allow_html=True,
            )

            configured_gpt_url = get_optional_secret("DURLUM_GPT_URL")
            temporary_gpt_url = st.text_input(
                "Durlum GPT bağlantısı",
                value=configured_gpt_url,
                placeholder="https://chatgpt.com/g/g-...",
                help="Kalıcı kullanım için bu bağlantıyı Streamlit Secrets içindeki DURLUM_GPT_URL alanına ekleyin.",
            )

            if temporary_gpt_url.startswith("https://"):
                st.link_button("DURLUM GPT'Yİ AÇ", temporary_gpt_url, use_container_width=True)
            else:
                st.link_button("ÖNCE ÖZEL GPT OLUŞTUR", "https://chatgpt.com/gpts/editor", use_container_width=True)

    primary_grid_text = (
        f"{int(primary_grid['rows'])} × {int(primary_grid['columns'])}"
        if primary_grid else "Yerleşim önerisi bulunamadı"
    )
    gpt_prompt = build_free_gpt_prompt(
        output_type=gpt_output_type,
        custom_request=gpt_custom_request,
        system_name=system_name,
        panel_length=int(panel_length),
        panel_width=int(panel_width),
        panel_version=panel_version,
        room_type=room_type,
        room_area=room_area,
        room_height=room_height,
        target_lux=target_lux,
        light_position=light_position,
        current_mesh=lighting_mesh,
        open_area_pct=float(lighting_mesh_row["open_area_pct"]),
        effective_transmission_pct=transmission * 100,
        current_lux=vals["with_mesh_lux"],
        no_mesh_lux=vals["no_mesh_lux"],
        current_fixture_count=int(fixture_count),
        required_fixture_count=required_count,
        additional_fixture_count=minimum_additional_count,
        power_w=power_w,
        current_power_kw=current_power_kw,
        current_power_density=current_power_density,
        recommended_count=recommended_count,
        recommended_grid=primary_grid_text,
        alternatives=gpt_alternatives,
    )

    with right_ai:
        st.markdown(
            "<div class='hero-card'>"
            "<div class='hero-content'>"
            "<h2>1. Metni Kopyala · 2. Durlum GPT’yi Aç · 3. Yapıştır</h2>"
            "<p>Kod kutusunun sağ üstündeki kopyalama simgesine basın. Ardından özel GPT bağlantısını açıp metni gönderin. "
            "Müşteri çizimleri veya gizli dosyalar otomatik olarak aktarılmaz; yalnızca aşağıdaki sayısal proje özeti kullanılır.</p>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        st.code(gpt_prompt, language=None, wrap_lines=True)
        st.download_button(
            "GPT proje özetini TXT indir",
            gpt_prompt.encode("utf-8"),
            file_name="durlum_gpt_proje_ozeti.txt",
            mime="text/plain",
            use_container_width=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(metric_card("Aktarılan alan", f"{tr_number(room_area,1)} m²", "Yalnızca sayısal özet"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("Aktarılan alternatif", f"{min(5, len(gpt_alternatives))} mesh", "Teknik olarak uygun"), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card("API maliyeti", "0 TL", "ChatGPT ekranında kullanım", "Ücretsiz", "badge-green"), unsafe_allow_html=True)

        st.markdown(
            "<div class='callout'><b>Gizlilik notu:</b> Müşteri adı, çizim, PDF veya ticari belge bu metne otomatik eklenmez. "
            "Gizli bilgi eklemeden önce şirket politikasını uygulayın.</div>",
            unsafe_allow_html=True,
        )

with tab_catalog:
    st.markdown("<div class='section-title'>Katalog Verisi</div><div class='section-subtitle'>RHOMBOS mesh teknik verilerini ve sistem panel sınırlarını temiz bir tabloda inceleyin.</div>", unsafe_allow_html=True)
    display_meshes = meshes.copy()
    for col in ["V1", "V2", "V3_BASIC", "V4", "V5", "V6", "is_standard", "taifun"]:
        display_meshes[col] = display_meshes[col].map({1: "✓", 0: "-"})
    display_meshes = display_meshes.rename(columns={
        "mesh_code": "Mesh",
        "mesh_length_mm": "ML (mm)",
        "mesh_width_mm": "MW (mm)",
        "web_width_mm": "WW (mm)",
        "web_thickness_mm": "WT (mm)",
        "open_area_pct": "OA (%)",
        "V3_BASIC": "V3 Basic",
        "is_standard": "Standart",
        "taifun": "TAIFUN",
    })
    st.dataframe(display_meshes, use_container_width=True, hide_index=True)
    st.markdown("<div class='section-title' style='margin-top:12px;'>Sistem Panel Sınırları</div>", unsafe_allow_html=True)
    st.dataframe(systems.rename(columns={
        "category": "Kategori",
        "system": "Sistem",
        "max_panel_length_mm": "Maks. boy (mm)",
        "max_panel_width_mm": "Maks. en (mm)",
        "recommended_max_area_m2": "Önerilen maks. alan (m²)",
    }), use_container_width=True, hide_index=True)

st.caption("Kaynak veri: durlum RHOMBOS Expanded Metal Ceilings, Open Cell Ceilings ve CHARACTER katalogları. V8 ürün ailesi sürümü teknik ön değerlendirme, entegrasyon ve ücretsiz GPT aktarımı içindir.")
