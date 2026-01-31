# 🎨 Frontend - Dashboard Vue.js 3

> Dashboard interativo para visualização de despesas de operadoras de saúde

---

## 📋 Visão Geral

Este frontend foi desenvolvido com **Vue.js 3** usando a **Composition API** e **Vite** como bundler, oferecendo:

- 🔍 **Busca de Operadoras** — Filtro por razão social, CNPJ, UF
- 📊 **Dashboard de Estatísticas** — Cards com métricas + gráficos
- 📋 **Tabela Paginada** — Listagem com ordenação
- 📱 **Responsividade** — Layout adaptável para desktop e mobile

---

## 🚀 Início Rápido

### Pré-requisitos

- **Node.js 18+** (recomendado: 20 LTS)
- **npm** ou **yarn**
- **API Backend** rodando em `http://localhost:8000`

### Instalação

```bash
cd frontend
npm install
```

### Desenvolvimento

```bash
npm run dev
# Acesse: http://localhost:5173
```

### Build de Produção

```bash
npm run build
# Arquivos gerados em: dist/
```

### Preview do Build

```bash
npm run preview
```

---

## 📁 Estrutura de Arquivos

```
frontend/
├── public/               # Arquivos estáticos
├── src/
│   ├── assets/           # CSS, imagens
│   ├── components/       # Componentes Vue
│   │   ├── SearchForm.vue      # Formulário de busca
│   │   ├── OperadorasTable.vue # Tabela de resultados
│   │   ├── StatsCards.vue      # Cards de estatísticas
│   │   └── ...
│   ├── services/         # Chamadas à API
│   │   └── api.js        # Axios configurado
│   ├── App.vue           # Componente raiz
│   ├── main.js           # Ponto de entrada
│   └── style.css         # Estilos globais
├── index.html            # Template HTML
├── package.json          # Dependências
└── vite.config.js        # Configuração Vite
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env.local` na pasta `frontend/`:

```env
# URL da API Backend
VITE_API_URL=http://localhost:8000

# Modo de desenvolvimento
VITE_DEBUG=true
```

### Proxy para API (vite.config.js)

```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
```

> **Nota:** Usamos `127.0.0.1` ao invés de `localhost` para evitar problemas de resolução DNS no Windows.

---

## 🧩 Componentes Principais

### SearchForm.vue
Formulário de busca com campos:
- Razão Social (texto)
- CNPJ (texto com máscara)
- UF (dropdown)

### OperadorasTable.vue
Tabela paginada com:
- Ordenação por coluna
- Navegação de páginas
- Link para detalhes

### StatsCards.vue
Cards com métricas:
- Total de operadoras
- Valor total de despesas
- Média por operadora
- Top 5 operadoras

### Charts.vue
Gráficos usando Chart.js:
- Distribuição por UF (pizza)
- Evolução trimestral (linha)
- Top 10 por despesa (barra)

---

## 🔗 Integração com API

### Serviço de API (services/api.js)

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const operadorasService = {
  listar: (params) => api.get('/api/operadoras', { params }),
  obter: (cnpj) => api.get(`/api/operadoras/${cnpj}`),
  despesas: (cnpj) => api.get(`/api/operadoras/${cnpj}/despesas`)
}

export const estatisticasService = {
  obter: () => api.get('/api/estatisticas'),
  distribuicaoUF: () => api.get('/api/estatisticas/distribuicao-uf')
}
```

---

## 🎨 Estilos

### CSS Variables

```css
:root {
  --color-primary: #4A90D9;
  --color-secondary: #6C757D;
  --color-success: #28A745;
  --color-danger: #DC3545;
  --color-warning: #FFC107;
  
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --border-radius: 8px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
}
```

### Responsividade

- **Desktop (>1024px)**: Layout em grid 3 colunas
- **Tablet (768-1024px)**: Layout em grid 2 colunas
- **Mobile (<768px)**: Layout em coluna única

---

## 🐳 Docker

### Build da Imagem

```bash
docker build -f docker/frontend/Dockerfile -t intuitive-frontend .
```

### Configuração Nginx

O arquivo `docker/frontend/nginx.conf` configura:
- Proxy reverso para API
- Compressão gzip
- Cache de assets estáticos
- SPA fallback (history mode)

---

## 🧪 Testes

### Testes Unitários (Vitest)

```bash
npm run test
```

### Testes E2E (Playwright) — Futuro

```bash
npm run test:e2e
```

---

## 📦 Dependências Principais

| Pacote | Versão | Uso |
|--------|--------|-----|
| vue | ^3.4 | Framework principal |
| vite | ^5.0 | Bundler/Dev Server |
| axios | ^1.6 | Cliente HTTP |
| chart.js | ^4.4 | Gráficos |
| vue-chartjs | ^5.3 | Wrapper Vue para Chart.js |

---

## 🔧 Scripts Disponíveis

| Comando | Descrição |
|---------|-----------|
| `npm run dev` | Servidor de desenvolvimento |
| `npm run build` | Build de produção |
| `npm run preview` | Preview do build |
| `npm run lint` | Verificação de código |

---

## ⚠️ Troubleshooting

### Erro de CORS

Se encontrar erros de CORS:

1. Verifique se a API está rodando
2. Confirme a URL em `VITE_API_URL`
3. Use o proxy do Vite em desenvolvimento

### Conexão recusada

No Windows, use `127.0.0.1` ao invés de `localhost`:

```javascript
// ✅ Correto
baseURL: 'http://127.0.0.1:8000'

// ❌ Pode falhar no Windows
baseURL: 'http://localhost:8000'
```

---

*Última atualização: Janeiro 2026*
