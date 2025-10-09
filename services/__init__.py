"""
Módulo de serviços
Contém toda a lógica de negócio da aplicação
"""

from .cliente_service import ClienteService, cliente_service
from .os_service import OSService, os_service
from .auth_service import AuthService, auth_service

__all__ = [
    'ClienteService', 'cliente_service',
    'OSService', 'os_service',
    'AuthService', 'auth_service'
]