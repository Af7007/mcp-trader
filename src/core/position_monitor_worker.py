#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSITION MONITOR WORKER
Worker dedicado para monitoramento contínuo de posições abertas.
Atualiza trailing stops em tempo real sem perder movimentos rápidos.

PROBLEMA RESOLVIDO:
- Agente principal checa a cada 15s → perde movimentos entre intervalos
- Worker checa a cada 1-2s → captura TODOS os movimentos importantes
"""

import logging
import threading
import time
from typing import Optional, Dict, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class PositionMonitorWorker:
    """
    Worker dedicado para monitoramento contínuo de posições abertas.

    Executa em thread separada do agente principal para garantir que
    trailing stops sejam atualizados em tempo real, sem perder movimentos
    rápidos entre os ciclos de análise.

    Características:
    - Thread dedicada com loop contínuo
    - Check interval configurável (padrão: 2s)
    - Atualiza trailing stops automaticamente
    - Não interfere com análise principal
    - Safe shutdown via flag
    """

    def __init__(
        self,
        mt5_client,
        symbol: str,
        check_interval: float = 2.0,
        trailing_callback: Optional[Callable] = None
    ):
        """
        Inicializa o worker de monitoramento.

        Args:
            mt5_client: Cliente MT5 para obter dados
            symbol: Símbolo a monitorar
            check_interval: Intervalo entre checks (segundos)
            trailing_callback: Função para atualizar trailing (agent method)
        """
        self.mt5 = mt5_client
        self.symbol = symbol
        self.check_interval = check_interval
        self.trailing_callback = trailing_callback

        # Threading
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._stop_flag = threading.Event()

        # Métricas
        self.total_checks = 0
        self.trailing_updates = 0
        self.last_check_time = None

        logger.info(f"Position Monitor Worker criado para {symbol} (check: {check_interval}s)")

    def start(self):
        """Inicia o worker em thread separada."""
        if self._running:
            logger.warning("Worker já está rodando")
            return

        self._running = True
        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        logger.info(f"Worker iniciado para {self.symbol}")

    def stop(self):
        """Para o worker gracefully."""
        if not self._running:
            return

        logger.info(f"Parando worker {self.symbol}...")
        self._running = False
        self._stop_flag.set()

        if self._thread:
            self._thread.join(timeout=5.0)

        logger.info(f"Worker parado. Checks: {self.total_checks}, Updates: {self.trailing_updates}")

    def is_running(self) -> bool:
        """Verifica se worker está ativo."""
        return self._running and self._thread and self._thread.is_alive()

    def _run_loop(self):
        """
        Loop principal do worker.
        Executa continuamente até _stop_flag ser setado.
        """
        logger.info(f"[WORKER] Loop iniciado para {self.symbol}")

        while not self._stop_flag.is_set():
            try:
                self._check_positions()
                self.total_checks += 1
                self.last_check_time = datetime.now()

                # Aguarda próximo ciclo (respeitando stop_flag)
                self._stop_flag.wait(timeout=self.check_interval)

            except Exception as e:
                logger.error(f"[WORKER] Erro no loop: {e}")
                time.sleep(self.check_interval)

        logger.info(f"[WORKER] Loop finalizado para {self.symbol}")

    def _check_positions(self):
        """
        Verifica posições abertas e atualiza trailing stops se necessário.
        """
        try:
            # Obter posições do símbolo
            positions = self.mt5.positions_get(symbol=self.symbol)

            if not positions:
                return  # Sem posições, nada a fazer

            # Obter preço atual
            tick = self.mt5.get_symbol_info_tick(self.symbol)
            if not tick:
                return

            # MT5 client retorna dict, não objeto
            current_bid = tick['bid'] if isinstance(tick, dict) else tick.bid
            current_ask = tick['ask'] if isinstance(tick, dict) else tick.ask

            # Processar cada posição
            for position in positions:
                # Chamar callback de trailing se fornecido
                if self.trailing_callback:
                    updated = self.trailing_callback(
                        position=position,
                        current_bid=current_bid,
                        current_ask=current_ask
                    )

                    if updated:
                        self.trailing_updates += 1

        except Exception as e:
            logger.error(f"[WORKER] Erro ao checar posições: {e}")

    def get_stats(self) -> Dict:
        """Retorna estatísticas do worker."""
        return {
            'running': self.is_running(),
            'total_checks': self.total_checks,
            'trailing_updates': self.trailing_updates,
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'check_interval': self.check_interval,
            'symbol': self.symbol
        }


class MultiSymbolMonitor:
    """
    Gerenciador de múltiplos workers (um por símbolo).
    Útil quando você roda BTC + Gold simultaneamente.
    """

    def __init__(self, mt5_client):
        self.mt5 = mt5_client
        self.workers: Dict[str, PositionMonitorWorker] = {}

    def add_symbol(
        self,
        symbol: str,
        check_interval: float = 2.0,
        trailing_callback: Optional[Callable] = None
    ):
        """Adiciona worker para um símbolo."""
        if symbol in self.workers:
            logger.warning(f"Worker para {symbol} já existe")
            return

        worker = PositionMonitorWorker(
            mt5_client=self.mt5,
            symbol=symbol,
            check_interval=check_interval,
            trailing_callback=trailing_callback
        )

        self.workers[symbol] = worker
        worker.start()

        logger.info(f"Worker adicionado para {symbol}")

    def remove_symbol(self, symbol: str):
        """Remove worker de um símbolo."""
        if symbol not in self.workers:
            return

        worker = self.workers[symbol]
        worker.stop()
        del self.workers[symbol]

        logger.info(f"Worker removido para {symbol}")

    def stop_all(self):
        """Para todos os workers."""
        logger.info("Parando todos os workers...")

        for symbol, worker in self.workers.items():
            worker.stop()

        self.workers.clear()
        logger.info("Todos os workers parados")

    def get_all_stats(self) -> Dict[str, Dict]:
        """Retorna stats de todos os workers."""
        return {
            symbol: worker.get_stats()
            for symbol, worker in self.workers.items()
        }


# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    from core.mt5_direct_client import get_mt5_client

    mt5 = get_mt5_client()

    def my_trailing_callback(position, current_bid, current_ask):
        """Exemplo de callback para trailing."""
        profit = position['profit']
        print(f"Position {position['ticket']}: Profit = ${profit:.2f}")

        # Aqui você implementaria a lógica de trailing stop
        # Retorna True se atualizou, False caso contrário
        return False

    # Criar worker
    worker = PositionMonitorWorker(
        mt5_client=mt5,
        symbol="BTCUSDc",
        check_interval=2.0,
        trailing_callback=my_trailing_callback
    )

    # Iniciar
    worker.start()

    try:
        # Rodar por 30 segundos
        time.sleep(30)
    finally:
        # Parar
        worker.stop()

        # Ver stats
        stats = worker.get_stats()
        print(f"\nEstatísticas: {stats}")
