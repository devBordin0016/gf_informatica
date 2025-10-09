"""
Script de teste para verificar a conexão com o banco de dados
Execute: python test_connection.py
"""

import sys
from database.connection import db

def main():
    """
    Testa a conexão e exibe informações do banco
    """
    print("=" * 60)
    print("?? TESTE DE CONEXÃO - GF INFORMÁTICA")
    print("=" * 60)
    
    # Teste 1: Conexão básica
    print("\n[1/3] Testando conexão com PostgreSQL...")
    if not db.test_connection():
        print("? Falha na conexão! Verifique o arquivo .env")
        sys.exit(1)
    
    # Teste 2: Verificar tabelas
    print("\n[2/3] Verificando tabelas criadas...")
    try:
        tables = db.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"? {len(tables)} tabelas encontradas:")
        for table in tables:
            print(f"   - {table['table_name']}")
            
    except Exception as e:
        print(f"? Erro ao verificar tabelas: {e}")
        sys.exit(1)
    
    # Teste 3: Verificar usuário admin
    print("\n[3/3] Verificando usuário administrador...")
    try:
        admin = db.execute_query("""
            SELECT id, username, nome_completo, email, ativo 
            FROM usuarios 
            WHERE username = %s
        """, ('admin',))
        
        if admin:
            print(f"? Usuário admin encontrado:")
            print(f"   - ID: {admin[0]['id']}")
            print(f"   - Nome: {admin[0]['nome_completo']}")
            print(f"   - Email: {admin[0]['email']}")
            print(f"   - Ativo: {admin[0]['ativo']}")
        else:
            print("? Usuário admin não encontrado!")
            
    except Exception as e:
        print(f"? Erro ao verificar usuário: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("? TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 60)
    print("\n?? Sistema pronto para uso!")

if __name__ == "__main__":
    main()