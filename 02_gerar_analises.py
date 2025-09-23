import pandas as pd
import plotly.express as px
import numpy as np
import time

def gerar_analises():
    """
    Carrega os dados pré-processados e gera todas as análises e visualizações.
    """
    # Carregar os dados pré-processados do arquivo Parquet
    print("Carregando dados pré-processados do arquivo Parquet...")
    start_time = time.time()
    try:
        full_df = pd.read_parquet('acidentes_tratados.parquet')
        print(f"Dados carregados com sucesso em {time.time() - start_time:.2f} segundos.")
        print(f"Total de {len(full_df)} linhas prontas para análise.")
    except FileNotFoundError:
        print("Erro: O arquivo 'acidentes_tratados.parquet' não foi encontrado.")
        print("Por favor, execute o script '01_preparar_dados.py' primeiro.")
        return

    # --- ANÁLISES --- #
    print("\n--- Realizando Análises ---")
    top_10_causas = full_df['causa_acidente'].value_counts().head(10)
    acidentes_por_uf = full_df['uf'].value_counts()

    # --- VISUALIZAÇÕES INTERATIVAS COM PLOTLY ---
    print("\nGerando gráficos interativos com Plotly...")

    # Gráfico 1: Top 10 Causas de Acidentes
    fig1 = px.bar(top_10_causas, y=top_10_causas.index, x=top_10_causas.values, orientation='h',
                  labels={'y': 'Causa do Acidente', 'x': 'Número de Acidentes'},
                  template='plotly_white', text=top_10_causas.values)
    fig1.update_layout(
        title={'text': '<b>Top 10 Causas de Acidentes</b><br><sup>Falta de atenção à condução é a causa predominante</sup>', 'x': 0.5},
        yaxis={'categoryorder': 'total ascending'}
    )
    fig1.update_traces(
        texttemplate='%{text:.2s}', textposition='outside',
        hovertemplate='<b>Causa</b>: %{y}<br><b>Total de Acidentes</b>: %{x}<extra></extra>'
    )
    fig1.write_html('dashboard/interactive_charts/top_10_causas.html')
    print("Gráfico 'top_10_causas.html' salvo.")

    # Gráfico 2: Histograma da Idade dos Condutores (Otimizado)
    idade_filtrada = full_df[(full_df['idade'] >= 18) & (full_df['idade'] <= 100)]['idade']
    counts, bins = np.histogram(idade_filtrada, bins=40)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    hist_data = pd.DataFrame({'Faixa de Idade': bin_centers, 'Frequência': counts})
    hist_data['Faixa de Idade'] = hist_data['Faixa de Idade'].round(1).astype(str)
    fig2 = px.bar(hist_data, x='Faixa de Idade', y='Frequência', template='plotly_white')
    fig2.update_layout(
        title={'text': '<b>Distribuição de Idade dos Condutores</b><br><sup>A maioria dos condutores envolvidos tem entre 20 e 40 anos</sup>', 'x': 0.5},
        xaxis_title='Idade (Agrupada)', yaxis_title='Frequência (Nº de Pessoas)', bargap=0.1
    )
    fig2.update_traces(hovertemplate='<b>Idade Aprox.</b>: %{x}<br><b>Nº de Pessoas</b>: %{y}<extra></extra>')
    fig2.write_html('dashboard/interactive_charts/histograma_idade.html')
    print("Gráfico 'histograma_idade.html' salvo.")

    # Gráfico 3: Proporção de Acidentes por Estado (Gráfico de Pizza)
    top_10_uf = acidentes_por_uf.head(10)
    outros_soma = acidentes_por_uf[10:].sum()
    pie_data = pd.concat([top_10_uf, pd.Series([outros_soma], index=['Outros'])])
    fig3 = px.pie(pie_data, values=pie_data.values, names=pie_data.index, template='plotly_white', hole=0.3)
    fig3.update_layout(
        title={'text': '<b>Proporção de Acidentes por Estado</b><br><sup>MG, PR e SC concentram a maior parte das ocorrências</sup>', 'x': 0.5}
    )
    fig3.update_traces(
        textposition='inside', textinfo='percent+label',
        hovertemplate='<b>Estado</b>: %{label}<br><b>Acidentes</b>: %{value}<br><b>Porcentagem</b>: %{percent}<extra></extra>'
    )
    fig3.write_html('dashboard/interactive_charts/proporcao_uf.html')
    print("Gráfico 'proporcao_uf.html' salvo.")

    # Gráfico 4: Total de Acidentes por Dia da Semana (Ordem Decrescente)
    acidentes_por_dia_desc = full_df['dia_semana'].value_counts()
    fig4 = px.bar(acidentes_por_dia_desc, x=acidentes_por_dia_desc.index, y=acidentes_por_dia_desc.values,
                  labels={'index': 'Dia da Semana', 'y': 'Número de Acidentes'},
                  template='plotly_white', text=acidentes_por_dia_desc.values)
    fig4.update_layout(
        title={'text': '<b>Total de Acidentes por Dia da Semana</b><br><sup>Fins de semana registram os maiores números de acidentes</sup>', 'x': 0.5},
        xaxis={'categoryorder': 'total descending'}
    )
    fig4.update_traces(
        texttemplate='%{text:.2s}', textposition='outside',
        hovertemplate='<b>Dia</b>: %{x}<br><b>Total de Acidentes</b>: %{y}<extra></extra>'
    )
    fig4.write_html('dashboard/interactive_charts/acidentes_por_dia.html')
    print("Gráfico 'acidentes_por_dia.html' salvo.")

    # --- NOVOS GRÁFICOS PARA ATIVIDADE ---
    print("\nGerando gráficos adicionais para a atividade...")
    df_sample = full_df.sample(n=5000, random_state=42)

    # Histograma: Ano de Fabricação do Veículo
    ano_filtrado = full_df[(full_df['ano_fabricacao_veiculo'] >= 1980) & (full_df['ano_fabricacao_veiculo'] <= 2025)]['ano_fabricacao_veiculo']
    fig_hist_ano = px.histogram(ano_filtrado, nbins=50, template='plotly_white')
    fig_hist_ano.update_layout(title={'text': '<b>Distribuição do Ano de Fabricação dos Veículos</b><br><sup>Picos em anos recentes indicam renovação da frota</sup>', 'x': 0.5}, xaxis_title='Ano de Fabricação', yaxis_title='Frequência')
    fig_hist_ano.write_html('dashboard/interactive_charts/hist_ano_veiculo.html')
    print("Gráfico 'hist_ano_veiculo.html' salvo.")

    # Pizza: Fase do Dia
    fase_dia_counts = full_df['fase_dia'].value_counts()
    fig_pie_fase_dia = px.pie(fase_dia_counts, values=fase_dia_counts.values, names=fase_dia_counts.index, template='plotly_white', hole=0.3)
    fig_pie_fase_dia.update_layout(title={'text': '<b>Proporção de Acidentes por Fase do Dia</b><br><sup>Maioria ocorre durante o dia</sup>', 'x': 0.5})
    fig_pie_fase_dia.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie_fase_dia.write_html('dashboard/interactive_charts/pie_fase_dia.html')
    print("Gráfico 'pie_fase_dia.html' salvo.")

    # Pizza: Condição Meteorológica
    condicao_counts = full_df['condicao_metereologica'].value_counts().head(5)
    fig_pie_condicao = px.pie(condicao_counts, values=condicao_counts.values, names=condicao_counts.index, template='plotly_white', hole=0.3)
    fig_pie_condicao.update_layout(title={'text': '<b>Condições Meteorológicas nos Acidentes (Top 5)</b><br><sup>Céu claro é a condição predominante</sup>', 'x': 0.5})
    fig_pie_condicao.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie_condicao.write_html('dashboard/interactive_charts/pie_condicao_meteo.html')
    print("Gráfico 'pie_condicao_meteo.html' salvo.")

    # Barras: Tipo de Pista
    pista_counts = full_df['tipo_pista'].value_counts()
    fig_bar_pista = px.bar(pista_counts, x=pista_counts.index, y=pista_counts.values, template='plotly_white', text=pista_counts.values)
    fig_bar_pista.update_layout(title={'text': '<b>Total de Acidentes por Tipo de Pista</b><br><sup>Pistas simples registram o maior número de acidentes</sup>', 'x': 0.5}, xaxis_title='Tipo de Pista', yaxis_title='Número de Acidentes')
    fig_bar_pista.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_bar_pista.write_html('dashboard/interactive_charts/bar_tipo_pista.html')
    print("Gráfico 'bar_tipo_pista.html' salvo.")

    # Dispersão: Idade vs. Ano de Fabricação
    fig_scatter_idade_ano = px.scatter(df_sample, x='idade', y='ano_fabricacao_veiculo', template='plotly_white', trendline='ols', trendline_color_override='red')
    fig_scatter_idade_ano.update_layout(title={'text': '<b>Relação entre Idade do Condutor e Ano do Veículo</b><br><sup>Leve tendência de condutores mais jovens terem carros mais novos</sup>', 'x': 0.5}, xaxis_title='Idade do Condutor', yaxis_title='Ano de Fabricação do Veículo')
    fig_scatter_idade_ano.write_html('dashboard/interactive_charts/scatter_idade_ano.html')
    print("Gráfico 'scatter_idade_ano.html' salvo.")

    # Dispersão: Idade vs. Total de Feridos
    fig_scatter_idade_feridos = px.scatter(df_sample, x='idade', y='total_feridos', template='plotly_white')
    fig_scatter_idade_feridos.update_layout(title={'text': '<b>Relação entre Idade do Condutor e Nº de Feridos</b><br><sup>Não há correlação clara visível</sup>', 'x': 0.5}, xaxis_title='Idade do Condutor', yaxis_title='Total de Feridos no Acidente')
    fig_scatter_idade_feridos.write_html('dashboard/interactive_charts/scatter_idade_feridos.html')
    print("Gráfico 'scatter_idade_feridos.html' salvo.")

    # --- ANÁLISE ESTATÍSTICA ADICIONAL ---
    print("\n--- Análise Estatística Descritiva ---")
    colunas_estatisticas = ['mortos', 'total_feridos', 'idade']
    for col in colunas_estatisticas:
        media = full_df[col].mean()
        mediana = full_df[col].median()
        desvio_padrao = full_df[col].std()
        print(f"\nEstatísticas para a coluna '{col}':")
        print(f"  - Média: {media:.4f}")
        print(f"  - Mediana: {mediana:.4f}")
        print(f"  - Desvio Padrão: {desvio_padrao:.4f}")
        if media > mediana:
            print("  - Comparação: A média é maior que a mediana, sugerindo assimetria à direita.")
        elif media < mediana:
            print("  - Comparação: A média é menor que a mediana, sugerindo assimetria à esquerda.")
        else:
            print("  - Comparação: Média e mediana próximas, sugerindo distribuição simétrica.")

if __name__ == "__main__":
    gerar_analises()
