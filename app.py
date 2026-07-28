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
  <p>RHOMBOS kataloğundaki mesh verileriyle panel uygunluğu, açık alan ve hızlı lümen yöntemi hesabı.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="note">
<b>V4 prototip:</b> Katalogdaki OA (açık alan) değeri ışık geçirgenliği için yalnızca başlangıç tahmini olarak kullanılabilir.
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
            ["Mesh üstünde", "Mesh altında / entegre OMEGA kanalında"],
            help="Armatür mesh altında veya entegre ışık kanalında ise bu ön hesapta mesh ışık kaybı uygulanmaz.",
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
    st.subheader("Aynı aydınlatma koşulunda mesh alternatifleri")
    st.caption("Bu tablo, armatür mesh üstündeyse katalogdaki açık alanı geçici geçirgenlik yaklaşımıyla karşılaştırır.")

    compare_correction = st.slider("Tüm alternatifler için düzeltme katsayısı", 0.50, 1.10, 0.90, 0.01, key="compare_correction")
    rows = []
    for _, row in meshes.iterrows():
        t = min(1.0, row["open_area_pct"] / 100 * compare_correction)
        result = lighting_values(
            room_area,
            int(fixture_count),
            lumens,
            utilization,
            maintenance,
            t,
            "Mesh üstünde" if light_position == "Mesh üstünde" else "Mesh altında",
            target_lux,
        )
        total_required = int(result["required_count"])
        rows.append(
            {
                "Mesh": row["mesh_code"],
                "ML × MW (mm)": f"{row['mesh_length_mm']:g} × {row['mesh_width_mm']:g}",
                "OA (%)": row["open_area_pct"],
                "Geçici T (%)": result["effective_t"] * 100,
                "Tahmini lux": round(result["with_mesh_lux"]),
                "Toplam gerekli": total_required,
                "İlave gerekli": max(0, total_required - int(fixture_count)),
                "Hedef durumu": "Uygun" if result["with_mesh_lux"] >= target_lux else "Hedef altı",
            }
        )
    comparison = pd.DataFrame(rows).sort_values(["Toplam gerekli", "Tahmini lux"], ascending=[True, False])
    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
        column_config={
            "OA (%)": st.column_config.NumberColumn(format="%.1f"),
            "Geçici T (%)": st.column_config.NumberColumn(format="%.1f"),
        },
    )

    st.download_button(
        "Karşılaştırmayı CSV indir",
        comparison.to_csv(index=False).encode("utf-8-sig"),
        file_name="mesh_aydinlatma_karsilastirmasi.csv",
        mime="text/csv",
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
    "Bu prototip teknik ön değerlendirme içindir; nihai proje hesabı olarak kullanılmadan önce firma verileri, "
    "proje standardı ve ölçümlerle doğrulanmalıdır."
)
