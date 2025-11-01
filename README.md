# GF Informática - Sistema de Gestão Comercial

Este projeto é um **sistema desktop completo** desenvolvido em **Python**, com o objetivo de **gerenciar ordens de serviço (OS) em assistências técnicas de computadores**.  
O sistema foi projetado para otimizar o controle de cadastros, serviços prestados e emissão de relatórios em **PDF**, utilizando **interface gráfica com Tkinter** e **banco de dados PostgreSQL** para armazenamento seguro das informações.

Este trabalho foi desenvolvido como parte de um **projeto acadêmico** do curso de **Ciência da Computação**, aplicando conceitos de **banco de dados, arquitetura modular e automação de processos comerciais**.  

---

## 🧩 Tecnologias Utilizadas

- 🐍 **Python** → Linguagem principal utilizada para o desenvolvimento do sistema e automação das funcionalidades.  
- 🖥️ **Tkinter** → Biblioteca padrão do Python para criação da **interface gráfica desktop**.  
- 🗃️ **PostgreSQL** → Banco de dados relacional responsável pelo armazenamento das informações de clientes, serviços e ordens.  
- 🧮 **PL/pgSQL** → Linguagem procedural utilizada no PostgreSQL para consultas e funções personalizadas no banco.  
- 🧾 **ReportLab / FPDF** → Biblioteca de geração de **relatórios e PDFs profissionais**.  
- ⚙️ **python-dotenv** → Utilizada para gerenciar variáveis de ambiente (.env) e credenciais do banco.  
- 🔌 **psycopg2** → Driver responsável pela conexão entre o Python e o banco de dados PostgreSQL.

---

## 🧩 Estrutura do Projeto

```bash
├── database/              # Módulo responsável pelo banco de dados e tabelas
├── logs/                  # Armazena logs de execução e erros do sistema
├── services/              # Contém as regras de negócio e funções principais do sistema
├── ui/                    # Interface do usuário (camada visual)
├── utils/                 # Funções auxiliares e utilitárias
│
├── .env.example           # Exemplo de variáveis de ambiente
├── .gitignore             # Arquivos ignorados pelo Git
├── README.md              # Documentação do projeto
├── debug_pdf.py           # Script de depuração para geração de PDFs
├── main.py                # Arquivo principal para executar o sistema
├── requirements.txt       # Dependências do projeto
├── reset_admin_password.py # Script para redefinir senha do admin
├── test_connection.py     # Teste de conexão com o banco de dados
└── test_services.py       # Testes automatizados das funções de serviço
```

---

## ⚙️ Funcionalidades

- Cadastro e gerenciamento de clientes e serviços.  
- Geração automática de relatórios e documentos em PDF.  
- Sistema de logs para auditoria de eventos.    
- Scripts de teste e manutenção do sistema.  
- Interface gráfica intuitiva desenvolvida com Tkinter.

---

## 🚀 Como Executar o Projeto

Siga as etapas abaixo para rodar o sistema localmente.

1. **Clone este repositório**

   ```bash
   git clone https://github.com/devBordin0016/gf_informatica.git
   cd gf_informatica

2. **Crie o ambiente virtual**

    ```bash
    python -m venv venv
    venv\Scripts\activate  # (Windows)
    source venv/bin/activate  # (Linux/Mac)
    ```

3. **Instale as dependências**

    ```bash
    pip install -r requirements.txt

4. **Configure o arquivo `.env`**

    - Copie o arquivo `.env.example` e renomeie para `.env`
    - Ajuste as variáveis conforme o ambiente local (exemplo: credenciais de banco, caminhos de logs, etc.)

5. **Execute o sistema**

    ```bash
    python main.py

---

## 📦 Requisitos do Sistema

- Python 3.10 ou superior  
- PostgreSQL 14+  
- Sistema operacional: Windows 10/11 ou Linux  
- Biblioteca ReportLab instalada  
- Conexão configurada via arquivo `.env`

---

## 📚 Artigos Científicos

> Ambos foram produzidos como parte das atividades avaliativas da disciplina **Arquitetura e Organização de Computadores** e **Modelagem de Dados**, sob orientação do professor **Eduardo Furlan**.

> [DESENVOLVIMENTO DE UM SISTEMA DE GESTÃO COMERCIAL EM PYTHON : APLICAÇÃO DE ARQUITETURA MODULAR E BANCO DE DADOS RELACIONAL](articles/artigo1.pdf)
> [METODOLOGIA MODULAR NO DESENVOLVIMENTO DE SISTEMAS DESKTOP EM PYTHON: ESTUDO DE CASO GF INFORMÁTICA](articles/artigo2.pdf)

## 📓 Diário de Bordo

[DIÁRIO DE BORDO DO PROJETO](articles/diario_de_bordo.pdf)

## 👨‍💻 Equipe

- **Gustavo de Lima** – Documentação, artigos, diário de bordo, apresentações e testes.  
- **Fernando Bordin** – Desenvolvimento, banco de dados, testes e geração de relatórios.  
- **Curso:** Ciência da Computação  
- **Disciplina:** Arquitetura e Organização de Computadores (Gustavo) e Modelagem de Dados (Fernando)  
- **Professor:** Eduardo Furlan
