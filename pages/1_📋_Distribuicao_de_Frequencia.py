import streamlit as st
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db_utils import load_aggregated_stats, load_faixa_etaria, load_st_conclusao, freq_table

st.set_page_config(page_title="Distribuição de Frequência", page_icon="📋", layout="wide")

st.title("📋 Distribuição de Frequência")
st.markdown("Tabelas de distribuição de frequência para as principais variáveis qualitativas do ENEM 2024.")

# ── helpers ──────────────────────────────────────────────────────────────────

def make_freq_table(df_agg, col_label):
    """Build a frequency table from an aggregated (valor, contagem) DataFrame."""
    total = df_agg["contagem"].sum()
    df = df_agg.copy()
    df.columns = [col_label, "Freq. Absoluta"]
    df["Freq. Relativa (%)"] = (df["Freq. Absoluta"] / total * 100).round(2)
    df["Freq. Acumulada"] = df["Freq. Absoluta"].cumsum()
    df["Freq. Acum. Rel. (%)"] = (df["Freq. Acumulada"] / total * 100).round(2)
    df = df.reset_index(drop=True)
    df.index += 1
    return df, total


def display_table(df, total, caption):
    st.caption(f"**{caption}** — Total: {total:,} registros")
    styled = df.style.format({
        "Freq. Absoluta": "{:,.0f}",
        "Freq. Relativa (%)": "{:.2f}%",
        "Freq. Acumulada": "{:,.0f}",
        "Freq. Acum. Rel. (%)": "{:.2f}%",
    }).background_gradient(subset=["Freq. Relativa (%)"], cmap="Reds")
    st.dataframe(styled, use_container_width=True)


# ── data ─────────────────────────────────────────────────────────────────────

with st.spinner("Carregando dados..."):
    stats = load_aggregated_stats()
    df_faixa = load_faixa_etaria()
    df_conclusao = load_st_conclusao()

# ── tabs ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Sexo", "Região", "UF", "Faixa Etária",
    "Cor/Raça", "Sit. Conclusão", "Dep. Admin. Escola", "Status Redação"
])

with tab1:
    df, total = make_freq_table(stats["sexo"], "Sexo")
    display_table(df, total, "Distribuição por Sexo")
    st.markdown("""
    **Análise:** O ENEM 2024 apresenta predominância de candidatas do sexo feminino, refletindo uma tendência
    histórica observada desde 2010, quando as mulheres passaram a representar mais de 50% dos inscritos.
    """)

with tab2:
    df, total = make_freq_table(stats["regiao"], "Região")
    display_table(df, total, "Distribuição por Região Geográfica")
    st.markdown("""
    **Análise:** A região **Nordeste** concentra o maior número de inscritos no ENEM 2024,
    seguida pelo **Sudeste**. Isso reflete tanto a maior população quanto políticas de acesso ao ensino
    superior nessas regiões, especialmente o SISU e o ProUni.
    """)

with tab3:
    df, total = make_freq_table(stats["uf"], "UF")
    display_table(df, total, "Distribuição por Unidade Federativa")
    st.markdown("""
    **Análise:** São Paulo (SP), Minas Gerais (MG) e Bahia (BA) concentram os maiores volumes
    de inscritos, enquanto Roraima (RR), Amapá (AP) e Acre (AC) apresentam os menores contingentes,
    proporcional ao tamanho populacional de cada estado.
    """)

with tab4:
    df, total = make_freq_table(df_faixa, "Faixa Etária")
    display_table(df, total, "Distribuição por Faixa Etária")
    st.markdown("""
    **Análise:** A maioria dos participantes tem entre **17 e 21 anos**, perfil típico de quem
    está concluindo ou recém-concluiu o ensino médio. A presença significativa de candidatos
    acima dos 25 anos evidencia o caráter inclusivo do exame para pessoas que buscam ingressar
    tardiamente no ensino superior.
    """)

with tab5:
    df, total = make_freq_table(stats["cor_raca"], "Cor/Raça")
    display_table(df, total, "Distribuição por Cor/Raça")
    st.markdown("""
    **Análise:** Candidatos que se autodeclaram **pardos** representam a maior parcela dos inscritos,
    seguidos por brancos e pretos. Essa distribuição é relevante para avaliar políticas de cotas
    raciais nas universidades públicas brasileiras.
    """)

with tab6:
    df, total = make_freq_table(df_conclusao, "Situação de Conclusão")
    display_table(df, total, "Situação de Conclusão do Ensino Médio")
    st.markdown("""
    **Análise:** A maior parte dos candidatos já concluiu o ensino médio, enquanto uma parcela
    significativa ainda está cursando. O ENEM permite a participação de treineiros e candidatos
    em qualquer fase do ensino médio, ampliando a base de participantes.
    """)

with tab7:
    df, total = make_freq_table(stats["dep_adm"], "Dependência Administrativa")
    display_table(df, total, "Distribuição por Dependência Administrativa da Escola")
    st.markdown("""
    **Análise:** A maioria dos candidatos é oriunda de **escolas públicas estaduais**,
    reforçando que o ENEM é amplamente utilizado por estudantes da rede pública. Candidatos
    de escolas privadas representam uma proporção menor, mas historicamente obtêm médias
    mais elevadas.
    """)

with tab8:
    df, total = make_freq_table(stats["status_redacao"], "Status da Redação")
    display_table(df, total, "Status da Redação")
    st.markdown("""
    **Análise:** A maioria das redações foi **presente e válida**. Redações com nota zero podem
    decorrer de fuga ao tema, cópia de texto-base, texto em branco ou ofensa aos direitos humanos.
    Ausências na redação automaticamente anulam as demais provas para fins de seleção no SISU.
    """)

st.markdown("---")
st.caption("Fonte: INEP — Microdados ENEM 2024 | Big Data IESB | Dados completos (4.332.944 participantes)")
