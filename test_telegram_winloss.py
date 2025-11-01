#!/usr/bin/env python3
"""
Teste das notificações WIN/LOSS do Telegram
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.core.telegram_notifier import get_telegram_notifier
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_telegram_messages():
    """Testa se as mensagens WIN/LOSS estão sendo criadas corretamente"""
    logger.info("="*80)
    logger.info("🧪 TESTE DE NOTIFICAÇÕES WIN/LOSS")
    logger.info("="*80)

    try:
        notifier = get_telegram_notifier()

        if not notifier.enabled:
            logger.warning("\n⚠️  TELEGRAM DESATIVADO!")
            logger.warning("Configure em .env:")
            logger.warning("  TELEGRAM_ENABLED=true")
            logger.warning("  TELEGRAM_BOT_TOKEN=seu_token")
            logger.warning("  TELEGRAM_CHAT_ID=seu_chat_id")
            return

        logger.info("\n✅ Telegram HABILITADO")
        logger.info(f"   Bot Token: {notifier.bot_token[:20]}..." if notifier.bot_token else "   Bot Token: NÃO CONFIGURADO")
        logger.info(f"   Chat ID: {notifier.chat_id}")

        # Teste 1: WIN
        logger.info("\n" + "="*80)
        logger.info("TESTE 1: NOTIFICAÇÃO WIN")
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
            logger.info("✅ Mensagem WIN enviada com sucesso ao Telegram!")
        else:
            logger.error("❌ Erro ao enviar mensagem WIN")

        # Teste 2: LOSS
        logger.info("\n" + "="*80)
        logger.info("TESTE 2: NOTIFICAÇÃO LOSS")
        logger.info("="*80)

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
            logger.info("✅ Mensagem LOSS enviada com sucesso ao Telegram!")
        else:
            logger.error("❌ Erro ao enviar mensagem LOSS")

        # Resumo
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMO DO TESTE")
        logger.info("="*80)

        if result_win and result_loss:
            logger.info("✅✅✅ TUDO FUNCIONANDO CORRETAMENTE! ✅✅✅")
            logger.info("\nVocê deve ter recebido 2 mensagens no Telegram:")
            logger.info("  1. ✅ WIN com contadores")
            logger.info("  2. ❌ LOSS com contadores")
            logger.info("\nVerifique seu Telegram agora!")
        else:
            logger.error("❌ Há um problema nas notificações")
            if not result_win:
                logger.error("  • Mensagem WIN falhou")
            if not result_loss:
                logger.error("  • Mensagem LOSS falhou")

    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}", exc_info=True)

if __name__ == '__main__':
    test_telegram_messages()
