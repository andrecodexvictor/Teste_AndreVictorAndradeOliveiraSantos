-- =============================================================
-- migration_add_indexes.sql - Índices para Otimização de Performance
-- =============================================================
-- BASEADO EM: sql-pro, sql-optimization-patterns, database-optimizer skills
--
-- PROBLEMA: Queries levando ~100 segundos com 2M registros
-- SOLUÇÃO: Índices compostos e covering indexes
--
-- EXECUÇÃO:
-- docker exec -i intuitive_care_mysql mysql -uroot -padm@123 intuitive_care_test < sql/migration_add_indexes.sql
-- =============================================================

USE intuitive_care_test;

-- =============================================================
-- ÍNDICE 1: Composto para JOIN despesas + operadoras
-- =============================================================
-- JUSTIFICATIVA: Todas as queries analíticas fazem JOIN via CNPJ
-- Este índice acelera o JOIN e permite filtro por valor
-- =============================================================
CREATE INDEX IF NOT EXISTS idx_despesas_cnpj_valor 
ON despesas(cnpj, valor);

-- =============================================================
-- ÍNDICE 2: Covering Index para Estatísticas
-- =============================================================
-- JUSTIFICATIVA: Permite "Index Only Scan" - lê apenas índice
-- Evita acesso à tabela para queries de SUM/AVG/COUNT
-- Pode acelerar 10-50x
-- =============================================================
CREATE INDEX IF NOT EXISTS idx_despesas_covering_stats 
ON despesas(cnpj, ano, trimestre, valor);

-- =============================================================
-- ÍNDICE 3: Composto para agregação por UF
-- =============================================================
-- JUSTIFICATIVA: Query distribuição por UF usa GROUP BY uf
-- Índice no uf + cnpj acelera o JOIN e GROUP BY
-- =============================================================
CREATE INDEX IF NOT EXISTS idx_operadoras_uf_cnpj 
ON operadoras(uf, cnpj);

-- =============================================================
-- ÍNDICE 4: Índice no valor para ordenação DESC
-- =============================================================
-- JUSTIFICATIVA: Top 5 operadoras ordena por SUM(valor) DESC
-- Índice no valor ajuda na ordenação
-- =============================================================
CREATE INDEX IF NOT EXISTS idx_despesas_valor 
ON despesas(valor DESC);

-- =============================================================
-- ATUALIZAR ESTATÍSTICAS DO OTIMIZADOR
-- =============================================================
-- IMPORTANTE: Necessário após criar índices para otimizador usar
-- =============================================================
ANALYZE TABLE operadoras;
ANALYZE TABLE despesas;
ANALYZE TABLE despesas_agregadas;

-- =============================================================
-- VERIFICAR ÍNDICES CRIADOS
-- =============================================================
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    CARDINALITY
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'intuitive_care_test'
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
