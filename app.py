"""
Calculadora de consumo de agua · Práctica 4.2 – Regresión lineal múltiple y correlación
Análisis y Exploración de Datos (INC-2505) · TecNM Campus Cuautla
Stack: DuckDB · pandas · statsmodels · scikit-learn · Plotly · Streamlit · Docker
"""
import platform

import duckdb
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly
import sklearn
import statsmodels
import statsmodels.api as sm
import streamlit as st
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson

# ===========================================================================
# CONFIGURACIÓN GENERAL
# ===========================================================================
AUTOR = "José de Jesús Pablo Jiménez"
CONTROL = "23680075"          # pon "" si no quieres mostrarlo en la página pública
MATERIA = "Análisis y Exploración de Datos (INC-2505)"
ESCUELA = "TecNM · Instituto Tecnológico de Cuautla"

st.set_page_config(page_title="Calculadora de consumo de agua · Práctica 4.2",
                   page_icon="💧", layout="wide", initial_sidebar_state="collapsed")

PRED = ["temperatura_max", "humedad_max", "personas_familia", "consumo_bidon_pc"]
ALL = PRED + ["cpc_consumo"]
INFO = {
    "temperatura_max": dict(corto="Temperatura", largo="Temperatura máxima (°C)", icono="🌡️",
                            unidad="cada +1 °C", paso=0.1, fmt="%.1f",
                            ayuda="Temperatura más alta del día en la zona del hogar."),
    "humedad_max": dict(corto="Humedad", largo="Humedad máxima (%)", icono="💧",
                        unidad="cada +1 punto de humedad", paso=1.0, fmt="%.0f",
                        ayuda="Humedad atmosférica máxima, en porcentaje."),
    "personas_familia": dict(corto="Personas", largo="Personas por hogar", icono="👨‍👩‍👧",
                             unidad="cada persona adicional en el hogar", paso=1.0, fmt="%.0f",
                             ayuda="Cuántas personas viven en la vivienda."),
    "consumo_bidon_pc": dict(corto="Bidón", largo="Consumo de bidón (lt/hab-día)", icono="🚰",
                             unidad="cada +1 lt/hab-día de agua de bidón", paso=0.05, fmt="%.2f",
                             ayuda="Litros de agua embotellada (bidón) por habitante al día."),
    "cpc_consumo": dict(corto="Consumo (CPC)", largo="Consumo per cápita (lt/hab-día)", icono="📈",
                        unidad="", paso=0.1, fmt="%.1f", ayuda=""),
}
SECCIONES = ["🏠 Inicio", "🔮 Predice", "📊 Gráficas", "🧪 Análisis", "ℹ️ Acerca de"]
GRAFICAS = ["1 · Correlaciones", "2 · Tendencia", "3 · Real vs. predicho",
            "4 · Errores del modelo", "5 · Normalidad (Q-Q)", "6 · ¿Qué pesa más?"]

C_PRIMARY, C_TEAL, C_ORANGE, C_INK, C_GRID = "#0369A1", "#0D9488", "#EA580C", "#0B1F33", "#E3ECF3"
PLOT_CFG = {"displaylogo": False, "responsive": True,
            "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
            "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "practica42_grafica"}}

# ===========================================================================
# ESTILOS (tipografía, color, botones, tarjetas)
# ===========================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');
:root{--primary:#0369A1;--primary2:#0891B2;--teal:#0D9488;--ink:#0B1F33;--muted:#53657A;--line:#D9E6F0;--ok:#15803D;--warn:#B45309;}
html, body, .stApp, [data-testid="stMarkdownContainer"], button, input, textarea, select {
  font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; }
h1,h2,h3,h4,.hero-title,.kpi-value,.big-number,.sec-title{font-family:'Outfit','Inter',system-ui,sans-serif !important;letter-spacing:-.01em;}
.stApp{background:radial-gradient(1100px 480px at 90% -8%, #D9EEF9 0%, rgba(217,238,249,0) 62%), #F4F8FB;color:var(--ink);}
#MainMenu, footer, .stDeployButton, [data-testid="stToolbar"], [data-testid="stDecoration"]{display:none !important;}
header[data-testid="stHeader"]{background:transparent;height:0;}
.block-container{max-width:1180px;padding-top:1.1rem;padding-bottom:3.5rem;}

/* Hero */
.hero{background:linear-gradient(135deg,#0369A1 0%,#0891B2 55%,#0D9488 100%);border-radius:24px;padding:2rem 2.2rem;color:#fff;
  position:relative;overflow:hidden;box-shadow:0 22px 44px -22px rgba(3,105,161,.6);margin-bottom:1rem;}
.hero:before{content:"";position:absolute;right:-70px;top:-70px;width:280px;height:280px;border-radius:50%;background:rgba(255,255,255,.10);}
.hero:after{content:"";position:absolute;right:90px;bottom:-110px;width:220px;height:220px;border-radius:50%;background:rgba(255,255,255,.07);}
.hero-eyebrow{font-size:.82rem;letter-spacing:.12em;text-transform:uppercase;opacity:.9;font-weight:600;}
.hero-title{font-size:2.4rem;font-weight:800;line-height:1.1;margin:.35rem 0 .6rem;}
.hero-sub{font-size:1.08rem;line-height:1.55;max-width:46rem;opacity:.96;}
.badge{display:inline-block;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.4);padding:.25rem .8rem;border-radius:999px;font-size:.82rem;margin:.9rem .45rem 0 0;font-weight:500;}

/* Tarjetas */
.card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:1.15rem 1.3rem;box-shadow:0 10px 26px -18px rgba(11,31,51,.35);height:100%;}
.card h4{margin:0 0 .4rem;font-size:1.1rem;font-weight:700;}
.card p{margin:0;color:#2B3F55;line-height:1.6;font-size:.98rem;}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.9rem;margin:.4rem 0 1.1rem;}
.kpi{background:#fff;border:1px solid var(--line);border-radius:18px;padding:1rem 1.2rem;box-shadow:0 10px 26px -18px rgba(11,31,51,.35);}
.kpi-label{font-size:.82rem;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.06em;}
.kpi-value{font-size:2.1rem;font-weight:800;color:var(--primary);line-height:1.15;margin:.2rem 0;}
.kpi-desc{font-size:.92rem;color:#2B3F55;line-height:1.45;}
.sec-title{font-size:1.65rem;font-weight:800;margin:.4rem 0 .15rem;}
.sec-sub{color:var(--muted);font-size:1.02rem;margin-bottom:.9rem;line-height:1.5;}
.step-num{display:inline-flex;width:2rem;height:2rem;border-radius:50%;align-items:center;justify-content:center;background:linear-gradient(135deg,#0369A1,#0891B2);color:#fff;font-weight:700;margin-bottom:.5rem;}

/* Explicación de gráficas */
.explain{background:#fff;border:1px solid var(--line);border-left:5px solid var(--primary);border-radius:16px;padding:1.1rem 1.25rem;box-shadow:0 10px 26px -18px rgba(11,31,51,.35);}
.ex-h{font-family:'Outfit',sans-serif;font-weight:700;font-size:1.02rem;margin:.55rem 0 .15rem;color:var(--primary);}
.ex-h:first-child{margin-top:0;}
.explain p{margin:0 0 .3rem;line-height:1.6;font-size:.98rem;color:#1E3247;}
.chip{display:inline-block;margin-top:.6rem;padding:.3rem .75rem;border-radius:999px;font-size:.85rem;font-weight:600;}
.chip.ok{background:#DCFCE7;color:#14532D;} .chip.warn{background:#FEF3C7;color:#7C2D12;} .chip.info{background:#E0F2FE;color:#0C4A6E;}

/* Resultado de predicción */
.result{background:linear-gradient(135deg,#0B3B5A 0%,#0369A1 60%,#0891B2 100%);color:#fff;border-radius:20px;padding:1.4rem 1.5rem;box-shadow:0 20px 40px -22px rgba(3,105,161,.7);}
.result .lbl{font-size:.82rem;letter-spacing:.1em;text-transform:uppercase;opacity:.85;font-weight:600;}
.big-number{font-size:3.1rem;font-weight:800;line-height:1.05;margin:.25rem 0;}
.big-number small{font-size:1.05rem;font-weight:500;opacity:.9;margin-left:.35rem;}
.result p{margin:.2rem 0 0;opacity:.95;line-height:1.5;}

/* Pipeline de despliegue y herramientas */
.flow{display:flex;flex-wrap:wrap;gap:.6rem;align-items:stretch;}
.flow-step{flex:1 1 150px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:.9rem 1rem;position:relative;text-align:center;}
.flow-step b{display:block;font-family:'Outfit',sans-serif;font-size:.98rem;margin-bottom:.15rem;}
.flow-step span{font-size:.85rem;color:var(--muted);line-height:1.35;display:block;}
.flow-step .ico{font-size:1.5rem;display:block;margin-bottom:.2rem;}
.tool-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:.8rem;}
.tool{background:#fff;border:1px solid var(--line);border-radius:16px;padding:.95rem 1.1rem;}
.tool b{font-family:'Outfit',sans-serif;font-size:1.02rem;}
.tool p{margin:.2rem 0 0;font-size:.93rem;color:#2B3F55;line-height:1.5;}
.footer{margin-top:2.2rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--muted);font-size:.88rem;text-align:center;line-height:1.6;}

/* Botones */
.stButton>button, .stDownloadButton>button{border-radius:12px;font-weight:600;padding:.55rem 1.15rem;min-height:2.85rem;
  border:1.5px solid var(--line);background:#fff;color:var(--ink);transition:transform .12s ease, box-shadow .12s ease, border-color .12s ease;}
.stButton>button:hover, .stDownloadButton>button:hover{border-color:var(--primary);color:var(--primary);transform:translateY(-1px);box-shadow:0 10px 20px -12px rgba(3,105,161,.55);}
.stButton>button:active{transform:translateY(0);}
.stButton>button:disabled{opacity:.45;transform:none;box-shadow:none;}
.stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"], button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,#0369A1,#0891B2);color:#fff;border:none;box-shadow:0 12px 22px -14px rgba(3,105,161,.8);}
.stButton>button[kind="primary"]:hover, .stDownloadButton>button[kind="primary"]:hover{color:#fff;filter:brightness(1.08);}
.stButton>button[kind="primary"] p, .stDownloadButton>button[kind="primary"] p{color:#fff;}
button:focus-visible{outline:3px solid #7DD3FC !important;outline-offset:2px;}

/* Navegación y selectores tipo "píldora" (st.radio horizontal) */
div[role="radiogroup"]{gap:.5rem;flex-wrap:wrap;}
div[role="radiogroup"] > label{background:#fff;border:1.5px solid var(--line);border-radius:999px;padding:.45rem 1.05rem;cursor:pointer;
  transition:all .12s ease;margin:0;}
div[role="radiogroup"] > label > div:first-of-type{display:none;}
div[role="radiogroup"] > label:hover{border-color:var(--primary);transform:translateY(-1px);}
div[role="radiogroup"] > label:has(input:checked){background:linear-gradient(135deg,#0369A1,#0891B2);border-color:transparent;box-shadow:0 10px 20px -12px rgba(3,105,161,.8);}
div[role="radiogroup"] > label:has(input:checked) p{color:#fff !important;font-weight:700;}
div[role="radiogroup"] > label p{font-weight:600;font-size:.95rem;}

/* Gráficas, pestañas y detalles */
[data-testid="stPlotlyChart"]{background:#fff;border:1px solid var(--line);border-radius:18px;padding:.4rem;box-shadow:0 10px 26px -18px rgba(11,31,51,.35);}
.stTabs [data-baseweb="tab-list"]{gap:.35rem;}
.stTabs [data-baseweb="tab"]{border-radius:10px 10px 0 0;padding:.6rem 1rem;font-weight:600;}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:14px;}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;border:1px solid var(--line);}

@media (max-width:640px){
  .hero{padding:1.4rem 1.2rem;border-radius:20px;} .hero-title{font-size:1.7rem;} .big-number{font-size:2.5rem;}
  .block-container{padding-left:.9rem;padding-right:.9rem;}
}
@media (prefers-reduced-motion:reduce){*{transition:none !important;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def html(s: str):
    """Renderiza HTML en una sola línea (evita que Markdown lo interprete como código)."""
    st.markdown("".join(line.strip() for line in s.strip().splitlines()), unsafe_allow_html=True)


def chip(kind: str, text: str) -> str:
    return f'<span class="chip {kind}">{text}</span>'


def encabezado(titulo: str, sub: str):
    html(f'<div class="sec-title">{titulo}</div><div class="sec-sub">{sub}</div>')


# ===========================================================================
# DATOS (DuckDB) Y MODELO
# ===========================================================================
SQL_PROFESOR = """
CREATE TABLE telemetria_agua AS
SELECT
    residencia_id,
    ROUND(18 + (random() * 14), 2) AS temperatura_max,
    ROUND(50 + (random() * 40), 2) AS humedad_max,
    ROUND(3 + (random() * 4), 0) AS personas_familia,
    ROUND(0.2 + (random() * 1.8), 2) AS consumo_bidon_pc,
    ROUND(
        94.0 + (2.5 * (18 + random() * 14))
             - (0.8 * (50 + random() * 40))
             - (5.2 * (3 + random() * 4))
             + (15.0 * (0.2 + random() * 1.8))
             + (random() * 6.0 - 3.0), 2
    ) AS cpc_consumo
FROM generate_series(1, {n}) AS t(residencia_id);
"""

SQL_CORREGIDO = """
CREATE TABLE telemetria_agua AS
SELECT
    residencia_id,
    temperatura_max,
    humedad_max,
    personas_familia,
    consumo_bidon_pc,
    ROUND(94.0 + (2.5 * temperatura_max)
               - (0.8 * humedad_max)
               - (5.2 * personas_familia)
               + (15.0 * consumo_bidon_pc)
               + error_aleatorio, 2) AS cpc_consumo
FROM (
    SELECT
        residencia_id,
        ROUND(18 + (random() * 14), 2)   AS temperatura_max,
        ROUND(50 + (random() * 40), 2)   AS humedad_max,
        ROUND(3 + (random() * 4), 0)     AS personas_familia,
        ROUND(0.2 + (random() * 1.8), 2) AS consumo_bidon_pc,
        (random() * 6.0 - 3.0)           AS error_aleatorio
    FROM generate_series(1, {n}) AS t(residencia_id)
);
"""


@st.cache_data(show_spinner=False)
def generar_datos(semilla: float, n: int, corregido: bool) -> pd.DataFrame:
    con = duckdb.connect(database=":memory:")
    con.execute(f"SELECT setseed({semilla})")
    con.execute((SQL_CORREGIDO if corregido else SQL_PROFESOR).format(n=n))
    df = con.execute("SELECT * FROM telemetria_agua").df()
    con.close()
    return df


@st.cache_data(show_spinner=False)
def ajustar_modelos(df: pd.DataFrame) -> dict:
    X = sm.add_constant(df[PRED])
    Y = df["cpc_consumo"]
    ols = sm.OLS(Y, X).fit()
    resid = ols.resid
    sw_stat, sw_p = stats.shapiro(resid)
    bp = het_breuschpagan(resid, X)
    skl = LinearRegression().fit(df[PRED], Y)
    y_pred = skl.predict(df[PRED])
    return {
        "resumen": ols.summary().as_text(),
        "params": ols.params.to_dict(), "pvalues": ols.pvalues.to_dict(),
        "conf": ols.conf_int().rename(columns={0: "IC 2.5%", 1: "IC 97.5%"}),
        "r2_ols": float(ols.rsquared), "r2_adj": float(ols.rsquared_adj),
        "f": float(ols.fvalue), "f_p": float(ols.f_pvalue), "se": float(np.sqrt(ols.mse_resid)),
        "resid": resid.to_numpy(), "sw": (float(sw_stat), float(sw_p)),
        "dw": float(durbin_watson(resid)), "bp_p": float(bp[1]),
        "y_pred": y_pred, "r2": float(r2_score(Y, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(Y, y_pred))),
        "coef_skl": dict(zip(PRED, skl.coef_)), "int_skl": float(skl.intercept_),
        "beta_std": {v: float(ols.params[v] * df[v].std() / Y.std()) for v in PRED},
    }


# ===========================================================================
# ESTADO Y AJUSTES
# ===========================================================================
DEFAULTS = {"semilla": 0.42, "n": 100, "corregido": True}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)
st.session_state.setdefault("nav", SECCIONES[0])
st.session_state.setdefault("grafica", GRAFICAS[0])


def ir_a(seccion: str):
    st.session_state.nav = seccion


def restablecer():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


def mover_grafica(delta: int):
    i = GRAFICAS.index(st.session_state.grafica) + delta
    st.session_state.grafica = GRAFICAS[max(0, min(len(GRAFICAS) - 1, i))]


# ===========================================================================
# CABECERA: navegación + ajustes
# ===========================================================================
nav_col, set_col = st.columns([5, 1.25], gap="small")
with nav_col:
    st.radio("Navegación", SECCIONES, key="nav", horizontal=True, label_visibility="collapsed")
with set_col:
    with st.popover("⚙️ Ajustes", use_container_width=True):
        st.markdown("**Simulación de datos**")
        st.number_input("Semilla (setseed)", min_value=0.0, max_value=1.0, step=0.01, format="%.2f",
                        key="semilla", help="Con la misma semilla se obtienen siempre los mismos datos.")
        st.slider("Número de hogares (n)", 30, 1000, step=10, key="n",
                  help="Más hogares = estimaciones más estables.")
        st.checkbox("Usar SQL corregido", key="corregido",
                    help="Activo: el consumo se calcula con las columnas mostradas. "
                         "Apagado: SQL literal de la guía, donde el consumo usa números aleatorios independientes.")
        st.button("↩ Restablecer valores de la práctica", on_click=restablecer, use_container_width=True)

semilla, n, corregido = float(st.session_state.semilla), int(st.session_state.n), bool(st.session_state.corregido)
with st.spinner("Preparando datos y entrenando el modelo…"):
    df = generar_datos(semilla, n, corregido)
    res = ajustar_modelos(df)

Y = df["cpc_consumo"].to_numpy()
y_pred, resid = res["y_pred"], res["resid"]
corr = df[ALL].corr(method="pearson")
mejor_var = max(PRED, key=lambda v: abs(res["beta_std"][v]))
SIG = f"{semilla}-{n}-{int(corregido)}"


# ===========================================================================
# UTILIDADES DE GRÁFICAS
# ===========================================================================
def estilo(fig: go.Figure, h: int = 470) -> go.Figure:
    fig.update_layout(
        height=h, margin=dict(l=12, r=12, t=28, b=12), paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, system-ui, sans-serif", size=14, color=C_INK),
        hoverlabel=dict(font_size=13, font_family="Inter, system-ui, sans-serif", bgcolor="#FFFFFF"),
        legend=dict(orientation="h", y=1.07, x=0), showlegend=False)
    fig.update_xaxes(gridcolor=C_GRID, zerolinecolor="#C6D6E3", ticks="outside", automargin=True)
    fig.update_yaxes(gridcolor=C_GRID, zerolinecolor="#C6D6E3", ticks="outside", automargin=True)
    return fig


def tarjeta_explicacion(que: str, como: str, datos: str, chip_html: str = "") -> str:
    return ('<div class="explain">'
            f'<div class="ex-h">👀 ¿Qué estás viendo?</div><p>{que}</p>'
            f'<div class="ex-h">🧭 Cómo leerla</div><p>{como}</p>'
            f'<div class="ex-h">📌 En tus datos</div><p>{datos}</p>{chip_html}</div>')


def fuerza(r: float) -> str:
    a = abs(r)
    return "fuerte" if a >= 0.6 else "moderada" if a >= 0.3 else "débil"


# ===========================================================================
# GRÁFICAS (cada una devuelve figura + explicación)
# ===========================================================================
def g_heatmap():
    labels = [INFO[v]["corto"] for v in ALL]
    z = corr.values
    fig = go.Figure(go.Heatmap(
        z=z.tolist(), x=labels, y=labels, text=np.round(z, 2).tolist(), texttemplate="%{text}",
        textfont=dict(size=14, color=C_INK), zmin=-1, zmax=1, xgap=3, ygap=3,
        colorscale=[[0, "#F97316"], [0.5, "#F8FAFC"], [1, "#0EA5E9"]],
        colorbar=dict(title="r", thickness=14, len=0.9),
        hovertemplate="%{y} × %{x}<br>r = %{z:.2f}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    estilo(fig, 480)
    top = corr["cpc_consumo"].drop("cpc_consumo")
    v = top.abs().idxmax()
    sub = corr.loc[PRED, PRED].values
    mx = float(np.max(np.abs(sub[~np.eye(4, dtype=bool)])))
    ok = mx < 0.7
    exp = tarjeta_explicacion(
        "Una tabla de colores que mide qué tan relacionadas están las variables, de −1 a +1. "
        "<b>Azul</b>: cuando una sube, la otra también. <b>Naranja</b>: cuando una sube, la otra baja. "
        "<b>Blanco</b>: no hay relación.",
        "Fíjate en la fila o columna <b>Consumo (CPC)</b>: cuanto más intenso el color, más se relaciona ese factor con el consumo. "
        "Las otras celdas revelan si los factores se parecen entre sí, algo que confunde al modelo (multicolinealidad).",
        f"La relación más fuerte con el consumo es <b>{INFO[v]['corto']}</b> (r = {top[v]:+.2f}, {fuerza(top[v])}). "
        f"Entre los factores, la correlación más alta es {mx:.2f}.",
        chip("ok" if ok else "warn", "✅ Sin multicolinealidad relevante" if ok else "⚠️ Factores muy parecidos entre sí"))
    return fig, exp


def g_tendencia():
    var = st.selectbox("Compara el consumo con…", PRED, key="g2_var",
                       format_func=lambda v: f"{INFO[v]['icono']} {INFO[v]['largo']}")
    x = df[var].to_numpy()
    b, a = np.polyfit(x, Y, 1)
    r = float(np.corrcoef(x, Y)[0, 1])
    xs = np.array([x.min(), x.max()])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x.tolist(), y=Y.tolist(), mode="markers", name="Hogares",
                             marker=dict(size=9, color=C_PRIMARY, opacity=0.65, line=dict(color="white", width=0.8)),
                             customdata=df["residencia_id"].tolist(),
                             hovertemplate=f"Hogar %{{customdata}}<br>{INFO[var]['corto']}: %{{x}}<br>Consumo: %{{y:.1f}} lt/hab-día<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs.tolist(), y=(a + b * xs).tolist(), mode="lines", name="Tendencia",
                             line=dict(color=C_ORANGE, width=3), hoverinfo="skip"))
    estilo(fig, 440)
    fig.update_layout(showlegend=True)
    fig.update_xaxes(title=INFO[var]["largo"])
    fig.update_yaxes(title="Consumo (lt/hab-día)")
    sentido = "sube" if b > 0 else "baja"
    exp = tarjeta_explicacion(
        f"Cada punto es un hogar. La línea naranja resume la tendencia entre <b>{INFO[var]['corto'].lower()}</b> y el consumo.",
        f"Si la línea {('sube' if b > 0 else 'baja')} hacia la derecha, más {INFO[var]['corto'].lower()} se asocia con "
        f"{'más' if b > 0 else 'menos'} consumo. Cuanto más pegados a la línea, más fuerte es la relación. "
        "Cambia la variable en el selector para explorar las demás.",
        f"En promedio, {INFO[var]['unidad']} el consumo {sentido} ≈ {abs(b):.2f} lt/hab-día (r = {r:+.2f}, relación {fuerza(r)}). "
        "Es una mirada individual; el modelo combina los cuatro factores a la vez.",
        chip("info", f"Relación {fuerza(r)}"))
    return fig, exp


def g_real_pred():
    lo, hi = float(min(Y.min(), y_pred.min())), float(max(Y.max(), y_pred.max()))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="Predicción perfecta",
                             line=dict(color=C_ORANGE, width=3, dash="dash"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=y_pred.tolist(), y=Y.tolist(), mode="markers", name="Hogares",
                             marker=dict(size=9, color=C_TEAL, opacity=0.7, line=dict(color="white", width=0.8)),
                             customdata=df["residencia_id"].tolist(),
                             hovertemplate="Hogar %{customdata}<br>Predicho: %{x:.1f}<br>Real: %{y:.1f}<extra></extra>"))
    estilo(fig, 440)
    fig.update_layout(showlegend=True)
    fig.update_xaxes(title="Consumo predicho por el modelo (lt/hab-día)")
    fig.update_yaxes(title="Consumo real (lt/hab-día)")
    r2 = res["r2"]
    nivel = ("ok", "✅ Ajuste excelente") if r2 >= 0.9 else ("ok", "✅ Buen ajuste") if r2 >= 0.7 else ("warn", "⚠️ Ajuste limitado")
    exp = tarjeta_explicacion(
        "Compara lo que el modelo <b>predijo</b> (eje horizontal) con el consumo <b>real</b> simulado (eje vertical).",
        "La línea naranja punteada es la predicción perfecta. Puntos sobre ella = acierto; puntos lejos = error. "
        "Si la nube sigue la diagonal, el modelo sirve.",
        f"El modelo explica el <b>{r2 * 100:.1f}%</b> de las variaciones del consumo y se equivoca en promedio "
        f"±{res['rmse']:.2f} lt/hab-día.", chip(*nivel))
    return fig, exp


def g_residuos():
    s = float(np.std(resid))
    fuera = np.abs(resid) > 2 * s
    fig = go.Figure()
    fig.add_hline(y=0, line=dict(color=C_ORANGE, width=3, dash="dash"))
    for mask, color, name in ((~fuera, "#7C3AED", "Normal"), (fuera, C_ORANGE, "Más de 2 desv.")):
        fig.add_trace(go.Scatter(
            x=y_pred[mask].tolist(), y=resid[mask].tolist(), mode="markers", name=name,
            marker=dict(size=9, color=color, opacity=0.7, line=dict(color="white", width=0.8)),
            customdata=df["residencia_id"].to_numpy()[mask].tolist(),
            hovertemplate="Hogar %{customdata}<br>Predicho: %{x:.1f}<br>Error: %{y:.2f}<extra></extra>"))
    estilo(fig, 440)
    fig.update_xaxes(title="Consumo predicho (lt/hab-día)")
    fig.update_yaxes(title="Error del modelo = real − predicho")
    ok = res["bp_p"] > 0.05
    exp = tarjeta_explicacion(
        "El <b>error</b> (residuo) es la diferencia entre el consumo real y el que predijo el modelo. Aquí se grafica contra la predicción.",
        "Lo ideal es una nube pareja alrededor de la línea en cero, sin forma de embudo ni de curva. "
        "Eso significa que el modelo se equivoca igual de poco con consumos bajos y altos (homocedasticidad).",
        f"Prueba de Breusch-Pagan: p = {res['bp_p']:.3f}. {int(fuera.sum())} hogar(es) (puntos naranjas) se alejan más de 2 desviaciones.",
        chip("ok" if ok else "warn", "✅ Varianza pareja" if ok else "⚠️ Posible varianza desigual"))
    return fig, exp


def g_qq():
    z = np.sort((resid - resid.mean()) / resid.std(ddof=1))
    teo = stats.norm.ppf((np.arange(1, len(z) + 1) - 0.5) / len(z))
    lo, hi = float(min(teo.min(), z.min())), float(max(teo.max(), z.max()))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", line=dict(color=C_ORANGE, width=3, dash="dash"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=teo.tolist(), y=z.tolist(), mode="markers",
                             marker=dict(size=9, color=C_PRIMARY, opacity=0.7, line=dict(color="white", width=0.8)),
                             hovertemplate="Teórico: %{x:.2f}<br>Observado: %{y:.2f}<extra></extra>"))
    estilo(fig, 440)
    fig.update_xaxes(title="Cuantiles teóricos (distribución normal)")
    fig.update_yaxes(title="Cuantiles de los errores (estandarizados)")
    ok = res["sw"][1] > 0.05
    exp = tarjeta_explicacion(
        "Compara los errores del modelo con una distribución normal (la clásica «campana»).",
        "Si los puntos siguen la diagonal, los errores son normales y las pruebas t y los intervalos de confianza del modelo son confiables. "
        "Desvíos fuertes en las puntas indican errores atípicos.",
        f"Prueba de Shapiro-Wilk: estadístico = {res['sw'][0]:.4f}, p = {res['sw'][1]:.3f}.",
        chip("ok" if ok else "warn", "✅ Errores con distribución normal" if ok else "⚠️ Se rechaza la normalidad"))
    return fig, exp


def g_influencia():
    orden = sorted(PRED, key=lambda v: abs(res["beta_std"][v]))
    vals = [res["beta_std"][v] for v in orden]
    fig = go.Figure(go.Bar(
        x=vals, y=[INFO[v]["corto"] for v in orden], orientation="h",
        marker=dict(color=[C_TEAL if x > 0 else C_ORANGE for x in vals]),
        text=[f"{x:+.2f}" for x in vals], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:+.2f}<extra></extra>"))
    estilo(fig, 400)
    fig.add_vline(x=0, line=dict(color=C_INK, width=1.5))
    fig.update_xaxes(title="Peso relativo (coeficiente estandarizado)")
    exp = tarjeta_explicacion(
        "El peso relativo de cada factor, con todas las variables llevadas a la misma escala para compararlas de forma justa.",
        "Barras hacia la <b>derecha</b> (verde-azulado) empujan el consumo hacia arriba; hacia la <b>izquierda</b> (naranja), hacia abajo. "
        "Mientras más larga la barra, más influencia.",
        f"El factor más influyente es <b>{INFO[mejor_var]['corto']}</b> ({res['beta_std'][mejor_var]:+.2f}).",
        chip("info", "Gráfica extra"))
    return fig, exp


BUILDERS = [g_heatmap, g_tendencia, g_real_pred, g_residuos, g_qq, g_influencia]


# ===========================================================================
# SECCIONES
# ===========================================================================
def seccion_inicio():
    badges = "".join(f'<span class="badge">{b}</span>' for b in
                     ["Regresión lineal múltiple", "DuckDB + Python", "Datos simulados", "Gráficas interactivas"])
    html(f'<div class="hero"><div class="hero-eyebrow">Práctica 4.2 · Análisis estadístico inferencial</div>'
         f'<div class="hero-title">💧 ¿Cuánta agua consume un hogar?</div>'
         f'<div class="hero-sub">Una calculadora que estima el consumo de agua potable por persona a partir del clima '
         f'y de cómo es el hogar. Pruébala, explora las gráficas y descubre qué factores pesan más.</div>{badges}</div>')
    kpis = [
        ("Precisión del modelo", f"{res['r2'] * 100:.1f}%", "de las variaciones del consumo se explican con 4 factores."),
        ("Error típico", f"±{res['rmse']:.1f}", "lt/hab-día de diferencia al predecir."),
        ("Factor que más pesa", INFO[mejor_var]["corto"], f"peso relativo {res['beta_std'][mejor_var]:+.2f} en el modelo."),
        ("Hogares analizados", f"{n}", "simulados con DuckDB y semilla fija."),
    ]
    html('<div class="kpi-grid">' + "".join(
        f'<div class="kpi"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div><div class="kpi-desc">{c}</div></div>'
        for a, b, c in kpis) + '</div>')

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        html('<div class="card"><h4>🎯 El problema</h4><p>Las compañías de agua necesitan anticipar cuánta agua consumirá cada hogar '
             'para planear el suministro. Medir casa por casa es lento y costoso, y el consumo cambia con el clima '
             'y con el tamaño de la familia.</p></div>')
    with c2:
        html('<div class="card"><h4>💡 La solución</h4><p>Un modelo estadístico —<b>regresión lineal múltiple</b>— aprende cómo la temperatura, '
             'la humedad, las personas por hogar y el consumo de agua de bidón se relacionan con el consumo per cápita (CPC), '
             'y lo usa para estimarlo en hogares nuevos.</p></div>')

    st.markdown("&nbsp;")
    html('<div class="sec-title" style="font-size:1.3rem">Cómo usar esta página</div>')
    pasos = [("1", "Prueba la calculadora", "Elige un escenario o mueve los controles y mira el consumo estimado al instante.",
              "🔮 Ir a la calculadora", SECCIONES[1], True),
             ("2", "Explora las gráficas", "Una a una, con una explicación en palabras simples de lo que muestra cada una.",
              "📊 Ver gráficas", SECCIONES[2], False),
             ("3", "Revisa el análisis", "Los pasos técnicos de la práctica: datos, correlación, modelo y supuestos.",
              "🧪 Ver análisis", SECCIONES[3], False)]
    for col, (num, tit, desc, btn, dest, prim) in zip(st.columns(3, gap="medium"), pasos):
        with col:
            html(f'<div class="card"><div class="step-num">{num}</div><h4>{tit}</h4><p>{desc}</p></div>')
            st.button(btn, key=f"ir_{num}", on_click=ir_a, args=(dest,), type="primary" if prim else "secondary",
                      use_container_width=True)
    st.caption("ℹ️ Los datos son simulados con fines académicos (caso inspirado en Arellano & Peña, 2020).")


def seccion_prediccion():
    encabezado("🔮 Calculadora de consumo",
               "Elige un escenario o ajusta los controles. El resultado se actualiza solo.")
    rng = {}
    for v in PRED:
        s = INFO[v]["paso"]
        lo = float(np.floor(df[v].min() / s) * s)
        hi = float(np.ceil(df[v].max() / s) * s)
        rng[v] = (round(lo, 2), round(hi, 2))

    def snap(v, val):
        s = INFO[v]["paso"]
        return float(np.clip(round(round(val / s) * s, 2), *rng[v]))

    medias = {v: snap(v, df[v].mean()) for v in PRED}
    for v in PRED:
        st.session_state.setdefault(f"p_{v}_{SIG}", medias[v])

    def aplicar(valores: dict):
        for v in PRED:
            st.session_state[f"p_{v}_{SIG}"] = snap(v, valores.get(v, medias[v]))

    escenarios = [
        ("🏠 Hogar típico", {}),
        ("☀️ Calor y aire seco", {"temperatura_max": df["temperatura_max"].quantile(.9), "humedad_max": df["humedad_max"].quantile(.1)}),
        ("🌧️ Fresco y húmedo", {"temperatura_max": df["temperatura_max"].quantile(.1), "humedad_max": df["humedad_max"].quantile(.9)}),
        ("👨‍👩‍👧‍👦 Familia numerosa", {"personas_familia": df["personas_familia"].max()}),
    ]
    izq, der = st.columns([1, 1.15], gap="large")
    with izq:
        html('<div class="card"><h4>1 · Elige un escenario</h4><p>Un atajo para empezar; luego puedes afinar cada valor.</p></div>')
        b1, b2 = st.columns(2)
        for i, (nombre, vals) in enumerate(escenarios):
            (b1 if i % 2 == 0 else b2).button(nombre, key=f"esc_{i}", on_click=aplicar, args=(vals,), use_container_width=True)
        html('<div class="card" style="margin-top:.8rem"><h4>2 · Ajusta los factores</h4></div>')
        x = {}
        for v in PRED:
            lo, hi = rng[v]
            x[v] = st.slider(f"{INFO[v]['icono']} {INFO[v]['largo']}", lo, hi, step=INFO[v]["paso"],
                             format=INFO[v]["fmt"], key=f"p_{v}_{SIG}", help=INFO[v]["ayuda"])

    par = res["params"]
    pred = par["const"] + sum(par[v] * x[v] for v in PRED)
    media = float(df["cpc_consumo"].mean())
    dif = (pred - media) / media * 100
    q1, q2 = df["cpc_consumo"].quantile([1 / 3, 2 / 3])
    nivel, kind = ("Consumo bajo", "ok") if pred < q1 else ("Consumo medio", "info") if pred < q2 else ("Consumo alto", "warn")
    lo_r, hi_r = pred - 1.96 * res["se"], pred + 1.96 * res["se"]
    with der:
        html(f'<div class="result"><div class="lbl">Consumo estimado</div>'
             f'<div class="big-number">{pred:.1f}<small>lt/hab-día</small></div>'
             f'<p>≈ <b>{abs(dif):.0f}% {"más" if dif >= 0 else "menos"}</b> que el hogar promedio ({media:.1f} lt/hab-día).</p>'
             f'<p>Rango probable (95%): <b>{lo_r:.1f} – {hi_r:.1f}</b> lt/hab-día.</p></div>')
        html(f'<div style="margin:.5rem 0 .2rem">{chip(kind, nivel)}</div>')
        g_lo, g_hi = float(min(df["cpc_consumo"].min(), pred)), float(max(df["cpc_consumo"].max(), pred))
        gauge = go.Figure(go.Indicator(
            mode="gauge", value=pred,
            gauge=dict(axis=dict(range=[g_lo, g_hi], tickfont=dict(size=12)), bar=dict(color=C_PRIMARY, thickness=0.28),
                       steps=[dict(range=[g_lo, q1], color="#DCFCE7"), dict(range=[q1, q2], color="#E0F2FE"),
                              dict(range=[q2, g_hi], color="#FEF3C7")],
                       threshold=dict(line=dict(color=C_INK, width=3), thickness=0.8, value=media))))
        estilo(gauge, 210).update_layout(margin=dict(l=20, r=20, t=10, b=0))
        st.plotly_chart(gauge, use_container_width=True, theme=None, config=PLOT_CFG, key="gauge")
        st.caption("Verde = consumo bajo · azul = medio · amarillo = alto. La línea negra marca el promedio de los hogares.")
        contrib = {v: par[v] * (x[v] - df[v].mean()) for v in PRED}
        orden = sorted(PRED, key=lambda v: abs(contrib[v]))
        vals = [contrib[v] for v in orden]
        fig = go.Figure(go.Bar(x=vals, y=[INFO[v]["corto"] for v in orden], orientation="h",
                               marker=dict(color=[C_TEAL if c >= 0 else C_ORANGE for c in vals]),
                               text=[f"{c:+.1f}" for c in vals], textposition="outside", cliponaxis=False,
                               hovertemplate="%{y}: %{x:+.1f} lt/hab-día<extra></extra>"))
        estilo(fig, 250).update_layout(margin=dict(l=10, r=30, t=10, b=10))
        fig.add_vline(x=0, line=dict(color=C_INK, width=1.5))
        fig.update_xaxes(title="Efecto sobre el consumo vs. un hogar promedio (lt/hab-día)")
        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOT_CFG, key="contrib")
        st.caption("Qué empuja tu estimación hacia arriba (verde-azulado) o hacia abajo (naranja).")


def seccion_graficas():
    encabezado("📊 Gráficas explicadas",
               "Una gráfica a la vez, con su explicación al lado. Pasa el cursor sobre los puntos para ver detalles, "
               "haz zoom arrastrando y usa el ícono de cámara para descargar la imagen.")
    st.radio("Gráfica", GRAFICAS, key="grafica", horizontal=True, label_visibility="collapsed")
    i = GRAFICAS.index(st.session_state.grafica)
    fig_col, exp_col = st.columns([1.7, 1], gap="large")
    with fig_col:
        fig, exp = BUILDERS[i]()
        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOT_CFG, key=f"g_{i}")
    with exp_col:
        html(exp)
    a, b, c = st.columns([1, 1.2, 1])
    a.button("← Anterior", on_click=mover_grafica, args=(-1,), disabled=i == 0, use_container_width=True, key="g_prev")
    b.markdown(f"<div style='text-align:center;padding-top:.6rem;color:#53657A;font-weight:600'>Gráfica {i + 1} de {len(GRAFICAS)}</div>",
               unsafe_allow_html=True)
    c.button("Siguiente →", on_click=mover_grafica, args=(1,), disabled=i == len(GRAFICAS) - 1,
             type="primary", use_container_width=True, key="g_next")


def seccion_analisis():
    encabezado("🧪 Análisis paso a paso",
               "El procedimiento técnico de la práctica, explicado en lenguaje simple. Cada pestaña es un paso.")
    t1, t2, t3, t4, t5 = st.tabs(["1 · Datos", "2 · Correlación", "3 · Modelo (OLS)", "4 · Supuestos", "5 · Métricas"])
    with t1:
        st.markdown("Los datos se **simulan con SQL en DuckDB** usando una semilla fija (`setseed`), por lo que cualquiera "
                    "que ejecute el mismo código obtiene exactamente la misma tabla.")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
        st.markdown(f"**{len(df)} hogares** · variable a predecir: `cpc_consumo`.")
        st.dataframe(df[ALL].describe().round(3), use_container_width=True)
        st.download_button("⬇️ Descargar datos (CSV)", df.to_csv(index=False).encode("utf-8"),
                           file_name="telemetria_agua.csv", mime="text/csv", type="primary")
        with st.expander("Ver el SQL que genera los datos"):
            st.code((SQL_CORREGIDO if corregido else SQL_PROFESOR).format(n=n), language="sql")
    with t2:
        st.markdown("La **correlación de Pearson (r)** mide qué tan juntas suben o bajan dos variables: "
                    "1 = suben juntas, −1 = una sube y la otra baja, 0 = sin relación lineal.")
        st.dataframe(corr.round(4), use_container_width=True)
        top = corr["cpc_consumo"].drop("cpc_consumo")
        st.dataframe(top.round(4).rename(lambda v: INFO[v]["largo"]).to_frame("r con el consumo"), use_container_width=True)
        v = top.abs().idxmax()
        st.info(f"La relación lineal más fuerte con el consumo es **{INFO[v]['corto']}** (r = {top[v]:+.4f}).")
    with t3:
        st.markdown("La **regresión lineal múltiple (MCO/OLS)** busca la fórmula que mejor combina los cuatro factores para estimar el consumo.")
        p = res["params"]
        st.code(f"CPC = {p['const']:.2f} + ({p['temperatura_max']:.2f} × Temp) + ({p['humedad_max']:.2f} × Humedad) "
                f"+ ({p['personas_familia']:.2f} × Personas) + ({p['consumo_bidon_pc']:.2f} × Bidón)", language="text")
        tab = res["conf"].copy()
        tab.insert(0, "Coeficiente", pd.Series(p))
        tab["p-valor"] = pd.Series(res["pvalues"])
        tab["¿Significativo?"] = np.where(tab["p-valor"] < 0.05, "Sí", "No")
        st.dataframe(tab.round(4), use_container_width=True)
        st.markdown("**En palabras simples** (manteniendo los demás factores iguales):")
        for v in PRED:
            b = p[v]
            sig = "efecto estadísticamente significativo" if res["pvalues"][v] < 0.05 else "efecto no significativo"
            st.markdown(f"- {INFO[v]['icono']} **{INFO[v]['corto']}**: {INFO[v]['unidad']} "
                        f"{'suma' if b > 0 else 'resta'} ≈ {abs(b):.2f} lt/hab-día ({sig}).")
        st.markdown(f"Modelo global: F = **{res['f']:.1f}** (p = {res['f_p']:.2e}) → "
                    f"{'significativo' if res['f_p'] < 0.05 else 'no significativo'} · R² ajustado = **{res['r2_adj']:.3f}**.")
        with st.expander("Ver la tabla técnica completa de statsmodels"):
            st.code(res["resumen"], language="text")
    with t4:
        st.markdown("Para que el modelo sea confiable, sus **errores (residuos)** deben cumplir tres supuestos.")
        sw_p, dw, bp = res["sw"][1], res["dw"], res["bp_p"]
        c1, c2, c3 = st.columns(3, gap="medium")
        for col, tit, val, ok, ex in (
                (c1, "Normalidad", f"Shapiro-Wilk p = {sw_p:.3f}", sw_p > 0.05, "Los errores siguen una campana normal."),
                (c2, "Independencia", f"Durbin-Watson = {dw:.3f}", 1.5 <= dw <= 2.5, "Un error no depende del anterior (ideal ≈ 2)."),
                (c3, "Varianza pareja", f"Breusch-Pagan p = {bp:.3f}", bp > 0.05, "El error es igual de grande en consumos bajos y altos.")):
            with col:
                html(f'<div class="card"><h4>{tit}</h4><p>{ex}</p><p style="margin-top:.4rem"><b>{val}</b></p>'
                     f'{chip("ok" if ok else "warn", "✅ Se cumple" if ok else "⚠️ Revisar")}</div>')
        st.caption("Las gráficas 4 y 5 de la sección «Gráficas» muestran estos supuestos de forma visual.")
    with t5:
        st.markdown("Con **scikit-learn** medimos qué tan bien predice el modelo.")
        m1, m2 = st.columns(2, gap="medium")
        with m1:
            html(f'<div class="kpi"><div class="kpi-label">R² (coeficiente de determinación)</div><div class="kpi-value">{res["r2"] * 100:.2f}%</div>'
                 f'<div class="kpi-desc">Porcentaje de la variación del consumo que el modelo explica.</div></div>')
        with m2:
            html(f'<div class="kpi"><div class="kpi-label">RMSE (error cuadrático medio raíz)</div><div class="kpi-value">{res["rmse"]:.4f}</div>'
                 f'<div class="kpi-desc">lt/hab-día: error típico de cada predicción.</div></div>')
        st.markdown("**Comparación con los valores de referencia de la guía**")
        ref = pd.DataFrame({
            "Métrica": ["R² (%)", "RMSE (lt/hab-día)", "Shapiro-Wilk (p)", "Durbin-Watson", "r (humedad vs. consumo)"],
            "Guía de la práctica": ["95.72", "2.0152", "0.5097", "2.0298", "−0.7042"],
            "Esta aplicación": [f"{res['r2'] * 100:.2f}", f"{res['rmse']:.4f}", f"{res['sw'][1]:.4f}", f"{res['dw']:.4f}",
                                f"{corr.loc['humedad_max', 'cpc_consumo']:+.4f}"]})
        st.dataframe(ref, use_container_width=True, hide_index=True)
        st.caption("Los valores no coinciden al decimal: dependen de la versión de DuckDB, del generador aleatorio y de "
                   "que el SQL original calcula el consumo con números aleatorios independientes (ver «Acerca de»).")


def seccion_acerca():
    encabezado("ℹ️ Acerca del proyecto", "Qué es, con qué se construyó y cómo llegó a internet.")
    ctrl = f" · Control {CONTROL}" if CONTROL else ""
    html(f'<div class="card"><h4>📘 Sobre la práctica</h4><p>Práctica de laboratorio 4.2 de <b>{MATERIA}</b>, subtema «Regresión lineal y correlación». '
         f'Predice el consumo per cápita de agua potable (lt/hab-día) con regresión lineal múltiple, basada en el caso de Arellano &amp; Peña (2020). '
         f'Autor: <b>{AUTOR}</b>{ctrl} · {ESCUELA}.</p></div>')
    st.markdown("&nbsp;")
    html('<div class="sec-title" style="font-size:1.3rem">🧰 Herramientas</div>')
    herramientas = [
        ("DuckDB", "Base de datos analítica. Genera los datos simulados con SQL y una semilla fija para que sean reproducibles."),
        ("pandas", "Organiza los datos en tablas y calcula las correlaciones."),
        ("statsmodels", "Ajusta la regresión (OLS) y las pruebas de supuestos de los errores."),
        ("scikit-learn", "Valida el modelo con las métricas R² y RMSE."),
        ("Plotly", "Gráficas interactivas: hover, zoom y descarga como imagen."),
        ("Streamlit", "Convierte el código Python en esta página web."),
        ("Docker", "Empaqueta la aplicación y sus dependencias en un contenedor portable."),
        ("Tailscale Funnel", "Publica el contenedor en internet con HTTPS, sin abrir puertos del router."),
        ("Debian", "Servidor propio donde corre el contenedor."),
    ]
    html('<div class="tool-grid">' + "".join(f'<div class="tool"><b>{a}</b><p>{b}</p></div>' for a, b in herramientas) + '</div>')
    st.markdown("&nbsp;")
    html('<div class="sec-title" style="font-size:1.3rem">🚀 Cómo se desplegó</div>')
    pasos = [("💻", "Código", "Python + SQL (app.py)"), ("📦", "Imagen Docker", "Dockerfile + dependencias"),
             ("🖥️", "Contenedor", "Servidor Debian propio, puerto local"), ("🌐", "Tailscale Funnel", "URL pública con HTTPS"),
             ("🧑‍💻", "Tu navegador", "Abre la URL y listo")]
    html('<div class="flow">' + "".join(
        f'<div class="flow-step"><span class="ico">{a}</span><b>{b}</b><span>{c}</span></div>' for a, b, c in pasos) + '</div>')
    st.markdown("&nbsp;")
    html('<div class="sec-title" style="font-size:1.3rem">🔎 Hallazgos durante el desarrollo</div>')
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        html('<div class="card"><h4>El SQL de la guía</h4><p>Calculaba el consumo con números aleatorios <b>independientes</b> de las columnas mostradas, '
             'así que no había relación que modelar (R² ≈ 7%). Se corrigió calculándolo a partir de las mismas columnas; '
             'la casilla «Usar SQL corregido» en Ajustes permite comparar ambas versiones.</p></div>')
    with c2:
        html('<div class="card"><h4>Compatibilidad del servidor</h4><p>Las versiones recientes de DuckDB se cerraban con «instrucción ilegal» '
             'porque el procesador del servidor no tiene instrucciones AVX. Se fijó una versión compatible '
             '(y Streamlit 1.40.2) para que el contenedor se mantenga estable.</p></div>')
    with st.expander("Versiones en uso"):
        st.code(f"Python {platform.python_version()} · Streamlit {st.__version__} · DuckDB {duckdb.__version__}\n"
                f"pandas {pd.__version__} · statsmodels {statsmodels.__version__} · scikit-learn {sklearn.__version__} · Plotly {plotly.__version__}",
                language="text")


# ===========================================================================
# ENRUTADOR + PIE
# ===========================================================================
{SECCIONES[0]: seccion_inicio, SECCIONES[1]: seccion_prediccion, SECCIONES[2]: seccion_graficas,
 SECCIONES[3]: seccion_analisis, SECCIONES[4]: seccion_acerca}[st.session_state.nav]()

html(f'<div class="footer">Práctica 4.2 · {MATERIA} · {ESCUELA}<br>'
     'Datos simulados con fines académicos · Hecho con Python, DuckDB y Streamlit</div>')
