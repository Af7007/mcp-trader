#!/usr/bin/env python3
"""
Teste específico para simular uma posição e verificar ativação de trailing no Gold AI
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.gold_ai_agent import GoldAIAgent

def testar_ativacao_trailing():
    print("=== TESTE ATIVACAO TRAILING GOLD AI ===")
    
    # Criar agente desabilitado (usar método tradicional)
    agent = GoldAIAgent(
        symbol="XAUUSDc", 
        volume=0.02,
        ai_enabled=False  # Usar método tradicional
    )
    
    print(f"Agente criado: {type(agent).__name__}")
    print(f"Trailing configurado: Ativa com ${agent.trailing_activation_dollar}, Protege ${agent.trailing_distance_dollar}")
    
    # Verificar se o método _manage_position_trailing existe e é herdado
    print(f"\n--- METODOS DE TRAILING ---")
    print(f"herda _manage_position_trailing: {hasattr(agent, '_manage_position_trailing')}")
    print(f"herda _update_trailing_from_worker: {hasattr(agent, '_update_trailing_from_worker')}")
    print(f"herda _safe_modify_sl: {hasattr(agent, '_safe_modify_sl')}")
    
    # Simular estado de uma posição aberta
    print(f"\n--- SIMULANDO POSICAO ---")
    
    # Simular uma posição BUY
    pos_simulada = {
        'ticket': 12345,
        'type': 0,  # BUY
        'price_open': 3000.0,
        'profit': 1.5,  # $1.50 de lucro (deveria ativar trailing)
        'volume': 0.02,
        'sl': 2998.0,
        'tp': 0.0
    }
    
    print(f"Posicao simulada:")
    print(f"  Tipo: BUY (type={pos_simulada['type']})")
    print(f"  Ticket: {pos_simulada['ticket']}")
    print(f"  Entry: ${pos_simulada['price_open']}")
    print(f"  Lucro atual: ${pos_simulada['profit']}")
    print(f"  Trailing ativa: ${agent.trailing_activation_dollar}")
    
    # Verificar se deveria ativar trailing
    if pos_simulada['profit'] >= agent.trailing_activation_dollar:
        print(f"  DEVERIA ATIVAR TRAILING: ${pos_simulada['profit']} >= ${agent.trailing_activation_dollar}")
    else:
        print(f"  NAO ATIVA TRAILING: ${pos_simulada['profit']} < ${agent.trailing_activation_dollar}")
    
    # Testar se o método _manage_position_trailing é executado
    print(f"\n--- TESTANDO EXECUCAO ---")
    
    # Simular que o agente tem essa posição
    agent.positions_entry_price[12345] = 3000.0
    agent.positions_trailing_active[12345] = False
    agent.positions_trailing_stop[12345] = 0.0
    agent.last_position_ticket = 12345
    
    # Tentar executar o método de gerenciamento de posição
    try:
        print(f"Executando _manage_position_trailing...")
        agent._manage_position_trailing(pos_simulada)
        print(f"Executou sem erros")
    except Exception as e:
        print(f"ERRO na execucao: {e}")
    
    print(f"\n--- VARIAVEIS APOS TESTE ---")
    print(f"trailing_active: {agent.trailing_active}")
    print(f"positions_trailing_active: {agent.positions_trailing_active}")
    print(f"positions_trailing_stop: {agent.positions_trailing_stop}")
    
    # Testar com lucro suficiente
    print(f"\n--- TESTE COM LUCRO MAIOR ---")
    pos_alto_lucro = {
        'ticket': 12346,
        'type': 0,  # BUY
        'price_open': 3000.0,
        'profit': 2.5,  # $2.50 de lucro (muito acima do threshold)
        'volume': 0.02,
        'sl': 2998.0,
        'tp': 0.0
    }
    
    agent.positions_entry_price[12346] = 3000.0
    agent.positions_trailing_active[12346] = False
    agent.positions_trailing_stop[12346] = 0.0
    
    print(f"Lucro: ${pos_alto_lucro['profit']} (deveria ativar)")
    try:
        agent._manage_position_trailing(pos_alto_lucro)
        print(f"Executou trailing com lucro alto")
        print(f"Trailing ativo apos: {agent.trailing_active}")
        print(f"Trailing stop calculado: {agent.positions_trailing_stop.get(12346, 'N/A')}")
    except Exception as e:
        print(f"ERRO no lucro alto: {e}")
    
    print(f"\n--- CONCLUSÃO ---")
    if agent.trailing_active:
        print(f"TRAILING FUNCIONANDO: O sistema ativa trailing quando necessário")
    else:
        print(f"TRAILING NAO ATIVA: Pode haver problema na condição de ativação")
        print(f"Possíveis causas:")
        print(f"1. Condições de cooldown impedindo execução")
        print(f"2. MT5 não responde para modificação de SL")
        print(f"3. Worker de monitoramento não iniciado")
        print(f"4. Preço de mercado não sendo atualizado")

if __name__ == "__main__":
    testar_ativacao_trailing()
