import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import json
import base64

def _img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(
    page_title="Indonesia Social Protection Targeting Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── DEN brand colours ─────────────────────────────── */
:root {
    --den-navy: #1a3358;
    --den-gold: #c8a84b;
    --den-light: #f0f4f8;
}

/* Section subheaders */
h2, h3 { color: #1a3358 !important; margin-top: 0.4rem !important; }

/* Hide hamburger menu and deploy button */
#MainMenu { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
header[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
}
/* Hide sidebar collapse/expand buttons so it can't be accidentally closed */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] button { display: none !important; }

.block-container { padding-top: 0.5rem !important; }

/* Gold divider */
hr { border-top: 2px solid #c8a84b !important; margin: 0.4rem 0 !important; }

/* Metric cards */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #dde4ef;
    border-top: 3px solid #c8a84b;
    border-radius: 6px;
    padding: 0.3rem 0.6rem;
    box-shadow: 0 1px 4px rgba(26,51,88,0.08);
}
div[data-testid="metric-container"] label {
    color: #1a3358 !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #1a3358 !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1a3358 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.6rem !important;
}
section[data-testid="stSidebar"] * {
    color: #e8edf5 !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #c8a84b !important;
}
section[data-testid="stSidebar"] hr {
    border-top: 1px solid rgba(200,168,75,0.35) !important;
}
section[data-testid="stSidebar"] .stSlider {
    margin-bottom: 0.1rem !important;
}
section[data-testid="stSidebar"] .stCheckbox {
    margin-bottom: 0.2rem !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #1a3358;
    font-weight: 600;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #c8a84b;
    border-bottom: 3px solid #c8a84b;
}

/* Info boxes */
div[data-testid="stInfo"] {
    background: #eef3fa;
    border-left: 4px solid #1a3358;
}
</style>
""", unsafe_allow_html=True)

# ── Year selection (read state before data load) ───────────────────────────────
sel_year = "2024" if st.session_state.get("year_sel", "March 2025") == "March 2024" else "2025"

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_hh_data(year):
    df = pd.read_parquet(f"rawdata/susmar{year}.parquet")
    df["pcode"] = "ID" + df["prov"].astype(str).str.zfill(2) + df["kab"].astype(str).str.zfill(2)
    return df

@st.cache_data
def load_ind_data(year):
    df = pd.read_parquet(f"rawdata/susmar{year}ind.parquet")
    df["pcode"] = "ID" + df["prov"].astype(str).str.zfill(2) + df["kab"].astype(str).str.zfill(2)
    return df

@st.cache_data
def load_geo():
    with open("data/indonesia_adm2.geojson", encoding="utf-8") as f:
        return json.load(f)

df_hh_raw  = load_hh_data(sel_year)
df_ind_raw = load_ind_data(sel_year)
geo        = load_geo()
GEO_PCODES = {f["properties"]["pcode"] for f in geo["features"]}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    _logo_sb = _img_b64("assets/den_logo.png")
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.6rem;margin-top:-1rem;margin-bottom:0.5rem">
  <img src="data:image/png;base64,{_logo_sb}" width="52" style="flex-shrink:0">
  <div>
    <div style="font-size:0.62rem;font-weight:700;color:#c8a84b;line-height:1.2">
      Dewan Ekonomi Nasional
    </div>
    <div style="font-size:0.72rem;font-weight:700;color:#ffffff;line-height:1.3;margin-top:0.1rem">
      Indonesia Social Protection<br>Targeting Monitor
    </div>
  </div>
</div>
<hr style="border-top:1px solid rgba(200,168,75,0.35);margin:0 0 0.4rem 0">
""", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.8rem;font-weight:700;color:#c8a84b;margin-bottom:0.2rem'>Target Settings</div>",
                unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.78rem;font-weight:600;margin-top:0.3rem'>PKH (Cash Transfer)</div>",
                unsafe_allow_html=True)
    pkh_decile   = st.slider("Bottom decile", 1, 10, 4, key="pkh_dec",
                             help="Households in decile 1 up to this value are PKH targets")
    use_comp_pkh = st.checkbox("Require household eligibility", value=True,
                               help="Household must have: child ≤5, school-enrolled member (SD–SMA), or elderly >60")

    st.markdown("<div style='font-size:0.78rem;font-weight:600;margin-top:0.3rem'>BPNT (Food Voucher)</div>",
                unsafe_allow_html=True)
    bpnt_decile  = st.slider("Bottom decile", 1, 10, 5, key="bpnt_dec")

    st.markdown("<div style='font-size:0.78rem;font-weight:600;margin-top:0.3rem'>PBI (Health Insurance)</div>",
                unsafe_allow_html=True)
    pbi_decile   = st.slider("Bottom decile", 1, 10, 5, key="pbi_dec")

    st.markdown("<div style='font-size:0.78rem;font-weight:600;margin-top:0.3rem'>PIP (School Assistance)</div>",
                unsafe_allow_html=True)
    pip_decile   = st.slider("Bottom decile", 1, 10, 4, key="pip_dec",
                             help="Target: school-aged individuals (pip_age=1) in selected deciles")

    st.markdown("<hr style='margin:0.4rem 0'>", unsafe_allow_html=True)
    st.caption(f"Susenas Maret {sel_year} · PKH/BPNT: wh · PBI/PIP: wi")

# ── Aggregation helpers (static) ──────────────────────────────────────────────
HH_AGG = ["w_pkh_tgt", "w_bpnt_tgt", "w_pkh_rec", "w_bpnt_rec",
           "w_ee_pkh", "w_ie_pkh", "w_ee_bpnt", "w_ie_bpnt"]
IND_AGG = ["w_pbi_tgt", "w_pbi_rec", "w_ee_pbi", "w_ie_pbi",
           "w_pip_tgt", "w_pip_rec", "w_ee_pip", "w_ie_pip"]

def hh_rates_row(row):
    return pd.Series({
        "EE_PKH":     round(row["w_ee_pkh"]  / row["w_pkh_tgt"]  * 100, 1) if row["w_pkh_tgt"]  > 0 else None,
        "IE_PKH":     round(row["w_ie_pkh"]  / row["w_pkh_rec"]  * 100, 1) if row["w_pkh_rec"]  > 0 else None,
        "EE_BPNT":    round(row["w_ee_bpnt"] / row["w_bpnt_tgt"] * 100, 1) if row["w_bpnt_tgt"] > 0 else None,
        "IE_BPNT":    round(row["w_ie_bpnt"] / row["w_bpnt_rec"] * 100, 1) if row["w_bpnt_rec"] > 0 else None,
        "EE_PKH_hh":  round(row["w_ee_pkh"]),
        "IE_PKH_hh":  round(row["w_ie_pkh"]),
        "EE_BPNT_hh": round(row["w_ee_bpnt"]),
        "IE_BPNT_hh": round(row["w_ie_bpnt"]),
    })

def ind_rates_row(row):
    return pd.Series({
        "EE_PBI":    round(row["w_ee_pbi"] / row["w_pbi_tgt"] * 100, 1) if row["w_pbi_tgt"] > 0 else None,
        "IE_PBI":    round(row["w_ie_pbi"] / row["w_pbi_rec"] * 100, 1) if row["w_pbi_rec"] > 0 else None,
        "EE_PBI_hh": round(row["w_ee_pbi"]),
        "IE_PBI_hh": round(row["w_ie_pbi"]),
        "EE_PIP":    round(row["w_ee_pip"] / row["w_pip_tgt"] * 100, 1) if row["w_pip_tgt"] > 0 else None,
        "IE_PIP":    round(row["w_ie_pip"] / row["w_pip_rec"] * 100, 1) if row["w_pip_rec"] > 0 else None,
        "EE_PIP_hh": round(row["w_ee_pip"]),
        "IE_PIP_hh": round(row["w_ie_pip"]),
    })

def groupby_hh(grp_df, *keys):
    sums  = grp_df.groupby(list(keys))[HH_AGG].sum().reset_index()
    rates = sums[HH_AGG].apply(hh_rates_row, axis=1)
    return pd.concat([sums[list(keys)], rates], axis=1)

def groupby_ind(grp_df, *keys):
    sums  = grp_df.groupby(list(keys))[IND_AGG].sum().reset_index()
    rates = sums[IND_AGG].apply(ind_rates_row, axis=1)
    return pd.concat([sums[list(keys)], rates], axis=1)

# ── Compute: PKH & BPNT (household level) ────────────────────────────────────
df = df_hh_raw.copy()
pkh_tgt  = ((df["decile"] <= pkh_decile) & (df["comp_pkh"] == 1)) if use_comp_pkh \
           else (df["decile"] <= pkh_decile)
bpnt_tgt = df["decile"] <= bpnt_decile
wh = df["wh"]
df["w_pkh_tgt"]  = pkh_tgt.astype(int)  * wh
df["w_bpnt_tgt"] = bpnt_tgt.astype(int) * wh
df["w_pkh_rec"]  = df["receive_pkh"]  * wh
df["w_bpnt_rec"] = df["receive_bpnt"] * wh
df["w_ee_pkh"]   = ((df["receive_pkh"]  == 0) &  pkh_tgt).astype(int)  * wh
df["w_ie_pkh"]   = ((df["receive_pkh"]  == 1) & ~pkh_tgt).astype(int)  * wh
df["w_ee_bpnt"]  = ((df["receive_bpnt"] == 0) &  bpnt_tgt).astype(int) * wh
df["w_ie_bpnt"]  = ((df["receive_bpnt"] == 1) & ~bpnt_tgt).astype(int) * wh

# ── Compute: PBI & PIP (individual level) ────────────────────────────────────
df_ind  = df_ind_raw.copy()
pbi_tgt = df_ind["decile"] <= pbi_decile
pip_tgt = (df_ind["decile"] <= pip_decile) & (df_ind["pip_age"] == 1)
wi = df_ind["wi"]
df_ind["w_pbi_tgt"] = pbi_tgt.astype(int) * wi
df_ind["w_pbi_rec"] = df_ind["receive_pbi"] * wi
df_ind["w_ee_pbi"]  = ((df_ind["receive_pbi"] == 0) &  pbi_tgt).astype(int) * wi
df_ind["w_ie_pbi"]  = ((df_ind["receive_pbi"] == 1) & ~pbi_tgt).astype(int) * wi
df_ind["w_pip_tgt"] = pip_tgt.astype(int) * wi
df_ind["w_pip_rec"] = df_ind["receive_pip"] * wi
df_ind["w_ee_pip"]  = ((df_ind["receive_pip"] == 0) &  pip_tgt).astype(int) * wi
df_ind["w_ie_pip"]  = ((df_ind["receive_pip"] == 1) & ~pip_tgt).astype(int) * wi

# ── Aggregate ─────────────────────────────────────────────────────────────────
hh_nat  = df[HH_AGG].sum()
ind_nat = df_ind[IND_AGG].sum()
nat_m = {
    "EE_PKH":  (hh_nat["w_ee_pkh"]  / hh_nat["w_pkh_tgt"]  * 100) if hh_nat["w_pkh_tgt"]  > 0 else None,
    "IE_PKH":  (hh_nat["w_ie_pkh"]  / hh_nat["w_pkh_rec"]  * 100) if hh_nat["w_pkh_rec"]  > 0 else None,
    "EE_BPNT": (hh_nat["w_ee_bpnt"] / hh_nat["w_bpnt_tgt"] * 100) if hh_nat["w_bpnt_tgt"] > 0 else None,
    "IE_BPNT": (hh_nat["w_ie_bpnt"] / hh_nat["w_bpnt_rec"] * 100) if hh_nat["w_bpnt_rec"] > 0 else None,
    "EE_PBI":  (ind_nat["w_ee_pbi"] / ind_nat["w_pbi_tgt"] * 100) if ind_nat["w_pbi_tgt"] > 0 else None,
    "IE_PBI":  (ind_nat["w_ie_pbi"] / ind_nat["w_pbi_rec"] * 100) if ind_nat["w_pbi_rec"] > 0 else None,
    "EE_PIP":  (ind_nat["w_ee_pip"] / ind_nat["w_pip_tgt"] * 100) if ind_nat["w_pip_tgt"] > 0 else None,
    "IE_PIP":  (ind_nat["w_ie_pip"] / ind_nat["w_pip_rec"] * 100) if ind_nat["w_pip_rec"] > 0 else None,
}

# Province
prov_hh  = groupby_hh(df, "prov", "provname")
prov_ind = groupby_ind(df_ind, "prov", "provname")
prov_df  = prov_hh.merge(
    prov_ind[["prov", "EE_PBI", "IE_PBI", "EE_PBI_hh", "IE_PBI_hh",
                       "EE_PIP", "IE_PIP", "EE_PIP_hh", "IE_PIP_hh"]],
    on="prov", how="left"
)

# District
dist_hh  = groupby_hh(df, "prov", "kab", "provname", "kabname", "pcode")
dist_ind = groupby_ind(df_ind, "prov", "kab", "provname", "kabname", "pcode")
dist_df  = dist_hh.merge(
    dist_ind[["prov", "kab", "EE_PBI", "IE_PBI", "EE_PBI_hh", "IE_PBI_hh",
                             "EE_PIP", "IE_PIP", "EE_PIP_hh", "IE_PIP_hh"]],
    on=["prov", "kab"], how="left"
)
dist_df["in_map"] = dist_df["pcode"].isin(GEO_PCODES)

# ── Page header ───────────────────────────────────────────────────────────────
_logo = _img_b64("assets/den_logo.png")
st.markdown(f"""
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.3rem">
  <img src="data:image/png;base64,{_logo}" width="72" style="flex-shrink:0">
  <div>
    <div style="font-size:1.5rem;font-weight:700;color:#1a3358;line-height:1.2">
      Indonesia Social Protection Targeting Monitor
      <span style="font-size:0.65rem;font-weight:700;color:#1a3358;background:#f5ecd2;
                   border:1px solid #c8a84b;border-radius:3px;padding:0.1rem 0.4rem;
                   vertical-align:middle;letter-spacing:0.05em">BETA</span>
    </div>
    <div style="font-size:0.85rem;color:#c8a84b;font-weight:600;margin-top:0.15rem">
      Dewan Ekonomi Nasional &nbsp;·&nbsp; Susenas Maret {sel_year}
    </div>
  </div>
</div>""", unsafe_allow_html=True)

pkh_label = f"Decile 1–{pkh_decile}" + (" + comp_pkh" if use_comp_pkh else "")

# ── National metrics (2 rows: EE / IE) ───────────────────────────────────────
_yr_col, _nat_col = st.columns([2, 5])
with _yr_col:
    st.radio("", ["March 2025", "March 2024"], key="year_sel",
             horizontal=True, label_visibility="collapsed")
with _nat_col:
    st.markdown("<div style='padding-top:0.45rem;font-size:1rem;font-weight:700;color:#1a3358'>🇮🇩 National</div>",
                unsafe_allow_html=True)

ee1, ee2, ee3, ee4 = st.columns(4)
ee1.metric("EE PKH",  f"{nat_m['EE_PKH']:.1f}%",  help="% of PKH target HH not receiving PKH")
ee2.metric("EE BPNT", f"{nat_m['EE_BPNT']:.1f}%", help="% of BPNT target HH not receiving BPNT")
ee3.metric("EE PBI",  f"{nat_m['EE_PBI']:.1f}%",  help="% of PBI target individuals not receiving PBI")
ee4.metric("EE PIP",  f"{nat_m['EE_PIP']:.1f}%",  help="% of PIP target individuals not receiving PIP")

st.markdown("<div style='margin-top:-1.4rem'></div>", unsafe_allow_html=True)
ie1, ie2, ie3, ie4 = st.columns(4)
ie1.metric("IE PKH",  f"{nat_m['IE_PKH']:.1f}%",  help="% of PKH recipients outside target")
ie2.metric("IE BPNT", f"{nat_m['IE_BPNT']:.1f}%", help="% of BPNT recipients outside target")
ie3.metric("IE PBI",  f"{nat_m['IE_PBI']:.1f}%",  help="% of PBI recipients outside target")
ie4.metric("IE PIP",  f"{nat_m['IE_PIP']:.1f}%",  help="% of PIP recipients outside target")

st.caption(
    f"Target — PKH: {pkh_label} · BPNT: Decile 1–{bpnt_decile} · "
    f"PBI: Decile 1–{pbi_decile} · PIP: Decile 1–{pip_decile} + school-age"
)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_prov, tab_dist, tab_map, tab_incid, tab_method = st.tabs(["🏙️ Province", "🗂️ District", "🗺️ Map", "📊 Incidences", "📖 Methodology & Data"])

components.html("""
<script>
function injectLink() {
    const tabList = window.parent.document.querySelector('[data-baseweb="tab-list"]');
    if (!tabList || window.parent.document.getElementById('pmt-calc-link')) return;
    const a = window.parent.document.createElement('a');
    a.id = 'pmt-calc-link';
    a.href = 'https://iecalculator.dewanekonomi.go.id/';
    a.target = '_blank';
    a.innerText = '🔗 IE/EE PMT Calculator ↗';
    a.style.cssText = [
        'font-size:0.78rem', 'font-weight:600', 'color:#1a3358',
        'background:#f5ecd2', 'border:1px solid #c8a84b', 'border-radius:4px',
        'padding:0.25rem 0.6rem', 'text-decoration:none', 'white-space:nowrap',
        'margin-left:1rem', 'align-self:center', 'display:inline-flex', 'align-items:center'
    ].join(';');
    tabList.style.alignItems = 'center';
    tabList.appendChild(a);
}
injectLink();
setTimeout(injectLink, 300);
setTimeout(injectLink, 1000);
</script>
""", height=0)

# ── Tab: Province ─────────────────────────────────────────────────────────────
with tab_prov:
    prog_prov = st.radio("Program", ["PKH", "BPNT", "PBI", "PIP"], horizontal=True, key="prog_prov")
    ee_col = f"EE_{prog_prov}"
    ie_col = f"IE_{prog_prov}"

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig_ee = px.bar(
            prov_df.sort_values(ee_col),
            x=ee_col, y="provname", orientation="h",
            title=f"Exclusion Error — {prog_prov} (%)",
            color=ee_col, color_continuous_scale=["#d6e0ef", "#1a3358"],
            labels={ee_col: "EE (%)", "provname": ""},
        )
        fig_ee.update_layout(height=950, coloraxis_showscale=False,
                             margin=dict(l=0), yaxis=dict(tickfont=dict(size=11)))
        st.plotly_chart(fig_ee, use_container_width=True)

    with chart_col2:
        fig_ie = px.bar(
            prov_df.sort_values(ie_col),
            x=ie_col, y="provname", orientation="h",
            title=f"Inclusion Error — {prog_prov} (%)",
            color=ie_col, color_continuous_scale=["#f5ecd2", "#c8a84b"],
            labels={ie_col: "IE (%)", "provname": ""},
        )
        fig_ie.update_layout(height=950, coloraxis_showscale=False,
                             margin=dict(l=0), yaxis=dict(tickfont=dict(size=11)))
        st.plotly_chart(fig_ie, use_container_width=True)

    show_cols = ["provname", "EE_PKH", "IE_PKH", "EE_BPNT", "IE_BPNT",
                 "EE_PBI", "IE_PBI", "EE_PIP", "IE_PIP"]
    show = prov_df[show_cols].copy().sort_values("provname").rename(columns={"provname": "Province"})
    for col in show_cols[1:]:
        show[col] = show[col].map(lambda x: f"{x:.1f}%" if x is not None else "—")
    st.dataframe(show, use_container_width=True, hide_index=True)

# ── Tab: District ─────────────────────────────────────────────────────────────
with tab_dist:
    col_filter, col_search = st.columns([2, 3])
    with col_filter:
        prov_order = dist_df[["prov", "provname"]].drop_duplicates().sort_values("prov")["provname"].tolist()
        prov_sel = st.selectbox("Filter by Province", ["All"] + prov_order)
    with col_search:
        kab_search = st.text_input("Search district name", placeholder="e.g. Bandung")

    d = dist_df.copy()
    if prov_sel != "All":
        d = d[d["provname"] == prov_sel]
    if kab_search:
        d = d[d["kabname"].str.contains(kab_search, case=False)]

    show_d_cols = ["prov", "kab", "provname", "kabname", "EE_PKH", "IE_PKH", "EE_BPNT", "IE_BPNT",
                   "EE_PBI", "IE_PBI", "EE_PIP", "IE_PIP"]
    show_d = d[show_d_cols].copy().sort_values(["prov", "kab"]).drop(columns=["prov", "kab"]).rename(
        columns={"provname": "Province", "kabname": "District"}
    )
    for col in show_d_cols[4:]:
        show_d[col] = show_d[col].map(lambda x: f"{x:.1f}%" if x is not None else "—")
    st.dataframe(show_d, use_container_width=True, hide_index=True)

    unmapped_count = (~dist_df["in_map"]).sum()
    if unmapped_count:
        st.caption(f"ℹ️ {unmapped_count} districts not shown on map (new Papua provinces)")

# ── Tab: Map ──────────────────────────────────────────────────────────────────
with tab_map:
    map_col1, map_col2, map_col3 = st.columns([1, 1, 2])
    with map_col1:
        map_prog  = st.radio("Program", ["PKH", "BPNT", "PBI", "PIP"], horizontal=True, key="map_prog")
    with map_col2:
        map_error = st.radio("Error type", ["EE", "IE"], horizontal=True, key="map_err")
    with map_col3:
        map_prov_filter = st.selectbox("Zoom to Province",
                                       ["All"] + sorted(dist_df["provname"].unique()),
                                       key="map_prov")

    metric_pct = f"{map_error}_{map_prog}"
    metric_hh  = f"{map_error}_{map_prog}_hh"
    err_label  = "Exclusion" if map_error == "EE" else "Inclusion"
    unit_label = "individuals" if map_prog in ("PBI", "PIP") else "HH"

    map_data = dist_df[dist_df["in_map"]][
        ["pcode", "provname", "kabname", metric_pct, metric_hh]
    ].dropna(subset=[metric_pct])

    zoom, center_lat, center_lon = 3.6, -2.0, 118.0
    if map_prov_filter != "All":
        map_data = map_data[map_data["provname"] == map_prov_filter]
        zoom = 6.5
        # Compute center from GeoJSON bounding boxes of matching districts
        prov_pcodes = set(map_data["pcode"])
        lats, lons = [], []
        for f in geo["features"]:
            if f["properties"]["pcode"] in prov_pcodes:
                coords = f["geometry"]["coordinates"]
                rings = coords[0] if f["geometry"]["type"] == "Polygon" \
                        else [pt for part in coords for ring in part for pt in ring]
                lons.extend(c[0] for c in rings)
                lats.extend(c[1] for c in rings)
        if lats:
            center_lat = (min(lats) + max(lats)) / 2
            center_lon = (min(lons) + max(lons)) / 2

    def make_map(color_col, title, color_scale, range_col, colorbar_title, suffix=""):
        fig = px.choropleth_mapbox(
            map_data,
            geojson=geo,
            locations="pcode",
            featureidkey="properties.pcode",
            color=color_col,
            color_continuous_scale=color_scale,
            range_color=range_col,
            mapbox_style="carto-positron",
            zoom=zoom,
            center={"lat": center_lat, "lon": center_lon},
            opacity=0.75,
            hover_name="kabname",
            hover_data={"provname": True, "pcode": False,
                        metric_pct: ":.1f", metric_hh: ":,.0f"},
            labels={"provname": "Province", metric_pct: "Error (%)", metric_hh: unit_label},
            title=title,
        )
        fig.update_layout(
            height=560,
            margin={"r": 0, "t": 36, "l": 0, "b": 0},
            coloraxis_colorbar=dict(title=colorbar_title, ticksuffix=suffix),
        )
        return fig

    st.plotly_chart(
        make_map(metric_pct, f"{err_label} Error — {map_prog} (%)",
                 "RdYlGn_r", [0, 100], "%", "%"),
        use_container_width=True,
    )

    max_hh = int(map_data[metric_hh].max()) if not map_data.empty else 1
    st.plotly_chart(
        make_map(metric_hh, f"{err_label} Error — {map_prog} ({unit_label})",
                 "YlOrRd", [0, max_hh], unit_label),
        use_container_width=True,
    )

    unmapped = dist_df[~dist_df["in_map"]][["provname", "kabname", metric_pct]].dropna(subset=[metric_pct])
    if not unmapped.empty:
        with st.expander(f"⚠️ {len(unmapped)} districts not on map (new Papua provinces)"):
            show_u = unmapped.copy().rename(columns={"provname": "Province", "kabname": "District"})
            show_u[metric_pct] = show_u[metric_pct].map(lambda x: f"{x:.1f}%")
            st.dataframe(show_u, use_container_width=True, hide_index=True)

# ── Tab: Incidences ───────────────────────────────────────────────────────────
with tab_incid:
    st.caption("Share of population receiving each program by welfare decile — national. Target settings in the sidebar do not apply here.")

    def incid_hh(col):
        g = df_hh_raw.groupby("decile").apply(
            lambda x: (x[col] * x["wh"]).sum() / x["wh"].sum() * 100
        ).reset_index(name="pct")
        g["not_pct"] = 100 - g["pct"]
        return g

    def incid_ind(col, mask=None):
        d = df_ind_raw if mask is None else df_ind_raw[mask]
        g = d.groupby("decile").apply(
            lambda x: (x[col] * x["wi"]).sum() / x["wi"].sum() * 100
        ).reset_index(name="pct")
        g["not_pct"] = 100 - g["pct"]
        return g

    def stacked_chart(data, title, note=""):
        fig = px.bar(
            data.melt(id_vars="decile", value_vars=["pct", "not_pct"],
                      var_name="status", value_name="share"),
            x="decile", y="share", color="status",
            color_discrete_map={"pct": "#1a3358", "not_pct": "#d6e0ef"},
            labels={"decile": "Welfare decile", "share": "%", "status": ""},
            title=title,
            barmode="stack",
        )
        fig.update_layout(
            height=320,
            margin=dict(t=40, b=30, l=0, r=0),
            yaxis=dict(range=[0, 100], ticksuffix="%"),
            xaxis=dict(tickmode="linear", dtick=1),
            legend=dict(orientation="h", y=-0.2,
                        itemclick=False, itemdoubleclick=False),
            showlegend=True,
        )
        fig.for_each_trace(lambda t: t.update(
            name="Receiving" if t.name == "pct" else "Not receiving",
            hovertemplate="%{y:.1f}%<extra>%{fullData.name}</extra>"
        ))
        if note:
            fig.add_annotation(x=10, y=105, text=note, showarrow=False,
                               font=dict(size=10, color="#888"), xanchor="right")
        return fig

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(stacked_chart(incid_hh("receive_pkh"),
            "PKH — % of households receiving, by decile"), use_container_width=True)
    with col2:
        st.plotly_chart(stacked_chart(incid_hh("receive_bpnt"),
            "BPNT — % of households receiving, by decile"), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(stacked_chart(incid_ind("receive_pbi"),
            "PBI — % of individuals receiving, by decile"), use_container_width=True)
    with col4:
        st.plotly_chart(stacked_chart(
            incid_ind("receive_pip", df_ind_raw["pip_age"] == 1),
            "PIP — % of school-aged individuals receiving, by decile",
            note="School-aged only (age 6–27)"), use_container_width=True)

# ── Year-specific variable names for methodology ──────────────────────────────
if sel_year == "2024":
    _pkh_var, _bpnt_var, _pip_var = "R2203", "R2208A2–A5", "R616"
    _sch_var1, _sch_var2 = "R610", "R612"
    _hh_n, _ind_n = "~343,000", "~1.21 million"
else:
    _pkh_var, _bpnt_var, _pip_var = "R2002", "R2006A2–A5", "R619"
    _sch_var1, _sch_var2 = "R611", "R613"
    _hh_n, _ind_n = "~343,000", "~1.17 million"

# ── Tab: Methodology & Data ───────────────────────────────────────────────────
with tab_method:
    st.markdown(f"""
<div style="border-left:4px solid #c8a84b;padding:0.6rem 1rem;background:#f8f5ec;
            border-radius:0 6px 6px 0;margin-bottom:1.2rem">
<strong style="color:#1a3358">About this dashboard</strong><br>
<span style="font-size:0.9rem">This monitor tracks targeting accuracy — how well Indonesia's four main social
protection programs reach their intended beneficiaries — using microdata from
Susenas Maret {sel_year}.</span>
</div>
""", unsafe_allow_html=True)

    with st.expander("1. Data Source", expanded=True):
        st.markdown(f"""
**Survey:** Susenas Maret {sel_year} (National Socioeconomic Survey, March wave)
**Publisher:** Badan Pusat Statistik (BPS)
**Coverage:** National, representative at district level
**Sample:**
- Household file: {_hh_n} households
- Individual file: {_ind_n} individuals

**Key variables used:**

| Variable | Source block | Description |
|---|---|---|
| `KAPITA` | Blok 4.3 | Nominal household expenditure per capita |
| `WERT` | KOR RT | Household sampling weight |
| `WEIND` / `FWT` | KOR IND | Individual / person sampling weight |
| `{_pkh_var}` | KOR RT | Received PKH last year |
| `{_bpnt_var}` | KOR RT | Received BPNT (Jan this year / Oct–Dec last year) |
| `R1101_A` | KOR IND | Received PBI health insurance subsidy |
| `{_pip_var}` | KOR IND | Received PIP school assistance |
| `R407` | KOR IND | Age |
| `{_sch_var1}`, `{_sch_var2}` | KOR IND | Currently in school; highest school level attended |
""")

    with st.expander("2. Welfare Measure and Deciles", expanded=True):
        st.markdown(r"""
Welfare is measured as **real per-capita household expenditure**, spatially
deflated to remove price differences across regions:

$$\text{real PCE}_i = \text{nominal PCE}_i \;\times\; \frac{\bar{z}}{\,z_{p,u}\,}$$

where $\bar{z}$ is the national mean poverty line (weighted by $w_i$), and
$z_{p,u}$ is the province $\times$ urban/rural poverty line for March 2025
(published by BPS).

**Welfare deciles** are then constructed by ranking real PCE with individual
sampling weight (`WEIND`) as the frequency weight, yielding population-
representative decile cut-offs.  Decile 1 = poorest 10%; Decile 10 = richest 10%.
""")

    with st.expander("3. Program Definitions and Eligibility Flags", expanded=True):
        st.markdown(f"""
**PKH — Program Keluarga Harapan (Conditional Cash Transfer)**

A household is flagged as a PKH target if it falls within the selected
welfare decile threshold **and** (optionally) satisfies the PKH component
eligibility (`comp_pkh`): child aged ≤ 5, school-enrolled member at SD–SMA
(school level 1–17), or elderly member aged > 60. The sidebar checkbox enables
or disables this demographic condition.

Receipt flag: `receive_pkh = 1` if `{_pkh_var}` = 1 (received PKH last year).

---

**BPNT — Bantuan Pangan Non Tunai (Food Voucher)**

A household is a BPNT target if it falls within the selected welfare decile
threshold (no additional demographic condition).

Receipt flag: `receive_bpnt = 1` if the household received BPNT in January
of the survey year or in October–December of the previous year (`{_bpnt_var}`),
covering the typical quarterly distribution cycle.

---

**PBI — Penerima Bantuan Iuran (Subsidized Health Insurance)**

An individual is a PBI target if they fall within the selected welfare decile
threshold. Unit of analysis: individual (weight `FWT`).

Receipt flag: `receive_pbi = 1` if `R1101_A` = "A" (government-subsidised BPJS Kesehatan).

---

**PIP — Program Indonesia Pintar (School Assistance)**

An individual is a PIP target if they are school-aged (`pip_age = 1`,
age 6–27) and fall within the selected welfare decile threshold.
Unit of analysis: individual (weight `FWT`).

Receipt flag: `receive_pip = 1` if `{_pip_var}` = 1.
""")

    with st.expander("4. Targeting Error Formulas", expanded=True):
        st.markdown(r"""
Let $w_i$ be the sampling weight, $T_i \in \{0,1\}$ the target indicator, and
$R_i \in \{0,1\}$ the receipt indicator for individual or household $i$.

**Exclusion Error (EE)** — share of the target population *not* receiving the benefit:

$$EE = \frac{\sum_i w_i \cdot \mathbf{1}[T_i=1,\; R_i=0]}{\sum_i w_i \cdot \mathbf{1}[T_i=1]}$$

**Inclusion Error (IE)** — share of recipients who are *outside* the target population:

$$IE = \frac{\sum_i w_i \cdot \mathbf{1}[T_i=0,\; R_i=1]}{\sum_i w_i \cdot \mathbf{1}[R_i=1]}$$

Both errors are expressed as percentages.  A perfect program would have
EE = 0 (no eligible person is missed) and IE = 0 (no ineligible person
receives the benefit).

**Weights used:**
- PKH and BPNT: household weight `WERT` (`wh`)
- PBI and PIP: individual weight `FWT` (`wi`)
""")

    with st.expander("5. Default Target Parameters", expanded=False):
        st.markdown("""
The sidebar sliders allow users to vary the welfare decile threshold for
each program.  The defaults below reflect the programmes' stated targeting
criteria:

| Program | Default decile threshold | Additional condition |
|---|---|---|
| PKH | Bottom 40% (decile ≤ 4) | `comp_pkh = 1` (enabled by default) |
| BPNT | Bottom 50% (decile ≤ 5) | None |
| PBI | Bottom 50% (decile ≤ 5) | None |
| PIP | Bottom 40% (decile ≤ 4) | `pip_age = 1` (age 6–27, always applied) |
""")

    with st.expander("6. Geographic Coverage", expanded=False):
        st.markdown("""
District-level estimates are mapped to BPS 2020 administrative boundaries
(514 districts/cities).  The survey covers all 38 provinces.

**Unmatched districts:** 26 districts in the new Papua provinces (created
after the 2020 boundary release — Pegunungan Bintang, Mappi, etc.) cannot
be displayed on the choropleth map but are included in all tabular outputs.

**Map join key:** `pcode = "ID" + prov.zfill(2) + kab.zfill(2)`
(matching the ADM2 GeoJSON `pcode` property from OCHA/BPS).
""")

    st.markdown("---")
    st.caption(
        "Dashboard developed for the National Economic Council (Dewan Ekonomi Nasional). "
        "Source code and methodology based on Susenas Maret 2025 processing scripts."
    )
