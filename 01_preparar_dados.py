import pandas as pd
import glob
import time

def preparar_dados():
    """
    Lê todos os arquivos CSV de acidentes, limpa os dados e salva o resultado
    em um arquivo Parquet para carregamento rápido no futuro.
    """
    print("Iniciando a preparação dos dados...")
    start_time = time.time()

    # Encontrar todos os arquivos CSV de acidentes no diretório
    path = r'c:\Users\Aluno\Projeto CD - Acidentes'
    all_files = [
        f for f in glob.glob(path + "/acidentes*.csv")
        if not f.endswith("acidentes_tratados.csv")
    ]

    if not all_files:
        print("Nenhum arquivo CSV de acidentes encontrado. Abortando.")
        return

    print(f"{len(all_files)} arquivos CSV encontrados. Carregando e concatenando...")
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

    # Filtrar apenas registros a partir de 2020
    if 'data_inversa' in full_df.columns:
        full_df['data_inversa'] = pd.to_datetime(full_df['data_inversa'], errors='coerce', dayfirst=True)
        linhas_antes_filtro = len(full_df)
        full_df = full_df[full_df['data_inversa'].dt.year >= 2020]
        linhas_removidas = linhas_antes_filtro - len(full_df)
        print(f"Registros removidos anteriores a 2020: {linhas_removidas}")
    else:
        print("Coluna 'data_inversa' não encontrada. Nenhum filtro de ano aplicado.")

    print("\nIniciando limpeza e tratamento dos dados...")
    # Preencher valores ausentes em 'causa_acidente'
    if 'causa_acidente' in full_df.columns:
        full_df['causa_acidente'] = full_df['causa_acidente'].fillna('Não Informado')

    # Preencher valores ausentes em colunas numéricas com a mediana
    colunas_numericas = full_df.select_dtypes(include=['number']).columns
    for col in colunas_numericas:
        if full_df[col].isnull().any():
            mediana = full_df[col].median()
            full_df[col] = full_df[col].fillna(mediana)

    # Preencher valores ausentes nas colunas de texto restantes
    colunas_texto = full_df.select_dtypes(include=['object']).columns
    for col in colunas_texto:
        if full_df[col].isnull().any():
            full_df[col] = full_df[col].fillna('Não Informado')

    # Padronizar a coluna 'dia_semana'
    dias_map = {
        'Sexta': 'sexta-feira', 'Segunda': 'segunda-feira', 'Sábado': 'sábado',
        'Domingo': 'domingo', 'Quarta': 'quarta-feira', 'Terça': 'terça-feira',
        'Quinta': 'quinta-feira'
    }
    full_df['dia_semana'] = full_df['dia_semana'].replace(dias_map).str.lower()

    # Criar coluna 'total_feridos'
    full_df['total_feridos'] = full_df['feridos_leves'] + full_df['feridos_graves']

    print("Limpeza de dados concluída.")

    # Salvar o DataFrame limpo em formato Parquet
    # Garantir que colunas de coordenadas estejam em formato string compatível com Parquet
    for coluna_coord in ['latitude', 'longitude']:
        if coluna_coord in full_df.columns:
            full_df[coluna_coord] = full_df[coluna_coord].astype('string')

    output_filename = 'acidentes_tratados.parquet'
    print(f"\nSalvando DataFrame limpo em '{output_filename}'...")
    full_df.to_parquet(output_filename, index=False)
    print("Arquivo Parquet salvo com sucesso!")

    end_time = time.time()
    print(f"\nProcesso de preparação concluído em {end_time - start_time:.2f} segundos.")

if __name__ == "__main__":
    preparar_dados()
