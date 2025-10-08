async function fetchJSON(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`Falha ao carregar ${path}`);
    return res.json();
}

function makeBarChart(ctx, labels, data, title, horizontal=false) {
    return new Chart(ctx, {
        type: horizontal ? 'bar' : 'bar',
        data: { labels, datasets: [{ label: title, data, backgroundColor: '#4f46e5' }] },
        options: {
            indexAxis: horizontal ? 'y' : 'x',
            responsive: true,
            plugins: { legend: { display: false }, tooltip: { enabled: true }, title: { display: true, text: title } },
            scales: { x: { ticks: { maxRotation: 0 } }, y: { beginAtZero: true } }
        }
    });
}

function makePieChart(ctx, labels, data, title) {
    const palette = ['#4f46e5','#22c55e','#ef4444','#06b6d4','#f59e0b','#8b5cf6','#10b981','#f43f5e','#0ea5e9','#84cc16'];
    return new Chart(ctx, {
        type: 'doughnut',
        data: { labels, datasets: [{ data, backgroundColor: palette.slice(0, labels.length) }] },
        options: { responsive: true, plugins: { legend: { position: 'bottom' }, title: { display: true, text: title } } }
    });
}

function makeLineChart(ctx, labels, data, title) {
    return new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: [{ label: title, data, borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.2)', fill: true }] },
        options: { responsive: true, plugins: { legend: { display: false }, title: { display: true, text: title } }, scales: { y: { beginAtZero: true } } }
    });
}

function makeScatterChart(ctx, points, title) {
    return new Chart(ctx, {
        type: 'scatter',
        data: { datasets: [{ label: title, data: points, backgroundColor: '#0ea5e9' }] },
        options: { responsive: true, plugins: { legend: { display: false }, title: { display: true, text: title } } }
    });
}

async function init() {
    try {
        const base = 'data';
        const [causas, dia, pista, histIdade, histAno, uf, fase, meteo, sIdAno, sIdFer, sFerMor, sAnoFer] = await Promise.all([
            fetchJSON(`${base}/top_10_causas.json`).catch(()=>null),
            fetchJSON(`${base}/acidentes_por_dia_semana.json`).catch(()=>null),
            fetchJSON(`${base}/tipo_pista.json`).catch(()=>null),
            fetchJSON(`${base}/hist_idade.json`).catch(()=>null),
            fetchJSON(`${base}/hist_ano_veiculo.json`).catch(()=>null),
            fetchJSON(`${base}/proporcao_uf.json`).catch(()=>null),
            fetchJSON(`${base}/fase_dia.json`).catch(()=>null),
            fetchJSON(`${base}/condicao_meteo.json`).catch(()=>null),
            fetchJSON(`${base}/scatter_idade_ano.json`).catch(()=>null),
            fetchJSON(`${base}/scatter_idade_feridos.json`).catch(()=>null),
            fetchJSON(`${base}/scatter_feridos_mortos.json`).catch(()=>null),
            fetchJSON(`${base}/scatter_ano_feridos.json`).catch(()=>null),
        ]);

        if (causas) makeBarChart(document.getElementById('chart_top_10_causas'), causas.labels, causas.data, 'Top 10 Causas (2024-2025)', true);
        if (dia) makeBarChart(document.getElementById('chart_acidentes_dia'), dia.labels, dia.data, 'Acidentes por Dia da Semana');
        if (pista) makeBarChart(document.getElementById('chart_tipo_pista'), pista.labels, pista.data, 'Acidentes por Tipo de Pista');

        if (histIdade) makeLineChart(document.getElementById('chart_hist_idade'), histIdade.bins, histIdade.counts, 'Distribuição de Idade');
        if (histAno) makeLineChart(document.getElementById('chart_hist_ano'), histAno.bins, histAno.counts, 'Ano de Fabricação do Veículo');

        if (uf) makePieChart(document.getElementById('chart_proporcao_uf'), uf.labels, uf.data, 'Proporção por UF');
        if (fase) makePieChart(document.getElementById('chart_fase_dia'), fase.labels, fase.data, 'Fase do Dia');
        if (meteo) makePieChart(document.getElementById('chart_condicao_meteo'), meteo.labels, meteo.data, 'Condição Meteorológica');

        if (sIdAno) makeScatterChart(document.getElementById('chart_scatter_idade_ano'), sIdAno.points, 'Idade x Ano do Veículo');
        if (sIdFer) makeScatterChart(document.getElementById('chart_scatter_idade_feridos'), sIdFer.points, 'Idade x Total de Feridos');
        if (sFerMor) makeScatterChart(document.getElementById('chart_scatter_feridos_mortos'), sFerMor.points, 'Feridos x Mortos');
        if (sAnoFer) makeScatterChart(document.getElementById('chart_scatter_ano_feridos'), sAnoFer.points, 'Ano do Veículo x Feridos');
    } catch (e) {
        console.error(e);
    }
}

document.addEventListener('DOMContentLoaded', init);


