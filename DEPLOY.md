# 🚀 Deploy no Vercel - Instruções

## Opção 1: Deploy via Interface Web (Recomendado)

### Passo 1: Preparar o Repositório
1. Crie um repositório no GitHub com todos os arquivos do projeto
2. Certifique-se de que os arquivos estão organizados:
   ```
   ├── dashboard/
   │   ├── index.html
   │   ├── app.js
   │   ├── style.css
   │   └── data/ (com todos os JSONs)
   ├── vercel.json
   ├── package.json
   └── README.md
   ```

### Passo 2: Deploy no Vercel
1. Acesse [vercel.com](https://vercel.com)
2. Faça login com sua conta GitHub
3. Clique em "New Project"
4. Importe seu repositório GitHub
5. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `./` (raiz do projeto)
   - **Build Command:** `python 01_preparar_dados.py && python 02_gerar_analises.py`
   - **Output Directory:** `dashboard`

### Passo 3: Configurações Avançadas
No arquivo `vercel.json` já está configurado:
- Rotas para servir arquivos estáticos
- Redirecionamento para `dashboard/index.html`
- Acesso aos dados em `/data/`

## Opção 2: Deploy via CLI (se tiver Node.js)

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

## ⚠️ Importante

1. **Dados:** Os CSVs de 2024-2025 devem estar na raiz do projeto
2. **Python:** O Vercel suporta Python, mas os dados precisam ser processados localmente
3. **Build:** Execute `python 01_preparar_dados.py && python 02_gerar_analises.py` antes do deploy
4. **Arquivos:** Certifique-se de que `dashboard/data/` contém todos os JSONs

## 🔧 Troubleshooting

- **Erro 404:** Verifique se os JSONs estão em `dashboard/data/`
- **Gráficos não carregam:** Verifique o console do navegador
- **Dados vazios:** Execute os scripts Python localmente primeiro

## 📱 Acesso

Após o deploy, o dashboard estará disponível em:
`https://seu-projeto.vercel.app`
