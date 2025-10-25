#!/usr/bin/env python3
"""
Notificador de eventos do agente para Telegram
Envia notificações de operações, resumos e alertas para um canal do Telegram
"""

import os
import logging
from typing import Optional, Dict, List
from datetime import datetime

try:
    from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Gerencia notificações para Telegram"""

    def __init__(self):
        """Inicializa o notificador com as credenciais do .env"""
        self.enabled = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

        self.bot = None

        if self.enabled:
            if not TELEGRAM_AVAILABLE:
                logger.warning("⚠️  Telegram não disponível. Instale: pip install python-telegram-bot")
                self.enabled = False
                return

            if not self.bot_token or not self.chat_id:
                logger.warning("⚠️  TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados no .env")
                self.enabled = False
                return

            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("✅ Telegram Notifier inicializado com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Telegram: {e}")
                self.enabled = False

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Envia uma mensagem simples para o Telegram.

        Args:
            text: Texto da mensagem
            parse_mode: "HTML" ou "Markdown"

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.enabled or not self.bot:
            return False

        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"❌ Erro ao enviar mensagem Telegram: {e}")
            return False

    def send_trade_opened(
        self,
        ticket: int,
        symbol: str,
        trade_type: str,
        volume: float,
        entry_price: float,
        tp: float,
        sl: float,
        indicators: Dict
    ) -> bool:
        """
        Notifica abertura de nova posição.

        Args:
            ticket: Número do ticket
            symbol: Símbolo negociado
            trade_type: BUY ou SELL
            volume: Volume em lotes
            entry_price: Preço de entrada
            tp: Take Profit
            sl: Stop Loss
            indicators: Dicionário com indicadores

        Returns:
            True se enviado com sucesso
        """
        emoji_type = "🟢" if trade_type == "BUY" else "🔴"
        emoji_signal = "📈" if trade_type == "BUY" else "📉"

        message = f"""
<b>{emoji_type} POSIÇÃO ABERTA - {symbol}</b>

<b>📊 Tipo:</b> {trade_type}
<b>💰 Volume:</b> {volume} lots
<b>{emoji_signal} Entrada:</b> ${entry_price:,.2f}
<b>🎯 TP:</b> ${tp:,.2f}
<b>🛑 SL:</b> ${sl:,.2f}

<b>📉 Indicadores:</b>
• <b>RSI:</b> {indicators.get('rsi', 0):.1f}
• <b>MACD:</b> {indicators.get('macd', 0):+.2f}
• <b>Tendência:</b> {indicators.get('trend', 'N/A')}
• <b>ATR:</b> {indicators.get('atr', 0):.2f}

<b>⏰</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
<b>🎫 Ticket:</b> #{ticket}
"""
        return self.send_message(message.strip())

    def send_trade_closed(
        self,
        ticket: int,
        symbol: str,
        trade_type: str,
        entry_price: float,
        close_price: float,
        profit: float,
        duration_seconds: int,
        daily_stats: Dict
    ) -> bool:
        """
        Notifica fechamento de posição com resultado.

        Args:
            ticket: Número do ticket
            symbol: Símbolo negociado
            trade_type: BUY ou SELL
            entry_price: Preço de entrada
            close_price: Preço de saída
            profit: Lucro em dólares
            duration_seconds: Duração em segundos
            daily_stats: Estatísticas do dia

        Returns:
            True se enviado com sucesso
        """
        emoji_result = "✅" if profit > 0 else "❌"
        emoji_profit = "💚" if profit > 0 else "❤️"

        minutes = duration_seconds // 60
        seconds = duration_seconds % 60

        message = f"""
<b>{emoji_result} POSIÇÃO FECHADA</b>

<b>🎫 Ticket:</b> #{ticket}
<b>{emoji_profit} Resultado:</b> {profit:+.2f}$
<b>📊 Tipo:</b> {trade_type}
<b>⏱️  Duração:</b> {minutes}m {seconds}s

<b>📊 Preços:</b>
• <b>Entrada:</b> ${entry_price:,.2f}
• <b>Saída:</b> ${close_price:,.2f}
• <b>Diferença:</b> ${close_price - entry_price:+.2f}

<b>📈 Hoje ({symbol}):</b>
• <b>Lucro:</b> ${daily_stats.get('total_profit', 0):+.2f}
• <b>Win Rate:</b> {daily_stats.get('win_rate', 0):.1f}%
• <b>Streak:</b> {daily_stats.get('winning_streak', 0)} 🔥
• <b>Operações:</b> {daily_stats.get('trades_count', 0)}/999

<b>⏰</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        return self.send_message(message.strip())

    def send_periodic_summary(
        self,
        symbol: str,
        state: str,
        daily_stats: Dict,
        positions_open: int,
        indicators: Dict,
        time_period: str = "últimos 30 minutos"
    ) -> bool:
        """
        Envia resumo periódico do agente.

        Args:
            symbol: Símbolo negociado
            state: Estado do agente
            daily_stats: Estatísticas do dia
            positions_open: Número de posições abertas
            indicators: Indicadores técnicos
            time_period: Período do resumo

        Returns:
            True se enviado com sucesso
        """
        emoji_state = "🟢" if state == "trading" else "🟡" if state == "analyzing" else "⚪"

        message = f"""
<b>📊 RESUMO DO AGENTE - {symbol}</b>

<b>⏰</b> {time_period}

<b>{emoji_state} Estado:</b> {state.upper()}
<b>💼 Posições abertas:</b> {positions_open}
<b>💰 Lucro da sessão:</b> ${daily_stats.get('total_profit', 0):+.2f}

<b>📈 Estatísticas:</b>
• <b>Total:</b> {daily_stats.get('trades_count', 0)} operações
• <b>✅ Vencedoras:</b> {daily_stats.get('wins', 0)} ({daily_stats.get('win_rate', 0):.1f}%)
• <b>❌ Perdedoras:</b> {daily_stats.get('losses', 0)}
• <b>🔥 Streak:</b> {daily_stats.get('winning_streak', 0)}

<b>📉 Mercado:</b>
• <b>Preço:</b> ${indicators.get('current_price', 0):,.2f}
• <b>Tendência:</b> {indicators.get('trend', 'N/A')}
• <b>RSI:</b> {indicators.get('rsi', 0):.1f}
• <b>MACD:</b> {indicators.get('macd', 0):+.2f}

<b>⏰</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        return self.send_message(message.strip())

    def send_market_analysis(
        self,
        symbol: str,
        indicators: Dict,
        signal: str
    ) -> bool:
        """
        Envia análise técnica do mercado.

        Args:
            symbol: Símbolo negociado
            indicators: Indicadores técnicos
            signal: Sinal gerado (BUY, SELL, NEUTRAL)

        Returns:
            True se enviado com sucesso
        """
        emoji_signal = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"

        message = f"""
<b>📊 ANÁLISE DE MERCADO - {symbol}</b>

<b>{emoji_signal} Sinal:</b> <b>{signal}</b>

<b>📉 Indicadores:</b>
• <b>Preço:</b> ${indicators.get('current_price', 0):,.2f}
• <b>Tendência:</b> {indicators.get('trend', 'N/A')}
• <b>RSI:</b> {indicators.get('rsi', 0):.1f}
• <b>MACD:</b> {indicators.get('macd', 0):+.2f}
• <b>ATR:</b> {indicators.get('atr', 0):.2f}

<b>📈 Médias Móveis:</b>
• <b>SMA20:</b> ${indicators.get('sma_20', 0):,.2f}
• <b>SMA50:</b> ${indicators.get('sma_50', 0):,.2f}

<b>🔷 Bollinger Bands:</b>
• <b>Upper:</b> ${indicators.get('bb_upper', 0):,.2f}
• <b>Middle:</b> ${indicators.get('bb_middle', 0):,.2f}
• <b>Lower:</b> ${indicators.get('bb_lower', 0):,.2f}

<b>⏰</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        return self.send_message(message.strip())

    def send_critical_alert(
        self,
        alert_type: str,
        title: str,
        description: str,
        details: Dict = None
    ) -> bool:
        """
        Envia alerta crítico.

        Args:
            alert_type: Tipo de alerta (HEDGE, ERROR, LIMIT, etc)
            title: Título do alerta
            description: Descrição do problema
            details: Detalhes adicionais

        Returns:
            True se enviado com sucesso
        """
        emoji_alert = "🚨" if alert_type == "ERROR" else "🛡️" if alert_type == "HEDGE" else "⚠️"

        details_text = ""
        if details:
            details_text = "\n\n<b>Detalhes:</b>\n"
            for key, value in details.items():
                details_text += f"• <b>{key}:</b> {value}\n"

        message = f"""
<b>{emoji_alert} ALERTA CRÍTICO</b>

<b>Tipo:</b> {alert_type}
<b>Título:</b> {title}
<b>Descrição:</b> {description}{details_text}
<b>⏰</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        return self.send_message(message.strip())

    def send_error_alert(self, error_message: str, context: str = "") -> bool:
        """
        Envia alerta de erro.

        Args:
            error_message: Mensagem de erro
            context: Contexto do erro (opcional)

        Returns:
            True se enviado com sucesso
        """
        return self.send_critical_alert(
            alert_type="ERROR",
            title="Erro no Agente",
            description=error_message,
            details={"Contexto": context} if context else None
        )


# Instância global
_telegram_notifier: Optional[TelegramNotifier] = None


def get_telegram_notifier() -> TelegramNotifier:
    """Retorna instância singleton do notificador Telegram."""
    global _telegram_notifier
    if _telegram_notifier is None:
        _telegram_notifier = TelegramNotifier()
    return _telegram_notifier
