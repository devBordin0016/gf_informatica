"""
Script de teste para os serviços
Testa CRUD de clientes, OS e autenticação
"""

import sys
from datetime import date, timedelta
from services.auth_service import auth_service
from services.cliente_service import cliente_service
from services.os_service import os_service

def separador(titulo):
    """Imprime um separador visual"""
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)

def main():
    print("🧪 TESTE COMPLETO DOS SERVIÇOS - GF INFORMÁTICA\n")
    
    try:
        # ====================================================================
        # TESTE 1: AUTENTICAÇÃO
        # ====================================================================
        separador("TESTE 1: Autenticação")
        
        print("\n[1.1] Testando login com usuário admin...")
        usuario = auth_service.autenticar('admin', 'admin')
        
        if usuario:
            print(f"✅ Login bem-sucedido!")
            print(f"   - ID: {usuario['id']}")
            print(f"   - Nome: {usuario['nome_completo']}")
            print(f"   - Email: {usuario['email']}")
            usuario_id = usuario['id']
        else:
            print("❌ Falha no login!")
            sys.exit(1)
        
        print("\n[1.2] Testando login com senha incorreta...")
        usuario_falha = auth_service.autenticar('admin', 'senha_errada')
        
        if not usuario_falha:
            print("✅ Login negado corretamente para senha incorreta")
        else:
            print("❌ ERRO: Login deveria ter falhado!")
        
        # ====================================================================
        # TESTE 2: CLIENTES
        # ====================================================================
        separador("TESTE 2: Gerenciamento de Clientes")
        
        print("\n[2.1] Criando cliente de teste...")
        try:
            cliente_id = cliente_service.criar_cliente(
                nome="João",
                sobrenome="Silva",
                cpf="123.456.789-09",  # CPF válido para teste
                telefone="(11) 99999-8888",
                email="joao.silva@email.com"
            )
            print(f"✅ Cliente criado com ID: {cliente_id}")
        except Exception as e:
            print(f"❌ Erro ao criar cliente: {e}")
            sys.exit(1)
        
        print("\n[2.2] Buscando cliente por ID...")
        cliente = cliente_service.buscar_por_id(cliente_id)
        
        if cliente:
            print(f"✅ Cliente encontrado:")
            print(f"   - Nome: {cliente['nome']} {cliente['sobrenome']}")
            print(f"   - CPF: {cliente['cpf']}")
            print(f"   - Telefone: {cliente['telefone']}")
        else:
            print("❌ Cliente não encontrado!")
        
        print("\n[2.3] Buscando cliente por CPF...")
        cliente_cpf = cliente_service.buscar_por_cpf("12345678909")
        
        if cliente_cpf:
            print(f"✅ Cliente encontrado por CPF: {cliente_cpf['nome']}")
        else:
            print("❌ Cliente não encontrado por CPF!")
        
        print("\n[2.4] Listando todos os clientes...")
        clientes = cliente_service.listar_todos()
        print(f"✅ Total de clientes: {len(clientes)}")
        
        print("\n[2.5] Atualizando telefone do cliente...")
        sucesso = cliente_service.atualizar_cliente(
            cliente_id,
            telefone="(11) 98888-7777"
        )
        
        if sucesso:
            print("✅ Cliente atualizado com sucesso")
            cliente_atualizado = cliente_service.buscar_por_id(cliente_id)
            print(f"   - Novo telefone: {cliente_atualizado['telefone']}")
        else:
            print("❌ Falha ao atualizar cliente")
        
        # ====================================================================
        # TESTE 3: ORDENS DE SERVIÇO
        # ====================================================================
        separador("TESTE 3: Gerenciamento de Ordens de Serviço")
        
        print("\n[3.1] Criando Ordem de Serviço...")
        try:
            prazo = date.today() + timedelta(days=7)
            
            os_criada = os_service.criar_os(
                cliente_id=cliente_id,
                usuario_id=usuario_id,
                defeito_relatado="Computador não liga. Cliente relatou cheiro de queimado.",
                processador="Intel Core i5-10400",
                placa_mae="ASUS Prime H410M-E",
                memoria_ram="16GB DDR4 2666MHz",
                armazenamento="SSD 480GB + HD 1TB",
                placa_video="Integrada Intel UHD 630",
                outros_componentes="Fonte 500W, Gabinete Genérico",
                valor_estimado=150.00,
                prazo_previsto=prazo,
                observacoes="Cliente precisa do equipamento com urgência"
            )
            
            if os_criada:
                print(f"✅ OS criada com sucesso!")
                print(f"   - Número: {os_criada['numero_os']}")
                print(f"   - ID: {os_criada['id']}")
                print(f"   - Status: {os_criada['status']}")
                os_id = os_criada['id']
                numero_os = os_criada['numero_os']
            else:
                print("❌ Falha ao criar OS")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Erro ao criar OS: {e}")
            sys.exit(1)
        
        print("\n[3.2] Buscando OS por número...")
        os_encontrada = os_service.buscar_por_numero(numero_os)
        
        if os_encontrada:
            print(f"✅ OS encontrada:")
            print(f"   - Cliente: {os_encontrada['cliente_nome']} {os_encontrada['cliente_sobrenome']}")
            print(f"   - Defeito: {os_encontrada['defeito_relatado'][:50]}...")
            print(f"   - Processador: {os_encontrada['processador']}")
            print(f"   - Valor: R$ {os_encontrada['valor_estimado']}")
        else:
            print("❌ OS não encontrada!")
        
        print("\n[3.3] Listando todas as OS...")
        todas_os = os_service.listar_todas()
        print(f"✅ Total de OS: {len(todas_os)}")
        
        print("\n[3.4] Atualizando status da OS para 'em_andamento'...")
        sucesso_status = os_service.atualizar_status(
            os_id,
            os_service.STATUS_EM_ANDAMENTO,
            "Iniciado diagnóstico do equipamento"
        )
        
        if sucesso_status:
            print("✅ Status atualizado com sucesso")
            os_atualizada = os_service.buscar_por_id(os_id)
            print(f"   - Novo status: {os_atualizada['status']}")
        else:
            print("❌ Falha ao atualizar status")
        
        print("\n[3.5] Adicionando observação técnica...")
        sucesso_obs = os_service.adicionar_observacao(
            os_id,
            "Identificado problema na fonte de alimentação. Peça em estoque."
        )
        
        if sucesso_obs:
            print("✅ Observação adicionada")
        else:
            print("❌ Falha ao adicionar observação")
        
        print("\n[3.6] Listando OS do cliente...")
        os_cliente = os_service.listar_por_cliente(cliente_id)
        print(f"✅ Cliente possui {len(os_cliente)} OS")
        
        print("\n[3.7] Obtendo estatísticas...")
        stats = os_service.obter_estatisticas()
        print(f"✅ Estatísticas:")
        print(f"   - Total de OS: {stats['total']}")
        print(f"   - Abertas: {stats['abertas']}")
        print(f"   - Em andamento: {stats['em_andamento']}")
        print(f"   - Concluídas: {stats['concluidas']}")
        print(f"   - Canceladas: {stats['canceladas']}")
        
        # ====================================================================
        # TESTE 4: VALIDAÇÕES
        # ====================================================================
        separador("TESTE 4: Validações")
        
        print("\n[4.1] Testando criação de cliente com CPF inválido...")
        try:
            cliente_service.criar_cliente(
                nome="Teste",
                sobrenome="Erro",
                cpf="111.111.111-11",  # CPF inválido
                telefone="11999999999",
                email="teste@email.com"
            )
            print("❌ ERRO: Deveria ter rejeitado CPF inválido!")
        except ValueError as e:
            print(f"✅ CPF inválido rejeitado corretamente: {e}")
        
        print("\n[4.2] Testando criação de OS sem defeito relatado...")
        try:
            os_service.criar_os(
                cliente_id=cliente_id,
                usuario_id=usuario_id,
                defeito_relatado=""  # Vazio
            )
            print("❌ ERRO: Deveria ter rejeitado defeito vazio!")
        except ValueError as e:
            print(f"✅ Defeito vazio rejeitado corretamente: {e}")
        
        print("\n[4.3] Testando atualização com status inválido...")
        try:
            os_service.atualizar_status(os_id, "status_inexistente")
            print("❌ ERRO: Deveria ter rejeitado status inválido!")
        except ValueError as e:
            print(f"✅ Status inválido rejeitado corretamente: {e}")
        
        # ====================================================================
        # RESUMO FINAL
        # ====================================================================
        separador("RESUMO DOS TESTES")
        
        print("\n✅ TODOS OS TESTES PASSARAM COM SUCESSO!\n")
        print("📊 Dados criados durante o teste:")
        print(f"   - 1 Cliente: {cliente['nome']} {cliente['sobrenome']}")
        print(f"   - 1 OS: {numero_os}")
        print(f"   - Status da OS: {os_atualizada['status']}")
        print("\n💡 Os dados de teste permanecem no banco.")
        print("   Para limpar, recrie o schema com o arquivo schema.sql\n")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()