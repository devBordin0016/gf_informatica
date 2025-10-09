"""
Utilitários de validação
Validações de CPF, email, telefone, etc.
"""

import re
from typing import Optional


class Validators:
    """
    Classe com métodos estáticos para validação de dados
    """
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """
        Valida CPF usando o algoritmo oficial
        
        Args:
            cpf: CPF com ou sem formatação
        
        Returns:
            True se válido, False caso contrário
        """
        # Remove caracteres não numéricos
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf_numeros) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf_numeros == cpf_numeros[0] * 11:
            return False
        
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf_numeros[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        if int(cpf_numeros[9]) != digito1:
            return False
        
        # Validação do segundo dígito verificador
        soma = sum(int(cpf_numeros[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        if int(cpf_numeros[10]) != digito2:
            return False
        
        return True
    
    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """
        Formata CPF no padrão 000.000.000-00
        
        Args:
            cpf: CPF com ou sem formatação
        
        Returns:
            CPF formatado
        """
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        if len(cpf_numeros) != 11:
            return cpf  # Retorna original se inválido
        
        return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """
        Valida formato de email
        
        Args:
            email: Email a ser validado
        
        Returns:
            True se válido, False caso contrário
        """
        if not email:
            return False
        
        # Regex básico para email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """
        Formata telefone no padrão (00) 00000-0000 ou (00) 0000-0000
        
        Args:
            telefone: Telefone com ou sem formatação
        
        Returns:
            Telefone formatado
        """
        numeros = re.sub(r'\D', '', telefone)
        
        if len(numeros) == 11:  # Celular com 9 dígitos
            return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        elif len(numeros) == 10:  # Fixo ou celular antigo
            return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        else:
            return telefone  # Retorna original se não for padrão conhecido
    
    @staticmethod
    def validar_valor(valor_str: str) -> Optional[float]:
        """
        Valida e converte string de valor monetário para float
        
        Args:
            valor_str: String com valor (ex: "150,50" ou "150.50")
        
        Returns:
            Float do valor ou None se inválido
        """
        if not valor_str or not valor_str.strip():
            return None
        
        try:
            # Remove espaços e substitui vírgula por ponto
            valor_limpo = valor_str.strip().replace(',', '.')
            valor = float(valor_limpo)
            
            if valor < 0:
                return None
            
            return round(valor, 2)
        except ValueError:
            return None
    
    @staticmethod
    def formatar_valor(valor: Optional[float]) -> str:
        """
        Formata valor float para string monetária (R$ 0,00)
        
        Args:
            valor: Valor em float
        
        Returns:
            String formatada
        """
        if valor is None:
            return "R$ 0,00"
        
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


# Instância global
validators = Validators()