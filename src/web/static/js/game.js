// ============================================
// GOLD LOSS ZERO GAME - Main JavaScript
// ============================================

class GoldGameApp {
    constructor() {
        // State
        this.prediction = null;
        this.positions = [];
        this.history = [];
        this.totalProfit = 0;
        this.wins = 0;
        this.losses = 0;
        this.streak = 0;
        this.candles = [];
        this.accountBalance = 0;
        
        // Elements
        this.loadingScreen = document.getElementById('loading-screen');
        this.gameContainer = document.getElementById('game-container');
        
        // Prediction elements
        this.signalDirection = document.getElementById('signal-direction');
        this.currentPrice = document.getElementById('current-price');
        this.scoreValue = document.getElementById('score-value');
        this.scoreFill = document.getElementById('score-fill');
        this.confidenceValue = document.getElementById('confidence-value');
        this.analysisText = document.getElementById('analysis-text');
        
        // Control elements
        this.volumeInput = document.getElementById('volume-input');
        this.slInput = document.getElementById('sl-input');
        this.btnBuy = document.getElementById('btn-buy');
        this.btnSell = document.getElementById('btn-sell');
        
        // Display elements
        this.accountBalanceEl = document.getElementById('account-balance');
        this.totalProfitEl = document.getElementById('total-profit');
        this.winRateEl = document.getElementById('win-rate');
        this.streakEl = document.getElementById('streak');
        this.positionsList = document.getElementById('positions-list');
        this.historyList = document.getElementById('history-list');
        
        // Chart canvas
        this.chartCanvas = document.getElementById('candles-chart');
        this.chartCtx = this.chartCanvas.getContext('2d');
        
        // Sound effects
        this.sounds = {
            win: document.getElementById('sound-win'),
            lose: document.getElementById('sound-lose'),
            trade: document.getElementById('sound-trade'),
            alert: document.getElementById('sound-alert')
        };
        
        // Canvas for particles
        this.canvas = document.getElementById('particles-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        
        // Initialize
        this.init();
    }
    
    async init() {
        console.log('🎰 Initializing Gold Loss Zero Game...');
        
        // Setup canvas
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Start particle animation
        this.animateParticles();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Register service worker
        this.registerServiceWorker();
        
        // Load game data
        await this.loadGameData();
        
        // Show game (remove loading screen)
        setTimeout(() => {
            this.loadingScreen.classList.add('hidden');
            this.gameContainer.classList.remove('hidden');
            this.playSound('alert');
        }, 2000);
        
        // Start polling
        this.startPolling();
        
        console.log('✅ Game initialized!');
    }
    
    setupEventListeners() {
        this.btnBuy.addEventListener('click', () => this.openPosition('BUY'));
        this.btnSell.addEventListener('click', () => this.openPosition('SELL'));
    }
    
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/static/service-worker.js');
                console.log('✅ Service Worker registered');
            } catch (error) {
                console.error('❌ Service Worker registration failed:', error);
            }
        }
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    // ============================================
    // PARTICLE EFFECTS
    // ============================================
    
    createParticle(x, y, color) {
        const particle = {
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            radius: Math.random() * 3 + 2,
            color: color,
            life: 1.0,
            decay: Math.random() * 0.02 + 0.01
        };
        this.particles.push(particle);
    }
    
    createCelebration(color = '#ffd700') {
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        
        for (let i = 0; i < 50; i++) {
            this.createParticle(centerX, centerY, color);
        }
    }
    
    animateParticles() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update and draw particles
        this.particles = this.particles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.life -= p.decay;
            
            if (p.life <= 0) return false;
            
            this.ctx.globalAlpha = p.life;
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            this.ctx.fill();
            
            return true;
        });
        
        this.ctx.globalAlpha = 1.0;
        
        requestAnimationFrame(() => this.animateParticles());
    }
    
    // ============================================
    // SOUND EFFECTS
    // ============================================
    
    playSound(type) {
        try {
            const sound = this.sounds[type];
            if (sound) {
                sound.currentTime = 0;
                sound.play().catch(e => console.warn('Sound play failed:', e));
            }
        } catch (e) {
            console.warn('Sound error:', e);
        }
    }
    
    // ============================================
    // API COMMUNICATION
    // ============================================
    
    async loadGameData() {
        try {
            // Load prediction
            await this.fetchPrediction();
            
            // Load positions
            await this.fetchPositions();
            
            // Load history
            await this.fetchHistory();
            
        } catch (error) {
            console.error('Error loading game data:', error);
        }
    }
    
    async fetchPrediction() {
        try {
            const response = await fetch('/api/game/prediction');
            const data = await response.json();
            
            if (data.prediction) {
                this.updatePrediction(data.prediction);
            }
            
            if (data.price) {
                this.updatePrice(data.price);
            }
            
            if (data.candles) {
                this.candles = data.candles;
                this.drawChart();
            }
            
            if (data.balance !== undefined) {
                this.accountBalance = data.balance;
                this.updateBalance();
            }
        } catch (error) {
            console.error('Error fetching prediction:', error);
        }
    }
    
    async fetchPositions() {
        try {
            const response = await fetch('/api/game/positions');
            const data = await response.json();
            
            this.positions = data.positions || [];
            this.updatePositionsDisplay();
        } catch (error) {
            console.error('Error fetching positions:', error);
        }
    }
    
    async fetchHistory() {
        try {
            const response = await fetch('/api/game/history');
            const data = await response.json();
            
            this.history = data.history || [];
            this.updateHistoryDisplay();
            this.updateStats(data.stats);
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    }
    
    async openPosition(type) {
        const volume = parseFloat(this.volumeInput.value);
        const sl = parseFloat(this.slInput.value);
        
        if (volume <= 0 || sl <= 0) {
            alert('⚠️ Volume e Stop Loss devem ser maiores que zero!');
            return;
        }
        
        try {
            // Disable buttons
            this.btnBuy.disabled = true;
            this.btnSell.disabled = true;
            
            // Play trade sound
            this.playSound('trade');
            
            const response = await fetch('/api/game/open', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, volume, sl })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Show celebration
                this.createCelebration(type === 'BUY' ? '#00ff88' : '#ff3333');
                
                // Reload positions
                await this.fetchPositions();
            } else {
                alert('❌ Erro ao abrir posição: ' + (data.error || 'Desconhecido'));
            }
            
        } catch (error) {
            console.error('Error opening position:', error);
            alert('❌ Erro ao abrir posição!');
        } finally {
            // Re-enable buttons after cooldown
            setTimeout(() => {
                this.updateButtonStates();
            }, 5000);
        }
    }
    
    // ============================================
    // UI UPDATES
    // ============================================
    
    updatePrediction(prediction) {
        this.prediction = prediction;
        
        const { type, score, confidence, reason } = prediction;
        
        // Update signal direction
        this.signalDirection.className = 'signal-direction ' + type.toLowerCase();
        
        if (type === 'BUY') {
            this.signalDirection.innerHTML = `
                <span class="signal-icon">📈</span>
                <span class="signal-text">Sugestão: COMPRAR</span>
            `;
        } else if (type === 'SELL') {
            this.signalDirection.innerHTML = `
                <span class="signal-icon">📉</span>
                <span class="signal-text">Sugestão: VENDER</span>
            `;
        } else {
            this.signalDirection.innerHTML = `
                <span class="signal-icon">📊</span>
                <span class="signal-text">Analise o gráfico</span>
            `;
        }
        
        // Update score
        this.scoreValue.textContent = score + '/100';
        this.scoreFill.style.width = score + '%';
        
        // Color score bar based on quality
        if (score >= 80) {
            this.scoreFill.style.background = 'linear-gradient(90deg, #00ff88, #00cc66)';
        } else if (score >= 60) {
            this.scoreFill.style.background = 'linear-gradient(90deg, #ffd700, #cc9900)';
        } else {
            this.scoreFill.style.background = 'linear-gradient(90deg, #ff3333, #cc0000)';
        }
        
        // Update confidence
        this.confidenceValue.textContent = confidence.toFixed(1) + '%';
        
        // Update analysis
        this.analysisText.textContent = reason || 'Análise em andamento...';
        
        // Update button states
        this.updateButtonStates();
        
        // Play alert if excellent score (apenas informativo)
        if (score >= 80) {
            this.playSound('alert');
            this.signalDirection.classList.add('celebrate');
            setTimeout(() => {
                this.signalDirection.classList.remove('celebrate');
            }, 500);
        }
    }
    
    updatePrice(price) {
        this.currentPrice.textContent = '$' + price.toFixed(2);
    }
    
    updateBalance() {
        this.accountBalanceEl.textContent = '$' + this.accountBalance.toFixed(2);
    }
    
    drawChart() {
        if (!this.candles || this.candles.length === 0) return;
        
        const ctx = this.chartCtx;
        const canvas = this.chartCanvas;
        
        // Clear canvas
        ctx.fillStyle = '#0f0f1e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Get last 20 candles
        const candles = this.candles.slice(-20);
        if (candles.length === 0) return;
        
        // Calculate min/max prices
        let minPrice = Infinity;
        let maxPrice = -Infinity;
        
        candles.forEach(c => {
            minPrice = Math.min(minPrice, c.low);
            maxPrice = Math.max(maxPrice, c.high);
        });
        
        // Add padding
        const padding = (maxPrice - minPrice) * 0.1;
        minPrice -= padding;
        maxPrice += padding;
        
        const priceRange = maxPrice - minPrice;
        
        // Chart dimensions
        const chartHeight = canvas.height - 40;
        const chartWidth = canvas.width - 40;
        const candleWidth = chartWidth / candles.length;
        const candleBodyWidth = candleWidth * 0.6;
        
        // Draw grid lines (horizontal)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 3; i++) {
            const y = 20 + (chartHeight / 3) * i;
            ctx.beginPath();
            ctx.moveTo(20, y);
            ctx.lineTo(canvas.width - 20, y);
            ctx.stroke();
            
            // Price labels
            const price = maxPrice - (priceRange / 3) * i;
            ctx.fillStyle = '#888';
            ctx.font = '10px Arial';
            ctx.textAlign = 'right';
            ctx.fillText('$' + price.toFixed(2), 15, y + 3);
        }
        
        // Draw candles
        candles.forEach((candle, i) => {
            const x = 20 + (i * candleWidth) + (candleWidth / 2);
            
            // Calculate y positions
            const openY = 20 + ((maxPrice - candle.open) / priceRange) * chartHeight;
            const closeY = 20 + ((maxPrice - candle.close) / priceRange) * chartHeight;
            const highY = 20 + ((maxPrice - candle.high) / priceRange) * chartHeight;
            const lowY = 20 + ((maxPrice - candle.low) / priceRange) * chartHeight;
            
            // Determine color
            const isBullish = candle.close >= candle.open;
            const color = isBullish ? '#00ff88' : '#ff3333';
            
            // Draw wick
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x, highY);
            ctx.lineTo(x, lowY);
            ctx.stroke();
            
            // Draw body
            ctx.fillStyle = color;
            const bodyTop = Math.min(openY, closeY);
            const bodyHeight = Math.abs(closeY - openY) || 1;
            ctx.fillRect(
                x - candleBodyWidth / 2,
                bodyTop,
                candleBodyWidth,
                bodyHeight
            );
            
            // Draw time label for last candle
            if (i === candles.length - 1) {
                ctx.fillStyle = '#ffd700';
                ctx.font = 'bold 10px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('NOW', x, canvas.height - 5);
            }
        });
        
        // Draw current price line
        if (this.currentPrice) {
            const priceText = this.currentPrice.textContent.replace('$', '');
            const price = parseFloat(priceText);
            if (!isNaN(price)) {
                const y = 20 + ((maxPrice - price) / priceRange) * chartHeight;
                
                // Price line
                ctx.strokeStyle = '#ffd700';
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                ctx.moveTo(20, y);
                ctx.lineTo(canvas.width - 20, y);
                ctx.stroke();
                ctx.setLineDash([]);
                
                // Price label
                ctx.fillStyle = '#ffd700';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'left';
                ctx.fillText('$' + price.toFixed(2), canvas.width - 75, y - 5);
            }
        }
    }
    
    updateButtonStates() {
        // Botões sempre habilitados - jogador decide!
        // Apenas limita a 3 posições simultâneas
        const maxPositions = this.positions.length >= 3;
        
        this.btnBuy.disabled = maxPositions;
        this.btnSell.disabled = maxPositions;
    }
    
    updatePositionsDisplay() {
        if (this.positions.length === 0) {
            this.positionsList.innerHTML = '<p class="empty-message">Nenhuma posição aberta</p>';
            return;
        }
        
        this.positionsList.innerHTML = this.positions.map(pos => `
            <div class="position-item">
                <span class="position-badge ${pos.type.toLowerCase()}">${pos.type}</span>
                <div class="position-info">
                    <span class="position-label">Ticket ${pos.ticket} | ${pos.volume} lotes</span>
                    <span class="position-value">Entry: $${pos.entry_price.toFixed(2)} | SL: $${pos.sl.toFixed(2)}</span>
                    ${pos.trailing_active ? '<span style="color: #00ff88;">🟢 Trailing Ativo</span>' : ''}
                </div>
                <div class="position-profit ${pos.profit >= 0 ? 'positive' : 'negative'}">
                    ${pos.profit >= 0 ? '+' : ''}$${pos.profit.toFixed(2)}
                </div>
            </div>
        `).join('');
    }
    
    updateHistoryDisplay() {
        if (this.history.length === 0) {
            this.historyList.innerHTML = '<p class="empty-message">Nenhum trade ainda</p>';
            return;
        }
        
        this.historyList.innerHTML = this.history.slice(0, 10).map(trade => `
            <div class="history-item">
                <span class="position-badge ${trade.type.toLowerCase()}">${trade.type}</span>
                <div class="position-info">
                    <span class="position-label">#${trade.ticket} | ${new Date(trade.close_time).toLocaleTimeString()}</span>
                    <span class="position-value">${trade.volume} lotes</span>
                </div>
                <div class="position-profit ${trade.profit >= 0 ? 'positive' : 'negative'}">
                    ${trade.profit >= 0 ? '+' : ''}$${trade.profit.toFixed(2)}
                </div>
            </div>
        `).join('');
    }
    
    updateStats(stats) {
        if (!stats) return;
        
        const { total_profit, wins, losses, streak } = stats;
        
        // Update total profit
        this.totalProfit = total_profit;
        this.totalProfitEl.textContent = (total_profit >= 0 ? '+' : '') + '$' + total_profit.toFixed(2);
        this.totalProfitEl.className = 'value ' + (total_profit >= 0 ? 'profit-positive' : 'profit-negative');
        
        // Update win rate
        const totalTrades = wins + losses;
        const winRate = totalTrades > 0 ? (wins / totalTrades * 100) : 0;
        this.winRateEl.textContent = winRate.toFixed(1) + '%';
        
        // Update streak
        this.streak = streak;
        this.streakEl.textContent = streak;
        
        // Celebration on wins
        if (wins > this.wins) {
            this.playSound('win');
            this.createCelebration('#00ff88');
            this.totalProfitEl.classList.add('celebrate');
            setTimeout(() => {
                this.totalProfitEl.classList.remove('celebrate');
            }, 500);
        }
        
        // Shake on losses
        if (losses > this.losses) {
            this.playSound('lose');
            this.createCelebration('#ff3333');
            this.totalProfitEl.classList.add('shake');
            setTimeout(() => {
                this.totalProfitEl.classList.remove('shake');
            }, 500);
        }
        
        this.wins = wins;
        this.losses = losses;
    }
    
    // ============================================
    // POLLING
    // ============================================
    
    startPolling() {
        // Poll prediction (with candles and balance) every 2 seconds
        setInterval(() => this.fetchPrediction(), 2000);
        
        // Poll positions every 2 seconds
        setInterval(() => this.fetchPositions(), 2000);
        
        // Poll history every 10 seconds
        setInterval(() => this.fetchHistory(), 10000);
    }
}

// ============================================
// INITIALIZE APP
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    window.goldGame = new GoldGameApp();
});
