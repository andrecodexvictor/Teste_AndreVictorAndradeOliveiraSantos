# =============================================================
# seed_database.py - Popula o banco com dados de exemplo
# =============================================================
"""
Script para popular o banco de dados com dados de exemplo.

Execute: python seed_database.py
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.database.connection import SessionLocal, engine
from src.infrastructure.database.models import OperadoraORM, DespesaORM, Base
import random

# Dados de exemplo
OPERADORAS_EXEMPLO = [
    {"cnpj": "00394460000141", "razao_social": "UNIMED BELO HORIZONTE COOPERATIVA DE TRABALHO MEDICO", "registro_ans": "343889", "modalidade": "COOPERATIVA_MEDICA", "uf": "MG"},
    {"cnpj": "01685053000156", "razao_social": "UNIMED RIO COOPERATIVA DE TRABALHO MEDICO DO RIO DE JANEIRO", "registro_ans": "355836", "modalidade": "COOPERATIVA_MEDICA", "uf": "RJ"},
    {"cnpj": "43202472000140", "razao_social": "UNIMED SAO PAULO COOPERATIVA DE TRABALHO MEDICO", "registro_ans": "352501", "modalidade": "COOPERATIVA_MEDICA", "uf": "SP"},
    {"cnpj": "00529411000182", "razao_social": "BRADESCO SAUDE S.A.", "registro_ans": "005711", "modalidade": "MEDICINA_GRUPO", "uf": "SP"},
    {"cnpj": "61079117000134", "razao_social": "SUL AMERICA COMPANHIA DE SEGURO SAUDE", "registro_ans": "006246", "modalidade": "SEGURADORA", "uf": "RJ"},
    {"cnpj": "51722957000191", "razao_social": "NOTRE DAME INTERMEDICA SAUDE S.A.", "registro_ans": "359017", "modalidade": "MEDICINA_GRUPO", "uf": "SP"},
    {"cnpj": "04233987000106", "razao_social": "HAPVIDA ASSISTENCIA MEDICA LTDA", "registro_ans": "368253", "modalidade": "MEDICINA_GRUPO", "uf": "CE"},
    {"cnpj": "44649812000138", "razao_social": "AMIL ASSISTENCIA MEDICA INTERNACIONAL S.A.", "registro_ans": "326305", "modalidade": "MEDICINA_GRUPO", "uf": "RJ"},
    {"cnpj": "02866714000151", "razao_social": "UNIMED CURITIBA SOCIEDADE COOPERATIVA DE MEDICOS", "registro_ans": "304701", "modalidade": "COOPERATIVA_MEDICA", "uf": "PR"},
    {"cnpj": "23704017000157", "razao_social": "UNIMED PORTO ALEGRE COOPERATIVA MEDICA LTDA", "registro_ans": "352081", "modalidade": "COOPERATIVA_MEDICA", "uf": "RS"},
    {"cnpj": "00952036000160", "razao_social": "CAIXA DE ASSISTENCIA DOS FUNCIONARIOS DO BANCO DO BRASIL", "registro_ans": "346659", "modalidade": "AUTOGESTAO", "uf": "DF"},
    {"cnpj": "02936310000190", "razao_social": "UNIMED CAMPINAS COOPERATIVA DE TRABALHO MEDICO", "registro_ans": "340669", "modalidade": "COOPERATIVA_MEDICA", "uf": "SP"},
    {"cnpj": "74014747000135", "razao_social": "UNIMED GOIANIA COOPERATIVA DE TRABALHO MEDICO", "registro_ans": "302147", "modalidade": "COOPERATIVA_MEDICA", "uf": "GO"},
    {"cnpj": "01623199000172", "razao_social": "PREVENT SENIOR PRIVATE OPERADORA DE SAUDE LTDA", "registro_ans": "358100", "modalidade": "MEDICINA_GRUPO", "uf": "SP"},
    {"cnpj": "07643478000117", "razao_social": "UNIMED FORTALEZA COOPERATIVA DE TRABALHO MEDICO LTDA", "registro_ans": "330213", "modalidade": "COOPERATIVA_MEDICA", "uf": "CE"},
]


def seed_database():
    """Popula o banco com dados de exemplo."""
    print("🌱 Iniciando seed do banco de dados...")
    
    # Cria as tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        # Verifica se já existem dados
        count = session.query(OperadoraORM).count()
        if count > 0:
            print(f"⚠️  Já existem {count} operadoras no banco. Limpando...")
            session.query(DespesaORM).delete()
            session.query(OperadoraORM).delete()
            session.commit()
        
        # Insere operadoras
        print("📋 Inserindo operadoras...")
        for op_data in OPERADORAS_EXEMPLO:
            operadora = OperadoraORM(**op_data)
            session.add(operadora)
        
        session.commit()
        print(f"   ✅ {len(OPERADORAS_EXEMPLO)} operadoras inseridas")
        
        # Insere despesas (2023 e 2024, 4 trimestres cada)
        print("💰 Inserindo despesas...")
        despesas_inseridas = 0
        
        for op_data in OPERADORAS_EXEMPLO:
            for ano in [2023, 2024]:
                for trimestre in range(1, 5):
                    # Valor base entre 10M e 500M
                    valor_base = random.uniform(10_000_000, 500_000_000)
                    # Adiciona alguma variação
                    valor = valor_base * (1 + random.uniform(-0.2, 0.2))
                    
                    despesa = DespesaORM(
                        cnpj=op_data["cnpj"],
                        razao_social=op_data["razao_social"],
                        ano=ano,
                        trimestre=trimestre,
                        valor=round(valor, 2),
                        status_qualidade="OK"
                    )
                    session.add(despesa)
                    despesas_inseridas += 1
        
        session.commit()
        print(f"   ✅ {despesas_inseridas} registros de despesas inseridos")
        
        # Resumo
        print("\n📊 Resumo do seed:")
        total_operadoras = session.query(OperadoraORM).count()
        total_despesas = session.query(DespesaORM).count()
        print(f"   - Operadoras: {total_operadoras}")
        print(f"   - Despesas: {total_despesas}")
        
        print("\n✅ Seed concluído com sucesso!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro durante seed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
