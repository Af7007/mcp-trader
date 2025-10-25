#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar integração com Telegram
Verifica conexão e envia mensagens de teste
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configurar encoding UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Carregar variáveis do .env
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.telegram_notifier import get_telegram_notifier

def test_telegram():
    """Testa conexão e funcionamento do Telegram."""
    print("="*70)
    print("🧪 TESTE DE INTEGRAÇÃO - TELEGRAM")
    print("="*70)
    print()

    # 1. Inicializar
    print("[1] Inicializando Telegram Notifier...")
    notifier = get_telegram_notifier()

    if not notifier.enabled:
        print("    ❌ Telegram não está habilitado")
        print()
        print("💡 Para habilitar:")
        print("    1. Configure TELEGRAM_BOT_TOKEN no .env")
        print("    2. Configure TELEGRAM_CHAT_ID no .env")
        print("    3. Defina TELEGRAM_ENABLED=true no .env")
        print()
        return False

    print("    ✅ Telegram Notifier inicializado")
    print()

    # 2. Testar mensagem simples
    print("[2] Enviando mensagem de teste...")
    success = notifier.send_message(
        "<b>🧪 TESTE</b>\n\nMensagem de teste simples.\n\n"
        f"<b>⏰</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    if success:
        print("    ✅ Mensagem enviada com sucesso")
    else:
        print("    ❌ Erro ao enviar mensagem")
        return False

    print()

    # 3. Testar notificação de abertura
    print("[3] Testando notificação de abertura de posição...")
    success = notifier.send_trade_opened(
        ticket=999999,
        symbol="BTCUSDm",
        trade_type="BUY",
        volume=0.03,
        entry_price=109545.50,
        tp=109645.50,
        sl=109245.50,
        indicators={
            'rsi': 65.3,
            'macd': 12.45,
            'trend': 'UP',
            'atr': 181.44
        }
    )

    if success:
        print("    ✅ Notificação de abertura enviada")
    else:
        print("    ❌ Erro ao enviar notificação de abertura")
        return False

    print()

    # 4. Testar notificação de fechamento
    print("[4] Testando notificação de fechamento de posição...")
    success = notifier.send_trade_closed(
        ticket=999999,
        symbol="BTCUSDm",
        trade_type="BUY",
        entry_price=109545.50,
        close_price=109650.00,
        profit=2.15,
        duration_seconds=225,
        daily_stats={
            'total_profit': 18.50,
            'win_rate': 75.0,
            'winning_streak': 3,
            'trades_count': 8,
            'wins': 6,
            'losses': 2
        }
    )

    if success:
        print("    ✅ Notificação de fechamento enviada")
    else:
        print("    ❌ Erro ao enviar notificação de fechamento")
        return False

    print()

    # 5. Testar resumo periódico
    print("[5] Testando resumo periódico...")
    success = notifier.send_periodic_summary(
        symbol="BTCUSDm",
        state="trading",
        daily_stats={
            'total_profit': 18.50,
            'win_rate': 75.0,
            'winning_streak': 3,
            'trades_count': 8,
            'wins': 6,
            'losses': 2
        },
        positions_open=2,
        indicators={
            'current_price': 109650.00,
            'trend': 'UP',
            'rsi': 58.2,
            'macd': 15.3,
            'atr': 181.44,
            'sma_20': 109567.89,
            'sma_50': 109423.45,
            'bb_upper': 109823.45,
            'bb_middle': 109650.00,
            'bb_lower': 109476.55
        },
        time_period="últimos 30 minutos"
    )

    if success:
        print("    ✅ Resumo periódico enviado")
    else:
        print("    ❌ Erro ao enviar resumo")
        return False

    print()

    # 6. Testar análise de mercado
    print("[6] Testando análise de mercado...")
    success = notifier.send_market_analysis(
        symbol="BTCUSDm",
        indicators={
            'current_price': 109650.00,
            'trend': 'UP',
            'rsi': 65.3,
            'macd': 12.45,
            'atr': 181.44,
            'sma_20': 109567.89,
            'sma_50': 109423.45,
            'bb_upper': 109823.45,
            'bb_middle': 109650.00,
            'bb_lower': 109476.55
        },
        signal="BUY"
    )

    if success:
        print("    ✅ Análise de mercado enviada")
    else:
        print("    ❌ Erro ao enviar análise")
        return False

    print()

    # 7. Testar alerta crítico
    print("[7] Testando alerta crítico...")
    success = notifier.send_critical_alert(
        alert_type="HEDGE",
        title="Hedge Ativado",
        description="Posição em prejuízo superior a $10. Hedge ativado automaticamente.",
        details={
            'Ticket': '123456',
            'Prejuízo': '-$12.50',
            'Ação': 'Posição oposta aberta'
        }
    )

    if success:
        print("    ✅ Alerta crítico enviado")
    else:
        print("    ❌ Erro ao enviar alerta")
        return False

    print()

    # 8. Testar alerta de erro
    print("[8] Testando alerta de erro...")
    success = notifier.send_error_alert(
        error_message="Erro ao obter rates para BTCUSDm",
        context="copy_rates_from_pos retornou None"
    )

    if success:
        print("    ✅ Alerta de erro enviado")
    else:
        print("    ❌ Erro ao enviar alerta de erro")
        return False

    print()
    print("="*70)
    print("✅ TODOS OS TESTES COMPLETADOS COM SUCESSO!")
    print("="*70)
    print()
    print("📱 As mensagens devem estar visíveis no seu canal do Telegram")
    print()
    return True

if __name__ == "__main__":
    success = test_telegram()
    sys.exit(0 if success else 1)
