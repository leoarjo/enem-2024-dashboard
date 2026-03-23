"""Utility functions for database connection and data loading."""
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

def _get_db_url():
    db = st.secrets["database"]
    return (
        f"postgresql+psycopg2://{db['user']}:{db['password']}"
        f"@{db['host']}/{db['name']}"
    )

DB_CONNECT_ARGS = {"options": "-c search_path=public"}

QUALITATIVE_VARS = {
    "sg_uf_prova": "UF da Prova",
    "regiao_nome_prova": "Região",
    "tp_sexo": "Sexo",
    "tp_faixa_etaria": "Faixa Etária",
    "tp_estado_civil": "Estado Civil",
    "tp_cor_raca": "Cor/Raça",
    "tp_nacionalidade": "Nacionalidade",
    "tp_st_conclusao": "Situação de Conclusão",
    "tp_ensino": "Tipo de Ensino",
    "in_treineiro": "Treineiro",
    "tp_dependencia_adm_esc": "Depend. Admin. Escola",
    "tp_localizacao_esc": "Localização Escola",
    "tp_lingua": "Língua Estrangeira",
    "tp_status_redacao": "Status da Redação",
    "tp_cor_raca": "Cor/Raça",
}

QUANTITATIVE_VARS = {
    "nota_cn_ciencias_da_natureza": "Ciências da Natureza",
    "nota_ch_ciencias_humanas": "Ciências Humanas",
    "nota_lc_linguagens_e_codigos": "Linguagens e Códigos",
    "nota_mt_matematica": "Matemática",
    "nota_redacao": "Redação",
    "nota_media_5_notas": "Média Geral",
    "idade_calculada": "Idade",
}

FAIXA_ETARIA_ORDER = [
    "16 anos ou menos", "17 anos", "18 anos", "19 anos", "20 anos",
    "21 anos", "22 anos", "23 anos", "24 anos", "25 anos",
    "Entre 26 e 30 anos", "Entre 31 e 35 anos", "Entre 36 e 40 anos",
    "Entre 41 e 45 anos", "Entre 46 e 50 anos", "Entre 51 e 55 anos",
    "Entre 56 e 60 anos", "Entre 61 e 65 anos", "Entre 66 e 70 anos",
    "Maior de 70 anos"
]


@st.cache_resource
def get_engine():
    return create_engine(_get_db_url(), connect_args=DB_CONNECT_ARGS)


def get_connection():
    return get_engine().connect()


@st.cache_data(ttl=3600, show_spinner="Carregando dados do Big Data IESB...")
def load_sample(n=50000):
    """Load a random sample from resultados (scores + geography) table."""
    conn = get_connection()
    # BERNOULLI(1.2) ≈ 52k rows from 4.3M; REPEATABLE for reproducibility
    query = """
        SELECT
            sg_uf_prova, regiao_nome_prova,
            tp_dependencia_adm_esc, tp_localizacao_esc,
            tp_lingua, tp_status_redacao,
            nota_cn_ciencias_da_natureza, nota_ch_ciencias_humanas,
            nota_lc_linguagens_e_codigos, nota_mt_matematica,
            nota_redacao, nota_media_5_notas
        FROM public.ed_enem_2024_resultados
        TABLESAMPLE BERNOULLI(1.2) REPEATABLE(42)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data(ttl=3600, show_spinner="Carregando dados demográficos...")
def load_sample_participantes(n=50000):
    """Load a random sample from participantes (demographics) table."""
    conn = get_connection()
    # BERNOULLI(1.2) ≈ 52k rows from 4.3M; REPEATABLE for reproducibility
    query = """
        SELECT
            sg_uf_prova, regiao_nome_prova, tp_faixa_etaria, idade_calculada,
            tp_sexo, tp_estado_civil, tp_cor_raca, tp_nacionalidade,
            tp_st_conclusao, tp_ensino, in_treineiro
        FROM public.ed_enem_2024_participantes
        TABLESAMPLE BERNOULLI(1.2) REPEATABLE(42)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data(ttl=3600, show_spinner="Carregando estatísticas agregadas...")
def load_aggregated_stats():
    """Load pre-aggregated statistics for performance."""
    conn = get_connection()
    stats = {}

    # Region counts
    df_reg = pd.read_sql("""
        SELECT regiao_nome_prova as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_participantes
        GROUP BY regiao_nome_prova
        ORDER BY contagem DESC
    """, conn)
    stats["regiao"] = df_reg

    # Sex counts
    df_sex = pd.read_sql("""
        SELECT tp_sexo as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_participantes
        GROUP BY tp_sexo
        ORDER BY contagem DESC
    """, conn)
    stats["sexo"] = df_sex

    # Cor/Raça
    df_raca = pd.read_sql("""
        SELECT tp_cor_raca as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_participantes
        GROUP BY tp_cor_raca
        ORDER BY contagem DESC
    """, conn)
    stats["cor_raca"] = df_raca

    # Treineiro
    df_trei = pd.read_sql("""
        SELECT in_treineiro as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_participantes
        GROUP BY in_treineiro
        ORDER BY contagem DESC
    """, conn)
    stats["treineiro"] = df_trei

    # UF
    df_uf = pd.read_sql("""
        SELECT sg_uf_prova as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_participantes
        GROUP BY sg_uf_prova
        ORDER BY contagem DESC
    """, conn)
    stats["uf"] = df_uf

    # Escola dependência admin (from resultados)
    df_dep = pd.read_sql("""
        SELECT TRIM(tp_dependencia_adm_esc) as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_resultados
        WHERE tp_dependencia_adm_esc IS NOT NULL
          AND TRIM(tp_dependencia_adm_esc) NOT IN ('', 'Não Respondeu', 'N\u00e3o Respondeu')
        GROUP BY TRIM(tp_dependencia_adm_esc)
        ORDER BY contagem DESC
    """, conn)
    stats["dep_adm"] = df_dep

    # Status redação (from resultados)
    df_red = pd.read_sql("""
        SELECT TRIM(tp_status_redacao) as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_resultados
        WHERE tp_status_redacao IS NOT NULL
          AND TRIM(tp_status_redacao) NOT IN ('', 'Missing - Sem informa\u00e7\u00e3o')
        GROUP BY TRIM(tp_status_redacao)
        ORDER BY contagem DESC
    """, conn)
    stats["status_redacao"] = df_red

    # Score stats by region (from resultados)
    df_notas = pd.read_sql("""
        SELECT TRIM(regiao_nome_prova) as regiao_nome_prova,
            ROUND(AVG(nota_cn_ciencias_da_natureza)::numeric, 1) as media_cn,
            ROUND(AVG(nota_ch_ciencias_humanas)::numeric, 1) as media_ch,
            ROUND(AVG(nota_lc_linguagens_e_codigos)::numeric, 1) as media_lc,
            ROUND(AVG(nota_mt_matematica)::numeric, 1) as media_mt,
            ROUND(AVG(nota_redacao)::numeric, 1) as media_redacao,
            ROUND(AVG(nota_media_5_notas)::numeric, 1) as media_geral
        FROM public.ed_enem_2024_resultados
        WHERE nota_media_5_notas IS NOT NULL
        GROUP BY TRIM(regiao_nome_prova)
        ORDER BY media_geral DESC
    """, conn)
    stats["notas_regiao"] = df_notas

    conn.close()
    return stats


@st.cache_data(ttl=3600, show_spinner="Carregando distribuição de faixa etária...")
def load_faixa_etaria():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT tp_faixa_etaria as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_participantes
        GROUP BY tp_faixa_etaria
        ORDER BY contagem DESC
    """, conn)
    conn.close()
    return df


@st.cache_data(ttl=3600, show_spinner="Carregando situação de conclusão...")
def load_st_conclusao():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT TRIM(tp_st_conclusao) as valor, COUNT(*) as contagem
        FROM public.ed_enem_2024_participantes
        WHERE tp_st_conclusao IS NOT NULL
          AND TRIM(tp_st_conclusao) NOT IN ('', 'Missing - Candidato sem Informa\u00e7\u00e3o')
        GROUP BY TRIM(tp_st_conclusao)
        ORDER BY contagem DESC
    """, conn)
    conn.close()
    return df


def freq_table(series, label="Variável"):
    """Build a frequency distribution table from a pandas Series."""
    vc = series.value_counts(dropna=False)
    total = len(series)
    df = pd.DataFrame({
        label: vc.index,
        "Frequência Absoluta": vc.values,
        "Frequência Relativa (%)": (vc.values / total * 100).round(2),
        "Frequência Acumulada": vc.values.cumsum(),
        "Freq. Acum. Rel. (%)": (vc.values.cumsum() / total * 100).round(2),
    })
    return df
