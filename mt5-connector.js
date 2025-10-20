/**
 * MT5 Connector for MCP Server
 * Conecta com MetaTrader 5 via API HTTP/REST
 */

import axios from 'axios';

export class MT5Connector {
    constructor(mt5ApiUrl = 'http://localhost:5000') {
        this.mt5ApiUrl = mt5ApiUrl;
        this.isConnected = false;
    }

    /**
     * Testa conexão com MT5 API
     */
    async healthCheck() {
        try {
            const response = await axios.get(`${this.mt5ApiUrl}/btcusd/stats`, { timeout: 5000 });
            this.isConnected = response.status === 200 && response.data.symbol === 'BTCUSDc';
            return this.isConnected;
        } catch (error) {
            this.isConnected = false;
            console.error('MT5 Health Check failed:', error.message);
            return false;
        }
    }

    /**
     * Obtém dados de mercado em tempo real
     */
    async getMarketData(symbol = 'BTCUSDc') {
        try {
            console.log('DEBUG - MT5 Connector: Fazendo requisição para /btcusd/stats');
            const response = await axios.get(`${this.mt5ApiUrl}/btcusd/stats`);
            console.log('DEBUG - MT5 Connector: Response recebida:', JSON.stringify(response.data, null, 2));

            // Verificar se tem tick e stats_1m
            const hasTick = response.data && response.data.tick;
            const hasStats = response.data && response.data.stats_1m;

            console.log('DEBUG - MT5 Connector: hasTick:', hasTick, 'hasStats:', hasStats);
            console.log('DEBUG - MT5 Connector: tick keys:', hasTick ? Object.keys(response.data.tick) : 'N/A');
            console.log('DEBUG - MT5 Connector: stats keys:', hasStats ? Object.keys(response.data.stats_1m) : 'N/A');

            // Retornar dados brutos para processamento posterior
            return response.data;

        } catch (error) {
            console.error('DEBUG - MT5 Connector: Erro ao obter dados:', error.message);
            return null; // Retornar null para indicar falha
        }
    }

    /**
     * Obtém indicadores técnicos
     */
    async getIndicators(symbol = 'BTCUSDc', timeframe = 'M1') {
        try {
            const response = await axios.get(`${this.mt5ApiUrl}/btcusd/indicators/${timeframe}`);
            return {
                symbol,
                timeframe,
                rsi: response.data.rsi,
                sma20: response.data.sma_20,
                bb_upper: response.data.bb_upper,
                bb_lower: response.data.bb_lower,
                macd: response.data.macd
            };
        } catch (error) {
            console.error('Failed to get indicators:', error.message);
            return null;
        }
    }

    /**
     * Obtém posições ativas
     */
    async getPositions(symbol = null) {
        try {
            // Nota: A API MT5 pode não ter endpoint direto para posições
            // Retornar mock por enquanto
            return [
                {
                    ticket: 123456,
                    symbol: 'BTCUSDc',
                    type: 'BUY',
                    lots: 0.02,
                    profit: 15.85,
                    openPrice: 108500,
                    currentPrice: 108550
                }
            ];
        } catch (error) {
            console.error('Failed to get positions:', error.message);
            return [];
        }
    }

    /**
     * Obtém saldo da conta
     */
    async getAccountInfo() {
        try {
            return {
                balance: 50000.00,
                equity: 50115.85,
                margin: 430.00,
                margin_free: 49685.00,
                profit: 115.85
            };
        } catch (error) {
            console.error('Failed to get account info:', error.message);
            return null;
        }
    }

    /**
     * Formata preços para legibilidade
     */
    formatPrice(price) {
        return parseFloat(price).toFixed(2);
    }

    /**
     * Cálculo de risco por posição
     */
    calculateRisk(positionSize, stopLoss, entryPrice) {
        const risk = Math.abs(stopLoss - entryPrice) * positionSize;
        const riskPercentage = (risk / 50000) * 100; // Baseado em conta $50k
        return {
            risk_usd: risk.toFixed(2),
            risk_pct: riskPercentage.toFixed(2) + '%'
        };
    }
}

export default MT5Connector;
