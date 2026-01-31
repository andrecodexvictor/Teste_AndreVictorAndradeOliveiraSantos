#!/usr/bin/env python
"""
Script para exportar CSVs consolidados a partir do banco de dados.
"""
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.models import DespesaORM, OperadoraORM
from pathlib import Path
import pandas as pd

# Conectar ao banco
engine = create_engine('mysql+pymysql://root:root@localhost:3306/ans_data')
Session = sessionmaker(bind=engine)
session = Session()

# Criar diretório
exports_dir = Path('data/exports')
exports_dir.mkdir(parents=True, exist_ok=True)

print('Exportando consolidado_despesas.csv...')
query = session.query(
    DespesaORM.cnpj,
    DespesaORM.razao_social,
    DespesaORM.ano,
    DespesaORM.trimestre,
    DespesaORM.valor,
    DespesaORM.status_qualidade,
    OperadoraORM.modalidade,
    OperadoraORM.uf,
    OperadoraORM.registro_ans
).outerjoin(
    OperadoraORM, DespesaORM.cnpj == OperadoraORM.cnpj
).order_by(DespesaORM.ano.desc(), DespesaORM.trimestre.desc())

results = query.all()
df = pd.DataFrame(results, columns=[
    'CNPJ', 'RAZAO_SOCIAL', 'ANO', 'TRIMESTRE', 'VALOR', 
    'STATUS_QUALIDADE', 'MODALIDADE', 'UF', 'REGISTRO_ANS'
])
df.to_csv(exports_dir / 'consolidado_despesas.csv', index=False, encoding='utf-8-sig')
print(f'Salvo: {len(df)} registros')

print('Exportando despesas_agregadas.csv...')
query_agg = session.query(
    DespesaORM.cnpj,
    OperadoraORM.razao_social,
    OperadoraORM.uf,
    func.count(DespesaORM.id).label('total_registros'),
    func.sum(DespesaORM.valor).label('total_despesas'),
    func.avg(DespesaORM.valor).label('media_despesas')
).outerjoin(
    OperadoraORM, DespesaORM.cnpj == OperadoraORM.cnpj
).group_by(DespesaORM.cnpj, OperadoraORM.razao_social, OperadoraORM.uf)

results_agg = query_agg.all()
df_agg = pd.DataFrame(results_agg, columns=[
    'CNPJ', 'RAZAO_SOCIAL', 'UF', 'TOTAL_REGISTROS', 'TOTAL_DESPESAS', 'MEDIA_DESPESAS'
])
df_agg.to_csv(exports_dir / 'despesas_agregadas.csv', index=False, encoding='utf-8-sig')
print(f'Salvo: {len(df_agg)} operadoras')

print('Concluido!')
