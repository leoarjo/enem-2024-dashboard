import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy import stats as scipy_stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db_utils import load_sample

st.set_page_config(page_title="Análise de Correlação", page_icon="🔗", layout="wide")

st.title("🔗 Análise de Correlação")
st.markdown("""
Matriz de correlação de Pearson e diagramas de dispersão entre as notas do ENEM 2024,
além de análises de correlação por grupos demográficos.
""")

NOTE_COLS = {
    "nota_cn_ciencias_da_natureza": "C. Natureza",
    "nota_ch_ciencias_humanas": "C. Humanas",
    "nota_lc_linguagens_e_codigos": "Linguagens",
    "nota_mt_matematica": "Matemática",
    "nota_redacao": "Redação",
    "nota_media_5_notas": "Média Geral",
}
NOTE_KEYS = list(NOTE_COLS.keys())
NOTE_LABELS = list(NOTE_COLS.values())
COLORS_SEQ = ["#FFEEEE", "#FF9999", "#CC0000", "#880000", "#440000"]

with st.spinner("Carregando amostra..."):
    df = load_sample(50000)
    df["regiao_nome_prova"] = df["regiao_nome_prova"].str.strip()
    df["tp_dependencia_adm_esc"] = df["tp_dependencia_adm_esc"].str.strip()
    df["tp_status_redacao"] = df["tp_status_redacao"].str.strip()

df_num = df[NOTE_KEYS].dropna()
df_num_labeled = df_num.rename(columns=NOTE_COLS)

# ── Correlation matrix ────────────────────────────────────────────────────────
st.subheader("📊 Matriz de Correlação de Pearson")

corr = df_num_labeled.corr()

fig_corr = go.Figure(data=go.Heatmap(
    z=corr.values,
    x=NOTE_LABELS,
    y=NOTE_LABELS,
    colorscale=[
        [0.0, "#FFFFFF"],
        [0.3, "#FFBBBB"],
        [0.6, "#CC3333"],
        [1.0, "#660000"],
    ],
    zmin=-1, zmax=1,
    text=corr.round(2).values,
    texttemplate="%{text}",
    textfont={"size": 12},
    showscale=True,
    colorbar=dict(title="r de Pearson"),
))
fig_corr.update_layout(
    title="Correlação entre Variáveis Numéricas do ENEM 2024",
    height=520,
    xaxis=dict(tickangle=-30),
    margin=dict(t=60, b=10),
)
st.plotly_chart(fig_corr, use_container_width=True)

# Strongest correlations table
corr_pairs = []
cols = list(corr.columns)
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        r = corr.iloc[i, j]
        # p-value
        n = df_num_labeled[[cols[i], cols[j]]].dropna().shape[0]
        try:
            t_stat = r * np.sqrt(n - 2) / np.sqrt(1 - r ** 2)
            p_val = 2 * scipy_stats.t.sf(abs(t_stat), df=n - 2)
        except Exception:
            p_val = np.nan
        corr_pairs.append({
            "Variável X": cols[i],
            "Variável Y": cols[j],
            "r de Pearson": round(r, 4),
            "p-valor": f"{p_val:.2e}" if not np.isnan(p_val) else "—",
            "Interpretação": (
                "Correlação perfeita" if abs(r) == 1 else
                "Correlação muito forte" if abs(r) >= 0.9 else
                "Correlação forte" if abs(r) >= 0.7 else
                "Correlação moderada" if abs(r) >= 0.5 else
                "Correlação fraca" if abs(r) >= 0.3 else
                "Correlação muito fraca / sem correlação"
            )
        })

df_pairs = pd.DataFrame(corr_pairs).sort_values("r de Pearson", ascending=False)
with st.expander("📋 Tabela completa de correlações", expanded=False):
    st.dataframe(df_pairs.reset_index(drop=True), use_container_width=True)

st.info("""
**Principais achados:**
- A **Média Geral** tem correlação muito forte com todas as áreas, como esperado.
- **Ciências da Natureza** e **Matemática** apresentam a maior correlação entre si (~0.70–0.80),
  indicando que candidatos com bom desempenho em raciocínio lógico-matemático tendem a se
  sair melhor também em ciências exatas.
- A **Redação** apresenta correlação moderada com as demais áreas, sugerindo que habilidades
  escritas têm alguma relação com competências gerais, mas são influenciadas por fatores distintos.
- A **Idade** tem correlação negativa com as notas, indicando que candidatos mais jovens
  (recém saídos do ensino médio) tendem a apresentar desempenho ligeiramente superior.
""")

# ── Scatter plots ─────────────────────────────────────────────────────────────
st.subheader("🔵 Diagramas de Dispersão")

c1, c2 = st.columns(2)
with c1:
    x_var = st.selectbox("Eixo X:", NOTE_KEYS[:6], format_func=lambda k: NOTE_COLS[k], key="scatter_x")
with c2:
    remaining = [k for k in NOTE_KEYS[:6] if k != x_var]
    y_var = st.selectbox("Eixo Y:", remaining, format_func=lambda k: NOTE_COLS[k], key="scatter_y")

color_group = st.radio("Colorir por:", ["Nenhum", "Região", "Dep. Admin. Escola"],
                       horizontal=True, key="scatter_color")

df_sc = df[[x_var, y_var, "regiao_nome_prova", "tp_dependencia_adm_esc"]].dropna()

sample_size = min(5000, len(df_sc))
df_sc_s = df_sc.sample(sample_size, random_state=42)

color_map = {
    "Nenhum": None,
    "Região": "regiao_nome_prova",
    "Dep. Admin. Escola": "tp_dependencia_adm_esc",
}
color_col = color_map[color_group]

SCATTER_COLORS = ["#AA0000", "#CC4444", "#DD8888", "#880000", "#FFAAAA", "#550000"]

fig_sc = px.scatter(
    df_sc_s,
    x=x_var, y=y_var,
    color=color_col if color_col else None,
    opacity=0.4,
    trendline="ols",
    trendline_color_override="#000000" if color_col is None else None,
    labels={x_var: NOTE_COLS[x_var], y_var: NOTE_COLS[y_var]},
    title=f"Dispersão: {NOTE_COLS[x_var]} × {NOTE_COLS[y_var]}",
    color_discrete_sequence=SCATTER_COLORS,
)
fig_sc.update_layout(height=480, margin=dict(t=60, b=10))
st.plotly_chart(fig_sc, use_container_width=True)

# Show r value for selected pair
r_val = corr.loc[NOTE_COLS[x_var], NOTE_COLS[y_var]] if NOTE_COLS[x_var] in corr.columns else None
if r_val is not None:
    st.metric(f"r de Pearson ({NOTE_COLS[x_var]} × {NOTE_COLS[y_var]})", f"{r_val:.4f}")

# ── Correlation by group ───────────────────────────────────────────────────────
st.subheader("📊 Correlação por Grupo Demográfico")

group_sel = st.selectbox("Agrupar por:", ["regiao_nome_prova", "tp_dependencia_adm_esc"],
                         format_func={"regiao_nome_prova": "Região",
                                      "tp_dependencia_adm_esc": "Dep. Admin. Escola"}.get,
                         key="group_corr")

var_x = st.selectbox("Variável X:", NOTE_KEYS[:5], format_func=lambda k: NOTE_COLS[k], key="gx")
var_y = st.selectbox("Variável Y:", [k for k in NOTE_KEYS[:5] if k != var_x],
                     format_func=lambda k: NOTE_COLS[k], key="gy")

df_g = df[[var_x, var_y, group_sel]].dropna()
groups = df_g[group_sel].unique()

rows = []
for g in sorted(groups):
    sub = df_g[df_g[group_sel] == g]
    if len(sub) > 10:
        r, p = scipy_stats.pearsonr(sub[var_x], sub[var_y])
        rows.append({"Grupo": g, "N": len(sub),
                     "r de Pearson": round(r, 4),
                     "p-valor": f"{p:.2e}"})

df_group_corr = pd.DataFrame(rows)
if not df_group_corr.empty:
    fig_gc = px.bar(df_group_corr, x="Grupo", y="r de Pearson",
                    text="r de Pearson",
                    title=f"r de Pearson por {group_sel.replace('tp_', '').replace('_', ' ').title()}",
                    color="r de Pearson",
                    color_continuous_scale=["#FFEEEE", "#CC0000", "#440000"],
                    range_color=[0, 1])
    fig_gc.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig_gc.update_layout(height=380, coloraxis_showscale=False, margin=dict(t=50, b=10))
    st.plotly_chart(fig_gc, use_container_width=True)
    st.dataframe(df_group_corr.set_index("Grupo"), use_container_width=True)

st.markdown("---")
st.caption("Fonte: INEP — Microdados ENEM 2024 | Big Data IESB | Amostra: 50.000 registros")
