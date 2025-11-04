#!/usr/bin/env python3
"""
CORREÇÃO DO PROBLEMA DE TRAILING STOP - BTC LOSS ZERO
======================================================

PROBLEMA IDENTIFICADO:
- self.trailing_distance é usada para exibição mas nunca atualizada
- self.current_trailing_distance_pontos é usada para cálculos reais
- Isso cria inconsistência: trailing funciona mas mostra 0.00%

SOLUÇÃO:
- Atualizar self.trailing_distance com o valor real quando ativo
- Corrigir exibição para mostrar valores corretos
- Manter compatibilidade com código existente
"""

def patch_btc_loss_zero_simple():
    """
    Cria um patch corrigido para o agente BTC LOSS ZERO
    """
    
    patch_code = '''
# CORREÇÃO 1: Atualizar _display_status para mostrar distância correta
# Substituir a linha:
# print(f"   Distancia Trailing: {self.trailing_distance:.2f}%")
# Por:
if self.trailing_active:
    # Calcular distância real como percentual
    if hasattr(self, 'current_trailing_distance_pontos') and self.entry_price > 0:
        distancia_real_pct = (self.current_trailing_distance_pontos / self.entry_price) * 100
        print(f"   Distancia Trailing: {distancia_real_pct:.2f}%")
    else:
        print(f"   Distancia Trailing: CALCULANDO...")
else:
    print(f"   Distancia Trailing: INATIVA")

# CORREÇÃO 2: Atualizar self.trailing_distance quando trailing é ativado
# Adicionar após linha: self.trailing_active = True
self.trailing_distance = (self.current_trailing_distance_pontos / self.entry_price) * 100

# CORREÇÃO 3: Atualizar self.trailing_distance quando trailing é atualizado
# Adicionar após linha: self.trailing_stop_price = new_stop
self.trailing_distance = (self.current_trailing_distance_pontos / self.entry_price) * 100

# CORREÇÃO 4: Resetar self.trailing_distance quando position é fechada
# Adicionar após linha: self.trailing_active = False
self.trailing_distance = 0.0

'''
    
    print("=== PATCH PARA CORREÇÃO DO TRAILING STOP ===")
    print()
    print("Aplicar as seguintes correções no arquivo:")
    print("src/agents/btc_loss_zero_simple.py")
    print()
    print("1. LINHA DE EXIBIÇÃO (aproximadamente linha 260):")
    print("   ALTERAR:")
    print('   if self.trailing_active:')
    print('       print(f"   Distancia Trailing: {self.trailing_distance:.2f}%")')
    print()
    print("   POR:")
    print("   if self.trailing_active:")
    print("       if hasattr(self, 'current_trailing_distance_pontos') and self.entry_price > 0:")
    print("           distancia_real_pct = (self.current_trailing_distance_pontos / self.entry_price) * 100")
    print('           print(f"   Distancia Trailing: {distancia_real_pct:.2f}%")')
    print('       else:')
    print('           print(f"   Distancia Trailing: CALCULANDO...")')
    print("   else:")
    print('       print(f"   Distancia Trailing: INATIVA")')
    print()
    
    print("2. QUANDO TRAILING É ATIVADO (aproximadamente linha 590):")
    print("   APÓS: self.trailing_active = True")
    print("   ADICIONAR:")
    print("   self.trailing_distance = (self.current_trailing_distance_pontos / self.entry_price) * 100")
    print()
    
    print("3. QUANDO TRAILING É ATUALIZADO (aproximadamente linha 650):")
    print("   APÓS: self.trailing_stop_price = new_stop")
    print("   ADICIONAR:")
    print("   self.trailing_distance = (self.current_trailing_distance_pontos / self.entry_price) * 100")
    print()
    
    print("4. QUANDO POSIÇÃO É FECHADA (aproximadamente linha 190):")
    print("   APÓS: self.trailing_active = False")
    print("   ADICIONAR:")
    print("   self.trailing_distance = 0.0")
    print()
    
    print("=== IMPLEMENTAÇÃO AUTOMÁTICA ===")
    print("Criando arquivo corrigido automaticamente...")
    
    return patch_code

def create_corrected_file():
    """
    Cria versão corrigida do arquivo
    """
    # Ler arquivo original
    import os
    original_file = "src/agents/btc_loss_zero_simple.py"
    
    if not os.path.exists(original_file):
        print(f"ERRO: Arquivo {original_file} não encontrado!")
        return False
    
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplicar correções
        
        # Correção 1: Atualizar exibição da distância
        old_display = '''        if self.trailing_active:
            print(f"   Distancia Trailing: {self.trailing_distance:.2f}%")'''
            
        new_display = '''        if self.trailing_active:
            if hasattr(self, 'current_trailing_distance_pontos') and self.entry_price > 0:
                distancia_real_pct = (self.current_trailing_distance_pontos / self.entry_price) * 100
                print(f"   Distancia Trailing: {distancia_real_pct:.2f}%")
            else:
                print(f"   Distancia Trailing: CALCULANDO...")
        else:
            print(f"   Distancia Trailing: INATIVA")'''
        
        content = content.replace(old_display, new_display)
        
        # Correção 2: Atualizar trailing_distance quando ativado
        old_activation = '''                self.trailing_active = True

                # Calcular trailing stop price (distância em pontos)'''
                
        new_activation = '''                self.trailing_active = True

                # Atualizar variável de exibição
                self.trailing_distance = (self.current_trailing_distance_pontos / self.entry_price) * 100

                # Calcular trailing stop price (distância em pontos)'''
        
        content = content.replace(old_activation, new_activation)
        
        # Correção 3: Atualizar trailing_distance quando atualizado
        old_update = '''                        self.trailing_stop_price = new_stop
                        movimento = new_stop - old_stop'''
                        
        new_update = '''                        self.trailing_stop_price = new_stop
                        self.trailing_distance = (self.current_trailing_distance_pontos / self.entry_price) * 100
                        movimento = new_stop - old_stop'''
        
        content = content.replace(old_update, new_update)
        
        # Correção 4: Resetar quando posição fechada
        old_reset = '''                self.trailing_active = False
                self.last_position_ticket = None'''
                
        new_reset = '''                self.trailing_active = False
                self.trailing_distance = 0.0
                self.last_position_ticket = None'''
        
        content = content.replace(old_reset, new_reset)
        
        # Salvar arquivo corrigido
        corrected_file = "src/agents/btc_loss_zero_simple_CORRIGIDO.py"
        with open(corrected_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"ARQUIVO CORRIGIDO CRIADO: {corrected_file}")
        print()
        print("COMPARAÇÃO:")
        print(f"Original: {original_file}")
        print(f"Corrigido: {corrected_file}")
        print()
        print("PARA APLICAR:")
        print(f"1. Fazer backup do arquivo original")
        print(f"2. Substituir o original pelo corrigido")
        print(f"3. Testar o agente")
        
        return True
        
    except Exception as e:
        print(f"ERRO ao criar arquivo corrigido: {e}")
        return False

def main():
    print("CORREÇÃO DO PROBLEMA DE TRAILING STOP - BTC LOSS ZERO")
    print("=" * 60)
    print()
    
    # Explicar problema
    patch_btc_loss_zero_simple()
    print()
    
    # Criar arquivo corrigido
    if create_corrected_file():
        print()
        print("=== TESTE ADICIONAL RECOMENDADO ===")
        print("Após aplicar a correção, execute:")
        print("python diagnosticar_trailing_stop.py")
        print()
        print("Para verificar se:")
        print("1. Distancia Trailing mostra valor correto")
        print("2. modify_position funciona no MT5")
        print("3. Worker está ativo e executando")
    else:
        print("Falha ao criar arquivo corrigido")

if __name__ == "__main__":
    main()
