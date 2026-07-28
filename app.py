from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Bunlar standart değeri olarak sunulmaz; ilk teklif aşamasında kullanılabilecek,
# kullanıcı tarafından değiştirilebilir örnek hedeflerdir.
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

st.set_page_config(
    page_title="Durlum Mesh & Aydınlatma",
    page_icon="◈",
    layout="wide",
)

st.markdown(
    """
<style>
:root {
    --d-blue: #003b5c;
    --d-cyan: #00a8c8;
    --d-green: #b4cc00;
    --soft: #f3f7f8;
    --text: #17313d;
}
.stApp { background: linear-gradient(180deg, #f8fbfc 0%, #eef4f6 100%); color: var(--text); }
.block-container { padding-top: 1.4rem; max-width: 1500px; }
.hero {
    padding: 1.5rem 1.7rem;
    border-radius: 22px;
    background: linear-gradient(120deg, #003b5c 0%, #006e85 70%, #00a8c8 100%);
    color: white;
    margin-bottom: 1rem;
    box-shadow: 0 14px 35px rgba(0, 59, 92, .18);
}
.hero h1 { margin: 0; font-size: 2.15rem; color: white; }
.hero p { margin: .35rem 0 0; opacity: .92; color: white; }
.note {
    border-left: 5px solid var(--d-green);
    background: white;
    color: var(--text);
    padding: .9rem 1rem;
    border-radius: 12px;
    margin: .7rem 0;
}
.layout-card {
    background: white;
    border: 1px solid #dce7ea;
    padding: 1rem 1.1rem;
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(0, 59, 92, .06);
    margin-top: .45rem;
}
.layout-card b { color: #003b5c; }
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dce7ea;
    padding: .8rem;
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(0, 59, 92, .06);
}
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: var(--text); }
.stButton button, .stDownloadButton button {
    border-radius: 11px;
    border: 0;
    background: #003b5c;
    color: white;
}
.small { font-size: .88rem; color: #52666e; }
.recommendation-card {
    background: white;
    border: 1px solid #dce7ea;
    border-left: 6px solid var(--d-cyan);
    padding: 1rem 1.1rem;
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(0, 59, 92, .06);
    margin: .55rem 0;
}
.recommendation-card h4 { margin: 0 0 .35rem 0; color: #003b5c; }
.recommendation-card .score { font-size: .9rem; color: #52666e; }
.recommendation-card ul { margin: .35rem 0 .15rem 1.15rem; }
.recommendation-card .good { color: #146c43; }
.recommendation-card .risk { color: #8a4b08; }
.filter-summary {
    background: #eaf6f8;
    border: 1px solid #cce7ed;
    border-radius: 14px;
    padding: .8rem 1rem;
    margin-bottom: .8rem;
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


def lighting_values(
    room_area_m2: float,
    fixture_count: int,
    lumens_per_fixture: float,
    utilization_factor: float,
    maintenance_factor: float,
    transmission: float,
    light_position: str,
    target_lux: float,
) -> dict[str, float]:
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
    """Gerekli sayıyı karşılayan yaklaşık dikdörtgen yerleşim seçenekleri üretir."""
    if required_count <= 0 or room_length <= 0 or room_width <= 0:
        return []

    aspect = room_length / room_width
    max_axis = max(2, math.ceil(math.sqrt(required_count)) * 3)
    candidates: list[dict[str, float]] = []

    for rows in range(1, max_axis + 1):  # en yönündeki sıra sayısı
        for columns in range(1, max_axis + 1):  # boy yönündeki armatür sayısı
            total = rows * columns
            if total < required_count:
                continue
            extra = total - required_count
            grid_aspect = columns / rows
            aspect_penalty = abs(math.log(max(grid_aspect, 1e-9) / aspect))
            score = extra * 0.25 + aspect_penalty
            candidates.append(
                {
                    "rows": rows,
                    "columns": columns,
                    "total": total,
                    "extra": extra,
                    "length_spacing": room_length / columns,
                    "width_spacing": room_width / rows,
                    "length_edge": room_length / (2 * columns),
                    "width_edge": room_width / (2 * rows),
                    "score": score,
                }
            )

    candidates.sort(key=lambda item: (item["score"], item["extra"], item["total"]))
    unique: list[dict[str, float]] = []
    seen: set[tuple[int, int]] = set()
    for item in candidates:
        key = (int(item["rows"]), int(item["columns"]))
        if key not in seen:
            unique.append(item)
            seen.add(key)
        if len(unique) >= limit:
            break
    return unique



def score_higher(series: pd.Series) -> pd.Series:
    """Yüksek değerin iyi olduğu 0-100 min-maks puanı."""
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
    """Düşük değerin iyi olduğu 0-100 min-maks puanı."""
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


def list_html(items: list[str], css_class: str) -> str:
    if not items:
        return "<span class='small'>—</span>"
    return f"<ul class='{css_class}'>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def describe_candidate(row: pd.Series, eligible: pd.DataFrame) -> tuple[list[str], list[str]]:
    advantages: list[str] = []
    risks: list[str] = []

    min_additional = int(eligible["İlave gerekli"].min())
    max_current_lux = float(eligible["Mevcut düzende lux"].max())
    min_energy = float(eligible["Hedefte güç (kW)"].min())

    if int(row["İlave gerekli"]) == min_additional:
        advantages.append("Uygun alternatifler içinde en az ilave armatür ihtiyacı")
    if math.isclose(float(row["Mevcut düzende lux"]), max_current_lux, rel_tol=1e-9, abs_tol=0.5):
        advantages.append("Mevcut armatür sayısıyla en yüksek tahmini aydınlık")
    if math.isclose(float(row["Hedefte güç (kW)"]), min_energy, rel_tol=1e-9, abs_tol=0.005):
        advantages.append("Hedef lux için en düşük tahmini kurulu güç grubunda")
    if bool(row["Standart"]):
        advantages.append("Katalogda standart mesh olarak işaretli")
    if float(row["OA (%)"]) >= 75:
        advantages.append("Yüksek açık alan; mesh üstü aydınlatmada daha düşük tahmini ışık kaybı")
    if float(row["OA (%)"]) <= 55:
        advantages.append("Daha kapalı tavan görünümü isteyen projeler için güçlü aday")
    if pd.notna(row.get("Fire (%)")) and math.isclose(
        float(row["Fire (%)"]), float(eligible["Fire (%)"].dropna().min()), rel_tol=1e-9, abs_tol=0.05
    ):
        advantages.append("Girilen proje verileri içinde en düşük fire değerine sahip")

    if int(row["İlave gerekli"]) > min_additional:
        risks.append(f"En iyi aydınlatma alternatifine göre {int(row['İlave gerekli']) - min_additional} fazla ilave armatür gerektiriyor")
    if float(row["OA (%)"]) >= 75:
        risks.append("Yüksek açık alan nedeniyle tavan üstü tesisat daha görünür olabilir")
    if float(row["OA (%)"]) <= 55:
        risks.append("Mesh üstü armatürde ışık kaybı ve enerji ihtiyacı daha yüksek olabilir")
    if not bool(row["Standart"]):
        risks.append("Katalogda standart mesh olarak işaretli değil")
    if pd.isna(row.get("Fire (%)")):
        risks.append("Bu mesh için proje bazlı fire verisi girilmedi")

    return advantages[:4], risks[:4]

def apply_room_preset() -> None:
    room_type = st.session_state.get("room_type", "Ofis / çalışma alanı")
    if room_type != "Özel / elle gir":
        st.session_state["target_lux"] = ROOM_TARGETS[room_type]


meshes, systems = load_data()

if "room_type" not in st.session_state:
    st.session_state["room_type"] = "Ofis / çalışma alanı"
if "target_lux" not in st.session_state:
    st.session_state["target_lux"] = ROOM_TARGETS[st.session_state["room_type"]]

st.markdown(
    """
<div class="hero">
  <h1>Durlum Mesh Seçim ve Aydınlatma Ön Hesap Aracı</h1>
  <p>RHOMBOS kataloğundaki mesh verileriyle panel uygunluğu, hızlı aydınlatma hesabı ve açıklanabilir alternatif önerileri.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="note">
<b>V5 prototip:</b> Katalogdaki OA (açık alan) değeri ışık geçirgenliği için yalnızca başlangıç tahmini olarak kullanılabilir.
Kesin sonuç için seçilen mesh, renk, yön ve armatür mesafesiyle lux ölçümü veya fotometrik simülasyon gerekir.
Mekân türü hedefleri düzenlenebilir örnek değerlerdir; proje standardı yerine geçmez.
</div>
""",
    unsafe_allow_html=True,
)

tab_project, tab_light, tab_compare, tab_catalog = st.tabs(
    ["1 · Panel / Mesh", "2 · Aydınlatma", "3 · Alternatif Karşılaştırma", "4 · Katalog Verisi"]
)

with tab_project:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Proje girdileri")
        system_name = st.selectbox("Tavan sistemi", systems["system"].tolist())
        panel_length = st.number_input("Panel boyu (mm)", min_value=100, max_value=6000, value=2200, step=10)
        panel_width = st.number_input("Panel eni (mm)", min_value=100, max_value=3000, value=595, step=5)
        panel_count = st.number_input("Panel adedi", min_value=1, max_value=100000, value=23, step=1)
        default_mesh_index = int(meshes.index[meshes["mesh_code"] == "M600"][0])
        mesh_code = st.selectbox("Mesh kodu", meshes["mesh_code"].tolist(), index=default_mesh_index)
        panel_version = st.selectbox("Panel versiyonu", ["V1", "V2", "V3_BASIC", "V4", "V5", "V6"])
        unit_weight = st.number_input(
            "Birim ağırlık (kg/m²) - ürün/proje verisi varsa",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            help="RHOMBOS mesh tablosunda kg/m² değeri yoktur. Doğrulanmış değer girildiğinde toplam ağırlık hesaplanır.",
        )

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
        st.subheader("Hızlı sonuç")
        c1, c2, c3 = st.columns(3)
        c1.metric("Tek panel", f"{tr_number(area_each, 3)} m²")
        c2.metric("Toplam alan", f"{tr_number(total_area, 2)} m²")
        c3.metric("Açık alan (OA)", f"%{tr_number(selected_mesh['open_area_pct'], 1)}")

        c4, c5, c6 = st.columns(3)
        c4.metric("Maks. panel boyu", f"{int(selected_system['max_panel_length_mm'])} mm")
        c5.metric("Maks. panel eni", f"{int(selected_system['max_panel_width_mm'])} mm")
        c6.metric("Önerilen maks. alan", f"{tr_number(selected_system['recommended_max_area_m2'], 1)} m²")

        if dimensions_ok:
            st.success("Panel ölçüleri seçilen sistemin katalog sınırları içinde.")
        else:
            st.error("Panel ölçülerinden en az biri seçilen sistemin katalog sınırını aşıyor.")

        if version_ok:
            st.success(f"{mesh_code}, {panel_version} panel versiyonu için katalogda teknik olarak mümkün görünüyor.")
        else:
            st.warning(f"{mesh_code}, {panel_version} panel versiyonu için katalog tablosunda uygun gösterilmiyor.")

        if unit_weight > 0:
            st.metric("Tahmini toplam ağırlık", f"{tr_number(total_area * unit_weight, 1)} kg")
        else:
            st.info("Toplam ağırlık için doğrulanmış kg/m² değerini girin; açık alandan ağırlık türetilmiyor.")

        st.caption(
            "Tunnel direction: normal genişletilmiş mesh, bakış yönüne göre daha açık veya kapalı görünebilir. "
            "Bu yüzden Q-R yönü proje kaydında ayrıca tutulmalıdır."
        )

with tab_light:
    st.subheader("Hızlı aydınlatma ön hesabı")
    a, b, c = st.columns(3)
    with a:
        room_type = st.selectbox(
            "Mekân türü",
            list(ROOM_TARGETS.keys()),
            key="room_type",
            on_change=apply_room_preset,
            help="Seçim hedef lux alanını örnek değerle doldurur. Değer elle değiştirilebilir.",
        )
        room_length = st.number_input("Mekân uzunluğu (m)", min_value=1.0, max_value=500.0, value=12.0, step=0.5)
        room_width = st.number_input("Mekân genişliği (m)", min_value=1.0, max_value=500.0, value=10.0, step=0.5)
        target_lux = st.number_input(
            "Hedef ortalama aydınlık (lux)",
            min_value=1.0,
            max_value=5000.0,
            step=25.0,
            key="target_lux",
        )
        st.caption("Bu hedef düzenlenebilir bir ön hesap girdisidir; proje standardına göre kontrol edilmelidir.")
        light_position = st.radio(
            "Armatür konumu",
            [
                "Mesh üstünde",
                "Mesh altında",
                "Mesh içine entegre",
                "Aydınlatma kanalında",
                "Sarkıt",
            ],
            help=(
                "Bu V5 ön hesabında yalnızca 'Mesh üstünde' seçeneğinde mesh geçirgenlik kaybı uygulanır. "
                "Diğer konumlarda armatür ışığının mesh tarafından doğrudan kesilmediği varsayılır."
            ),
        )
    with b:
        fixture_count = st.number_input("Mevcut armatür sayısı", min_value=1, max_value=10000, value=18, step=1)
        lumens = st.number_input("Bir armatürün ışık akısı (lm)", min_value=100.0, max_value=200000.0, value=4000.0, step=100.0)
        power_w = st.number_input("Bir armatürün gücü (W)", min_value=0.0, max_value=5000.0, value=35.0, step=1.0)
        utilization = st.slider("Kullanım faktörü (UF)", 0.10, 1.00, 0.60, 0.01)
        maintenance = st.slider("Bakım faktörü (MF)", 0.10, 1.00, 0.80, 0.01)
    with c:
        transmission_mode = st.radio(
            "Mesh ışık geçirgenliği kaynağı",
            ["Katalog OA değerini geçici tahmin olarak kullan", "Ölçülmüş geçirgenlik değerini kullan"],
        )
        lighting_mesh = st.selectbox("Aydınlatma için mesh", meshes["mesh_code"].tolist(), key="lighting_mesh")
        lighting_mesh_row = meshes.loc[meshes["mesh_code"] == lighting_mesh].iloc[0]
        if transmission_mode.startswith("Katalog"):
            correction = st.slider(
                "Yön / renk / mesafe düzeltme katsayısı",
                0.50,
                1.10,
                0.90,
                0.01,
                help="Deney verisi oluşana kadar kullanılan belirsizlik katsayısı. OA × katsayı şeklinde uygulanır.",
            )
            transmission = min(1.0, lighting_mesh_row["open_area_pct"] / 100 * correction)
            st.caption(
                f"Katalog OA: %{lighting_mesh_row['open_area_pct']:.1f} → geçici etkin geçirgenlik: %{transmission*100:.1f}"
            )
        else:
            measured_t = st.number_input("Ölçülmüş ışık geçirgenliği (%)", min_value=1.0, max_value=100.0, value=75.0, step=0.5)
            transmission = measured_t / 100

    room_area = room_length * room_width
    vals = lighting_values(
        room_area,
        int(fixture_count),
        lumens,
        utilization,
        maintenance,
        transmission,
        "Mesh üstünde" if light_position == "Mesh üstünde" else "Mesh altında",
        target_lux,
    )
    required_count = int(vals["required_count"])
    minimum_additional_count = max(0, required_count - int(fixture_count))
    surplus_count = max(0, int(fixture_count) - required_count)
    grids = grid_options(required_count, room_length, room_width)
    primary_grid = grids[0] if grids else None

    # Matematiksel minimum armatür sayısı her zaman düzgün bir dikdörtgen yerleşime
    # karşılık gelmeyebilir. Bu nedenle grid önerisinin gerçek toplamını ayrıca tutuyoruz.
    recommended_count = int(primary_grid["total"]) if primary_grid else required_count
    recommended_additional_count = max(0, recommended_count - int(fixture_count))
    placement_extra_count = max(0, recommended_count - required_count)
    recommended_vals = lighting_values(
        room_area,
        recommended_count,
        lumens,
        utilization,
        maintenance,
        transmission,
        "Mesh üstünde" if light_position == "Mesh üstünde" else "Mesh altında",
        target_lux,
    )
    current_power_kw = fixture_count * power_w / 1000
    current_power_density = (fixture_count * power_w) / room_area if room_area > 0 else 0.0
    recommended_power_kw = recommended_count * power_w / 1000
    recommended_power_density = (recommended_count * power_w) / room_area if room_area > 0 else 0.0

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Mekân alanı", f"{tr_number(room_area, 1)} m²")
    r2.metric("Mesh olmadan", f"{tr_number(vals['no_mesh_lux'], 0)} lux")
    r3.metric("Seçili düzen", f"{tr_number(vals['with_mesh_lux'], 0)} lux")
    r4.metric("Hedef", f"{tr_number(target_lux, 0)} lux")

    n1, n2, n3, n4 = st.columns(4)
    n1.metric("Mevcut armatür", f"{int(fixture_count)} adet")
    n2.metric("Minimum hesaplanan", f"{required_count} adet")
    n3.metric("Yerleşime uygun önerilen", f"{recommended_count} adet")
    n4.metric("İlave alınması gereken", f"{recommended_additional_count} adet")

    g1, g2, g3, g4 = st.columns(4)
    if primary_grid:
        g1.metric("Önerilen yaklaşık grid", f"{int(primary_grid['rows'])} × {int(primary_grid['columns'])}")
    else:
        g1.metric("Önerilen yaklaşık grid", "—")
    g2.metric("Grid nedeniyle fazladan", f"{placement_extra_count} adet")
    g3.metric("Önerilen düzende lux", f"{tr_number(recommended_vals['with_mesh_lux'], 0)} lux")
    g4.metric("Işık kaybı", f"%{tr_number(vals['loss_pct'], 1)}")

    st.markdown("#### Mevcut düzen ve önerilen düzen karşılaştırması")
    comparison_power = pd.DataFrame(
        [
            {
                "Düzen": "Mevcut düzen",
                "Armatür sayısı": int(fixture_count),
                "Tahmini aydınlık (lux)": vals["with_mesh_lux"],
                "Toplam güç (kW)": current_power_kw,
                "Güç yoğunluğu (W/m²)": current_power_density,
                "Hedef farkı (lux)": vals["with_mesh_lux"] - target_lux,
            },
            {
                "Düzen": "Önerilen grid",
                "Armatür sayısı": recommended_count,
                "Tahmini aydınlık (lux)": recommended_vals["with_mesh_lux"],
                "Toplam güç (kW)": recommended_power_kw,
                "Güç yoğunluğu (W/m²)": recommended_power_density,
                "Hedef farkı (lux)": recommended_vals["with_mesh_lux"] - target_lux,
            },
        ]
    )
    st.dataframe(
        comparison_power,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tahmini aydınlık (lux)": st.column_config.NumberColumn(format="%.0f"),
            "Toplam güç (kW)": st.column_config.NumberColumn(format="%.2f"),
            "Güç yoğunluğu (W/m²)": st.column_config.NumberColumn(format="%.2f"),
            "Hedef farkı (lux)": st.column_config.NumberColumn(format="%+.0f"),
        },
    )

    if vals["with_mesh_lux"] >= target_lux:
        if surplus_count > 0:
            st.success(
                f"Ön hesaba göre hedef karşılanıyor. Mevcut sayı, tahmini minimum ihtiyacın {surplus_count} adet üzerinde."
            )
        else:
            st.success(f"Ön hesaba göre hedef {target_lux:.0f} lux karşılanıyor.")
    else:
        shortage = target_lux - vals["with_mesh_lux"]
        st.warning(
            f"Ön hesaba göre mevcut düzen hedefin yaklaşık {shortage:.0f} lux altında. "
            f"Matematiksel minimum {required_count} armatürdür ve minimuma göre {minimum_additional_count} ilave gerekir. "
            f"Düzgün yerleşim için önerilen {recommended_count} armatürdür; bu düzene geçmek için "
            f"{recommended_additional_count} ilave armatür gerekir."
        )

    st.subheader("Yaklaşık armatür yerleşim önerisi")
    if primary_grid:
        st.markdown(
            f"""
<div class="layout-card">
<b>Birinci öneri:</b> En yönünde <b>{int(primary_grid['rows'])} sıra</b> × boy yönünde
<b>{int(primary_grid['columns'])} armatür</b> = <b>{int(primary_grid['total'])} adet</b>.<br>
Mevcut düzene göre <b>{recommended_additional_count} ilave armatür</b> gerekir ve ön hesapta yaklaşık
<b>{tr_number(recommended_vals['with_mesh_lux'], 0)} lux</b> elde edilir.<br><br>
Boy yönünde yaklaşık merkez aralığı: <b>{tr_number(primary_grid['length_spacing'], 2)} m</b> &nbsp;•&nbsp;
En yönünde yaklaşık merkez aralığı: <b>{tr_number(primary_grid['width_spacing'], 2)} m</b><br>
Duvarlardan yaklaşık ilk merkez mesafesi: boy yönünde <b>{tr_number(primary_grid['length_edge'], 2)} m</b>,
en yönünde <b>{tr_number(primary_grid['width_edge'], 2)} m</b>.<br>
Önerilen düzenin toplam gücü yaklaşık <b>{tr_number(recommended_power_kw, 2)} kW</b>,
güç yoğunluğu ise <b>{tr_number(recommended_power_density, 2)} W/m²</b> olur.
</div>
""",
            unsafe_allow_html=True,
        )

        layout_rows = []
        for index, option in enumerate(grids, start=1):
            layout_rows.append(
                {
                    "Seçenek": index,
                    "Sıra × sütun": f"{int(option['rows'])} × {int(option['columns'])}",
                    "Toplam armatür": int(option["total"]),
                    "Hesaba göre fazla": int(option["extra"]),
                    "Boy aralığı (m)": option["length_spacing"],
                    "En aralığı (m)": option["width_spacing"],
                }
            )
        st.dataframe(
            pd.DataFrame(layout_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Boy aralığı (m)": st.column_config.NumberColumn(format="%.2f"),
                "En aralığı (m)": st.column_config.NumberColumn(format="%.2f"),
            },
        )
        st.caption(
            "Yerleşim, armatürlerin eşit aralıklarla dikdörtgen grid üzerinde dağıtıldığı basit bir geometrik öneridir. "
            "Kirişler, mobilya, çalışma düzlemi, kaçış yolları ve fotometrik dağılım hesaba katılmaz."
        )

    st.markdown(
        """
<div class="note">
<b>Hesap yöntemi:</b> E<sub>ort</sub> = N × Φ × UF × MF × T / Alan.<br>
Bu modül ön teklif ve alternatif karşılaştırma içindir; kamaşma, düzgünlük, ışık dağılımı ve gün ışığı hesabı içermez.
</div>
""",
        unsafe_allow_html=True,
    )

with tab_compare:
    st.subheader("Açıklanabilir mesh alternatifleri")
    st.caption(
        "Program önce teknik olarak uygun olmayan seçenekleri eler; kalan meshleri seçilen önceliğe göre puanlar. "
        "Aydınlatma kıyası, ölçülmüş mesh geçirgenlikleri eklenene kadar OA tabanlı geçici yaklaşımdır."
    )

    st.markdown(
        f"""
<div class="filter-summary">
<b>Aktif proje koşulu:</b> {system_name} · {int(panel_length)} × {int(panel_width)} mm panel ·
{panel_version} versiyonu · mevcut seçim {mesh_code}<br>
<b>Aydınlatma koşulu:</b> {tr_number(room_area, 1)} m² · {int(fixture_count)} armatür ·
{tr_number(lumens, 0)} lm/armatür · hedef {tr_number(target_lux, 0)} lux · {light_position}
</div>
""",
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3)
    with f1:
        priority = st.selectbox(
            "Öneri önceliği",
            [
                "Dengeli seçim",
                "En iyi aydınlatma",
                "En az ilave armatür",
                "En düşük enerji tüketimi",
                "En düşük fire",
            ],
        )
        visual_preference = st.selectbox(
            "Görsel tercih",
            ["Nötr", "Daha açık tavan", "Daha kapalı görünüm"],
            help="Açık alan oranını öneri puanına dahil eder; kesin görsel sonuç değildir.",
        )
        only_standard = st.checkbox("Yalnızca katalogda standart işaretli meshleri öner", value=False)
    with f2:
        oa_min = st.number_input("Minimum açık alan OA (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        oa_max = st.number_input("Maksimum açık alan OA (%)", min_value=0.0, max_value=100.0, value=100.0, step=1.0)
        use_max_additional = st.checkbox("İlave armatür üst sınırı kullan", value=False)
        max_additional = st.number_input(
            "En fazla ilave armatür",
            min_value=0,
            max_value=10000,
            value=40,
            step=1,
            disabled=not use_max_additional,
        )
    with f3:
        use_max_power_density = st.checkbox("Güç yoğunluğu üst sınırı kullan", value=False)
        max_power_density = st.number_input(
            "Maksimum güç yoğunluğu (W/m²)",
            min_value=0.0,
            max_value=500.0,
            value=20.0,
            step=0.5,
            disabled=not use_max_power_density,
        )
        compare_correction = st.slider(
            "Alternatifler için OA düzeltme katsayısı",
            0.50,
            1.10,
            0.90,
            0.01,
            key="compare_correction_v5",
            help="Mesh üstü aydınlatmada geçici T = OA × katsayı olarak uygulanır.",
        )

    if oa_min > oa_max:
        st.error("Minimum OA, maksimum OA değerinden büyük olamaz.")
        st.stop()

    with st.expander("İsteğe bağlı proje bazlı fire verisi"):
        st.info(
            "Fire mesh kataloğunun sabit bir değeri değildir; panel ölçüsü, yön, ham malzeme ve nesting planına bağlıdır. "
            "Elinizde doğrulanmış proje sonucu varsa ilgili mesh satırına yüzde değeri girin."
        )
        fire_seed = pd.DataFrame({"Mesh": meshes["mesh_code"].tolist(), "Fire (%)": [None] * len(meshes)})
        fire_editor = st.data_editor(
            fire_seed,
            use_container_width=True,
            hide_index=True,
            disabled=["Mesh"],
            key="mesh_fire_editor_v5",
            column_config={
                "Fire (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
            },
        )
        fire_map = {
            str(row["Mesh"]): float(row["Fire (%)"])
            for _, row in fire_editor.iterrows()
            if pd.notna(row["Fire (%)"])
        }

    candidate_rows: list[dict[str, object]] = []
    eliminated_rows: list[dict[str, str]] = []

    for _, mesh_row in meshes.iterrows():
        reasons: list[str] = []
        code = str(mesh_row["mesh_code"])
        panel_area = panel_length * panel_width / 1_000_000

        if panel_length > selected_system["max_panel_length_mm"]:
            reasons.append(f"Panel boyu sistem sınırını aşıyor ({int(selected_system['max_panel_length_mm'])} mm)")
        if panel_width > selected_system["max_panel_width_mm"]:
            reasons.append(f"Panel eni sistem sınırını aşıyor ({int(selected_system['max_panel_width_mm'])} mm)")
        if panel_area > selected_system["recommended_max_area_m2"]:
            reasons.append(f"Panel alanı önerilen sınırı aşıyor ({selected_system['recommended_max_area_m2']:.1f} m²)")
        if not bool(mesh_row[panel_version]):
            reasons.append(f"{panel_version} panel versiyonuyla katalogda uyumlu değil")
        if float(mesh_row["open_area_pct"]) < oa_min or float(mesh_row["open_area_pct"]) > oa_max:
            reasons.append(f"OA kullanıcı sınırı dışında (%{oa_min:.0f}–%{oa_max:.0f})")
        if only_standard and not bool(mesh_row["is_standard"]):
            reasons.append("Katalogda standart mesh olarak işaretli değil")

        estimated_t = min(1.0, float(mesh_row["open_area_pct"]) / 100 * compare_correction)
        result = lighting_values(
            room_area,
            int(fixture_count),
            lumens,
            utilization,
            maintenance,
            estimated_t,
            "Mesh üstünde" if light_position == "Mesh üstünde" else "Mesh altında",
            target_lux,
        )
        required_total = int(result["required_count"])
        additional = max(0, required_total - int(fixture_count))
        power_kw_target = required_total * power_w / 1000
        power_density_target = required_total * power_w / room_area if room_area > 0 else 0.0

        if use_max_additional and additional > int(max_additional):
            reasons.append(f"İlave armatür sınırını aşıyor ({additional} > {int(max_additional)})")
        if use_max_power_density and power_density_target > float(max_power_density):
            reasons.append(
                f"Güç yoğunluğu sınırını aşıyor ({power_density_target:.1f} > {float(max_power_density):.1f} W/m²)"
            )
        if priority == "En düşük fire" and code not in fire_map:
            reasons.append("En düşük fire sıralaması için fire değeri girilmedi")

        if reasons:
            eliminated_rows.append({"Mesh": code, "Elenme nedeni": " · ".join(reasons)})
            continue

        candidate_rows.append(
            {
                "Mesh": code,
                "ML × MW (mm)": f"{mesh_row['mesh_length_mm']:g} × {mesh_row['mesh_width_mm']:g}",
                "OA (%)": float(mesh_row["open_area_pct"]),
                "Geçici T (%)": float(result["effective_t"] * 100),
                "Mevcut düzende lux": float(result["with_mesh_lux"]),
                "Işık kaybı (%)": float(result["loss_pct"]),
                "Toplam gerekli": required_total,
                "İlave gerekli": additional,
                "Hedefte güç (kW)": power_kw_target,
                "Hedefte W/m²": power_density_target,
                "Standart": bool(mesh_row["is_standard"]),
                "TAIFUN": bool(mesh_row["taifun"]),
                "Fire (%)": fire_map.get(code),
            }
        )

    eligible = pd.DataFrame(candidate_rows)

    if eligible.empty:
        st.error("Seçilen kriterleri aynı anda karşılayan mesh bulunamadı.")
        if eliminated_rows:
            st.markdown("#### Elenen meshler ve nedenleri")
            st.dataframe(pd.DataFrame(eliminated_rows), use_container_width=True, hide_index=True)
    else:
        eligible["Aydınlatma puanı"] = score_higher(eligible["Mevcut düzende lux"])
        eligible["İlave puanı"] = score_lower(eligible["İlave gerekli"])
        eligible["Enerji puanı"] = score_lower(eligible["Hedefte güç (kW)"])
        eligible["Görsel puan"] = visual_preference_score(eligible["OA (%)"], visual_preference)
        eligible["Standart puanı"] = eligible["Standart"].map({True: 100.0, False: 50.0})
        eligible["Fire puanı"] = score_lower(eligible["Fire (%)"]) if eligible["Fire (%)"].notna().any() else 50.0

        if priority == "En iyi aydınlatma":
            eligible["Öneri puanı"] = eligible["Aydınlatma puanı"]
        elif priority == "En az ilave armatür":
            eligible["Öneri puanı"] = eligible["İlave puanı"]
        elif priority == "En düşük enerji tüketimi":
            eligible["Öneri puanı"] = eligible["Enerji puanı"]
        elif priority == "En düşük fire":
            eligible["Öneri puanı"] = eligible["Fire puanı"]
        else:
            if eligible["Fire (%)"].notna().any():
                eligible["Öneri puanı"] = (
                    eligible["İlave puanı"] * 0.30
                    + eligible["Enerji puanı"] * 0.20
                    + eligible["Aydınlatma puanı"] * 0.20
                    + eligible["Görsel puan"] * 0.15
                    + eligible["Fire puanı"] * 0.10
                    + eligible["Standart puanı"] * 0.05
                )
            else:
                eligible["Öneri puanı"] = (
                    eligible["İlave puanı"] * 0.35
                    + eligible["Enerji puanı"] * 0.25
                    + eligible["Aydınlatma puanı"] * 0.20
                    + eligible["Görsel puan"] * 0.15
                    + eligible["Standart puanı"] * 0.05
                )

        eligible = eligible.sort_values(
            ["Öneri puanı", "İlave gerekli", "Hedefte güç (kW)", "OA (%)"],
            ascending=[False, True, True, False],
        ).reset_index(drop=True)
        eligible.insert(0, "Sıra", range(1, len(eligible) + 1))

        top_three = eligible.head(3)
        st.markdown("### İlk üç öneri")
        for _, candidate in top_three.iterrows():
            advantages, risks = describe_candidate(candidate, eligible)
            fire_text = "—" if pd.isna(candidate["Fire (%)"]) else f"%{tr_number(candidate['Fire (%)'], 1)}"
            st.markdown(
                f"""
<div class="recommendation-card">
<h4>{int(candidate['Sıra'])}. öneri · {candidate['Mesh']}</h4>
<div class="score">Öneri puanı: <b>{tr_number(candidate['Öneri puanı'], 1)}/100</b> ·
OA %{tr_number(candidate['OA (%)'], 1)} · mevcut düzende {tr_number(candidate['Mevcut düzende lux'], 0)} lux ·
hedef için {int(candidate['Toplam gerekli'])} armatür · ilave {int(candidate['İlave gerekli'])} ·
{tr_number(candidate['Hedefte güç (kW)'], 2)} kW · fire {fire_text}</div>
<b class="good">Avantajlar</b>{list_html(advantages, 'good')}
<b class="risk">Dikkat edilmesi gerekenler</b>{list_html(risks, 'risk')}
</div>
""",
                unsafe_allow_html=True,
            )

        best = eligible.iloc[0]
        current_mesh_row = meshes.loc[meshes["mesh_code"] == mesh_code].iloc[0]
        current_t = min(1.0, float(current_mesh_row["open_area_pct"]) / 100 * compare_correction)
        current_result = lighting_values(
            room_area,
            int(fixture_count),
            lumens,
            utilization,
            maintenance,
            current_t,
            "Mesh üstünde" if light_position == "Mesh üstünde" else "Mesh altında",
            target_lux,
        )
        current_required = int(current_result["required_count"])
        current_additional = max(0, current_required - int(fixture_count))
        current_power = current_required * power_w / 1000

        st.markdown("### Mevcut seçim ile birinci öneri")
        delta_additional = current_additional - int(best["İlave gerekli"])
        delta_power = current_power - float(best["Hedefte güç (kW)"])
        delta_lux = float(best["Mevcut düzende lux"]) - float(current_result["with_mesh_lux"])
        delta_oa = float(best["OA (%)"]) - float(current_mesh_row["open_area_pct"])

        current_vs_best = pd.DataFrame(
            [
                {
                    "Seçenek": f"Mevcut · {mesh_code}",
                    "OA (%)": float(current_mesh_row["open_area_pct"]),
                    "Mevcut düzende lux": float(current_result["with_mesh_lux"]),
                    "Toplam gerekli": current_required,
                    "İlave gerekli": current_additional,
                    "Hedefte güç (kW)": current_power,
                },
                {
                    "Seçenek": f"Önerilen · {best['Mesh']}",
                    "OA (%)": float(best["OA (%)"]),
                    "Mevcut düzende lux": float(best["Mevcut düzende lux"]),
                    "Toplam gerekli": int(best["Toplam gerekli"]),
                    "İlave gerekli": int(best["İlave gerekli"]),
                    "Hedefte güç (kW)": float(best["Hedefte güç (kW)"]),
                },
            ]
        )
        st.dataframe(
            current_vs_best,
            use_container_width=True,
            hide_index=True,
            column_config={
                "OA (%)": st.column_config.NumberColumn(format="%.1f"),
                "Mevcut düzende lux": st.column_config.NumberColumn(format="%.0f"),
                "Hedefte güç (kW)": st.column_config.NumberColumn(format="%.2f"),
            },
        )

        comparison_sentences: list[str] = []
        if delta_additional > 0:
            comparison_sentences.append(f"yaklaşık {delta_additional} daha az ilave armatür")
        elif delta_additional < 0:
            comparison_sentences.append(f"yaklaşık {abs(delta_additional)} daha fazla ilave armatür")
        if delta_power > 0.005:
            comparison_sentences.append(f"yaklaşık {tr_number(delta_power, 2)} kW daha düşük hedef kurulu gücü")
        elif delta_power < -0.005:
            comparison_sentences.append(f"yaklaşık {tr_number(abs(delta_power), 2)} kW daha yüksek hedef kurulu gücü")
        if abs(delta_lux) >= 1:
            comparison_sentences.append(f"mevcut armatürlerle {tr_number(abs(delta_lux), 0)} lux {'daha fazla' if delta_lux > 0 else 'daha az'}")
        if abs(delta_oa) >= 0.1:
            comparison_sentences.append(f"OA farkı {delta_oa:+.1f} puan")

        if str(best["Mesh"]) == mesh_code:
            st.success("Mevcut mesh seçimi, girilen kriterlere göre birinci sırada kaldı.")
        else:
            st.info(
                f"{best['Mesh']}, {mesh_code} seçimine göre "
                + (", ".join(comparison_sentences) if comparison_sentences else "benzer bir teknik sonuç")
                + " sunuyor. Nihai karar görsel beklenti, gerçek geçirgenlik, maliyet ve üretim verisiyle doğrulanmalıdır."
            )

        st.markdown("### Tüm uygun alternatifler")
        display_columns = [
            "Sıra",
            "Mesh",
            "ML × MW (mm)",
            "OA (%)",
            "Geçici T (%)",
            "Mevcut düzende lux",
            "Işık kaybı (%)",
            "Toplam gerekli",
            "İlave gerekli",
            "Hedefte güç (kW)",
            "Hedefte W/m²",
            "Fire (%)",
            "Standart",
            "Öneri puanı",
        ]
        st.dataframe(
            eligible[display_columns],
            use_container_width=True,
            hide_index=True,
            column_config={
                "OA (%)": st.column_config.NumberColumn(format="%.1f"),
                "Geçici T (%)": st.column_config.NumberColumn(format="%.1f"),
                "Mevcut düzende lux": st.column_config.NumberColumn(format="%.0f"),
                "Işık kaybı (%)": st.column_config.NumberColumn(format="%.1f"),
                "Hedefte güç (kW)": st.column_config.NumberColumn(format="%.2f"),
                "Hedefte W/m²": st.column_config.NumberColumn(format="%.2f"),
                "Fire (%)": st.column_config.NumberColumn(format="%.1f"),
                "Öneri puanı": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f"),
            },
        )

        export_columns = [col for col in display_columns if col != "Öneri puanı"] + ["Öneri puanı"]
        st.download_button(
            "Öneri tablosunu CSV indir",
            eligible[export_columns].to_csv(index=False).encode("utf-8-sig"),
            file_name="mesh_alternatif_onerileri_v5.csv",
            mime="text/csv",
        )

        if eliminated_rows:
            with st.expander(f"Elenen meshler ve nedenleri ({len(eliminated_rows)} adet)"):
                st.dataframe(pd.DataFrame(eliminated_rows), use_container_width=True, hide_index=True)

        if light_position != "Mesh üstünde":
            st.warning(
                "Seçilen armatür konumunda V5 modeli mesh ışık kaybını uygulamıyor. Bu nedenle aydınlatma ve enerji "
                "sonuçları meshler arasında eşit olabilir; sıralamayı teknik uygunluk, görsel tercih, standart ve varsa fire verisi belirler."
            )

        st.markdown(
            """
<div class="note">
<b>Puanlama şeffaflığı:</b> Dengeli seçim; ilave armatür, hedef enerji, mevcut düzende aydınlık,
görsel açık alan tercihi, katalogdaki standart işareti ve varsa girilmiş fire verisini birlikte değerlendirir.
Bu bir karar destek sıralamasıdır; mimari ve mühendislik onayı yerine geçmez.
</div>
""",
            unsafe_allow_html=True,
        )

with tab_catalog:
    st.subheader("RHOMBOS katalog verisi")
    display_meshes = meshes.copy()
    for col in ["V1", "V2", "V3_BASIC", "V4", "V5", "V6", "is_standard", "taifun"]:
        display_meshes[col] = display_meshes[col].map({1: "✓", 0: "-"})
    display_meshes = display_meshes.rename(
        columns={
            "mesh_code": "Mesh",
            "mesh_length_mm": "ML (mm)",
            "mesh_width_mm": "MW (mm)",
            "web_width_mm": "WW (mm)",
            "web_thickness_mm": "WT (mm)",
            "open_area_pct": "OA (%)",
            "V3_BASIC": "V3 Basic",
            "is_standard": "Standart",
            "taifun": "TAIFUN",
        }
    )
    st.dataframe(display_meshes, use_container_width=True, hide_index=True)

    st.subheader("Sistem panel sınırları")
    st.dataframe(
        systems.rename(
            columns={
                "category": "Kategori",
                "system": "Sistem",
                "max_panel_length_mm": "Maks. boy (mm)",
                "max_panel_width_mm": "Maks. en (mm)",
                "recommended_max_area_m2": "Önerilen maks. alan (m²)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.caption(
    "Kaynak veri: durlum RHOMBOS Expanded Metal Ceilings kataloğu. "
    "V5 prototipi teknik ön değerlendirme ve alternatif sıralaması içindir; nihai proje hesabı olarak kullanılmadan önce firma verileri, "
    "proje standardı ve ölçümlerle doğrulanmalıdır."
)
