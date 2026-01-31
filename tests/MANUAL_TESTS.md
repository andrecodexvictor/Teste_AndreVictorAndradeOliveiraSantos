# 📋 Plano de Testes Humanizados (Manuais)

> **Projeto:** Intuitive Care - API de Análise de Despesas ANS  
> **Data:** 2026-01-31  
> **Versão:** 1.0.0

---

## 🎯 Objetivo

Este documento descreve os **testes manuais** que complementam os testes automatizados, focando em:
- Experiência do usuário (UX)
- Fluxos de ponta a ponta
- Cenários de borda e edge cases
- Validação visual e comportamental

---

## 📋 Checklist de Pré-Requisitos

Antes de executar os testes manuais:

- [ ] Backend iniciado (`uvicorn src.main:app --reload`)
- [ ] MySQL rodando com dados de seed
- [ ] Frontend iniciado (`npm run dev` no diretório frontend/)
- [ ] Navegador com DevTools aberto (para inspecionar requests)

---

## 🧪 Cenários de Teste

### 1. Health Check e Disponibilidade

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| HC-01 | Health check básico | GET http://localhost:8000/health | JSON com status: "healthy" | ⬜ |
| HC-02 | Verificar versão | GET http://localhost:8000/health | Deve exibir version: "1.0.0" | ⬜ |
| HC-03 | Endpoint raiz | GET http://localhost:8000/ | JSON com mensagem e links | ⬜ |
| HC-04 | Documentação | GET http://localhost:8000/docs | Página HTML com endpoints | ⬜ |

---

### 2. Listagem de Operadoras

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| OP-01 | Lista padrão | GET /api/operadoras | Lista paginada (20 itens) | ⬜ |
| OP-02 | Paginação página 2 | GET /api/operadoras?page=2 | Itens diferentes da página 1 | ⬜ |
| OP-03 | Limite customizado | GET /api/operadoras?limit=5 | Exatamente 5 itens | ⬜ |
| OP-04 | Filtro razão social | GET /api/operadoras?razao_social=UNIMED | Apenas operadoras com "UNIMED" | ⬜ |
| OP-05 | Filtro CNPJ parcial | GET /api/operadoras?cnpj=114 | Operadoras com CNPJ iniciando em 114 | ⬜ |
| OP-06 | Filtro combinado | GET /api/operadoras?razao_social=UNIMED&uf=SP | Filtro combinado funciona | ⬜ |
| OP-07 | Página inexistente | GET /api/operadoras?page=999 | Lista vazia, total correto | ⬜ |
| OP-08 | Limite máximo | GET /api/operadoras?limit=500 | Erro 422 (limite max=100) | ⬜ |

---

### 3. Detalhes de Operadora

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| OD-01 | Operadora existente | GET /api/operadoras/{cnpj_valido} | Detalhes com total_despesas | ⬜ |
| OD-02 | Operadora inexistente | GET /api/operadoras/99999999999999 | Erro 404 com mensagem | ⬜ |
| OD-03 | CNPJ mal formatado | GET /api/operadoras/abc | Erro 404 (não encontrada) | ⬜ |
| OD-04 | Operadora sem despesas | Encontrar operadora sem dados financeiros | total_despesas = 0 | ⬜ |

---

### 4. Histórico de Despesas

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| DE-01 | Todas despesas | GET /api/operadoras/{cnpj}/despesas | Lista de despesas ordenada | ⬜ |
| DE-02 | Filtro por ano | GET /api/operadoras/{cnpj}/despesas?ano=2024 | Apenas despesas de 2024 | ⬜ |
| DE-03 | Filtro por trimestre | GET /api/operadoras/{cnpj}/despesas?trimestre=1 | Apenas Q1 | ⬜ |
| DE-04 | Trimestre inválido | GET /api/operadoras/{cnpj}/despesas?trimestre=5 | Erro 422 | ⬜ |
| DE-05 | Operadora inexistente | GET /api/operadoras/00000/despesas | Erro 404 | ⬜ |

---

### 5. Estatísticas

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| ES-01 | Estatísticas gerais | GET /api/estatisticas | Total, média, top 5 | ⬜ |
| ES-02 | Cache funcionando | GET /api/estatisticas 2x rápido | Segunda resposta mais rápida | ⬜ |
| ES-03 | Distribuição UF | GET /api/estatisticas/distribuicao-uf | Lista de UFs com totais | ⬜ |
| ES-04 | Top 5 ordenado | Verificar top_5_operadoras | Ordenado do maior para menor | ⬜ |

---

### 6. Segurança

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| SE-01 | Headers presentes | Inspecionar qualquer resposta | X-Frame-Options: DENY | ⬜ |
| SE-02 | CORS localhost | Request de localhost:5173 | Resposta permitida | ⬜ |
| SE-03 | CORS bloqueado | Request de origem não autorizada | Sem Access-Control-Allow-Origin | ⬜ |
| SE-04 | SQL Injection | Tentar CNPJ: "'; DROP TABLE--" | Erro 404 (não executar SQL) | ⬜ |
| SE-05 | XSS no filtro | razao_social=<script>alert(1)</script> | Não executar script | ⬜ |
| SE-06 | Rate limit | 150 requests em 1 minuto | Erro 429 após limite | ⬜ |

---

### 7. Frontend Integration

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| FE-01 | Carregar lista | Acessar página inicial | Tabela com operadoras | ⬜ |
| FE-02 | Paginação visual | Clicar em "Próxima página" | Novos dados carregados | ⬜ |
| FE-03 | Busca por nome | Digitar no campo de busca | Filtro aplicado em tempo real | ⬜ |
| FE-04 | Ver detalhes | Clicar em uma operadora | Modal/página com detalhes | ⬜ |
| FE-05 | Gráfico de UF | Navegar para estatísticas | Gráfico de pizza/barra | ⬜ |
| FE-06 | Responsividade | Redimensionar janela | Layout adapta corretamente | ⬜ |
| FE-07 | Loading state | Requisição lenta (throttle) | Indicador de carregamento | ⬜ |
| FE-08 | Erro de rede | Desligar backend | Mensagem de erro amigável | ⬜ |

---

### 8. Performance

| ID | Cenário | Passos | Resultado Esperado | Status |
|----|---------|--------|-------------------|--------|
| PF-01 | Tempo de resposta lista | GET /api/operadoras | < 500ms | ⬜ |
| PF-02 | Tempo estatísticas | GET /api/estatisticas | < 1s (sem cache) | ⬜ |
| PF-03 | Tempo estatísticas cache | GET /api/estatisticas (2ª vez) | < 100ms | ⬜ |
| PF-04 | Carga de 50 usuários | Usar ferramenta de load test | Sem degradação significativa | ⬜ |

---

## 🔍 Procedimento de Teste

### Como executar:

1. **Iniciar ambiente:**
   ```bash
   # Terminal 1 - Backend
   cd c:\Users\adm\Desktop\estagio
   uvicorn src.main:app --reload --port 8000
   
   # Terminal 2 - Frontend
   cd c:\Users\adm\Desktop\estagio\frontend
   npm run dev
   ```

2. **Testar endpoints:**
   - Use Postman, Insomnia ou curl
   - Collection disponível em: `docs/Postman_Collection.json`

3. **Registrar resultados:**
   - ✅ = Passou
   - ❌ = Falhou (descrever problema)
   - ⬜ = Não testado
   - ⚠️ = Passou com ressalvas

---

## 📝 Template de Registro de Bug

```markdown
## Bug Report

**ID do Teste:** [ex: OP-04]
**Severidade:** [Crítico/Alto/Médio/Baixo]
**Reproduzível:** [Sempre/Às vezes/Raramente]

**Passos para reproduzir:**
1. 
2. 
3. 

**Resultado esperado:**

**Resultado obtido:**

**Screenshots/Logs:**

**Ambiente:**
- Browser:
- Backend version:
- Data/Hora:
```

---

## 📊 Critérios de Aceitação

| Categoria | Critério | Mínimo |
|-----------|----------|--------|
| Funcionalidade | Testes passando | 95% |
| Segurança | Testes passando | 100% |
| Performance | Tempo resposta | < 1s |
| UX | Fluxos completos | 100% |

---

## 📅 Histórico de Execução

| Data | Executor | Testes | Passou | Falhou | Notas |
|------|----------|--------|--------|--------|-------|
| 2026-01-31 | - | - | - | - | Template criado |

---

## 📚 Referências

- [Postman Collection](../docs/Postman_Collection.json)
- [API Docs](http://localhost:8000/docs)
- [README](../README.md)
