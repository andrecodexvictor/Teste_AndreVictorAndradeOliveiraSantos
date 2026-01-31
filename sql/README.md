# 🗄️ SQL - Schema e Queries

> Definição do banco de dados e queries analíticas para o sistema de despesas ANS

---

## 📋 Visão Geral

Este diretório contém:

- **schema.sql** — DDL (Data Definition Language) com criação de tabelas e índices
- **queries.sql** — 3 queries analíticas conforme requisitos do teste

---

## 📁 Arquivos

### schema.sql

Define a estrutura do banco de dados:

```sql
-- Tabela de Operadoras (cadastro ANS)
CREATE TABLE operadoras (
    cnpj VARCHAR(14) PRIMARY KEY,
    razao_social VARCHAR(255) NOT NULL,
    registro_ans VARCHAR(10),
    modalidade VARCHAR(50),
    uf VARCHAR(2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_razao_social (razao_social),
    INDEX idx_uf (uf),
    INDEX idx_modalidade (modalidade)
);

-- Tabela de Despesas Financeiras (demonstrações contábeis)
CREATE TABLE despesas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cnpj VARCHAR(14) NOT NULL,
    razao_social VARCHAR(255),
    ano INT NOT NULL,
    trimestre INT NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    descricao VARCHAR(255),
    valor DECIMAL(15,2) NOT NULL,
    status_qualidade VARCHAR(20) DEFAULT 'OK',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cnpj) REFERENCES operadoras(cnpj) ON DELETE CASCADE,
    INDEX idx_cnpj (cnpj),
    INDEX idx_ano_trimestre (ano, trimestre),
    INDEX idx_valor (valor DESC)
);
```

### queries.sql

Contém as 3 queries analíticas requeridas:

---

## 📊 Query 1: Top 10 Operadoras com Maiores Despesas

```sql
-- Top 10 operadoras com maiores despesas totais
SELECT 
    o.cnpj,
    o.razao_social,
    o.modalidade,
    o.uf,
    SUM(d.valor) AS total_despesas,
    COUNT(DISTINCT CONCAT(d.ano, '-', d.trimestre)) AS trimestres_ativos
FROM operadoras o
INNER JOIN despesas d ON o.cnpj = d.cnpj
WHERE d.status_qualidade = 'OK'
GROUP BY o.cnpj, o.razao_social, o.modalidade, o.uf
ORDER BY total_despesas DESC
LIMIT 10;
```

**Uso:** Dashboard principal, ranking de operadoras

---

## 📊 Query 2: Top 10 por Trimestre Específico

```sql
-- Top 10 operadoras em um trimestre específico
SELECT 
    o.cnpj,
    o.razao_social,
    d.ano,
    d.trimestre,
    SUM(d.valor) AS despesa_trimestre
FROM operadoras o
INNER JOIN despesas d ON o.cnpj = d.cnpj
WHERE d.ano = :ano 
  AND d.trimestre = :trimestre
  AND d.status_qualidade = 'OK'
GROUP BY o.cnpj, o.razao_social, d.ano, d.trimestre
ORDER BY despesa_trimestre DESC
LIMIT 10;
```

**Uso:** Análise temporal, filtro por período

---

## 📊 Query 3: Agregação por UF

```sql
-- Distribuição de despesas por UF
SELECT 
    o.uf,
    COUNT(DISTINCT o.cnpj) AS total_operadoras,
    SUM(d.valor) AS total_despesas,
    AVG(d.valor) AS media_despesa,
    MIN(d.valor) AS menor_despesa,
    MAX(d.valor) AS maior_despesa
FROM operadoras o
INNER JOIN despesas d ON o.cnpj = d.cnpj
WHERE d.status_qualidade = 'OK'
  AND o.uf IS NOT NULL
GROUP BY o.uf
ORDER BY total_despesas DESC;
```

**Uso:** Dashboard geográfico, mapa de calor

---

## 🔧 Índices e Performance

### Índices Criados

| Tabela | Índice | Colunas | Justificativa |
|--------|--------|---------|---------------|
| operadoras | PRIMARY | cnpj | Busca direta por CNPJ |
| operadoras | idx_razao_social | razao_social | Filtro de busca por nome |
| operadoras | idx_uf | uf | Agregação geográfica |
| despesas | idx_cnpj | cnpj | JOIN com operadoras |
| despesas | idx_ano_trimestre | ano, trimestre | Filtro temporal |
| despesas | idx_valor | valor DESC | Ordenação por ranking |

### Trade-offs

| Decisão | Benefício | Custo |
|---------|-----------|-------|
| Índice em valor DESC | Queries de ranking rápidas | Escrita mais lenta |
| FK com CASCADE | Integridade referencial | Deleções em cascata |
| VARCHAR(14) para CNPJ | Simplicidade | Sem leading zeros auto |

---

## 🐳 Docker - Inicialização

O banco é inicializado automaticamente pelo Docker Compose:

```yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: intuitive_care
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./sql/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
```

---

## 💡 Uso Manual

### Criar banco

```bash
mysql -u root -p -e "CREATE DATABASE intuitive_care CHARACTER SET utf8mb4;"
```

### Aplicar schema

```bash
mysql -u root -p intuitive_care < sql/schema.sql
```

### Executar queries

```bash
mysql -u root -p intuitive_care < sql/queries.sql
```

---

*Última atualização: Janeiro 2026*
