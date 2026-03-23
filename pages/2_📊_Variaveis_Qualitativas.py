import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db_utils import load_aggregated_stats, load_faixa_etaria, load_st_conclusao

st.set_page_config(page_title="Variáveis Qualitativas", page_icon="📊", layout="wide")

st.title("📊 Variáveis Qualitativas")
st.markdown("Gráficos de barras, pizza e demais visualizações para as variáveis categóricas do ENEM 2024.")

IESB_RED = "#AA0000"
COLOR_SEQ = px.colors.qualitative.Set2

with st.spinner("Carregando dados..."):
    stats = load_aggregated_stats()
    df_faixa = load_faixa_etaria()
    df_conclusao = load_st_conclusao()

# ── helper ────────────────────────────────────────────────────────────────────

def bar_chart(df_agg, x_col, title, color=IESB_RED, orientation="v", top_n=None):
    df = df_agg.copy()
    df.columns = ["Categoria", "Contagem"]
    if top_n:
        df = df.head(top_n)
    pct = (df["Contagem"] / df["Contagem"].sum() * 100).round(1)
    df["Pct"] = pct.values
    if orientation == "h":
        fig = px.bar(df, y="Categoria", x="Contagem", orientation="h",
                     text=df["Pct"].apply(lambda x: f"{x}%"),
                     title=title, color_discrete_sequence=[color])
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
    else:
        fig = px.bar(df, x="Categoria", y="Contagem",
                     text=df["Pct"].apply(lambda x: f"{x}%"),
                     title=title, color_discrete_sequence=[color])
        fig.update_xaxes(tickangle=-30)
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, height=420, margin=dict(t=50, b=10))
    return fig


def pie_chart(df_agg, title, colors=None):
    df = df_agg.copy()
    df.columns = ["Categoria", "Contagem"]
    fig = px.pie(df, names="Categoria", values="Contagem", title=title,
                 color_discrete_sequence=colors or COLOR_SEQ)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=420, margin=dict(t=50, b=10))
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ═════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Sexo & Treineiro", "Região & UF", "Cor/Raça",
    "Faixa Etária", "Escola", "Redação & Conclusão"
])

# ── Tab 1: Sexo & Treineiro ───────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig = pie_chart(stats["sexo"], "Distribuição por Sexo",
                        colors=["#AA0000", "#E8A0A0"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        df_trei = stats["treineiro"].copy()
        df_trei["valor"] = df_trei["valor"].map({"Sim": "Treineiro", "Não": "Regular"})
        fig = pie_chart(df_trei, "Treineiros vs. Regulares",
                        colors=["#E8A0A0", "#AA0000"])
        st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretação:**
    - O ENEM 2024 conta com maioria feminina (~57%), tendência consolidada nos últimos anos.
    - Candidatos **treineiros** (estudantes do ensino médio que fazem o exame sem fins de aproveitamento)
      representam uma parcela relevante, evidenciando o uso do ENEM como simulado nacional.
    """)

# ── Tab 2: Região & UF ───────────────────────────────────────────────────────
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        fig = bar_chart(stats["regiao"], "Região", "Inscritos por Região Geográfica")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = bar_chart(stats["uf"], "UF", "Inscritos por UF (Top 15)",
                        orientation="h", top_n=15, color="#CC3333")
        st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretação:**
    - O **Nordeste** é a região com maior número de inscritos, refletindo tanto o
      contingente populacional quanto o protagonismo do ENEM como porta de entrada para
      universidades federais da região.
    - **São Paulo** lidera entre os estados, seguido por **Minas Gerais** e **Bahia**.
    """)

# ── Tab 3: Cor/Raça ───────────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        fig = bar_chart(stats["cor_raca"], "Cor/Raça", "Distribuição por Cor/Raça (Autodeclaração)",
                        color="#CC3333")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = pie_chart(stats["cor_raca"], "Composição Racial dos Inscritos",
                        colors=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretação:**
    - Candidatos **pardos** constituem o maior grupo racial autodeclarado (~43%), seguidos por
      **brancos** (~37%) e **pretos** (~12%).
    - A distribuição racial dos participantes é relevante para avaliar o impacto das políticas
      de cotas raciais instituídas pela Lei nº 12.711/2012.
    """)

# ── Tab 4: Faixa Etária ───────────────────────────────────────────────────────
with tab4:
    # Try to order by age
    ORDER_MAP = {
        "16 anos ou menos": 0, "17 anos": 1, "18 anos": 2, "19 anos": 3, "20 anos": 4,
        "21 anos": 5, "22 anos": 6, "23 anos": 7, "24 anos": 8, "25 anos": 9,
        "Entre 26 e 30 anos": 10, "Entre 31 e 35 anos": 11, "Entre 36 e 40 anos": 12,
        "Entre 41 e 45 anos": 13, "Entre 46 e 50 anos": 14, "Entre 51 e 55 anos": 15,
        "Entre 56 e 60 anos": 16, "Entre 61 e 65 anos": 17, "Entre 66 e 70 anos": 18,
        "Maior de 70 anos": 19,
    }
    df_f = df_faixa.copy()
    df_f.columns = ["Faixa Etária", "Contagem"]
    df_f["ordem"] = df_f["Faixa Etária"].map(ORDER_MAP).fillna(99)
    df_f = df_f.sort_values("ordem")

    total = df_f["Contagem"].sum()
    df_f["Pct"] = (df_f["Contagem"] / total * 100).round(1)

    fig = px.bar(df_f, x="Faixa Etária", y="Contagem",
                 text=df_f["Pct"].apply(lambda x: f"{x}%"),
                 title="Distribuição por Faixa Etária",
                 color="Contagem",
                 color_continuous_scale=["#FFCCCC", "#AA0000"])
    fig.update_xaxes(tickangle=-45)
    fig.update_traces(textposition="outside")
    fig.update_layout(height=480, coloraxis_showscale=False,
                      margin=dict(t=50, b=120))
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretação:**
    - O pico de participação ocorre nas faixas de **17 e 18 anos**, típicos do último
      ou recém-concluído ensino médio.
    - A cauda longa de participantes mais velhos evidencia que o ENEM é também usado
      por adultos que buscam uma segunda oportunidade de acesso ao ensino superior.
    """)

# ── Tab 5: Escola ─────────────────────────────────────────────────────────────
with tab5:
    c1, c2 = st.columns(2)
    with c1:
        fig = bar_chart(stats["dep_adm"], "Dep. Admin.",
                        "Dependência Administrativa da Escola", color="#880000")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = pie_chart(stats["dep_adm"], "Composição por Tipo de Escola",
                        colors=["#AA0000", "#CC5555", "#EE9999", "#FFCCCC"])
        st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretação:**
    - Candidatos oriundos de **escolas públicas estaduais** representam a maioria esmagadora.
    - Escolas privadas, apesar de menor representatividade em número, historicamente
      apresentam desempenho médio superior, o que motiva debates sobre equidade educacional.
    """)

# ── Tab 6: Redação & Conclusão ────────────────────────────────────────────────
with tab6:
    c1, c2 = st.columns(2)
    with c1:
        fig = bar_chart(stats["status_redacao"], "Status",
                        "Status da Redação", orientation="h", color="#CC3333")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = bar_chart(df_conclusao, "Situação",
                        "Situação de Conclusão do Ensino Médio", orientation="h",
                        color="#880000")
        st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretação:**
    - A maioria das redações é classificada como **presente e válida** (competente), demonstrando
      comprometimento dos candidatos.
    - Redações com **nota zero** por fuga ao tema ou descumprimento das regras representam um
      percentual pequeno, mas relevante, do total.
    """)

st.markdown("---")
st.caption("Fonte: INEP — Microdados ENEM 2024 | Big Data IESB | Dados completos (4.332.944 participantes)")
