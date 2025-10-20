/**
 * Database Connector for MCP Server
 * Conecta com banco de dados Django do sistema MLP
 */

import axios from 'axios';

export class DBConnector {
    constructor(djangoApiUrl = 'http://localhost:5001') {
        this.djangoApiUrl = djangoApiUrl;
        this.isConnected = false;
    }

    /**
     * Testa conexão com API Django
     */
    async healthCheck() {
        try {
            const response = await axios.get(`${this.djangoApiUrl}/quant/`, { timeout: 5000 });
            this.isConnected = response.status === 200;
            return this.isConnected;
        } catch (error) {
            this.isConnected = false;
            console.error('Django API Health Check failed:', error.message);
            return false;
        }
    }

    /**
     * Obtém resumo do dashboard
     */
    async getDashboardSummary() {
        try {
            const response = await axios.get(`${this.djangoApiUrl}/quant/dashboard/summary/`);
            return response.data;
        } catch (error) {
            console.error('Failed to get dashboard summary:', error.message);
            return null;
        }
    }

    /**
     * Obtém histórico de analyises MLP
     */
    async getMLPAnalyses() {
        try {
            const response = await axios.get(`${this.djangoApiUrl}/quant/mlp/analyses/`);
            return {
                total_analyses: response.data.total || 0,
                recent_analyses: response.data.recent || [],
                success_rate: response.data.success_rate || 0.0
            };
        } catch (error) {
            console.error('Failed to get MLP analyses:', error.message);
            return null;
        }
    }

    /**
     * Obtém histórico de trades
     */
    async getTradeHistory(limit = 10) {
        try {
            const response = await axios.get(`${this.djangoApiUrl}/quant/mlp/trades/`);
            const trades = response.data.trades || [];
            return trades.slice(0, limit).map(trade => ({
                ticket: trade.ticket,
                symbol: trade.symbol,
                type: trade.type,
                profit: trade.profit,
                open_time: trade.open_time,
                close_time: trade.close_time,
                pnl: trade.pnl
            }));
        } catch (error) {
            console.error('Failed to get trade history:', error.message);
            return [];
        }
    }

    /**
     * Obtém estatísticas de P&L diário
     */
    async getDailyPnL() {
        try {
            const response = await axios.get(`${this.djangoApiUrl}/quant/daily-pnl/`);
            const pnl = response.data.pnl || [];
            return pnl.map(day => ({
                date: day.date,
                pnl: day.pnl,
                win_trades: day.win_trades,
                loss_trades: day.loss_trades
            }));
        } catch (error) {
            console.error('Failed to get daily P&L:', error.message);
            return [];
        }
    }

    /**
     * Obtém controle atual do bot MLP
     */
    async getMLPControl() {
        try {
            const response = await axios.get(`${this.djangoApiUrl}/quant/mlp/control/`);
            return {
                running: response.data.running || false,
                confidence_threshold: response.data.confidence_threshold || 90,
                total_trades: response.data.total_trades || 0,
                active_positions: response.data.active_positions || 0
            };
        } catch (error) {
            console.error('Failed to get MLP control:', error.message);
            return {
                running: false,
                confidence_threshold: 90,
                total_trades: 0,
                active_positions: 0
            };
        }
    }

    /**
     * Inicia/para bot MLP via API Django
     */
    async controlMLPBot(command, parameters = {}) {
        try {
            const endpoint = command === 'start' ? 'start/' : 'stop/';

            const response = await axios.post(`${this.djangoApiUrl}/quant/mlp/bot/${endpoint}`, parameters);

            return {
                success: true,
                message: response.data.message || 'Command executed',
                status: command === 'start' ? 'started' : 'stopped'
            };
        } catch (error) {
            console.error('Failed to control MLP bot:', error.message);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Salva análise no banco de dados
     */
    async saveAnalysis(analysis) {
        try {
            const response = await axios.post(`${this.djangoApiUrl}/quant/mlp/save-analysis/`, {
                symbol: analysis.symbol,
                signal: analysis.signal,
                confidence: analysis.confidence,
                rsi: analysis.rsi,
                timestamp: analysis.timestamp
            });

            return {
                success: true,
                id: response.data.id
            };
        } catch (error) {
            console.error('Failed to save analysis:', error.message);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Obtém métricas de performance
     */
    async getPerformanceMetrics() {
        try {
            const pnl = await this.getDailyPnL();
            const trades = await this.getTradeHistory(100);

            const totalTrades = trades.length;
            const winningTrades = trades.filter(t => t.pnl > 0).length;
            const totalPnL = trades.reduce((sum, t) => sum + t.pnl, 0);

            const winRate = totalTrades > 0 ? (winningTrades / totalTrades * 100) : 0;

            return {
                total_trades: totalTrades,
                winning_trades: winningTrades,
                losing_trades: totalTrades - winningTrades,
                win_rate: winRate.toFixed(1),
                total_pnl: totalPnL.toFixed(2),
                avg_pnl_per_trade: totalTrades > 0 ? (totalPnL / totalTrades).toFixed(2) : "0",
                best_day: pnl.length > 0 ? pnl.reduce((max, day) => day.pnl > max.pnl ? day : max, pnl[0]) : null,
                worst_day: pnl.length > 0 ? pnl.reduce((min, day) => day.pnl < min.pnl ? day : min, pnl[0]) : null
            };
        } catch (error) {
            console.error('Failed to calculate performance metrics:', error.message);
            return null;
        }
    }

    /**
     * Faz backup dos dados críticos
     */
    async backupData() {
        try {
            const response = await axios.post(`${this.djangoApiUrl}/quant/backup/`);
            return {
                success: true,
                backup_file: response.data.backup_file,
                timestamp: response.data.timestamp
            };
        } catch (error) {
            console.error('Failed to backup data:', error.message);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Formata dados para apresentação
     */
    formatTradeHistory(trades) {
        return trades.map(trade => ({
            'Ticket': trade.ticket,
            'Symbol': trade.symbol,
            'Type': trade.type,
            'P&L': `$${trade.pnl?.toFixed(2) || '0.00'}`,
            'Status': trade.close_time ? 'Closed' : 'Open'
        }));
    }

    /**
     * Gera relatório diário
     */
    generateDailyReport() {
        const report = {
            today: new Date().toISOString().split('T')[0],
            summary: {},
            recommendations: [],
            alerts: []
        };

        return this.getPerformanceMetrics().then(metrics => {
            report.summary = metrics;
            return report;
        });
    }
}

export default DBConnector;
