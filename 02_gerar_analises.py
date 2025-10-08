import pandas as pd
import numpy as np
import time
import os
import json

try:
    import polars as pl  # opcional para performance
except Exception:
    pl = None

def gerar_analises():
    """
    Carrega o parquet e exporta JSONs leves para o frontend (Chart.js).
    """
    print("Carregando dados pré-processados do arquivo Parquet...")
    start_time = time.time()
    full_df = None
    
    try:
        if pl is not None:
            full_df = pl.read_parquet('acidentes_tratados.parquet').to_pandas()
        else:
            full_df = pd.read_parquet('acidentes_tratados.parquet')
        print(f"Dados carregados em {time.time() - start_time:.2f}s. Linhas: {len(full_df)}")
    except FileNotFoundError:
        print("Erro: 'acidentes_tratados.parquet' não encontrado. Tentando ler CSVs 2024-2025...")
    except Exception as e:
        print(f"Falha ao ler parquet ({e}). Tentando CSVs 2024-2025...")

    if full_df is None:
        base = os.path.dirname(__file__)
        candidatos = [os.path.join(base, 'acidentes2024.csv'), os.path.join(base, 'acidentes2025.csv')]
        arquivos = [p for p in candidatos if os.path.exists(p)]
        if not arquivos:
            print("Nenhum CSV 2024/2025 encontrado. Abortando.")
            return
        frames = []
        for p in arquivos:
            try:
                if pl is not None:
                    frames.append(pl.read_csv(p, separator=';', encoding='latin-1').to_pandas())
                else:
                    frames.append(pd.read_csv(p, sep=';', encoding='latin-1', low_memory=False))
            except Exception as e:
                print(f"Falha ao ler {p}: {e}")
        if not frames:
            print("Falha geral ao ler CSVs. Abortando.")
            return
        full_df = pd.concat(frames, ignore_index=True)
        print(f"CSVs carregados. Linhas: {len(full_df)}")

    # Segurança: manter apenas 2024-2025
    if 'data_inversa' in full_df.columns:
        full_df['data_inversa'] = pd.to_datetime(full_df['data_inversa'], errors='coerce')
        full_df = full_df[full_df['data_inversa'].dt.year.isin([2024, 2025])]
        print(f"Registros após filtro 2024-2025: {len(full_df)}")

    os.makedirs('dashboard/data', exist_ok=True)

    # Utilidades
    def write_json(name, payload):
        with open(os.path.join('dashboard', 'data', name), 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)

    # Top 10 causas
    if 'causa_acidente' in full_df.columns:
        s = full_df['causa_acidente'].fillna('Não Informado').value_counts().head(10)
        write_json('top_10_causas.json', {'labels': s.index.tolist(), 'data': s.values.tolist()})

    # Acidentes por dia da semana (ordem customizada)
    if 'dia_semana' in full_df.columns:
        ordem = [
            'sábado','domingo','sexta-feira','segunda-feira','quinta-feira','quarta-feira','terça-feira'
        ]
        s = full_df['dia_semana'].fillna('não informado').str.lower().value_counts()
        # reordenar conforme lista
        labels = [d for d in ordem if d in s.index]
        data = [int(s[d]) for d in labels]
        write_json('acidentes_por_dia_semana.json', {'labels': labels, 'data': data})

    # Tipo de pista
    if 'tipo_pista' in full_df.columns:
        s = full_df['tipo_pista'].fillna('Não Informado').value_counts()
        write_json('tipo_pista.json', {'labels': s.index.tolist(), 'data': s.values.tolist()})

    # Histograma idade
    if 'idade' in full_df.columns:
        idade = pd.to_numeric(full_df['idade'], errors='coerce')
        idade = idade[(idade >= 18) & (idade <= 100)].dropna()
        counts, bins = np.histogram(idade, bins=40)
        mids = ((bins[:-1] + bins[1:]) / 2).round(1).astype(float).tolist()
        write_json('hist_idade.json', {'bins': mids, 'counts': counts.astype(int).tolist()})

    # Histograma ano de fabricação
    if 'ano_fabricacao_veiculo' in full_df.columns:
        anos = pd.to_numeric(full_df['ano_fabricacao_veiculo'], errors='coerce')
        anos = anos[(anos >= 1980) & (anos <= 2025)].dropna()
        counts, bins = np.histogram(anos, bins=50)
        mids = ((bins[:-1] + bins[1:]) / 2).round(0).astype(int).tolist()
        write_json('hist_ano_veiculo.json', {'bins': mids, 'counts': counts.astype(int).tolist()})

    # Proporção por UF
    if 'uf' in full_df.columns:
        s = full_df['uf'].fillna('Não Informado').value_counts()
        top = s.head(10)
        outros = int(s.iloc[10:].sum())
        labels = top.index.tolist() + (["Outros"] if outros > 0 else [])
        data = top.values.tolist() + ([outros] if outros > 0 else [])
        write_json('proporcao_uf.json', {'labels': labels, 'data': data})

    # Pizza: fase do dia
    if 'fase_dia' in full_df.columns:
        s = full_df['fase_dia'].fillna('Não Informado').value_counts()
        write_json('fase_dia.json', {'labels': s.index.tolist(), 'data': s.values.tolist()})

    # Pizza: condição meteorológica (top 5)
    if 'condicao_metereologica' in full_df.columns:
        s = full_df['condicao_metereologica'].fillna('Não Informado').value_counts().head(5)
        write_json('condicao_meteo.json', {'labels': s.index.tolist(), 'data': s.values.tolist()})

    # Dispersões (amostras leves)
    rng = np.random.default_rng(42)
    def sample_points(df_points, max_points=4000):
        if len(df_points) <= max_points:
            return df_points
        idx = rng.choice(len(df_points), size=max_points, replace=False)
        return df_points.iloc[idx]

    if {'idade','ano_fabricacao_veiculo'}.issubset(full_df.columns):
        dfp = pd.DataFrame({
            'x': pd.to_numeric(full_df['idade'], errors='coerce').clip(lower=0, upper=100),
            'y': pd.to_numeric(full_df['ano_fabricacao_veiculo'], errors='coerce').clip(lower=1980, upper=2025)
        }).dropna()
        dfp = sample_points(dfp)
        write_json('scatter_idade_ano.json', {'points': dfp.to_dict(orient='records')})

    if {'idade','total_feridos'}.issubset(full_df.columns):
        dfp = pd.DataFrame({
            'x': pd.to_numeric(full_df['idade'], errors='coerce').clip(lower=0, upper=100),
            'y': pd.to_numeric(full_df['total_feridos'], errors='coerce').clip(lower=0, upper=50)
        }).dropna()
        dfp = sample_points(dfp)
        write_json('scatter_idade_feridos.json', {'points': dfp.to_dict(orient='records')})

    if {'total_feridos','mortos'}.issubset(full_df.columns):
        dfp = pd.DataFrame({
            'x': pd.to_numeric(full_df['total_feridos'], errors='coerce').clip(lower=0, upper=50),
            'y': pd.to_numeric(full_df['mortos'], errors='coerce').clip(lower=0, upper=10)
        }).dropna()
        dfp = sample_points(dfp)
        write_json('scatter_feridos_mortos.json', {'points': dfp.to_dict(orient='records')})

    if {'ano_fabricacao_veiculo','total_feridos'}.issubset(full_df.columns):
        dfp = pd.DataFrame({
            'x': pd.to_numeric(full_df['ano_fabricacao_veiculo'], errors='coerce').clip(lower=1980, upper=2025),
            'y': pd.to_numeric(full_df['total_feridos'], errors='coerce').clip(lower=0, upper=50)
        }).dropna()
        dfp = sample_points(dfp)
        write_json('scatter_ano_feridos.json', {'points': dfp.to_dict(orient='records')})

    # Relatório simples com estatísticas (para consulta rápida)
    try:
        estat_cols = [c for c in ['mortos', 'total_feridos', 'idade'] if c in full_df.columns]
        linhas = []
        for c in estat_cols:
            linhas.append(f"- {c}: média {full_df[c].mean():.2f}, mediana {full_df[c].median():.2f}, desvio {full_df[c].std():.2f}")
        os.makedirs('dashboard', exist_ok=True)
        with open('dashboard/analise_estatistica.md', 'w', encoding='utf-8') as f:
            f.write('# Estatísticas rápidas\n\n')
            f.write('\n'.join(linhas))
    except Exception as e:
        print(f"Falha ao escrever estatísticas: {e}")

    print("JSONs gerados com sucesso em dashboard/data/")

if __name__ == "__main__":
    gerar_analises()