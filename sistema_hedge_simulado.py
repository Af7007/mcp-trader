#!/usr/bin/env python3
"""
SISTEMA HEDGE SIMULADO - DEMONSTRAÇÃO COMPLETA
Versão funcional do sistema de hedge
"""

import time
import random
from agents.manager import AgentManager
from core.database import setup_database

class SistemaHedgeSimulado:
    """Sistema completo de hedge simulando dados reais"""

    def __init__(self):
        setup_database()
        self.manager = AgentManager()
        self.ativos_dados = {
            'EURUSD': {'spread': 0.0002, 'volatilidade': 0.001},
            'GBPUSD': {'spread': 0.0003, 'volatilidade': 0.0015},
            'XAUUSD': {'spread': 0.20, 'volatilidade': 0.02},
            'BTCUSD': {'spread': 5.0, 'volatilidade': 0.10}
        }
        self.worker_rodando = False

    def gerar_precos_simulados(self):
        """Gera dados de preço simulados baseados em mercado real"""
        precos = {}
        base_time = time.time()

        for ativo in self.ativos_dados:
            # Movimento browniano simples + tendência
            base_price = {
                'EURUSD': 1.0850,
                'GBPUSD': 1.2750,
                'XAUUSD': 1950.0,
                'BTCUSD': 45000.0
            }.get(ativo, 100.0)

            # Simular movimento de mercado
            volatility = self.ativos_dados[ativo]['volatilidade']
            spread = self.ativos_dados[ativo]['spread']

            # Gerar série de preços (últimas 20 velas)
            prices = []
            current_price = base_price

            for i in range(20):
                # Movimento aleatório + tendência leve
                movimento = random.gauss(0, volatility) + 0.0001
                current_price += movimento
                prices.append(current_price)

            precos[ativo] = {
                'close': prices,
                'bid': prices[-1] - spread/2,
                'ask': prices[-1] + spread/2,
                'spread': spread,
                'volume': random.randint(1000, 10000)
            }

        return precos

    def calcular_indicadores_simulados(self, precos):
        """Calcula indicadores técnicos simulados"""
        indicadores = {}

        for ativo, dados in precos.items():
            closes = dados['close']

            # RSI simulado (14 períodos)
            rsi = self.calcular_rsi_simulado(closes)

            # Bollinger Bands
            sma20 = sum(closes[-20:]) / 20
            std20 = sum((x - sma20) ** 2 for x in closes[-20:]) ** 0.5 / 20 ** 0.5
            upper = sma20 + 2 * std20
            lower = sma20 - 2 * std20

            indicadores[ativo] = {
                'rsi': rsi[-1],  # Último RSI
                'rsi_series': rsi,
                'bollinger': {
                    'upper': upper,
                    'middle': sma20,
                    'lower': lower
                },
                'preco_atual': closes[-1]
            }

        return indicadores

    def calcular_rsi_simulado(self, closes, period=14):
        """Calcula RSI de forma simulada"""
        rsi_values = []

        for i in range(len(closes)):
            if i < period + 1:
                rsi_values.append(50.0)  # Neutro inicialmente
            else:
                # Simulação realista do RSI
                gains = sum(max(closes[j] - closes[j-1], 0) for j in range(i-period, i))
                losses = sum(max(closes[j-1] - closes[j], 0) for j in range(i-period, i))

                if losses == 0:
                    rsi = 100.0
                else:
                    rs = gains / losses
                    rsi = 100 - (100 / (1 + rs))

                rsi_values.append(rsi)

        return rsi_values

    def calcular_correlacao_simulada(self, ativo1, ativo2, precos):
        """Calcula correlação entre dois ativos simulando dados reais"""
        if ativo1 not in precos or ativo2 not in precos:
            return 0.5

        closes1 = precos[ativo1]['close'][-20:]
        closes2 = precos[ativo2]['close'][-20:]

        # Correlação baseada em direção dos movimentos
        movimentos1 = [closes1[i] - closes1[i-1] for i in range(1, len(closes1))]
        movimentos2 = [closes2[i] - closes2[i-1] for i in range(1, len(closes2))]

        # Contar movimentos na mesma direção
        mesmo_direcao = sum(1 for m1, m2 in zip(movimentos1, movimentos2) if (m1 > 0) == (m2 > 0))

        correlacao = (mesmo_direcao / len(movimentos1)) * 2 - 1  # Normalize para -1 a 1
        return correlacao

    def executar_analise_hedge(self):
        """Executa uma rodada de análise de hedge simulada"""
        print("
[ANALISE] Executando análise de hedge simulada..."
        # Gerar preços simulados
        precos = self.gerar_precos_simulados()

        # Calcular indicadores
        indicadores = self.calcular_indicadores_simulados(precos)

        # Mostrar condições de mercado
        print("📊 CONDIÇÕES DE MERCADO:")
        for ativo, ind in indicadores.items():
            print(f"  {ativo}: ${precos[ativo]['close'][-1]:.4f} | RSI: {ind['rsi']:.1f} | BB: {ind['bollinger']['lower']:.4f}-{ind['bollinger']['upper']:.4f}")

        # Análise de correlação EURUSD vs GBPUSD
        correlacao_eurusd_gbpusd = self.calcular_correlacao_simulada('EURUSD', 'GBPUSD', precos)
        print("
🔗 CORRELAÇÃO:"        print(f"  EURUSD vs GBPUSD: {correlacao_eurusd_gbpusd:.3f}")

        # Corrida de hedge entre EURUSD e GBPUSD
        resultado = self.analisar_sinal_hedge('EURUSD', 'GBPUSD', precos, indicadores)
        return resultado

    def analisar_sinal_hedge(self, ativo1, ativo2, precos, indicadores):
        """Analisa oportunidade de hedge entre dois ativos"""
        if ativo1 not in indicadores or ativo2 not in indicadores:
            return {"sinal": "none", "motivo": "ativos nao disponiveis"}

        # Lógica de hedge: sinais divergentes ou correlação fraca
        rsi1 = indicadores[ativo1]['rsi']
        rsi2 = indicadores[ativo2]['rsi']
        preco1 = precos[ativo1]['close'][-1]
        preco2 = precos[ativo2]['close'][-1]

        # Seção de decisão de hedge
        if rsi1 > 70 and rsi2 < 30:  # Possível divergência
            sinal = "short_long"
            motivo = f"{ativo1} sobrecomprado + {ativo2} sobrevendido = oportunidade hedge"
            confidence = 0.75
        elif rsi2 > 70 and rsi1 < 30:  # Divergência oposta
            sinal = "long_short"
            motivo = f"{ativo2} sobrecomprado + {ativo1} sobrevendido = oportunidade hedge"
            confidence = 0.75
        elif abs(rsi1 - rsi2) > 40:  # Divergência significativa
            sinal = "divergence_trade"
            motivo = f"Divergência RSI significa oportunidade de correção"
            confidence = 0.60
        else:
            sinal = "none"
            motivo = "Condições normais - aguardar sinal"
            confidence = 0.10

        resultado = {
            "sinal": sinal,
            "motivo": motivo,
            "confidence": confidence,
            "ativos": [ativo1, ativo2],
            "rsi": {ativo1: rsi1, ativo2: rsi2},
            "precos": {ativo1: preco1, ativo2: preco2}
        }

        return resultado

    def executar_operacao_hedge_simulada(self, analise):
        """Executa operação de hedge simulada"""
        if analise['sinal'] == 'none':
            return {"operation": "none", "reason": "no good hedge opportunity"}

        sinal = analise['sinal']
        ativos = analise['ativos']
        confidence = analise['confidence']

        # Simular execução apenas se confiança alta
        if confidence > 0.6:
            # Simular tempo de execução
            time.sleep(1)

            # Simular resultado da operação
            if random.random() > 0.3:  # 70% sucesso na simulação
                resultado = "success"
                mensagens = [
                    f"✅ HEDGE EXECUTADO: {sinal.upper()} entre {ativos[0]} e {ativos[1]}",
                    f"🎯 Posições abertas com TP/SL configurado",
                    f"📊 Acompanhamento iniciado no worker"
                ]
            else:
                resultado = "retry"
                mensagens = [
                    f"⚠️ HEDGE PARCIAL: Apenas uma posição executada",
                    f"🔄 Sistema tentará completar depois"
                ]

            return {
                "operation": resultado,
                "messages": mensagens,
                "details": analise
            }
        else:
            return {"operation": "wait", "reason": "confidence too low"}

    def iniciar_monitoramento_worker(self):
        """Inicia worker de monitoramento simulando execução real"""
        if self.worker_rodando:
            print("Worker já está rodando!")
            return

        def monitor_worker():
            print("🔄 Worker de hedge iniciado...")

            analises_executadas = 0
            operacoes_realizadas = 0
            t0 = time.time()

            while self.worker_rodando:
                try:
                    # Análise completa
                    analise = self.executar_analise_hedge()

                    # Tomar decisão de execução
                    if analise['sinal'] != 'none':
                        operacao = self.executar_operacao_hedge_simulada(analise)
                        if operacao['operation'] in ['success', 'retry']:
                            for msg in operacao.get('messages', []):
                                print(f"[WORKER] {msg}")
                            operacoes_realizadas += 1
                        elif operacao['operation'] == 'wait':
                            print(f"[WORKER] {operacao.get('reason', 'aguardando melhor oportunidade')}")
                    else:
                        print(".")

                    analises_executadas += 1

                    # Estatísticas a cada 5 análises
                    if analises_executadas % 5 == 0:
                        elapsed = time.time() - t0
                        print(f"[WORKER] Analises: {analises_executadas} | Operacoes: {operacoes_realizadas} | Tempo: {elapsed:.0f}s")

                    # Pausa entre análises
                    time.sleep(random.randint(8, 15))  # 8-15 segundos simulando mercado

                except Exception as e:
                    print(f"[WORKER] Erro na analise: {e}")
                    time.sleep(5)

        import threading
        self.worker_rodando = True
        monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        monitor_thread.start()

        print("✅ Worker de hedge iniciou monitoramento!")
        print("⏰ Pressione Ctrl+C para parar")

    def parar_monitoramento(self):
        """Para o monitoramento do worker"""
        self.worker_rodando = False
        print("\n🛑 Monitoramento de hedge parado")

def main():
    sistema = SistemaHedgeSimulado()

    print("=" * 70)
    print("🛡️  SISTEMA HEDGE OPERACIONAL - SIMULAÇÃO REALISTA")
    print("=" * 70)
    print("")
    print("🎯 FUNCIONALIDADES:")
    print("  • Análise de correlação em tempo real")
    print("  • Detecção de sinais de hedge")
    print("  • Execução automática de operações")
    print("  • Monitoramento contínuo por worker")
    print("")
    print("📊 ATIVOS DE HEDGE:")
    print("  • EURUSD - Euro vs Dollar (Índice Principal)")
    print("  • GBPUSD - Libra vs Dollar (Correlacionado)")
    print("  • XAUUSD - Ouro vs Dollar (Commodity)")
    print("  • BTCUSD - Bitcoin vs Dollar (Crypto)")
    print("")
    print("🎮 COMANDOS:")
    print("  'analise' - Executar análise única")
    print("  'hedge' - Executar operação de hedge")
    print("  'worker start' - Iniciar monitoramento")
    print("  'worker stop' - Parar monitoramento")
    print("  'stats' - Ver estatísticas")
    print("  'sair' - Sair do sistema")
    print("=" * 70)

    try:
        while True:
            comando = input("\n💬 Comando: ").strip().lower()

            if comando == 'sair':
                break
            elif comando == 'analise':
                analise = sistema.executar_analise_hedge()
                print("
🎯 RESULTADO DA ANÁLISE:"                print(f"  Sinal: {analise['sinal']}")
                print(f"  Motivo: {analise['motivo']}")
                print(f"  Confiança: {analise.get('confidence', 0):.1%}")

            elif comando == 'hedge':
                print("
🔄 VERIFICANDO OPORTUNIDADES DE HEDGE..."                analise = sistema.executar_analise_hedge()
                operacao = sistema.executar_operacao_hedge_simulada(analise)

                print("
🎯 DECISÃO DE HEDGE:"                if operacao['operation'] == 'none':
                    print("  ❌ Nenhuma oportunidade de hedge identificada")
                elif operacao['operation'] in ['success', 'retry']:
                    for msg in operacao.get('messages', []):
                        print(f"  ✅ {msg}")
                else:
                    print(f"  ⏳ {operacao.get('reason', 'aguardando melhor oportunidade')}")

            elif comando == 'worker start':
                sistema.iniciar_monitoramento_worker()
            elif comando == 'worker stop':
                sistema.parar_monitoramento()
            elif comando == 'stats':
                print("
📊 ESTATÍSTICAS DO SISTEMA:"                print("  • Análise: Ativa em tempo real"                print("  • Hedge Available: EURUSD↔GBPUSD, commodities"                print("  • Execução: Simulada com dados realistas"                print("  • Interface web: http://localhost:3000"                print("  • Monitoramento: Worker ativo"            else:
                print(f"Comando desconhecido: {comando}")
                print("Digite 'analise', 'hedge', 'worker start', 'worker stop', 'stats' ou 'sair'")

    except KeyboardInterrupt:
        print("\n👋 Obrigado por usar o Sistema Hedge Operacional!")
        sistema.parar_monitoramento()

if __name__ == "__main__":
    main()
