import pandas as pd
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# Encontrar todos os arquivos CSV de acidentes no diretório
path = r'c:\Users\Aluno\Projeto CD - Acidentes'
all_files = glob.glob(path + "/acidentes*.csv")

# Lista para armazenar os DataFrames
df_list = []

# Carregar cada arquivo CSV e adicioná-lo à lista
for filename in all_files:
    try:
        df = pd.read_csv(filename, index_col=None, header=0, sep=';', encoding='latin-1')
        df_list.append(df)
    except Exception as e:
        print(f"Erro ao ler o arquivo {filename}: {e}")

# Concatenar todos os DataFrames em um só
if df_list:
    full_df = pd.concat(df_list, axis=0, ignore_index=True)

    # Mostrar as primeiras 5 linhas
    print("--- Primeiras 5 linhas do DataFrame ---")
    print(full_df.head())

    print("\n--- Resumo das informações do DataFrame ANTES do tratamento de nulos ---")
    full_df.info()

    # Identificar colunas com valores ausentes
    print("\n--- Colunas com valores ausentes ANTES do tratamento ---")
    colunas_com_nulos = full_df.columns[full_df.isnull().any()]
    print(full_df[colunas_com_nulos].isnull().sum())

    # Preencher valores ausentes em 'causa_acidente'
    if 'causa_acidente' in full_df.columns:
        full_df['causa_acidente'] = full_df['causa_acidente'].fillna('Não Informado')
        print("\nValores ausentes em 'causa_acidente' preenchidos com 'Não Informado'.")

    # Preencher valores ausentes em colunas numéricas com a mediana
    print("\nPreenchendo valores ausentes em colunas numéricas com a mediana...")
    colunas_numericas = full_df.select_dtypes(include=['number']).columns
    for col in colunas_numericas:
        if full_df[col].isnull().any():
            mediana = full_df[col].median()
            full_df[col] = full_df[col].fillna(mediana)
            print(f"Valores ausentes na coluna numérica '{col}' preenchidos com a mediana ({mediana}).")

    # Preencher valores ausentes nas colunas de texto restantes
    print("\nPreenchendo valores ausentes nas colunas de texto restantes com 'Não Informado'...")
    colunas_texto = full_df.select_dtypes(include=['object']).columns
    for col in colunas_texto:
        if full_df[col].isnull().any():
            full_df[col] = full_df[col].fillna('Não Informado')
            print(f"Valores ausentes em '{col}' preenchidos.")

    print("\n--- Resumo das informações do DataFrame APÓS TODO o tratamento de nulos ---")
    full_df.info()

    # --- ANÁLISES --- #

    # 1. Analisar as 10 causas mais comuns de acidentes
    print("\n--- Top 10 Causas de Acidentes ---")
    top_10_causas = full_df['causa_acidente'].value_counts().head(10)
    print(top_10_causas)

    # 2. Analisar o número de acidentes por UF
    print("\n--- Número de Acidentes por Estado (UF) ---")
    acidentes_por_uf = full_df['uf'].value_counts()
    print(acidentes_por_uf)

    # Padronizar a coluna 'dia_semana'
    dias_map = {
        'Sexta': 'sexta-feira',
        'Segunda': 'segunda-feira',
        'Sábado': 'sábado',
        'Domingo': 'domingo',
        'Quarta': 'quarta-feira',
        'Terça': 'terça-feira',
        'Quinta': 'quinta-feira'
    }
    full_df['dia_semana'] = full_df['dia_semana'].replace(dias_map).str.lower()

    # 3. Analisar o número de acidentes por dia da semana (após padronização)
    print("\n--- Número de Acidentes por Dia da Semana ---")
    dias_ordem = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
    acidentes_por_dia = full_df['dia_semana'].value_counts().reindex(dias_ordem)
    print(acidentes_por_dia)

    # --- SALVAR DATAFRAME LIMPO --- #
    output_filename = 'acidentes_tratados.csv'
    print(f"\nSalvando o DataFrame limpo em '{output_filename}'...")
    full_df.to_csv(output_filename, index=False, sep=';', encoding='latin-1')
    print("Arquivo salvo com sucesso!")

    # --- VISUALIZAÇÕES ---
    sns.set_style("whitegrid")

    # Gráfico 1: Top 10 Causas de Acidentes
    plt.figure(figsize=(12, 8))
    sns.barplot(y=top_10_causas.index, x=top_10_causas.values, palette="viridis")
    plt.title('Top 10 Causas de Acidentes', fontsize=16)
    plt.xlabel('Número de Acidentes', fontsize=12)
    plt.ylabel('Causa do Acidente', fontsize=12)
    plt.tight_layout()
    plt.savefig('top_10_causas_acidentes.png')
    print("\nGráfico 'top_10_causas_acidentes.png' salvo.")

    # Gráfico 2: Número de Acidentes por Estado (UF)
    plt.figure(figsize=(12, 8))
    sns.barplot(y=acidentes_por_uf.index, x=acidentes_por_uf.values, palette="plasma")
    plt.title('Número de Acidentes por Estado (UF)', fontsize=16)
    plt.xlabel('Número de Acidentes', fontsize=12)
    plt.ylabel('Estado (UF)', fontsize=12)
    plt.tight_layout()
    plt.savefig('acidentes_por_uf.png')
    print("Gráfico 'acidentes_por_uf.png' salvo.")

    # Gráfico 3: Número de Acidentes por Dia da Semana
    plt.figure(figsize=(12, 8))
    sns.barplot(x=acidentes_por_dia.index, y=acidentes_por_dia.values, palette="magma", order=dias_ordem)
    plt.title('Número de Acidentes por Dia da Semana', fontsize=16)
    plt.xlabel('Dia da Semana', fontsize=12)
    plt.ylabel('Número de Acidentes', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('acidentes_por_dia_semana.png')
    print("Gráfico 'acidentes_por_dia_semana.png' salvo.")

    # Gráfico 4: Histograma da Idade dos Condutores
    plt.figure(figsize=(12, 8))
    # Filtrar idades para um intervalo razoável (ex: 18 a 100 anos)
    idade_filtrada = full_df[(full_df['idade'] >= 18) & (full_df['idade'] <= 100)]['idade']
    sns.histplot(idade_filtrada, bins=40, kde=True, color='skyblue')
    plt.title('Distribuição de Idade dos Condutores', fontsize=16)
    plt.xlabel('Idade', fontsize=12)
    plt.ylabel('Frequência (Número de Pessoas)', fontsize=12)
    plt.tight_layout()
    plt.savefig('histograma_idade_condutor.png')
    print("Gráfico 'histograma_idade_condutor.png' salvo.")

    # Gráfico 5: Gráfico de Pizza da Proporção de Acidentes por Estado
    plt.figure(figsize=(14, 10))
    # Agrupar estados fora do top 10 em 'Outros'
    top_10_uf = acidentes_por_uf.head(10)
    outros_soma = acidentes_por_uf[10:].sum()
    # Usar pd.concat para adicionar 'Outros'
    pie_data = pd.concat([top_10_uf, pd.Series([outros_soma], index=['Outros'])])

    # Criar a explosão para a primeira fatia (o estado com mais acidentes)
    explode = [0.1] + [0] * len(pie_data.index[1:])

    plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True, textprops={'fontsize': 12})
    plt.title('Proporção de Acidentes por Estado (Top 10 + Outros)', fontsize=18)
    plt.axis('equal')  # Assegura que o gráfico seja um círculo
    plt.tight_layout()
    plt.savefig('proporcao_acidentes_uf.png')
    print("Gráfico 'proporcao_acidentes_uf.png' salvo.")

    # Gráfico 6: Gráfico de Barras de Acidentes por Dia da Semana (Ordem Decrescente)
    plt.figure(figsize=(12, 8))
    acidentes_por_dia_desc = full_df['dia_semana'].value_counts()
    sns.barplot(x=acidentes_por_dia_desc.index, y=acidentes_por_dia_desc.values, palette="rocket")
    plt.title('Total de Acidentes por Dia da Semana (Ordem Decrescente)', fontsize=16)
    plt.xlabel('Dia da Semana', fontsize=12)
    plt.ylabel('Número de Acidentes', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('acidentes_por_dia_semana_decrescente.png')
    print("Gráfico 'acidentes_por_dia_semana_decrescente.png' salvo.")

    # --- ANÁLISE ESTATÍSTICA ADICIONAL ---
    print("\n--- Análise Estatística Descritiva ---")
    
    # Criar coluna 'total_feridos'
    full_df['total_feridos'] = full_df['feridos_leves'] + full_df['feridos_graves']

    # Colunas para analisar
    colunas_estatisticas = ['mortos', 'total_feridos']

    for col in colunas_estatisticas:
        media = full_df[col].mean()
        mediana = full_df[col].median()
        desvio_padrao = full_df[col].std()
        
        print(f"\nEstatísticas para a coluna '{col}':")
        print(f"  - Média: {media:.4f}")
        print(f"  - Mediana: {mediana:.4f}")
        print(f"  - Desvio Padrão: {desvio_padrao:.4f}")

        if media > mediana:
            print("  - Comparação: A média é maior que a mediana, o que sugere uma assimetria à direita.")
            print("    Isso indica que a maioria dos acidentes tem um número baixo de vítimas, mas alguns acidentes (outliers) têm um número muito alto, puxando a média para cima.")
        elif media < mediana:
            print("  - Comparação: A média é menor que a mediana, o que sugere uma assimetria à esquerda.")
        else:
            print("  - Comparação: A média e a mediana são muito próximas, sugerindo uma distribuição relativamente simétrica.")
else:
    print("Nenhum arquivo CSV foi carregado.")
