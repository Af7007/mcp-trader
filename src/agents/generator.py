#!/usr/bin/env python3
"""
Agent Generator - Cria agentes a partir de linguagem natural
Parse de comandos como: "Crie agente XAUUSD com RSI, TP $3, SL $1"
"""

import re
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Tuple, Union

logger = logging.getLogger(__name__)


class IndicatorType(str, Enum):
    """Tipos de indicadores suportados"""
    RSI = "RSI"
    BOLLINGER = "BOLLINGER"
    MA = "MA"  # Moving Average
    ATR = "ATR"  # Average True Range
    MACD = "MACD"
    STOCHASTIC = "STOCHASTIC"
    EMA = "EMA"  # Exponential Moving Average


class OrderType(str, Enum):
    """Tipos de ordem"""
    BUY = "BUY"
    SELL = "SELL"
    BUY_SELL = "BUY_SELL"  # Ambos


class AgentStrategy(str, Enum):
    """Estratégias de trading suportadas"""
    SINGLE_ASSET = "SINGLE_ASSET"  # Agente tradicional
    HEDGE_PAIR = "HEDGE_PAIR"      # Hedge entre dois pares correlacionados
    BASKET_HEDGE = "BASKET_HEDGE"  # Hedge múltiplo com vários ativos


@dataclass
class Indicator:
    """Configuração de indicador"""
    type: IndicatorType
    period: int = 14
    threshold_high: float = 70.0
    threshold_low: float = 30.0
    params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}


@dataclass
class AgentConfig:
    """Configuração de agente"""
    id: str
    name: str
    symbol: str
    order_type: OrderType
    volume: float
    indicators: List[Indicator]
    strategy: AgentStrategy = AgentStrategy.SINGLE_ASSET
    hedge_symbols: Optional[List[str]] = None  # Para estratégias de hedge
    hedge_volumes: Optional[List[float]] = None  # Volumes relativos para hedge
    correlation_threshold: float = 0.7  # Correlação mínima para hedge
    max_hedge_positions: int = 2  # Máximo de posições no hedge
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_stop: Optional[float] = None
    max_positions: int = 1
    timeframe: int = 60  # em minutos
    status: str = "active"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.hedge_symbols is None:
            self.hedge_symbols = []
        if self.hedge_volumes is None:
            self.hedge_volumes = []


class AgentGenerator:
    """Gerador de agentes a partir de linguagem natural"""
    
    # Símbolos conhecidos
    KNOWN_SYMBOLS = {
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD', 'NZDUSD',
        'XAUUSD', 'XAGUSD', 'BTCUSD', 'ETHUSD',
        'SPX500', 'US100', 'US30'
    }
    
    def __init__(self):
        self.agents: Dict[str, AgentConfig] = {}
        logger.info("✅ Agent Generator inicializado")
    
    def _is_hedge_command(self, command: str) -> bool:
        """Verificar se é um comando de hedge"""
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in [
            'hedge', 'cobertura', 'protegidos', 'par seguro',
            'estrategia de hedge', 'posição coberta'
        ])

    def parse_command(self, command: str) -> Optional[AgentConfig]:
        """
        Parse de comando em linguagem natural

        Exemplos:
        - "Crie agente XAUUSD com RSI, TP $3, SL $1"
        - "Agente EURUSD: compre quando RSI < 30, venda quando RSI > 70, TP 50 pips, SL 20 pips"
        - "Criar agente GBPUSD com Bollinger Bands, volume 0.1, TP 100, SL 50"
        - "Criar agente de hedge entre EURUSD e GBPUSD com correlação > 70%"
        """
        try:
            logger.info(f"🔍 Parseando comando: {command}")

            # Verificar se é comando de hedge
            if self._is_hedge_command(command):
                return self._parse_hedge_command(command)
            else:
                return self._parse_single_asset_command(command)

        except Exception as e:
            logger.error(f"❌ Erro ao parsear comando: {e}")
            return None

    def _parse_single_asset_command(self, command: str) -> Optional[AgentConfig]:
        """Parse de comando para agente single asset"""

        # Extrair símbolo
        symbol = self._extract_symbol(command)
        if not symbol:
            logger.error("❌ Símbolo não encontrado no comando")
            return None

        # Extrair tipo de ordem
        order_type = self._extract_order_type(command)

        # Extrair volume
        volume = self._extract_volume(command)
        if volume is None:
            volume = 0.1  # Default

        # Extrair indicadores
        indicators = self._extract_indicators(command)
        if not indicators:
            logger.warning("⚠️  Nenhum indicador encontrado, usando RSI padrão")
            indicators = [Indicator(type=IndicatorType.RSI)]

        # Extrair TP/SL
        take_profit = self._extract_take_profit(command)
        stop_loss = self._extract_stop_loss(command)
        trailing_stop = self._extract_trailing_stop(command)

        # Extrair timeframe
        timeframe = self._extract_timeframe(command)

        # Gerar nome do agente
        agent_name = self._generate_agent_name(symbol, indicators)

        # Criar configuração
        agent_config = AgentConfig(
            id=str(uuid.uuid4())[:8],
            name=agent_name,
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            indicators=indicators,
            strategy=AgentStrategy.SINGLE_ASSET,
            take_profit=take_profit,
            stop_loss=stop_loss,
            trailing_stop=trailing_stop,
            timeframe=timeframe
        )

        logger.info(f"✅ Agente single asset parseado com sucesso: {agent_name}")
        return agent_config

    def _parse_hedge_command(self, command: str) -> Optional[AgentConfig]:
        """Parse de comando para agente de hedge"""
        logger.info("🔄 Detectado comando de hedge, parseando...")

        # Extrair símbolos para hedge
        hedge_symbols = self._extract_hedge_symbols(command)
        if len(hedge_symbols) < 2:
            logger.error("❌ Hedge precisa de pelo menos 2 símbolos")
            return None

        # Símbolo principal é o primeiro
        main_symbol = hedge_symbols[0]

        # Extrair volumes para hedge
        volumes = self._extract_hedge_volumes(command, len(hedge_symbols))
        main_volume = volumes[0]

        # Extrair indicadores
        indicators = self._extract_indicators(command)
        if not indicators:
            logger.warning("⚠️  Nenhum indicador encontrado, usando RSI padrão")
            indicators = [Indicator(type=IndicatorType.RSI)]

        # Extrair correlação
        correlation_threshold = self._extract_correlation_threshold(command)

        # Extrair TP/SL
        take_profit = self._extract_take_profit(command)
        stop_loss = self._extract_stop_loss(command)
        trailing_stop = self._extract_trailing_stop(command)

        # Extrair timeframe
        timeframe = self._extract_timeframe(command)

        # Gerar nome do agente
        agent_name = self._generate_hedge_agent_name(hedge_symbols, indicators)

        # Criar configuração
        agent_config = AgentConfig(
            id=str(uuid.uuid4())[:8],
            name=agent_name,
            symbol=main_symbol,
            order_type=OrderType.BUY_SELL,  # Hedge sempre tem ambas as direções
            volume=main_volume,
            indicators=indicators,
            strategy=AgentStrategy.HEDGE_PAIR if len(hedge_symbols) == 2 else AgentStrategy.BASKET_HEDGE,
            hedge_symbols=hedge_symbols,
            hedge_volumes=volumes,
            correlation_threshold=correlation_threshold,
            take_profit=take_profit,
            stop_loss=stop_loss,
            trailing_stop=trailing_stop,
            timeframe=timeframe
        )

        logger.info(f"✅ Agente de hedge parseado com sucesso: {agent_name}")
        return agent_config
    
    def _extract_symbol(self, command: str) -> Optional[str]:
        """Extrair símbolo (ex: EURUSD, XAUUSD)"""
        command_upper = command.upper()
        
        # Procurar símbolos conhecidos
        for symbol in self.KNOWN_SYMBOLS:
            if symbol in command_upper:
                # Adicionar 'c' se não tiver
                return symbol + 'c'
        
        # Se não encontrou símbolo conhecido, procurar padrão genérico
        # Procurar padrão: XXXYYY (exatamente 6 letras)
        pattern = r'\b([A-Z]{3}[A-Z]{3})\b'
        match = re.search(pattern, command_upper)
        if match:
            symbol = match.group(1)
            # Adicionar 'c' se não tiver
            return symbol + 'c'
        
        return None
    
    def _extract_order_type(self, command: str) -> OrderType:
        """Extrair tipo de ordem (BUY, SELL, BUY_SELL)"""
        command_lower = command.lower()
        
        if 'venda' in command_lower or 'sell' in command_lower:
            if 'compra' in command_lower or 'buy' in command_lower:
                return OrderType.BUY_SELL
            return OrderType.SELL
        
        return OrderType.BUY  # Default
    
    def _extract_volume(self, command: str) -> Optional[float]:
        """Extrair volume (ex: 0.1, 0.01, 1.0)"""
        # Procurar padrão: volume 0.1, 0.01 lots, etc
        pattern = r'(?:volume|vol|lots?)\s*[:\s]*(\d+\.?\d*)'
        match = re.search(pattern, command.lower())
        if match:
            return float(match.group(1))
        
        # Procurar padrão: 0.1, 0.01
        pattern = r'\b(\d+\.\d+)\b'
        matches = re.findall(pattern, command)
        if matches:
            # Retornar o primeiro número que parece ser volume (entre 0.01 e 10)
            for num in matches:
                val = float(num)
                if 0.01 <= val <= 10:
                    return val
        
        return None
    
    def _extract_indicators(self, command: str) -> List[Indicator]:
        """Extrair indicadores (RSI, Bollinger, MA, etc)"""
        indicators = []
        command_upper = command.upper()
        
        # RSI
        if 'RSI' in command_upper:
            period = self._extract_period(command, 'RSI')
            threshold_high = self._extract_threshold(command, 'RSI', 'high', 70)
            threshold_low = self._extract_threshold(command, 'RSI', 'low', 30)
            indicators.append(Indicator(
                type=IndicatorType.RSI,
                period=period,
                threshold_high=threshold_high,
                threshold_low=threshold_low
            ))
        
        # Bollinger Bands
        if 'BOLLINGER' in command_upper or 'BANDS' in command_upper:
            period = self._extract_period(command, 'BOLLINGER', 20)
            indicators.append(Indicator(
                type=IndicatorType.BOLLINGER,
                period=period
            ))
        
        # Moving Average
        if 'MA' in command_upper or 'MOVING AVERAGE' in command_upper:
            period = self._extract_period(command, 'MA', 50)
            indicators.append(Indicator(
                type=IndicatorType.MA,
                period=period
            ))
        
        # EMA
        if 'EMA' in command_upper:
            period = self._extract_period(command, 'EMA', 12)
            indicators.append(Indicator(
                type=IndicatorType.EMA,
                period=period
            ))
        
        # MACD
        if 'MACD' in command_upper:
            indicators.append(Indicator(type=IndicatorType.MACD))
        
        # ATR
        if 'ATR' in command_upper:
            period = self._extract_period(command, 'ATR', 14)
            indicators.append(Indicator(
                type=IndicatorType.ATR,
                period=period
            ))
        
        # Stochastic
        if 'STOCHASTIC' in command_upper:
            period = self._extract_period(command, 'STOCHASTIC', 14)
            indicators.append(Indicator(
                type=IndicatorType.STOCHASTIC,
                period=period
            ))
        
        return indicators
    
    def _extract_period(self, command: str, indicator: str, default: int = 14) -> int:
        """Extrair período de indicador (ex: RSI 14, MA 50)"""
        pattern = rf'{indicator}\s*(?:período|period)?\s*(\d+)'
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return default
    
    def _extract_threshold(self, command: str, indicator: str, direction: str, default: float) -> float:
        """Extrair threshold de indicador (ex: RSI > 70, RSI < 30)"""
        if direction == 'high':
            pattern = rf'{indicator}\s*[>>=]+\s*(\d+)'
        else:
            pattern = rf'{indicator}\s*[<<=]+\s*(\d+)'
        
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return default
    
    def _extract_take_profit(self, command: str) -> Optional[float]:
        """Extrair Take Profit (ex: TP $3, TP 50 pips)"""
        # TP em dólares
        pattern = r'(?:TP|TAKE\s*PROFIT)\s*\$?\s*(\d+\.?\d*)'
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None
    
    def _extract_stop_loss(self, command: str) -> Optional[float]:
        """Extrair Stop Loss (ex: SL $1, SL 20 pips)"""
        # SL em dólares
        pattern = r'(?:SL|STOP\s*LOSS)\s*\$?\s*(\d+\.?\d*)'
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None
    
    def _extract_trailing_stop(self, command: str) -> Optional[float]:
        """Extrair Trailing Stop (ex: trailing stop 20 pips)"""
        pattern = r'(?:TRAILING\s*STOP)\s*(\d+\.?\d*)'
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None
    
    def _extract_timeframe(self, command: str) -> int:
        """Extrair timeframe em minutos (ex: H1 = 60, M15 = 15)"""
        command_upper = command.upper()
        
        # H1, H4, etc
        if 'H1' in command_upper:
            return 60
        if 'H4' in command_upper:
            return 240
        if 'H8' in command_upper:
            return 480
        if 'D1' in command_upper or 'DAILY' in command_upper:
            return 1440
        
        # M5, M15, M30, etc
        pattern = r'M(\d+)'
        match = re.search(pattern, command_upper)
        if match:
            return int(match.group(1))
        
        return 60  # Default: H1
    
    def _extract_hedge_symbols(self, command: str) -> List[str]:
        """Extrair símbolos para hedge (ex: entre EURUSD e GBPUSD)"""
        symbols = []
        command_upper = command.upper()

        # Procurar padrão: entre X e Y, ou X e Y
        patterns = [
            r'entre\s+([A-Z]{6})\s+e\s+([A-Z]{6})',
            r'entre\s+([A-Z]{6}),?\s+e\s+([A-Z]{6})',
            r'([A-Z]{6})\s+e\s+([A-Z]{6})',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, command_upper, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        for symbol in match:
                            if symbol in self.KNOWN_SYMBOLS:
                                symbols.append(symbol + 'c')
                    else:
                        if match in self.KNOWN_SYMBOLS:
                            symbols.append(match + 'c')

        # Remover duplicatas mantendo ordem
        seen = set()
        unique_symbols = []
        for symbol in symbols:
            if symbol not in seen:
                unique_symbols.append(symbol)
                seen.add(symbol)

        return unique_symbols

    def _extract_hedge_volumes(self, command: str, num_symbols: int) -> List[float]:
        """Extrair volumes para hedge"""
        volumes = []

        # Procurar volumes específicos
        volume_patterns = [
            r'volume[s]?\s*:?\s*([\d\.,]+)',
            r'volume\s+(\d+\.?\d*)',
            r'lot[s]?\s*:?\s*(\d+\.?\d*)'
        ]

        found_volumes = []
        for pattern in volume_patterns:
            matches = re.findall(pattern, command.lower())
            if matches:
                for match in matches:
                    try:
                        # Converter string com possíveis vírgulas para float
                        vol_str = match.replace(',', '.')
                        vol = float(vol_str)
                        if 0.01 <= vol <= 10:
                            found_volumes.append(vol)
                    except ValueError:
                        continue

        # Se encontrou volumes específicos, usar eles
        if len(found_volumes) >= num_symbols:
            volumes = found_volumes[:num_symbols]
        else:
            # Usar volume padrão
            default_volume = 0.1
            volumes = [default_volume] * num_symbols

        return volumes

    def _extract_correlation_threshold(self, command: str) -> float:
        """Extrair threshold de correlação (ex: correlação > 70%)"""
        # Procurar padrões de correlação
        patterns = [
            r'correla[cç][aã]o\s*[><=]+\s*(\d+(?:\.\d+)?)%?',
            r'correlação\s+de\s+(\d+(?:\.\d+)?)%?',
            r'correlation\s*[><=]+\s*(\d+(?:\.\d+)?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return float(match.group(1)) / 100.0  # Converter para decimal

        return 0.7  # Default: 70%

    def _generate_agent_name(self, symbol: str, indicators: List[Indicator]) -> str:
        """Gerar nome do agente"""
        indicator_names = '_'.join([ind.type.value for ind in indicators[:2]])
        return f"{symbol}_{indicator_names}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _generate_hedge_agent_name(self, symbols: List[str], indicators: List[Indicator]) -> str:
        """Gerar nome do agente de hedge"""
        symbols_short = [s[:-1] for s in symbols]  # Remover 'c' dos símbolos
        symbols_name = '_'.join(symbols_short[:3])  # Máximo 3 símbolos no nome
        indicator_names = '_'.join([ind.type.value for ind in indicators[:2]])

        strategy = "HEDGE"
        return f"{strategy}_{symbols_name}_{indicator_names}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def create_agent(self, command: str) -> Optional[AgentConfig]:
        """Criar agente a partir de comando"""
        agent_config = self.parse_command(command)
        if agent_config:
            self.agents[agent_config.id] = agent_config
            logger.info(f"✅ Agente criado: {agent_config.name} (ID: {agent_config.id})")
            return agent_config
        return None
    
    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        """Obter agente por ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[AgentConfig]:
        """Listar todos os agentes"""
        return list(self.agents.values())
    
    def delete_agent(self, agent_id: str) -> bool:
        """Deletar agente"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"✅ Agente deletado: {agent_id}")
            return True
        return False
    
    def export_agent(self, agent_id: str) -> Optional[Dict]:
        """Exportar configuração do agente"""
        agent = self.get_agent(agent_id)
        if agent:
            return {
                'id': agent.id,
                'name': agent.name,
                'symbol': agent.symbol,
                'order_type': agent.order_type.value,
                'volume': agent.volume,
                'indicators': [
                    {
                        'type': ind.type.value,
                        'period': ind.period,
                        'threshold_high': ind.threshold_high,
                        'threshold_low': ind.threshold_low,
                        'params': ind.params
                    }
                    for ind in agent.indicators
                ],
                'take_profit': agent.take_profit,
                'stop_loss': agent.stop_loss,
                'trailing_stop': agent.trailing_stop,
                'max_positions': agent.max_positions,
                'timeframe': agent.timeframe,
                'status': agent.status,
                'created_at': agent.created_at.isoformat()
            }
        return None


# Exemplos de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    generator = AgentGenerator()
    
    # Exemplo 1: RSI simples
    print("\n" + "="*60)
    print("Exemplo 1: RSI simples")
    print("="*60)
    agent1 = generator.create_agent(
        "Crie agente XAUUSD com RSI, TP $3, SL $1, volume 0.1"
    )
    if agent1:
        print(f"✅ Agente criado: {agent1.name}")
        print(f"   ID: {agent1.id}")
        print(f"   Símbolo: {agent1.symbol}")
        print(f"   Volume: {agent1.volume}")
        print(f"   TP: ${agent1.take_profit}, SL: ${agent1.stop_loss}")
        print(f"   Indicadores: {[ind.type.value for ind in agent1.indicators]}")
    
    # Exemplo 2: Bollinger Bands
    print("\n" + "="*60)
    print("Exemplo 2: Bollinger Bands")
    print("="*60)
    agent2 = generator.create_agent(
        "Agente EURUSD com Bollinger Bands período 20, volume 0.05, TP 50, SL 20"
    )
    if agent2:
        print(f"✅ Agente criado: {agent2.name}")
        print(f"   Indicadores: {[ind.type.value for ind in agent2.indicators]}")
    
    # Exemplo 3: Múltiplos indicadores
    print("\n" + "="*60)
    print("Exemplo 3: Múltiplos indicadores")
    print("="*60)
    agent3 = generator.create_agent(
        "Criar agente GBPUSD com RSI e MA 50, compre quando RSI < 30 e preço > MA, volume 0.1"
    )
    if agent3:
        print(f"✅ Agente criado: {agent3.name}")
        print(f"   Indicadores: {[ind.type.value for ind in agent3.indicators]}")
    
    # Listar todos os agentes
    print("\n" + "="*60)
    print("Agentes criados:")
    print("="*60)
    for agent in generator.list_agents():
        print(f"  • {agent.name} ({agent.id})")
