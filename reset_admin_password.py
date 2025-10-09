"""
Script para resetar a senha do usuário admin
Execute: python reset_admin_password.py
"""

import bcrypt
from database.connection import db

def gerar_hash(senha):
    """Gera hash bcrypt da senha"""
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

def main():
    print("=" * 60)
    print("🔐 RESET DE SENHA - USUÁRIO ADMIN")
    print("=" * 60)
    
    nova_senha = "admin"
    
    print(f"\n[1/3] Gerando hash bcrypt para senha: '{nova_senha}'...")
    hash_senha = gerar_hash(nova_senha)
    print(f"✅ Hash gerado: {hash_senha[:50]}...")
    
    print("\n[2/3] Atualizando senha no banco de dados...")
    try:
        query = """
            UPDATE usuarios 
            SET password_hash = %s
            WHERE username = 'admin'
        """
        
        rows = db.execute_update(query, (hash_senha,))
        
        if rows > 0:
            print(f"✅ Senha atualizada com sucesso! ({rows} registro)")
        else:
            print("❌ Nenhum registro atualizado. Usuário 'admin' não encontrado?")
            return
            
    except Exception as e:
        print(f"❌ Erro ao atualizar senha: {e}")
        return
    
    print("\n[3/3] Testando login com nova senha...")
    from services.auth_service import auth_service
    
    usuario = auth_service.autenticar('admin', nova_senha)
    
    if usuario:
        print("✅ Login testado com sucesso!")
        print(f"   - ID: {usuario['id']}")
        print(f"   - Nome: {usuario['nome_completo']}")
        print(f"   - Email: {usuario['email']}")
    else:
        print("❌ Falha no teste de login!")
        return
    
    print("\n" + "=" * 60)
    print("✅ SENHA RESETADA COM SUCESSO!")
    print("=" * 60)
    print(f"\n   Usuário: admin")
    print(f"   Senha: {nova_senha}")
    print("\n⚠️  Lembre-se de alterar a senha após o primeiro login!\n")

if __name__ == "__main__":
    main()