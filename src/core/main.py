#!/usr/bin/env python3
"""
Worker em Segundo Plano para o Trading Chatbot.

Responsabilidades:
- Monitorar trades abertos no banco de dados.
- Verificar se os trades foram fechados no MT5.
- Atualizar o status dos trades no banco de dados.
- (Futuro) Analisar o mercado e abrir novas operações.
"""

import sys
import os
import time
import logging
import requests
import uuid

# Adicionar o diretório 'src' ao path para encontrar os módulos core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TradingWorker")

MT5_MCP_URL = "http://localhost:8000/mcp"


def call_mt5_tool(tool_name: str, **kwargs):
    """Função síncrona para chamar uma ferramenta do MT5 MCP."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": kwargs}
    }
    try:
        response = requests.post(MT5_MCP_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")
        return result.get("result")
    except requests.exceptions.RequestException as e:
        logger.error(f"Falha na comunicação com o MT5 MCP: {e}")
        return None


def monitor_open_trades():
    """
    Busca trades abertos no DB e verifica seu status no MT5.
    """
    logger.info("Verificando trades abertos...")
    open_trades = database.get_open_trades()

    if not open_trades:
        logger.info("Nenhum trade aberto para monitorar.")
        return

    # Obter todas as posições abertas de uma vez para otimizar
    active_positions_data = call_mt5_tool("positions_get")
    if active_positions_data is None:
        logger.error("Não foi possível obter posições ativas do MT5. Pulando ciclo.")
        return

    active_tickets = {pos['ticket'] for pos in active_positions_data}

    for trade in open_trades:
        trade_ticket = trade['ticket']
        logger.info(f"Monitorando trade com ticket: {trade_ticket}")

        # Se o ticket do trade não está mais na lista de posições ativas, ele foi fechado.
        if trade_ticket not in active_tickets:
            logger.info(f"Trade {trade_ticket} parece ter sido fechado. Verificando histórico.")

            # Buscar o resultado no histórico de deals (negócios)
            deals = call_mt5_tool("history_deals_get", position=trade_ticket)
            if deals:
                # Um trade pode ter múltiplos deals (abertura, fechamento, etc.)
                # O lucro/prejuízo final é a soma dos profits de todos os deals da posição.
                final_profit = sum(d['profit'] for d in deals)
                closing_deal = max(deals, key=lambda d: d['time']) # O último deal é o de fechamento
                reason = "closed" # Razão genérica por enquanto

                logger.info(f"Trade {trade_ticket} fechado com lucro/prejuízo de: {final_profit}")
                database.update_trade_status(trade_ticket, "closed", final_profit, reason)
            else:
                logger.warning(f"Não foi possível encontrar o histórico do deal para o trade {trade_ticket}.")


def analyze_market_for_opportunities():
    """
    (Placeholder) Função para analisar o mercado e criar novas ordens.
    """
    logger.info("Analisando mercado por novas oportunidades (lógica a ser implementada)...")
    # Exemplo:
    # 1. Chamar `call_mt5_tool("copy_rates_from_pos", ...)` para obter dados de velas.
    # 2. Calcular indicadores (RSI, Médias Móveis, etc.).
    # 3. Se uma condição de entrada for atendida:
    #    a. Chamar `call_mt5_tool("buy_market", ...)`
    #    b. Se a ordem for bem-sucedida, registrar no DB com `database.create_trade(...)`
    pass


if __name__ == "__main__":
    logger.info("🚀 Iniciando Worker de Trading em segundo plano...")
    database.setup_database()  # Garante que o DB e as tabelas existam

    while True:
        try:
            monitor_open_trades()
            analyze_market_for_opportunities()
        except Exception as e:
            logger.error(f"Erro no loop principal do worker: {e}", exc_info=True)

        logger.info("Ciclo do worker concluído. Aguardando 60 segundos...")
        time.sleep(60)