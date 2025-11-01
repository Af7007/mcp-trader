#!/usr/bin/env python3
"""
Teste direto do Telegram com variáveis de ambiente carregadas
"""

import sys
import os

# Carregar .env explicitamente
from dotenv import load_dotenv
load_dotenv()

# Mostrar se as variáveis foram carregadas
bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

print("="*80)
print("VERIFICACAO DE VARIAVEIS DE AMBIENTE")
print("="*80)
print(f"\nTELEGRAM_ENABLED: {os.getenv('TELEGRAM_ENABLED', 'NÃO CONFIGURADO')}")
print(f"TELEGRAM_BOT_TOKEN: {bot_token[:20] if bot_token else 'NÃO CONFIGURADO'}...")
print(f"TELEGRAM_CHAT_ID: {chat_id if chat_id else 'NÃO CONFIGURADO'}")

if not bot_token or not chat_id:
    print("\n❌ ERRO: Variáveis não estão configuradas!")
    print("\nConfigure em .env:")
    print("  TELEGRAM_BOT_TOKEN=seu_token_aqui")
    print("  TELEGRAM_CHAT_ID=seu_chat_id_aqui")
    sys.exit(1)

print("\n✅ Variáveis carregadas com sucesso!\n")

sys.path.insert(0, os.path.dirname(__file__))

from src.core.telegram_notifier import TelegramNotifier
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_win_loss_messages():
    """Testa notificações WIN/LOSS"""
    logger.info("="*80)
    logger.info("🧪 TESTE DE NOTIFICAÇÕES WIN/LOSS")
    logger.info("="*80)

    try:
        # Criar notifier diretamente
        notifier = TelegramNotifier()

        if not notifier.enabled:
            logger.error("\n❌ TELEGRAM DESATIVADO!")
            logger.error(f"   Bot Token vazio: {not notifier.bot_token}")
            logger.error(f"   Chat ID vazio: {not notifier.chat_id}")
            logger.error(f"   Bot object: {notifier.bot}")
            return

        logger.info("\n✅ Telegram INICIALIZADO")

        # TESTE 1: WIN
        logger.info("\n" + "="*80)
        logger.info("📊 TESTE 1: NOTIFICAÇÃO WIN")
        logger.info("="*80)

        result_win = notifier.send_trade_closed(
            ticket=125967293,
            symbol="XAUUSDm",
            trade_type="SELL",
            entry_price=4070.00,
            close_price=4065.00,
            profit=5.00,
            duration_seconds=525,
            daily_stats={
                'total_profit': 27.50,
                'win_rate': 71.4,
                'winning_streak': 2,
                'trades_count': 7,
                'wins': 5,
                'losses': 2
            },
            total_wins=5,
            total_losses=2
        )

        if result_win:
            logger.info("✅ Mensagem WIN enviada ao Telegram!")
        else:
            logger.error("❌ Falha ao enviar WIN")

        # TESTE 2: LOSS
        logger.info("\n" + "="*80)
        logger.info("📊 TESTE 2: NOTIFICAÇÃO LOSS")
        logger.info("="*80)

        import time
        time.sleep(2)  # Aguardar um pouco entre mensagens

        result_loss = notifier.send_trade_closed(
            ticket=125967294,
            symbol="XAUUSDm",
            trade_type="SELL",
            entry_price=4068.00,
            close_price=4073.00,
            profit=-5.00,
            duration_seconds=312,
            daily_stats={
                'total_profit': 22.50,
                'win_rate': 62.5,
                'winning_streak': 0,
                'trades_count': 8,
                'wins': 5,
                'losses': 3
            },
            total_wins=5,
            total_losses=3
        )

        if result_loss:
            logger.info("✅ Mensagem LOSS enviada ao Telegram!")
        else:
            logger.error("❌ Falha ao enviar LOSS")

        # RESUMO
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMO")
        logger.info("="*80)

        if result_win and result_loss:
            logger.info("\n✅✅✅ SUCESSO! ✅✅✅")
            logger.info("\nVocê deve ter recebido 2 mensagens no Telegram:")
            logger.info("  1️⃣  ✅ WIN com Wins: 5, Losses: 2")
            logger.info("  2️⃣  ❌ LOSS com Wins: 5, Losses: 3")
            logger.info("\n🚀 As notificações estão funcionando perfeitamente!")
        else:
            logger.error("\n❌ Falha em uma ou mais mensagens")

    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)

if __name__ == '__main__':
    test_win_loss_messages()
