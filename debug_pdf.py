"""
Script de debug para identificar o erro no PDF
"""

import traceback
from services.os_service import os_service

def debug_pdf():
    """Debug da geração de PDF"""
    
    print("=" * 60)
    print("DEBUG - GERAÇÃO DE PDF")
    print("=" * 60)
    
    # Passo 1: Buscar uma OS existente
    print("\n[1/4] Buscando OS no banco...")
    try:
        os_list = os_service.listar_todas(limite=1)
        
        if not os_list:
            print("❌ Nenhuma OS encontrada no banco!")
            print("   Crie uma OS primeiro pelo sistema.")
            return
        
        os_data = os_list[0]
        print(f"✅ OS encontrada: {os_data['numero_os']}")
        print(f"   Cliente: {os_data['cliente_nome']} {os_data['cliente_sobrenome']}")
        
    except Exception as e:
        print(f"❌ Erro ao buscar OS: {e}")
        traceback.print_exc()
        return
    
    # Passo 2: Importar o gerador
    print("\n[2/4] Importando gerador de PDF...")
    try:
        from utils.pdf_generator import pdf_generator
        print("✅ Gerador importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar gerador: {e}")
        traceback.print_exc()
        return
    
    # Passo 3: Tentar gerar PDF
    print(f"\n[3/4] Gerando PDF para OS ID {os_data['id']}...")
    try:
        output_path = f"DEBUG_OS_{os_data['numero_os']}.pdf"
        
        # Aqui está o ponto crítico - vamos ver o erro completo
        pdf_path = pdf_generator.gerar_pdf_os(os_data['id'], output_path)
        
        print(f"✅ PDF gerado com sucesso: {pdf_path}")
        
    except Exception as e:
        print(f"\n❌ ERRO DETECTADO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {e}")
        print(f"\n📍 TRACEBACK COMPLETO:")
        print("-" * 60)
        traceback.print_exc()
        print("-" * 60)
        
        # Informações adicionais
        print("\n🔍 INFORMAÇÕES ADICIONAIS:")
        print(f"   Python: {__import__('sys').version}")
        print(f"   fpdf2: {__import__('fpdf').__version__}")
        
        return
    
    # Passo 4: Verificar arquivo
    print("\n[4/4] Verificando arquivo gerado...")
    import os as os_module
    
    if os_module.path.exists(output_path):
        size = os_module.path.getsize(output_path)
        print(f"✅ Arquivo existe: {output_path}")
        print(f"   Tamanho: {size} bytes")
    else:
        print(f"❌ Arquivo não encontrado: {output_path}")
    
    print("\n" + "=" * 60)
    print("DEBUG CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    debug_pdf()