#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementacao de Protecoes Avancadas para Sistemas Automatizados XAUUSD
Based nas recomendacoes dos relatorios de analise de losses
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ProtecoesAutomatizadasXAUUSD:
    """
    Classe com implementacoes de protecoes para os sistemas automatizados
    Baseado na analise de losses expressivos identificados
    """
    
    def __init__(self):
        # Parametros de protecao baseados na analise
        self.parametros = {
            'volume_maximo': 0.20,  # Reduzido de 0.34
            'volume_ultra_seguro': 0.01,  # Configuracao atual
            'stop_loss_maximo_pct': 0.02,  # 2% maximo
            'trailing_gain_trigger': 0.005,  # 0.5% gain para ativar
            'trailing_break_even': 0.01,  # 1% gain para break-even
            'pausa_losses_consecutivos': 2,  # Pausar apos 2 losses
            'pausa_loss_grande': 200,  # Pausar apos loss > $200
            'volume_maximo_24h': 1.0,  # Volume maximo diario
            'max_trades_dia': 20  # Maximo trades por dia
        }
        
        # Indicadores tecnicos obrigatorios
        self.indicadores_obrigatorios = ['RSI', 'MACD', 'Support_Resistance']
        
        # Sistema de monitoreo
        self.trades_hoje = []
        self.losses_consecutivos = 0
        self.sistema_pausado = False
    
    def verificar_entrada_permitida(self, symbol, volume, sistema):
        """
        Verifica se a entrada e permitida baseada nas protecoes
        """
        verificacoes = {
            'volume_ok': volume <= self.parametros['volume_maximo'],
            'volume_ultra_seguro_ok': volume <= self.parametros['volume_ultra_seguro'],
            'sistema_ativo': not self.sistema_pausado,
            'limite_diario_ok': self._verificar_limite_diario(),
            'losses_consecutivos_ok': self.losses_consecutivos < self.parametros['pausa_losses_consecutivos']
        }
        
        # Para XAUUSD, aplicar regras mais restritivas
        if 'XAU' in symbol:
            if not verificacoes['sistema_ativo']:
                return False, "Sistema pausado apos losses consecutivos"
            if not verificacoes['volume_ultra_seguro_ok']:
                return False, "Volume muito alto para XAUUSD"
        
        permitido = all(verificacoes.values())
        razao = "Permitido" if permitido else "Bloqueado: " + str([k for k, v in verificacoes.items() if not v])
        
        return permitido, razao
    
    def calcular_stop_loss(self, symbol, entry_price, volume, tipo):
        """
        Calcula stop loss automatico baseado nos parametros
        """
        # SL baseado no volume e tipo
        if volume > 0.15:
            sl_pct = 0.015  # 1.5% para volumes grandes
        elif volume > 0.10:
            sl_pct = 0.02   # 2% para volumes medios
        else:
            sl_pct = 0.025  # 2.5% para volumes pequenos
        
        # Ajuste para tipo de operacao
        if tipo == 'BUY':
            stop_loss = entry_price * (1 - sl_pct)
        else:  # SELL
            stop_loss = entry_price * (1 + sl_pct)
        
        return round(stop_loss, 2)
    
    def verificar_indicadores_tecnicos(self, symbol, dados_mercado):
        """
        Verifica se os indicadores tecnicos confirmam a operacao
        IMPLEMENTACAO ESPECIFICA: ['RSI', 'MACD', 'Support_Resistance']
        """
        verificacoes = {}
        
        # RSI (Relative Strength Index) - IMPLEMENTACAO ESPECIFICA
        if 'RSI' in self.indicadores_obrigatorios:
            rsi = self._calcular_rsi(dados_mercado)
            verificacoes['rsi_ok'] = self._validar_rsi(rsi)
            print(f"[RSI] Valor: {rsi:.2f} | Valido: {verificacoes['rsi_ok']}")
        else:
            verificacoes['rsi_ok'] = True
        
        # MACD (Moving Average Convergence Divergence) - IMPLEMENTACAO ESPECIFICA
        if 'MACD' in self.indicadores_obrigatorios:
            macd = self._calcular_macd(dados_mercado)
            verificacoes['macd_ok'] = self._validar_macd(macd)
            print(f"[MACD] MACD: {macd['macd']:.4f} | Signal: {macd['signal']:.4f} | Valido: {verificacoes['macd_ok']}")
        else:
            verificacoes['macd_ok'] = True
        
        # Support and Resistance - IMPLEMENTACAO ESPECIFICA
        if 'Support_Resistance' in self.indicadores_obrigatorios:
            sr_level = self._identificar_support_resistance(dados_mercado)
            verificacoes['sr_ok'] = self._validar_support_resistance(sr_level, dados_mercado[-1])
            print(f"[SR] Suporte: {sr_level['support']:.2f} | Resistencia: {sr_level['resistance']:.2f} | Valido: {verificacoes['sr_ok']}")
        else:
            verificacoes['sr_ok'] = True
        
        # Trend Analysis (adicional)
        verificacoes['trend_ok'] = self._validar_tendencia(dados_mercado)
        
        todos_ok = all(verificacoes.values())
        return todos_ok, verificacoes
    
    def implementar_trailing_stop(self, symbol, entry_price, current_price, tipo, sl_atual, profit_atual):
        """
        IMPLEMENTACAO ESPECIFICA: Ativar apos ganho de 0.5%
        IMPLEMENTACAO ESPECIFICA: Movimentar SL para break-even com +1%
        """
        gain_pct = profit_atual / (entry_price * 100)  # Assuming lot size 100
        
        novo_sl = sl_atual
        
        print(f"[TRAILING] Gain atual: {gain_pct:.3%} | Trigger: {self.parametros['trailing_gain_trigger']:.3%}")
        
        # ATIVAR TRAILING STOP APOS GANHO DE 0.5% - IMPLEMENTACAO ESPECIFICA
        if gain_pct >= self.parametros['trailing_gain_trigger']:
            
            if tipo == 'BUY':
                # Para BUY, mover SL para cima
                if profit_atual > 0:
                    # MOVIMENTAR SL PARA BREAK-EVEN COM +1% - IMPLEMENTACAO ESPECIFICA
                    if gain_pct >= self.parametros['trailing_break_even']:
                        novo_sl = entry_price * 0.9995  # Ligeiramente acima do break-even
                        print(f"[TRAILING BUY] Break-even ativado: SL {sl_atual:.2f} -> {novo_sl:.2f}")
                    else:
                        # Trailing stop 50% do ganho
                        trailing_distance = (current_price - entry_price) * 0.5
                        novo_sl = current_price - trailing_distance
                        print(f"[TRAILING BUY] Trailing ativado: SL {sl_atual:.2f} -> {novo_sl:.2f}")
                else:
                    novo_sl = sl_atual
                    print(f"[TRAILING BUY] Aguardando profit positivo")
                    
            else:  # SELL
                # Para SELL, mover SL para baixo
                if profit_atual > 0:
                    # MOVIMENTAR SL PARA BREAK-EVEN COM +1% - IMPLEMENTACAO ESPECIFICA
                    if gain_pct >= self.parametros['trailing_break_even']:
                        novo_sl = entry_price * 1.0005  # Ligeiramente abaixo do break-even
                        print(f"[TRAILING SELL] Break-even ativado: SL {sl_atual:.2f} -> {novo_sl:.2f}")
                    else:
                        # Trailing stop 50% do ganho
                        trailing_distance = (entry_price - current_price) * 0.5
                        novo_sl = current_price + trailing_distance
                        print(f"[TRAILING SELL] Trailing ativado: SL {sl_atual:.2f} -> {novo_sl:.2f}")
                else:
                    novo_sl = sl_atual
                    print(f"[TRAILING SELL] Aguardando profit positivo")
        else:
            print(f"[TRAILING] Aguardando gatilho de 0.5%")
        
        return round(novo_sl, 2)
    
    def processar_resultado_trade(self, trade_result):
        """
        Processa resultado do trade e atualiza protecoes
        """
        # Atualizar contador de losses consecutivos
        if trade_result['profit'] < 0:
            self.losses_consecutivos += 1
            
            # Pausar sistema apos 2 losses consecutivos
            if self.losses_consecutivos >= self.parametros['pausa_losses_consecutivos']:
                self.sistema_pausado = True
                self._registrar_pausa_automatica("2 losses consecutivos")
            
            # Pausar apos loss muito grande
            if abs(trade_result['profit']) > self.parametros['pausa_loss_grande']:
                self.sistema_pausado = True
                self._registrar_pausa_automatica(f"Loss > ${self.parametros['pausa_loss_grande']}")
        
        else:
            # Reset contador apos gain
            self.losses_consecutivos = 0
        
        # Atualizar trades de hoje
        self.trades_hoje.append({
            'timestamp': datetime.now(),
            'profit': trade_result['profit'],
            'volume': trade_result['volume']
        })
        
        # Limpar trades antigos (mais de 24h)
        self._limpar_trades_antigos()
    
    def _calcular_rsi(self, dados):
        """Calcula RSI - IMPLEMENTACAO ESPECIFICA"""
        # Implementacao simplificada - em producao usar bibliotecca especializada
        if len(dados) < 14:
            return 50  # Valor neutro
        
        closes = dados[-14:]  # Ultimos 14 periodos
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _validar_rsi(self, rsi):
        """Valida sinal do RSI - IMPLEMENTACAO ESPECIFICA"""
        # Evitar overbought (>70) e oversold (<30)
        return 30 <= rsi <= 70
    
    def _calcular_macd(self, dados):
        """Calcula MACD - IMPLEMENTACAO ESPECIFICA"""
        if len(dados) < 26:
            return {'macd': 0, 'signal': 0}
        
        closes = dados[-26:]  # Ultimos 26 periodos
        ema12 = self._calcular_ema(closes, 12)
        ema26 = self._calcular_ema(closes, 26)
        macd = ema12 - ema26
        signal = self._calcular_ema([macd], 9)  # Signal line simplificada
        
        return {'macd': macd, 'signal': signal}
    
    def _calcular_ema(self, valores, periodo):
        """Calcula EMA simplificado"""
        if len(valores) < periodo:
            return valores[-1] if valores else 0
        
        multiplier = 2 / (periodo + 1)
        ema = valores[0]
        
        for valor in valores[1:]:
            ema = (valor * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _validar_macd(self, macd_data):
        """Valida sinal do MACD - IMPLEMENTACAO ESPECIFICA"""
        # MACD deve estar acima ou abaixo da signal line de forma consistente
        # Para BUY: MACD > Signal
        # Para SELL: MACD < Signal
        return macd_data['macd'] != macd_data['signal']  # Simplificado
    
    def _identificar_support_resistance(self, dados):
        """Identifica niveis de suporte e resistencia - IMPLEMENTACAO ESPECIFICA"""
        # Implementacao simplificada
        if len(dados) < 20:
            return {'support': min(dados), 'resistance': max(dados)}
        
        highs = dados[-20:]
        lows = dados[-20:]
        
        resistance = max(highs)
        support = min(lows)
        
        return {'support': support, 'resistance': resistance}
    
    def _validar_support_resistance(self, sr_levels, preco_atual):
        """Valida posicao relativa aos niveis de SR - IMPLEMENTACAO ESPECIFICA"""
        # Verificar se preco atual esta longe dos niveles extremos
        # Para BUY: comprar proximo ao suporte
        # Para SELL: vender proximo a resistencia
        
        suporte = sr_levels['support']
        resistencia = sr_levels['resistance']
        
        # Distancia do suporte (%)
        dist_suporte = abs(preco_atual - suporte) / suporte * 100
        dist_resistencia = abs(preco_atual - resistencia) / preco_atual * 100
        
        # Permitir operacoes se preco estiver a menos de 2% dos niveles
        return dist_suporte <= 2.0 or dist_resistencia <= 2.0
    
    def _validar_tendencia(self, dados):
        """Valida tendencia do mercado"""
        if len(dados) < 10:
            return True
        
        # Verificar se ultimos 5 periodos estao acima/abaixo dos anteriores
        recentes = dados[-5:]
        anteriores = dados[-10:-5]
        
        tendencia_recente = sum(recentes) / len(recentes)
        tendencia_anterior = sum(anteriores) / len(anteriores)
        
        # Evitar operacoes contra tendencia muito forte
        diff_pct = abs(tendencia_recente - tendencia_anterior) / tendencia_anterior
        return diff_pct <= 0.05  # Max 5% de diferenca
    
    def _verificar_limite_diario(self):
        """Verifica limite diario de trades"""
        volume_atual = sum(trade['volume'] for trade in self.trades_hoje if 
                          (datetime.now() - trade['timestamp']).days == 0)
        
        return volume_atual <= self.parametros['volume_maximo_24h']
    
    def _limpar_trades_antigos(self):
        """Remove trades com mais de 24h"""
        agora = datetime.now()
        self.trades_hoje = [trade for trade in self.trades_hoje if 
                           (agora - trade['timestamp']).days == 0]
    
    def _registrar_pausa_automatica(self, motivo):
        """Registra motivo da pausa automatica"""
        print(f"[PAUSA AUTOMATICA] Sistema pausado: {motivo}")
        print(f"[PAUSA AUTOMATICA] Losses consecutivos: {self.losses_consecutivos}")
        print(f"[PAUSA AUTOMATICA] Para reativar, execute: sistema.reativar_manualmente()")
    
    def reativar_manualmente(self):
        """Reativa sistema manualmente (apos analise)"""
        self.sistema_pausado = False
        self.losses_consecutivos = 0
        print("[REATIVACAO] Sistema reativado manualmente")


# Exemplo de uso e teste das funcionalidades especificas
def exemplo_uso_implementacao():
    """
    Exemplo de como usar as protecoes implementadas
    """
    print("=== EXEMPLO DE USO DAS PROTECoes AUTOMATIZADAS ===")
    
    # Inicializar sistema de protecoes
    protecoes = ProtecoesAutomatizadasXAUUSD()
    
    # Simular dados de mercado para XAUUSD
    precos_xauusd = [3980, 3985, 3990, 3985, 3992, 3998, 4005, 4010, 4008, 4012, 
                     4015, 4020, 4025, 4028, 4030, 4032, 4035, 4038, 4040, 4042]
    
    print("\n1. VERIFICANDO ENTRADA PERMITIDA:")
    permitido, razao = protecoes.verificar_entrada_permitida("XAUUSD", 0.01, "BTC_Hedge_Agent")
    print(f"   Entrada permitida: {permitido} | {razao}")
    
    print("\n2. TESTANDO INDICADORES TECNICOS:")
    indicadores_ok, detalhes = protecoes.verificar_indicadores_tecnicos("XAUUSD", precos_xauusd)
    print(f"   Indicadores OK: {indicadores_ok}")
    for indicador, ok in detalhes.items():
        print(f"   - {indicador}: {'OK' if ok else 'NOK'}")
    
    print("\n3. CALCULANDO STOP LOSS:")
    sl = protecoes.calcular_stop_loss("XAUUSD", 4010.00, 0.01, "BUY")
    print(f"   Stop Loss calculado: ${sl:.2f}")
    
    print("\n4. TESTANDO TRAILING STOP:")
    # Simular ganho de 0.8% (passou de 0.5% trigger)
    novo_sl = protecoes.implementar_trailing_stop("XAUUSD", 4010.00, 4042.00, "BUY", 3980.00, 32.00)
    print(f"   Novo SL: ${novo_sl:.2f}")
    
    print("\n5. TESTANDO PAUSA AUTOMATICA:")
    # Simular loss de $250
    protecoes.processar_resultado_trade({
        'profit': -250.0,
        'volume': 0.01
    })
    print(f"   Sistema pausado: {protecoes.sistema_pausado}")
    print(f"   Losses consecutivos: {protecoes.losses_consecutivos}")
    
    print("\n=== FIM DO EXEMPLO ===")


if __name__ == "__main__":
    exemplo_uso_implementacao()
