import streamlit as st

st.set_page_config(
    page_title="ENEM 2024 - Análise Exploratória",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #AA0000;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid #AA0000;
        padding: 1rem;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 ENEM 2024 — Análise Exploratória de Dados</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Centro Universitário IESB • Ciência de Dados e Inteligência Artificial</div>', unsafe_allow_html=True)

st.markdown("""
## Bem-vindo ao Dashboard de Análise do ENEM 2024

Este painel interativo apresenta uma **Análise Exploratória de Dados (AED)** completa sobre os microdados do
**Exame Nacional do Ensino Médio (ENEM) 2024**, utilizando as bases de dados disponíveis no *Big Data IESB*.

### Sobre o ENEM
O ENEM é o maior exame do Brasil, realizado pelo Instituto Nacional de Estudos e Pesquisas Educacionais
Anísio Teixeira (INEP). Em 2024, mais de **4,3 milhões** de inscritos realizaram o exame, avaliando
competências em cinco áreas do conhecimento.

### Navegação
Utilize o **menu lateral** para acessar as seções de análise:

| Seção | Descrição |
|-------|-----------|
| 📋 Distribuição de Frequência | Tabelas de frequência para variáveis qualitativas |
| 📊 Variáveis Qualitativas | Gráficos de barras e pizza |
| 📈 Variáveis Quantitativas | Histogramas e Box Plots das notas |
| 🔗 Análise de Correlação | Matriz de correlação e dispersão entre notas |

### Fonte dos Dados
- **Tabela 1:** `ed_enem_2024_participantes` — Dados cadastrais e socioeconômicos
- **Tabela 2:** `ed_enem_2024_resultados` — Notas e resultados
- **Servidor:** Big Data IESB (`bigdata.dataiesb.com`)
- **Total de registros:** ~4.332.944 participantes
""")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Inscritos", "4.332.944", help="Total de inscritos no ENEM 2024")
with col2:
    st.metric("Áreas Avaliadas", "5", help="CN, CH, LC, MT e Redação")
with col3:
    st.metric("Estados", "27", help="26 estados + DF")
with col4:
    st.metric("Ano", "2024", help="Edição 2024 do ENEM")

st.markdown("---")
st.info("💡 **Dica:** As análises utilizam amostragem estratificada de 50.000 registros para garantir desempenho interativo. Os resultados são estatisticamente representativos da população total.")
