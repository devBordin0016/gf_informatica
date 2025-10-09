-- ============================================================================
-- GF INFORMÁTICA - SISTEMA DE ORDEM DE SERVIÇO
-- Schema do Banco de Dados PostgreSQL
-- ============================================================================
-- Versão: 1.0.0
-- Data: 2025
-- ============================================================================

-- Remover tabelas existentes (cuidado em produção!)
DROP TABLE IF EXISTS ordens_servico CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP SEQUENCE IF EXISTS os_numero_seq;

-- ============================================================================
-- TABELA: usuarios
-- Armazena dados de usuários do sistema (técnicos/atendentes)
-- ============================================================================
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Hash bcrypt da senha
    nome_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_email ON usuarios(email);

-- ============================================================================
-- TABELA: clientes
-- Armazena dados dos clientes da assistência técnica
-- ============================================================================
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,  -- Formato: 000.000.000-00
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(150),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para busca rápida
CREATE INDEX idx_clientes_cpf ON clientes(cpf);
CREATE INDEX idx_clientes_nome ON clientes(nome);
CREATE INDEX idx_clientes_telefone ON clientes(telefone);

-- ============================================================================
-- SEQUENCE: Numeração automática das OS
-- Gera números sequenciais para as Ordens de Serviço (OS0001, OS0002...)
-- ============================================================================
CREATE SEQUENCE os_numero_seq START 1;

-- ============================================================================
-- TABELA: ordens_servico
-- Armazena as Ordens de Serviço com todas as informações
-- ============================================================================
CREATE TABLE ordens_servico (
    id SERIAL PRIMARY KEY,
    numero_os VARCHAR(10) UNIQUE NOT NULL,  -- Formato: OS0001, OS0002...
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    
    -- Configuração do Hardware (colunas separadas conforme solicitado)
    processador VARCHAR(150),
    placa_mae VARCHAR(150),
    memoria_ram VARCHAR(100),
    armazenamento VARCHAR(150),
    placa_video VARCHAR(150),
    outros_componentes TEXT,  -- Campo livre para informações adicionais
    
    -- Informações do problema
    defeito_relatado TEXT NOT NULL,
    
    -- Informações adicionais conforme solicitado
    valor_estimado DECIMAL(10, 2),  -- Valor em reais (ex: 150.50)
    prazo_previsto DATE,  -- Data prevista para conclusão
    observacoes TEXT,  -- Observações técnicas
    
    -- Status da OS
    status VARCHAR(20) DEFAULT 'aberta' CHECK (status IN ('aberta', 'em_andamento', 'concluida', 'cancelada')),
    
    -- Datas de controle
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    concluido_em TIMESTAMP  -- Preenchido quando status = 'concluida'
);

-- Índices para melhor performance
CREATE INDEX idx_os_numero ON ordens_servico(numero_os);
CREATE INDEX idx_os_cliente ON ordens_servico(cliente_id);
CREATE INDEX idx_os_status ON ordens_servico(status);
CREATE INDEX idx_os_data ON ordens_servico(criado_em);

-- ============================================================================
-- FUNÇÃO: Gerar número da OS automaticamente
-- Gera o próximo número sequencial no formato OS0001, OS0002, etc.
-- ============================================================================
CREATE OR REPLACE FUNCTION gerar_numero_os()
RETURNS TRIGGER AS $$
BEGIN
    -- Gera o número da OS no formato OS0001, OS0002...
    NEW.numero_os := 'OS' || LPAD(nextval('os_numero_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger que executa a função antes de inserir uma nova OS
CREATE TRIGGER trigger_gerar_numero_os
    BEFORE INSERT ON ordens_servico
    FOR EACH ROW
    WHEN (NEW.numero_os IS NULL)  -- Só gera se não foi informado
    EXECUTE FUNCTION gerar_numero_os();

-- ============================================================================
-- FUNÇÃO: Atualizar timestamp automaticamente
-- Atualiza o campo 'atualizado_em' sempre que um registro é modificado
-- ============================================================================
CREATE OR REPLACE FUNCTION atualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualização automática de timestamp
CREATE TRIGGER trigger_atualizar_usuarios
    BEFORE UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_timestamp();

CREATE TRIGGER trigger_atualizar_clientes
    BEFORE UPDATE ON clientes
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_timestamp();

CREATE TRIGGER trigger_atualizar_os
    BEFORE UPDATE ON ordens_servico
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_timestamp();

-- ============================================================================
-- INSERÇÃO DO USUÁRIO ADMINISTRADOR INICIAL
-- Usuário: admin / Senha: admin (hash bcrypt)
-- ?? ALTERE A SENHA APÓS O PRIMEIRO LOGIN!
-- ============================================================================
-- Hash bcrypt para a senha 'admin': $2b$12$KIXxLVvWKfHxG8h4LdVP6.Hk7JZqJ5h5xKqJqvqxKqJqJqJqJqJqJ
-- Nota: Este é um hash de exemplo. Será gerado corretamente pelo código Python.

INSERT INTO usuarios (username, password_hash, nome_completo, email, ativo)
VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpKFzLDKWEKy',  -- Senha: admin
    'Administrador',
    'admin@gfinformatica.com.br',
    TRUE
);

-- ============================================================================
-- COMENTÁRIOS NAS TABELAS (Documentação do schema)
-- ============================================================================
COMMENT ON TABLE usuarios IS 'Usuários do sistema (técnicos e atendentes)';
COMMENT ON TABLE clientes IS 'Clientes da assistência técnica';
COMMENT ON TABLE ordens_servico IS 'Ordens de Serviço com informações completas';

COMMENT ON COLUMN clientes.cpf IS 'CPF do cliente no formato 000.000.000-00';
COMMENT ON COLUMN ordens_servico.numero_os IS 'Número sequencial automático (OS0001, OS0002...)';
COMMENT ON COLUMN ordens_servico.status IS 'Status: aberta, em_andamento, concluida, cancelada';
COMMENT ON COLUMN ordens_servico.valor_estimado IS 'Valor estimado do serviço em reais';
COMMENT ON COLUMN ordens_servico.prazo_previsto IS 'Data prevista para conclusão do serviço';

-- ============================================================================
-- FIM DO SCHEMA
-- ============================================================================