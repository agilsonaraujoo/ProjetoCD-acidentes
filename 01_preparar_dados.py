import pandas as pd
import glob
import time
import os

def preparar_dados():
    """
    Lê todos os arquivos CSV de acidentes, limpa os dados e salva o resultado
    em um arquivo Parquet para carregamento rápido no futuro.
    """
    print("Iniciando a preparação dos dados...")
    start_time = time.time()

    # Ler explicitamente apenas 2024 e 2025
    path = os.path.dirname(__file__)
    candidatos = [
        os.path.join(path, "acidentes2024.csv"),
        os.path.join(path, "acidentes2025.csv"),
    ]
    all_files = [f for f in candidatos if os.path.exists(f)]

    if not all_files:
        print("Nenhum arquivo CSV de acidentes encontrado. Abortando.")
        return

    print(f"{len(all_files)} arquivos CSV (2024-2025) encontrados. Carregando e concatenando...")
    df_list = []
    for filename in all_files:
        try:
            df = pd.read_csv(filename, index_col=None, header=0, sep=';', encoding='latin-1', low_memory=False)
            df_list.append(df)
        except Exception as e:
            print(f"Erro ao ler o arquivo {filename}: {e}")

    if not df_list:
        print("Nenhum DataFrame foi carregado. Abortando.")
        return

    full_df = pd.concat(df_list, axis=0, ignore_index=True)
    print(f"Dados concatenados. Total de {len(full_df)} linhas.")

    # Filtrar apenas registros de 2024 e 2025
    if 'data_inversa' in full_df.columns:
        full_df['data_inversa'] = pd.to_datetime(full_df['data_inversa'], errors='coerce', dayfirst=True)
        linhas_antes_filtro = len(full_df)
        full_df = full_df[full_df['data_inversa'].dt.year.isin([2024, 2025])]
        linhas_removidas = linhas_antes_filtro - len(full_df)
        print(f"Registros removidos fora do intervalo 2024-2025: {linhas_removidas}")
    else:
        print("Coluna 'data_inversa' não encontrada. Nenhum filtro de ano aplicado.")

    print("\nIniciando limpeza e tratamento dos dados...")

    # Conversões numéricas seguras
    for col in ['idade', 'ano_fabricacao_veiculo', 'feridos_leves', 'feridos_graves', 'mortos']:
        if col in full_df.columns:
            full_df[col] = pd.to_numeric(full_df[col], errors='coerce')

    # Regras de faixas plausíveis (mantém NaN para fora de faixa)
    if 'idade' in full_df.columns:
        full_df.loc[~full_df['idade'].between(0, 100), 'idade'] = pd.NA
    if 'ano_fabricacao_veiculo' in full_df.columns:
        full_df.loc[~full_df['ano_fabricacao_veiculo'].between(1980, 2025), 'ano_fabricacao_veiculo'] = pd.NA
    # Preencher valores ausentes em 'causa_acidente'
    if 'causa_acidente' in full_df.columns:
        full_df['causa_acidente'] = full_df['causa_acidente'].fillna('Não Informado')

    # Preencher valores ausentes em colunas numéricas com a mediana (exceto idade/ano)
    colunas_numericas = full_df.select_dtypes(include=['number']).columns
    colunas_excluir_mediana = {'idade', 'ano_fabricacao_veiculo'}
    for col in colunas_numericas:
        if col in colunas_excluir_mediana:
            continue
        if full_df[col].isnull().any():
            if col in {'feridos_leves', 'feridos_graves', 'mortos'}:
                # Para contagens, preferir preencher com 0
                full_df[col] = full_df[col].fillna(0)
            else:
                mediana = full_df[col].median()
                full_df[col] = full_df[col].fillna(mediana)

    # Preencher valores ausentes nas colunas de texto restantes
    colunas_texto = full_df.select_dtypes(include=['object']).columns
    for col in colunas_texto:
        if full_df[col].isnull().any():
            full_df[col] = full_df[col].fillna('Não Informado')

    # Padronizar a coluna 'dia_semana'
    if 'dia_semana' in full_df.columns:
        dias_map = {
            'Sexta': 'sexta-feira', 'Segunda': 'segunda-feira', 'Sábado': 'sábado',
            'Domingo': 'domingo', 'Quarta': 'quarta-feira', 'Terça': 'terça-feira',
            'Quinta': 'quinta-feira'
        }
        full_df['dia_semana'] = full_df['dia_semana'].replace(dias_map).str.lower()

    # Criar coluna 'total_feridos'
    if {'feridos_leves', 'feridos_graves'}.issubset(full_df.columns):
        full_df['total_feridos'] = full_df['feridos_leves'].fillna(0) + full_df['feridos_graves'].fillna(0)

    print("Limpeza de dados concluída.")

    # Salvar o DataFrame limpo em formato Parquet
    # Garantir que colunas de coordenadas estejam em formato string compatível com Parquet
    for coluna_coord in ['latitude', 'longitude']:
        if coluna_coord in full_df.columns:
            full_df[coluna_coord] = full_df[coluna_coord].astype('string')

    output_filename = 'acidentes_tratados.parquet'
    print(f"\nSalvando DataFrame limpo em '{output_filename}'...")
    try:
        full_df.to_parquet(output_filename, index=False, engine='pyarrow', compression='zstd', compression_level=3)
    except Exception:
        # Fallback para compressão padrão caso zstd não esteja disponível
        full_df.to_parquet(output_filename, index=False)
    print("Arquivo Parquet salvo com sucesso!")

    end_time = time.time()
    print(f"\nProcesso de preparação concluído em {end_time - start_time:.2f} segundos.")

if __name__ == "__main__":
    preparar_dados()
