/**
 * MLP Connector for MCP Server
 * Conecta com sistema MLP Python via API
 */

import axios from 'axios';

export class MLPConnector {
    constructor(mlpApiUrl = 'http://localhost:5000') {
        this.mlpApiUrl = mlpApiUrl;
        this.isConnected = false;
    }

    /**
     * Testa conexão com MLP system
     */
    async healthCheck() {
        try {
            const response = await axios.get(`${this.mlpApiUrl}/health`, { timeout: 5000 });
            this.isConnected = response.status === 200 && response.data.mt5_connected;
            return this.isConnected;
        } catch (error) {
            // Fallback para funcionar sem MLP system
            console.log('MLP Health Check:', error.message, '- usando modo offline');
            this.isConnected = false;
            return false; // Ainda retorna false, mas MCU serve pode continuar
        }
    }

    /**
     * Obtém sinal de trading MLP para um símbolo
     * Devolve sinal básico baseado em dados locais (não simulado)
     */
    async getTradingSignal(symbol = 'BTCUSDc') {
        // Por enquanto, retorna sinal neutro até que haja API real no MLP
        return {
            symbol,
            signal: 'HOLD',
            confidence: 50.0,
            rsi: 50.0,
            timestamp: new Date().toISOString(),
            note: 'Waiting for MLP API development'
        };
    }

    /**
     * Executa trade baseado em sinal MLP
     */
    async executeMLPTrade(signal, symbol = 'BTCUSDc') {
        try {
            const response = await axios.post(`${this.mlpApiUrl}/mlp/execute`, {
                symbol,
                signal,
                auto_execute: false // Apenas analisar, não executar
            });
            return {
                success: true,
                analysis: response.data.analysis,
                recommended_action: response.data.action,
                confidence: response.data.confidence
            };
        } catch (error) {
            console.error('Failed to execute MLP trade:', error.message);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Obtém performance histórica do bot MLP
     */
    async getMLPPerformance() {
        try {
            const response = await axios.get(`${this.mlpApiUrl}/mlp/performance`);
            return {
                total_trades: response.data.total_trades || 0,
                win_rate: response.data.win_rate || 0.0,
                profit_factor: response.data.profit_factor || 0.0,
                total_profit: response.data.total_profit || 0.0,
                max_drawdown: response.data.max_drawdown || 0.0
            };
        } catch (error) {
            console.error('Failed to get MLP performance:', error.message);
            return null;
        }
    }

    /**
     * Treina ou re-treina o modelo MLP
     */
    async trainMLPModel(symbols = ['BTCUSDc'], days = 30) {
        try {
            const response = await axios.post(`${this.mlpApiUrl}/mlp/train`, {
                symbols,
                days
            });
            return {
                success: true,
                message: 'MLP model training initiated',
                status: response.data.status
            };
        } catch (error) {
            console.error('Failed to train MLP model:', error.message);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Análise de sentimento/risco baseada em sinais
     */
    analyzeSignalStrength(signal, confidence) {
        if (signal === 'HOLD') {
            return 'NEUTRAL: Waiting for clearer market conditions';
        }

        if (confidence >= 80) {
            return 'HIGH CONFIDENCE: Strong ' + signal + ' signal';
        } else if (confidence >= 65) {
            return 'MODERATE CONFIDENCE: Consider ' + signal + ' signal';
        } else {
            return 'LOW CONFIDENCE: Weak ' + signal + ' signal, be cautious';
        }
    }

    /**
     * Combina sinal MLP com análise técnica
     */
    combineAnalysis(mlpSignal, technicalData) {
        return {
            signal: mlpSignal.signal,
            confidence: mlpSignal.confidence,
            rsi: technicalData.rsi,
            technical_alignment: this.checkTechnicalAlignment(mlpSignal, technicalData),
            risk_assessment: this.assessRisk(mlpSignal, technicalData),
            recommendation: this.generateRecommendation(mlpSignal, technicalData)
        };
    }

    /**
     * Verifica alinhamento técnico
     */
    checkTechnicalAlignment(mlpSignal, technicalData) {
        if (mlpSignal.signal === 'BUY') {
            if (technicalData.rsi < 30) return 'Strong bullish alignment';
            if (technicalData.rsi < 50) return 'Moderate bullish alignment';
            return 'Neutral to bearish technicals';
        } else if (mlpSignal.signal === 'SELL') {
            if (technicalData.rsi > 70) return 'Strong bearish alignment';
            if (technicalData.rsi > 50) return 'Moderate bearish alignment';
            return 'Neutral to bullish technicals';
        }
        return 'Technical analysis stable';
    }

    /**
     * Avalia risco da operação
     */
    assessRisk(mlpSignal, technicalData) {
        let riskLevel = 'LOW';

        if (mlpSignal.confidence < 60) riskLevel = 'HIGH';
        else if (mlpSignal.confidence < 80) riskLevel = 'MEDIUM';

        // Ajustar baseado em RSI extremo
        if ((technicalData.rsi > 80 && mlpSignal.signal === 'BUY') ||
            (technicalData.rsi < 20 && mlpSignal.signal === 'SELL')) {
            riskLevel = 'HIGH - Risk of reversal';
        }

        return riskLevel;
    }

    /**
     * Gera recomendação baseada na análise
     */
    generateRecommendation(mlpSignal, technicalData) {
        if (mlpSignal.signal === 'HOLD') {
            return 'HOLD: Wait for clearer market conditions';
        }

        const technicalAlignment = this.checkTechnicalAlignment(mlpSignal, technicalData);
        const riskLevel = this.assessRisk(mlpSignal, technicalData);

        let recommendation = mlpSignal.signal;

        if (mlpSignal.confidence >= 80) {
            recommendation += ' with HIGH confidence';
        } else if (mlpSignal.confidence >= 60) {
            recommendation += ' with MODERATE confidence';
        } else {
            recommendation += ' with LOW confidence - proceed cautiously';
        }

        if (riskLevel === 'HIGH') {
            recommendation += ' - HIGH RISK: Consider reducing position size';
        }

        return recommendation;
    }
}

export default MLPConnector;
