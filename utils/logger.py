"""
Configuração de logging para a aplicação
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Configura um logger para a aplicação
    
    Args:
        name: Nome do logger
        log_file: Nome do arquivo de log (opcional)
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    # Cria pasta de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Define nome do arquivo de log
    if not log_file:
        log_file = f"gf_informatica_{datetime.now().strftime('%Y%m%d')}.log"
    
    log_path = log_dir / log_file
    
    # Configura o logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Apenas warnings e erros no console
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Adiciona handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Logger padrão da aplicação
app_logger = setup_logger('gf_informatica')