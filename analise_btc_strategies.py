#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise de Estratégias BTC - Sistema completo de análise
Utiliza os dados armazenados pelo BTC Logger para analisar performance
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.btc_logger import BTCLogger


class BTCStrategyAnalyzer:
    """
    Analisador completo de estratégias BTC
    """
    
    def __init__(self, db_path: str = "btc_trading_logs.db"):
        """
        Inicializa analisador
        """
        self.logger = BTCLogger(db_path)
        
    def run_complete_analysis(self):
        """
        Executa análise completa das estratégias
        """
        print("=" * 80)
        print("ANÁLISE COMPLETA DE ESTRATÉGIAS BTC")
        print("=" * 80)
        print()
        
        # 1. Resumo geral
        self._show_general_summary()
        
        # 2. Performance por estratégia
        self._show_strategy_performance()
        
        # 3. Análise de ciclos recentes
        self._show_recent_cycles_analysis()
        
        # 4. Análise de trades executados
        self._show_trades_analysis()
        
        # 5. Recomendações
        self._show_recommendations()
        
    def _show_general_summary(self):
        """
        Exibe resumo geral
        """
        print("📊 RESUMO GERAL")
        print("-" * 40)
        
        summary = self.logger.get_analysis_summary()
        
        print(f"Total de Ciclos: {summary['total_cycles']}")
        print(f"Total de Trades: {summary['total_trades']}")
        print(f"Total de Sinais: {summary['total_signals']}")
        print(f"Taxa de Acerto: {summary['win_rate']:.1f}%")
        print(f"Lucro Médio: ${summary['avg_profit_loss']:.2f}")
        print()
        
        # Performance por estratégia
        if summary['strategy_stats']:
            print("Performance por Estratégia:")
            for stat in summary['strategy_stats']:
                strength, signals, successful, rate = stat
                print(f"  {strength}: {signals} sinais, {successful} sucesso, {rate:.1f}% taxa")
        print()
        
    def _show_strategy_performance(self):
        """
        Exibe performance detalhada das estratégias
        """
        print("🎯 PERFORMANCE DETALHADA DAS ESTRATÉGIAS")
        print("-" * 50)
        
        performance = self.logger.get_strategy_performance(limit=100)
        
        if not performance:
            print("Nenhuma estratégia encontrada no banco de dados.")
            return
        
        # Agrupar por estratégia
        strategies = {}
        for perf in performance:
            strategy = perf[2]  # strategy_name
            if strategy not in strategies:
                strategies[strategy] = []
            strategies[strategy].append(perf)
        
        for strategy_name, stats in strategies.items():
            print(f"\n📈 Estratégia: {strategy_name}")
            print("=" * 30)
            
            total_signals = sum(s[4] for s in stats)  # total_signals
            total_successful = sum(s[5] for s in stats)  # successful_trades
            total_profit_loss = sum(s[7] for s in stats)  # total_profit_loss
            
            success_rate = (total_successful / total_signals * 100) if total_signals > 0 else 0
            avg_profit = (total_profit_loss / total_signals) if total_signals > 0 else 0
            
            print(f"  Sinais Totais: {total_signals}")
            print(f"  Trades Sucesso: {total_successful}")
            print(f"  Taxa de Acerto: {success_rate:.1f}%")
            print(f"  Lucro Médio: ${avg_profit:.2f}")
            print(f"  Lucro Total: ${total_profit_loss:.2f}")
            
            # Detalhes por força
            strengths = {}
            for s in stats:
                strength = s[3]  # signal_strength
                if strength not in strengths:
                    strengths[strength] = {
                        'signals': 0,
                        'successful': 0,
                        'profit_loss': 0
                    }
                strengths[strength]['signals'] += s[4]
                strengths[strength]['successful'] += s[5]
                strengths[strength]['profit_loss'] += s[7]
            
            print(f"\n  Detalhes por Força:")
            for strength_name, data in strengths.items():
                rate = (data['successful'] / data['signals'] * 100) if data['signals'] > 0 else 0
                avg_profit = (data['profit_loss'] / data['signals']) if data['signals'] > 0 else 0
                print(f"    {strength_name}: {data['signals']} sinais, {rate:.1f}% sucesso, ${avg_profit:.2f} médio")
        
    def _show_recent_cycles_analysis(self):
        """
        Exibe análise de ciclos recentes
        """
        print("\n🔄 ANÁLISE DE CICLOS RECENTES")
        print("-" * 40)
        
        cycles = self.logger.get_recent_cycles(limit=50)
        
        if not cycles:
            print("Nenhum ciclo encontrado no banco de dados.")
            return
        
        # Converter para DataFrame com tratamento de erro
        try:
            # Verificar se há dados suficientes
            if not cycles:
                print("Nenhum ciclo encontrado para análise.")
                return
            
            # Obter número de colunas do primeiro registro
            num_columns = len(cycles[0]) if cycles else 0
            expected_columns = 24  # número esperado de colunas
            
            if num_columns != expected_columns:
                print(f"Erro: Número inesperado de colunas ({num_columns} vs {expected_columns})")
                print("Tentando análise com colunas disponíveis...")
                
                # Criar DataFrame com colunas dinâmicas
                df = pd.DataFrame(cycles)
                
                # Renomear colunas conhecidas
                column_mapping = {
                    0: 'id', 1: 'timestamp', 2: 'cycle_number', 3: 'symbol', 4: 'price',
                    5: 'bb_upper', 6: 'bb_middle', 7: 'bb_lower', 8: 'bb_position',
                    9: 'rsi', 10: 'rsi_overbought', 11: 'rsi_oversold',
                    12: 'volume_current', 13: 'volume_avg', 14: 'volume_multiplier',
                    15: 'trend', 16: 'momentum', 17: 'signal_type', 18: 'signal_strength',
                    19: 'signal_reason', 20: 'signal_price', 21: 'sl_price', 22: 'tp_price',
                    23: 'order_result'
                }
                
                # Aplicar renomeação se possível
                for i, col_name in column_mapping.items():
                    if i < len(df.columns):
                        df = df.rename(columns={df.columns[i]: col_name})
            else:
                df = pd.DataFrame(cycles, columns=[
                    'id', 'timestamp', 'cycle_number', 'symbol', 'price', 'bb_upper', 'bb_middle', 
                    'bb_lower', 'bb_position', 'rsi', 'rsi_overbought', 'rsi_oversold',
                    'volume_current', 'volume_avg', 'volume_multiplier', 'trend', 'momentum',
                    'signal_type', 'signal_strength', 'signal_reason', 'signal_price',
                    'sl_price', 'tp_price', 'order_result', 'order_error', 'agent_version'
                ])
        except Exception as e:
            print(f"Erro ao criar DataFrame: {e}")
            return
        
        # Estatísticas dos indicadores
        print("Estatísticas dos Indicadores:")
        print(f"  RSI Médio: {df['rsi'].mean():.1f}")
        print(f"  RSI Mínimo: {df['rsi'].min():.1f}")
        print(f"  RSI Máximo: {df['rsi'].max():.1f}")
        print(f"  Momentum Médio: {df['momentum'].mean():.2f}")
        print(f"  Volume Médio: {df['volume_current'].mean():.0f}")
        
        # Análise de sinais
        signals_df = df[df['signal_type'].notna()]
        if not signals_df.empty:
            print(f"\nAnálise de Sinais ({len(signals_df)} sinais):")
            
            # Sinais por tipo
            signal_types = signals_df['signal_type'].value_counts()
            print("  Sinais por Tipo:")
            for signal_type, count in signal_types.items():
                print(f"    {signal_type}: {count}")
            
            # Sinais por força
            signal_strengths = signals_df['signal_strength'].value_counts()
            print("  Sinais por Força:")
            for strength, count in signal_strengths.items():
                print(f"    {strength}: {count}")
            
            # Taxa de sucesso por força
            success_by_strength = signals_df.groupby('signal_strength')['order_result'].apply(
                lambda x: (x == '10009').sum() / len(x) * 100
            )
            print("  Taxa de Sucesso por Força:")
            for strength, rate in success_by_strength.items():
                print(f"    {strength}: {rate:.1f}%")
        
        # Análise de posições BB
        bb_positions = df['bb_position'].value_counts()
        print(f"\nPosições nas Bandas de Bollinger:")
        for position, count in bb_positions.items():
            print(f"  {position}: {count}")
        
    def _show_trades_analysis(self):
        """
        Exibe análise de trades executados
        """
        print("\n💰 ANÁLISE DE TRADES EXECUTADOS")
        print("-" * 40)
        
        # Obter trades recentes
        trades = self.logger.get_recent_cycles(limit=100)
        
        # Filtrar apenas trades executados
        executed_trades = [cycle for cycle in trades if cycle[16] == 'Flexible' and cycle[17] is not None]
        
        if not executed_trades:
            print("Nenhum trade executado encontrado no banco de dados.")
            return
        
        print(f"Total de Trades Executados: {len(executed_trades)}")
        
        # Análise de lucros/perdas
        profits = []
        for trade in executed_trades:
            if trade[17] == '10009':  # sucesso
                # Calcular lucro aproximado (diferença entre TP e preço de entrada)
                if trade[18]:  # sl_price
                    if trade[19]:  # tp_price
                        entry_price = trade[14] or trade[3]  # signal_price ou price
                        if trade[15] == 'BUY':
                            profit = trade[19] - entry_price  # TP - entry
                        else:  # SELL
                            profit = entry_price - trade[19]  # entry - TP
                        profits.append(profit)
        
        if profits:
            print(f"Lucro Médio por Trade: ${sum(profits)/len(profits):.2f}")
            print(f"Lucro Total: ${sum(profits):.2f}")
            print(f"Trades Positivos: {sum(1 for p in profits if p > 0)}")
            print(f"Trades Negativos: {sum(1 for p in profits if p < 0)}")
            print(f"Taxa de Acerto: {sum(1 for p in profits if p > 0)/len(profits)*100:.1f}%")
        
    def _show_recommendations(self):
        """
        Exibe recomendações baseadas na análise
        """
        print("\n💡 RECOMENDAÇÕES")
        print("-" * 30)
        
        performance = self.logger.get_strategy_performance(limit=50)
        
        if not performance:
            print("Execute o agente por algum tempo para gerar dados para análise.")
            return
        
        # Encontrar melhores estratégias
        strategies = {}
        for perf in performance:
            strategy = perf[2]  # strategy_name
            if strategy not in strategies:
                strategies[strategy] = []
            strategies[strategy].append(perf)
        
        best_strategies = []
        for strategy_name, stats in strategies.items():
            total_signals = sum(s[4] for s in stats)
            total_successful = sum(s[5] for s in stats)
            success_rate = (total_successful / total_signals * 100) if total_signals > 0 else 0
            
            if total_signals >= 5:  # mínimo de sinais para análise
                best_strategies.append((strategy_name, success_rate, total_signals))
        
        # Ordenar por taxa de sucesso
        best_strategies.sort(key=lambda x: x[1], reverse=True)
        
        print("Top 5 Estratégias por Taxa de Acerto:")
        for i, (strategy, rate, signals) in enumerate(best_strategies[:5]):
            print(f"  {i+1}. {strategy}: {rate:.1f}% ({signals} sinais)")
        
        print("\nRecomendações de Parâmetros:")
        
        # Análise de RSI
        cycles = self.logger.get_recent_cycles(limit=100)
        if cycles:
            df = pd.DataFrame(cycles)
            rsi_values = df['rsi'].dropna()
            
            if not rsi_values.empty:
                rsi_mean = rsi_values.mean()
                print(f"  RSI Médio Atual: {rsi_mean:.1f}")
                
                if rsi_mean > 60:
                    print("  📈 RSI muito alto - considere reduzir rsi_overbought para 65-70")
                elif rsi_mean < 40:
                    print("  📉 RSI muito baixo - considere reduzir rsi_oversold para 30-35")
                else:
                    print("  ✅ RSI em faixa adequada (40-60)")
        
        print("\nRecomendações Gerais:")
        print("  1. Monitore a performance por pelo menos 100 ciclos")
        print("  2. Ajuste parâmetros baseado na taxa de acerto")
        print("  3. Considere diferentes condições de mercado")
        print("  4. Use trailing stop para maximizar lucros")
        print("  5. Diversifique entre estratégias para reduzir risco")
        
    def export_analysis_report(self, filename: str = None):
        """
        Exporta relatório completo de análise
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"btc_strategy_analysis_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE ANÁLISE DE ESTRATÉGIAS BTC\n")
            f.write("=" * 60 + "\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            # Resumo geral
            summary = self.logger.get_analysis_summary()
            f.write("RESUMO GERAL\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total de Ciclos: {summary['total_cycles']}\n")
            f.write(f"Total de Trades: {summary['total_trades']}\n")
            f.write(f"Total de Sinais: {summary['total_signals']}\n")
            f.write(f"Taxa de Acerto: {summary['win_rate']:.1f}%\n")
            f.write(f"Lucro Médio: ${summary['avg_profit_loss']:.2f}\n\n")
            
            # Performance detalhada
            performance = self.logger.get_strategy_performance(limit=100)
            if performance:
                f.write("PERFORMANCE DAS ESTRATÉGIAS\n")
                f.write("-" * 30 + "\n")
                
                for perf in performance:
                    f.write(f"Estratégia: {perf[2]}\n")
                    f.write(f"  Sinais: {perf[4]}\n")
                    f.write(f"  Sucessos: {perf[5]}\n")
                    f.write(f"  Taxa: {perf[9]:.1f}%\n")
                    f.write(f"  Lucro Médio: ${perf[8]:.2f}\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("FIM DO RELATÓRIO\n")
        
        print(f"\n📄 Relatório exportado para: {filename}")
        return filename


def main():
    """
    Função principal
    """
    print("🔍 ANALISADOR DE ESTRATÉGIAS BTC")
    print("=" * 50)
    
    analyzer = BTCStrategyAnalyzer()
    
    while True:
        print("\nOpções:")
        print("1. Análise Completa")
        print("2. Resumo Geral")
        print("3. Performance por Estratégia")
        print("4. Análise de Ciclos Recentes")
        print("5. Análise de Trades")
        print("6. Recomendações")
        print("7. Exportar Relatório")
        print("8. Sair")
        
        try:
            option = input("\nEscolha uma opção (1-8): ").strip()
            
            if option == '1':
                analyzer.run_complete_analysis()
            elif option == '2':
                analyzer._show_general_summary()
            elif option == '3':
                analyzer._show_strategy_performance()
            elif option == '4':
                analyzer._show_recent_cycles_analysis()
            elif option == '5':
                analyzer._show_trades_analysis()
            elif option == '6':
                analyzer._show_recommendations()
            elif option == '7':
                analyzer.export_analysis_report()
            elif option == '8':
                print("Saindo...")
                break
            else:
                print("Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")


if __name__ == "__main__":
    main()
