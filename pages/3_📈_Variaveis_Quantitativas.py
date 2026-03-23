import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db_utils import load_sample, load_aggregated_stats, load_sample_participantes

st.set_page_config(page_title="Variáveis Quantitativas", page_icon="📈", layout="wide")

st.title("📈 Variáveis Quantitativas")
st.markdown("Histogramas, Box Plots e estatísticas descritivas para as notas e demais variáveis numéricas do ENEM 2024.")

IESB_RED = "#AA0000"
NOTE_COLS = {
    "nota_cn_ciencias_da_natureza": "Ciências da Natureza",
    "nota_ch_ciencias_humanas": "Ciências Humanas",
    "nota_lc_linguagens_e_codigos": "Linguagens e Códigos",
    "nota_mt_matematica": "Matemática",
    "nota_redacao": "Redação",
    "nota_media_5_notas": "Média Geral",
}
NOTE_LABELS = list(NOTE_COLS.values())
NOTE_KEYS = list(NOTE_COLS.keys())

COLORS = ["#AA0000", "#CC3333", "#EE6666", "#880000", "#DD4444", "#BB2222"]

with st.spinner("Carregando amostra de dados..."):
    df = load_sample(50000)          # resultados: scores + region
    df_demo = load_sample_participantes(50000)  # participantes: demographics
    stats = load_aggregated_stats()

df_notas = stats["notas_regiao"]

# ── Descriptive statistics ───────────────────────────────────────────────────

st.subheader("📐 Estatísticas Descritivas")

note_df = df[NOTE_KEYS].copy()
note_df.columns = NOTE_LABELS

desc = note_df.describe().T.rename(columns={
    "count": "N válidos", "mean": "Média", "std": "Desvio Padrão",
    "min": "Mínimo", "25%": "Q1", "50%": "Mediana",
    "75%": "Q3", "max": "Máximo"
})
desc = desc[["N válidos", "Mínimo", "Q1", "Mediana", "Média", "Q3", "Máximo", "Desvio Padrão"]]
desc = desc.round(2)

styled = desc.style.format("{:.2f}").background_gradient(
    subset=["Média", "Desvio Padrão"], cmap="Reds"
)
st.dataframe(styled, use_container_width=True)

# ── Nota media por região ────────────────────────────────────────────────────
st.subheader("📊 Média das Notas por Região")

fig_reg = go.Figure()
regioes = df_notas["regiao_nome_prova"].tolist()
areas = ["media_cn", "media_ch", "media_lc", "media_mt", "media_redacao"]
labels = ["Ciências da Natureza", "Ciências Humanas", "Linguagens e Códigos", "Matemática", "Redação"]
bar_colors = ["#AA0000", "#CC4444", "#DD6666", "#EE8888", "#880000"]

for area, label, color in zip(areas, labels, bar_colors):
    fig_reg.add_trace(go.Bar(
        name=label,
        x=regioes,
        y=df_notas[area].tolist(),
        marker_color=color,
    ))

fig_reg.update_layout(
    barmode="group", height=420, title="Média das Notas por Área e Região Geográfica",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=70, b=10),
)
st.plotly_chart(fig_reg, use_container_width=True)

# ── Tabs: Histograms / Box Plots ──────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["📊 Histogramas", "📦 Box Plots", "📉 Densidade"])

with tab1:
    st.markdown("#### Distribuição das Notas por Área do Conhecimento")

    col_select = st.selectbox(
        "Selecione a área:",
        options=NOTE_KEYS,
        format_func=lambda x: NOTE_COLS[x],
        key="hist_select"
    )

    df["regiao_nome_prova"] = df["regiao_nome_prova"].str.strip()
    df_hist = df[[col_select, "regiao_nome_prova"]].dropna()
    df_hist.columns = ["Nota", "Região"]

    color_by = st.radio("Colorir por:", ["Nenhum", "Região"],
                        horizontal=True, key="hist_color")

    if color_by == "Nenhum":
        fig = px.histogram(df_hist, x="Nota", nbins=50,
                           title=f"Histograma — {NOTE_COLS[col_select]}",
                           color_discrete_sequence=[IESB_RED])
    else:
        fig = px.histogram(df_hist, x="Nota", color="Região", nbins=50,
                           barmode="overlay",
                           title=f"Histograma por Região — {NOTE_COLS[col_select]}",
                           color_discrete_sequence=COLORS)
        fig.update_traces(opacity=0.6)

    fig.update_layout(height=450, margin=dict(t=50, b=10))
    fig.update_xaxes(title_text="Nota")
    fig.update_yaxes(title_text="Frequência")
    st.plotly_chart(fig, use_container_width=True)

    mean_v = df_hist["Nota"].mean()
    med_v = df_hist["Nota"].median()
    std_v = df_hist["Nota"].std()
    c1, c2, c3 = st.columns(3)
    c1.metric("Média", f"{mean_v:.1f}")
    c2.metric("Mediana", f"{med_v:.1f}")
    c3.metric("Desvio Padrão", f"{std_v:.1f}")

    diff = abs(mean_v - med_v)
    if diff < 5:
        assimetria = "aproximadamente simétrica"
    elif mean_v > med_v:
        assimetria = "assimétrica positiva (cauda à direita)"
    else:
        assimetria = "assimétrica negativa (cauda à esquerda)"

    st.info(f"""
    **Análise:** A distribuição de **{NOTE_COLS[col_select]}** é {assimetria}.
    Média = {mean_v:.1f} | Mediana = {med_v:.1f} | DP = {std_v:.1f}.
    """)

with tab2:
    st.markdown("#### Box Plots das Notas")

    group_by = st.radio("Agrupar por:", ["Área do Conhecimento", "Região"],
                        horizontal=True, key="box_group")

    df["regiao_nome_prova"] = df["regiao_nome_prova"].str.strip()
    df_m = df[NOTE_KEYS + ["regiao_nome_prova"]].copy()

    if group_by == "Área do Conhecimento":
        df_long = df_m[NOTE_KEYS].melt(var_name="area", value_name="nota")
        df_long["Área"] = df_long["area"].map(NOTE_COLS)
        df_long = df_long.dropna()
        fig = px.box(df_long, x="Área", y="nota",
                     title="Box Plot — Distribuição das Notas por Área",
                     color="Área", color_discrete_sequence=COLORS)
        fig.update_xaxes(tickangle=-20)
    else:
        nota_sel2 = st.selectbox("Área:", NOTE_KEYS,
                                 format_func=lambda x: NOTE_COLS[x], key="box_nota2")
        df_bx2 = df_m[[nota_sel2, "regiao_nome_prova"]].dropna()
        df_bx2.columns = ["Nota", "Região"]
        fig = px.box(df_bx2, x="Região", y="Nota",
                     title=f"Box Plot por Região — {NOTE_COLS[nota_sel2]}",
                     color="Região", color_discrete_sequence=COLORS)
        fig.update_xaxes(tickangle=-20)

    fig.update_layout(height=480, showlegend=False, margin=dict(t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Como interpretar o Box Plot:**
    - A **linha central** representa a mediana (50º percentil).
    - A **caixa** delimita o intervalo interquartil (IQR = Q3 − Q1), abrangendo 50% dos dados.
    - Os **bigodes** se estendem até 1,5× o IQR.
    - Pontos além dos bigodes são **outliers** potenciais.
    """)

with tab3:
    st.markdown("#### Curvas de Densidade das Notas")
    nota_sel3 = st.selectbox("Selecione a área:", NOTE_KEYS,
                             format_func=lambda x: NOTE_COLS[x], key="kde_nota")
    df["regiao_nome_prova"] = df["regiao_nome_prova"].str.strip()
    df_kde = df[[nota_sel3, "regiao_nome_prova"]].dropna()
    df_kde.columns = ["Nota", "Região"]

    fig = px.violin(df_kde, y="Nota", x="Região", box=True, points=False,
                    color="Região", color_discrete_sequence=COLORS,
                    title=f"Violin Plot por Região — {NOTE_COLS[nota_sel3]}")
    fig.update_layout(height=480, showlegend=False, margin=dict(t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Violin Plot** combina box plot com estimativa de densidade (KDE), permitindo
    visualizar a forma completa da distribuição. Porções mais largas indicam maior
    concentração de candidatos naquela faixa de nota.
    """)

st.markdown("---")
st.caption("Fonte: INEP — Microdados ENEM 2024 | Big Data IESB | Amostra: 50.000 registros")
