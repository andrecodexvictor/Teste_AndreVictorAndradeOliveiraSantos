# =============================================================
# run_etl.py - Executa Pipeline ETL com Dados Reais da ANS
# =============================================================
"""
Script para baixar e processar dados reais da ANS.

FONTES:
- Operadoras: https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/
- Despesas: https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/

EXECUÇÃO:
    python run_etl.py

OPÇÕES:
    --trimestres N   Número de trimestres para baixar (padrão: 2)
    --skip-download  Pular download se arquivos já existem
"""

import sys
import os
import argparse
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from loguru import logger
from sqlalchemy import text
from src.etl.downloader import ANSDownloader
from src.etl.processor import DataProcessor
from src.infrastructure.database.connection import SessionLocal, engine
from src.infrastructure.database.models import OperadoraORM, DespesaORM, DespesaAgregadaORM, Base


def carregar_mapa_registro_cnpj(session):
    """Carrega mapa de Registro ANS -> CNPJ."""
    logger.info("🗺️ Carregando mapa de operadoras...")
    ops = session.query(OperadoraORM.registro_ans, OperadoraORM.cnpj).filter(OperadoraORM.registro_ans.isnot(None)).all()
    # Cria dict normalizando registro ans (strip)
    return {str(o.registro_ans).strip(): o.cnpj for o in ops}


import re

def limpar_cnpj(cnpj):
    """Remove caracteres não numéricos do CNPJ e faz padding."""
    if not cnpj:
        return ""
    # Remove tudo que não é dígito
    clean = re.sub(r'\D', '', str(cnpj))
    return clean.zfill(14)

def carregar_operadoras_no_banco(df_operadoras, session):
    """Carrega operadoras no banco de dados."""
    logger.info("💾 Carregando operadoras no banco...")
    
    count = 0
    total_rows = len(df_operadoras)
    
    for _, row in df_operadoras.iterrows():
        try:
            # Limpa CNPJ
            cnpj_raw = row.get('CNPJ', '')
            cnpj = limpar_cnpj(cnpj_raw)
            
            if not cnpj or len(cnpj) != 14:
                # logger.warning(f"CNPJ inválido ignorado: {cnpj_raw}")
                continue

            # Busca Registro ANS em várias colunas possíveis
            # O arquivo atual parece usar 'REGISTRO_OPERADORA'
            reg_ans = row.get('REGISTRO_ANS') or row.get('Registro_ANS') or row.get('REGISTRO_OPERADORA') or row.get('Registro_Operadora')
            
            operadora = OperadoraORM(
                cnpj=cnpj,
                razao_social=str(row.get('RAZAO_SOCIAL', row.get('Razao_Social', '')))[:255],
                registro_ans=str(reg_ans)[:10] if reg_ans else None,
                modalidade=str(row.get('MODALIDADE', row.get('Modalidade', '')))[:50] if row.get('MODALIDADE') or row.get('Modalidade') else None,
                uf=str(row.get('UF', ''))[:2] if row.get('UF') else None,
            )
            session.add(operadora)
            count += 1
            
            if count % 1000 == 0:
                session.commit()
                logger.info(f"   {count}/{total_rows} operadoras inseridas...")
                
        except Exception as e:
            logger.warning(f"   ⚠️ Erro ao inserir operadora: {e}")
            continue
    
    session.commit()
    logger.info(f"   ✅ {count} novas operadoras inseridas")
    return count


import math

def carregar_despesas_no_banco(df_despesas, session, mapa_reg_cnpj):
    """Carrega despesas no banco de dados com lookup de CNPJ e Bulk Insert."""
    logger.info("💾 Carregando despesas no banco (Bulk Insert)...")
    
    # Cria set de CNPJs válidos para verificação rápida
    cnpjs_validos = set(mapa_reg_cnpj.values())
    
    batch_size = 10000
    batch = []
    total_inserted = 0
    skipped = 0
    
    # Pre-cálculo para lookup mais rápido
    # (Nada complexo, mantemos a lógica por linha pois o lookup é fuzzy)
    
    # itertuples é mais rápido que iterrows
    # colunas: Index, CNPJ, RAZAO_SOCIAL, VALOR, ANO, TRIMESTRE, STATUS (nomes normalizados pelo processor)
    # Mas nomes das colunas dependem do DF. Vamos checar colunas.
    # O processor normaliza para: CNPJ, RAZAO_SOCIAL, VALOR, ANO, TRIMESTRE, STATUS (opcional)
    
    # Vamos usar to_dict('records') para iteração mais simples se memória permitir (700k rows ~ 100MB ok)
    records = df_despesas.to_dict('records')
    total_records = len(records)
    
    logger.info(f"   Preparando {total_records} registros para inserção...")
    
    for row in records:
        try:
            # Resolve CNPJ
            reg_ans_or_cnpj = str(row.get('CNPJ', '')).strip()
            clean_val = limpar_cnpj(reg_ans_or_cnpj)
            
            cnpj = None
            
            # 1. Verifica CNPJ válido
            if clean_val in cnpjs_validos:
                cnpj = clean_val
            else:
                # 2. Lookup de Registro ANS
                term = reg_ans_or_cnpj.lstrip('0')
                term_clean = clean_val.lstrip('0')
                candidates = [term, term_clean, reg_ans_or_cnpj, clean_val]
                
                for cand in candidates:
                    if cand in mapa_reg_cnpj:
                        cnpj = mapa_reg_cnpj[cand]
                        break
            
            if not cnpj:
                skipped += 1
                continue
                
            # Sanitiza valor
            val = row.get('VALOR', 0)
            try:
                val_float = float(val)
                if math.isnan(val_float) or math.isinf(val_float):
                    val_float = 0.0
            except (ValueError, TypeError):
                val_float = 0.0
            
            # Adiciona ao batch
            batch.append({
                'cnpj': cnpj,
                'razao_social': str(row.get('RAZAO_SOCIAL', ''))[:255],
                'ano': int(row.get('ANO', 0)),
                'trimestre': int(row.get('TRIMESTRE', 0)),
                'valor': val_float,
                'status_qualidade': str(row.get('STATUS', 'OK'))[:20]
            })
            
            if len(batch) >= batch_size:
                session.bulk_insert_mappings(DespesaORM, batch)
                session.commit()
                total_inserted += len(batch)
                logger.info(f"   ⚡ {total_inserted}/{total_records} despesas inseridas...")
                batch = []
                
        except Exception as e:
            # Em bulk, um erro na construção falha o loop? Não, try/except protege construção.
            # Erro no bulk_insert falha o batch inteiro.
            # Assumimos dados limpos o suficiente.
            logger.warning(f"   ⚠️ Erro ao preparar registro: {e}")
            continue
    
    # Insere remanescentes
    if batch:
        session.bulk_insert_mappings(DespesaORM, batch)
        session.commit()
        total_inserted += len(batch)
    
    logger.info(f"   ✅ Total inserido: {total_inserted} (Ignorados: {skipped})")
    return total_inserted


def main():
    parser = argparse.ArgumentParser(description='ETL - Dados da ANS')
    parser.add_argument('--trimestres', type=int, default=2, help='Número de trimestres')
    parser.add_argument('--skip-download', action='store_true', help='Pular download')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏥 ETL - Dados da ANS para Banco de Dados")
    print("=" * 60)
    
    # Inicializa componentes
    downloader = ANSDownloader()
    processor = DataProcessor()
    session = SessionLocal()
    
    # Cria tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    try:
        # =========================================================
        # ETAPA 0: Limpeza do Banco
        # =========================================================
        logger.info("🧹 Limpando banco de dados antigo...")
        
        # Desabilita verificação de chave estrangeira para limpar tudo
        session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        
        # Limpa tabelas na ordem
        session.execute(text("TRUNCATE TABLE despesas_agregadas"))
        try:
            session.execute(text("TRUNCATE TABLE despesas"))
        except:
             pass # Tabela pode nao existir
        try:
            session.execute(text("TRUNCATE TABLE operadoras"))
        except:
             pass
        
        session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        session.commit()
        logger.info("✅ Banco limpo com sucesso")

        # =========================================================
        # ETAPA 1: Baixar e carregar operadoras ativas
        # =========================================================
        print("\n📥 ETAPA 1: Operadoras Ativas")
        print("-" * 40)
        
        arquivo_operadoras = downloader.baixar_operadoras_ativas()
        
        if arquivo_operadoras and arquivo_operadoras.exists():
            logger.info(f"📄 Arquivo: {arquivo_operadoras}")
            
            # Processa arquivo
            df_operadoras = processor.read_file(arquivo_operadoras)
            logger.info(f"   Colunas encontradas: {df_operadoras.columns.tolist()}")
            
            # Normaliza (opcional, ou ajuste manual)
            # Vamos garantir que temos as colunas certas
            # Mapeamento ad-hoc se necessário
            
            logger.info(f"   Linhas lidas: {len(df_operadoras)}")
            
            # Carrega no banco
            carregar_operadoras_no_banco(df_operadoras, session)
        else:
            logger.warning("⚠️ Não foi possível baixar operadoras")
            
        
        # Carrega mapa de CNPJs
        mapa_cnpj = carregar_mapa_registro_cnpj(session)
        logger.info(f"   Mapa carregado: {len(mapa_cnpj)} operadoras")
        
        # =========================================================
        # ETAPA 2: Baixar e carregar demonstrações contábeis
        # =========================================================
        print("\n📥 ETAPA 2: Demonstrações Contábeis")
        print("-" * 40)
        
        # Obtém últimos trimestres
        trimestres = downloader.get_ultimos_trimestres(args.trimestres)
        logger.info(f"📅 Trimestres a processar: {trimestres}")
        
        total_despesas = 0
        
        for ano, trimestre in trimestres:
            logger.info(f"\n📦 Processando {trimestre}T{ano}...")
            
            # Baixa arquivo
            arquivo_zip = downloader.baixar_demonstracoes_contabeis(ano, trimestre)
            
            if arquivo_zip and arquivo_zip.exists():
                # Extrai ZIP
                arquivos_extraidos = downloader.extrair_zip(arquivo_zip)
                
                for arquivo in arquivos_extraidos:
                    if arquivo.suffix.lower() in ['.csv', '.txt']:
                        logger.info(f"   📄 Processando: {arquivo.name}")
                        
                        try:
                            # Lê arquivo
                            df = processor.read_file(arquivo)
                            
                            if df.empty:
                                continue
                            
                            # Normaliza colunas
                            df = processor.normalize_columns(df)
                            
                            # Adiciona ano e trimestre se não existir
                            if 'ANO' not in df.columns:
                                df['ANO'] = ano
                            if 'TRIMESTRE' not in df.columns:
                                df['TRIMESTRE'] = trimestre
                            
                            # Filtra apenas despesas
                            df_despesas = processor.filter_despesas(df)
                            
                            if not df_despesas.empty:
                                # Valida dados
                                df_despesas = processor.validate_dataframe(df_despesas)
                                
                                # Carrega no banco
                                count = carregar_despesas_no_banco(df_despesas, session, mapa_cnpj)
                                total_despesas += count
                                
                        except Exception as e:
                            logger.warning(f"   ⚠️ Erro ao processar {arquivo.name}: {e}")
                            continue
            else:
                logger.warning(f"   ⚠️ Não foi possível baixar {trimestre}T{ano}")
        
        # =========================================================
        # RESUMO
        # =========================================================
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL")
        print("=" * 60)
        
        total_operadoras = session.query(OperadoraORM).count()
        total_despesas = session.query(DespesaORM).count()
        
        print(f"   ✅ Operadoras: {total_operadoras}")
        print(f"   ✅ Despesas: {total_despesas}")
        print("\n🎉 ETL concluído com sucesso!")
        print("   Acesse: http://localhost:8000/api/estatisticas")
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
