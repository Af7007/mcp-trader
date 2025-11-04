// ============================================
// GOLD LOSS ZERO GAME v2.0 - Premium
// ============================================

class GoldGameV2 {
    constructor() {
        // State
        this.accountBalance = 0;
        this.totalProfit = 0;
        this.positions = [];
        this.history = [];
        this.wins = 0;
        this.losses = 0;
        this.streak = 0;
        this.currentPrice = 0;
        this.prediction = null;
        this.soundEnabled = true;
        
        // Chart
        this.chart = null;
        this.candles = [];
        
        // Init
        this.initElements();
        this.initSounds();
        this.initChart();
        this.initEventListeners();
        this.registerServiceWorker();
        
        // Start
        this.startGame();
    }
    
    initElements() {
        // Top bar
        this.accountBalanceEl = document.getElementById('account-balance');
        this.totalProfitEl = document.getElementById('total-profit');
        this.winRateEl = document.getElementById('win-rate');
        this.streakEl = document.getElementById('streak');
        this.btnSound = document.getElementById('btn-sound');
        
        // Center panel
        this.opIcon = document.getElementById('op-icon');
        this.opStatus = document.getElementById('op-status');
        this.profitMega = document.getElementById('profit-mega');
        this.profitValue = document.getElementById('profit-value');
        
        // Controls - Stepper
        this.volumeDisplay = document.getElementById('volume-display');
        this.slDisplay = document.getElementById('sl-display');
        this.btnVolumeMinus = document.getElementById('volume-minus');
        this.btnVolumePlus = document.getElementById('volume-plus');
        this.btnSlMinus = document.getElementById('sl-minus');
        this.btnSlPlus = document.getElementById('sl-plus');
        this.btnBuy = document.getElementById('btn-buy');
        this.btnSell = document.getElementById('btn-sell');
        
        // Values
        this.volumeValue = 0.02;
        this.slValue = 5.00;
        
        // Analysis
        this.currentPriceEl = document.getElementById('current-price');
        this.signalIndicator = document.getElementById('signal-indicator');
        this.scoreCircle = document.getElementById('score-circle');
        this.scoreProgress = document.getElementById('score-progress');
        this.scoreValue = document.getElementById('score-value');
        this.analysisDetails = document.getElementById('analysis-details');
        
        // Lists
        this.positionsList = document.getElementById('positions-list');
        this.historyList = document.getElementById('history-list');
        this.positionsCount = document.getElementById('positions-count');
        
        // Loading
        this.loadingScreen = document.getElementById('loading-screen');
        this.gameContainer = document.getElementById('game-container');
    }
    
    initSounds() {
        // Howler.js sound system
        this.sounds = {
            trade: new Howl({ src: ['/static/sounds/trade.mp3'], volume: 0.5 }),
            win: new Howl({ src: ['/static/sounds/win.mp3'], volume: 0.7 }),
            lose: new Howl({ src: ['/static/sounds/lose.mp3'], volume: 0.6 }),
            alert: new Howl({ src: ['/static/sounds/alert.mp3'], volume: 0.4 }),
            click: new Howl({ src: ['/static/sounds/click.mp3'], volume: 0.3 }),
            trailing: new Howl({ src: ['/static/sounds/trailing.mp3'], volume: 0.5 })
        };
    }
    
    initChart() {
        this.chartCanvas = document.getElementById('price-chart');
        this.chartCtx = this.chartCanvas.getContext('2d');
    }
    
    initEventListeners() {
        // Trading buttons
        this.btnBuy.addEventListener('click', () => this.trade('BUY'));
        this.btnSell.addEventListener('click', () => this.trade('SELL'));
        this.btnSound.addEventListener('click', () => this.toggleSound());
        
        // Volume stepper
        this.btnVolumeMinus.addEventListener('click', () => this.changeVolume(-0.01));
        this.btnVolumePlus.addEventListener('click', () => this.changeVolume(0.01));
        
        // SL stepper
        this.btnSlMinus.addEventListener('click', () => this.changeSL(-0.50));
        this.btnSlPlus.addEventListener('click', () => this.changeSL(0.50));
    }
    
    changeVolume(delta) {
        this.volumeValue = Math.max(0.01, Math.min(1.00, this.volumeValue + delta));
        this.volumeDisplay.textContent = this.volumeValue.toFixed(2);
        
        // Animation
        gsap.fromTo(this.volumeDisplay, 
            { scale: 1.2, color: '#FFD700' },
            { scale: 1, color: '#FFD700', duration: 0.3 }
        );
        
        this.playSound('click');
    }
    
    changeSL(delta) {
        this.slValue = Math.max(1.00, Math.min(50.00, this.slValue + delta));
        this.slDisplay.textContent = '$' + this.slValue.toFixed(2);
        
        // Animation
        gsap.fromTo(this.slDisplay, 
            { scale: 1.2, color: '#FFD700' },
            { scale: 1, color: '#FFD700', duration: 0.3 }
        );
        
        this.playSound('click');
    }
    
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/static/service-worker.js');
                console.log('✅ Service Worker OK');
            } catch (e) {
                console.warn('Service Worker failed:', e);
            }
        }
    }
    
    // ============================================
    // GAME FLOW
    // ============================================
    
    async startGame() {
        console.log('🎰 Starting Gold Loss Zero Game v2.0...');
        
        // Load initial data
        await this.loadGameData();
        
        // Hide loading screen
        setTimeout(() => {
            this.loadingScreen.classList.add('hidden');
            this.gameContainer.classList.remove('hidden');
            this.playSound('alert');
            this.celebrate('start');
        }, 2000);
        
        // Start polling
        this.startPolling();
    }
    
    async loadGameData() {
        await Promise.all([
            this.fetchPrediction(),
            this.fetchPositions(),
            this.fetchHistory()
        ]);
    }
    
    startPolling() {
        setInterval(() => this.fetchPrediction(), 2000);
        setInterval(() => this.fetchPositions(), 2000);
        setInterval(() => this.fetchHistory(), 10000);
    }
    
    // ============================================
    // API CALLS
    // ============================================
    
    async fetchPrediction() {
        try {
            const res = await fetch('/api/game/prediction');
            const data = await res.json();
            
            if (data.prediction) this.updatePrediction(data.prediction);
            if (data.price) this.updatePrice(data.price);
            if (data.candles) this.updateChart(data.candles);
            if (data.balance !== undefined) this.updateBalance(data.balance);
        } catch (e) {
            console.error('Fetch prediction error:', e);
        }
    }
    
    async fetchPositions() {
        try {
            const res = await fetch('/api/game/positions');
            const data = await res.json();
            
            this.positions = data.positions || [];
            this.updatePositionsDisplay();
            this.updateMegaProfit();
        } catch (e) {
            console.error('Fetch positions error:', e);
        }
    }
    
    async fetchHistory() {
        try {
            const res = await fetch('/api/game/history');
            const data = await res.json();
            
            const prevWins = this.wins;
            const prevLosses = this.losses;
            
            this.history = data.history || [];
            this.updateHistoryDisplay();
            
            if (data.stats) {
                this.updateStats(data.stats, prevWins, prevLosses);
            }
        } catch (e) {
            console.error('Fetch history error:', e);
        }
    }
    
    async trade(type) {
        const volume = this.volumeValue;
        const sl = this.slValue;
        
        if (volume <= 0 || sl <= 0) {
            alert('⚠️ Volume e SL devem ser > 0');
            return;
        }
        
        // Disable buttons
        this.btnBuy.disabled = true;
        this.btnSell.disabled = true;
        
        // Sound + animation
        this.playSound('trade');
        this.playSound('click');
        
        // Button animation
        const btn = type === 'BUY' ? this.btnBuy : this.btnSell;
        gsap.to(btn, {
            scale: 0.9,
            duration: 0.1,
            yoyo: true,
            repeat: 1
        });
        
        try {
            const res = await fetch('/api/game/open', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, volume, sl })
            });
            
            const data = await res.json();
            
            if (data.success) {
                // Celebrate
                this.celebrate('trade');
                await this.fetchPositions();
            } else {
                alert('❌ Erro: ' + (data.error || 'Desconhecido'));
                this.playSound('lose');
            }
        } catch (e) {
            console.error('Trade error:', e);
            alert('❌ Erro ao abrir posição');
        } finally {
            setTimeout(() => {
                this.btnBuy.disabled = false;
                this.btnSell.disabled = false;
            }, 1000);
        }
    }
    
    // ============================================
    // UI UPDATES
    // ============================================
    
    updateBalance(balance) {
        this.accountBalance = balance;
        this.animateNumber(this.accountBalanceEl, balance, '$');
    }
    
    updatePrice(price) {
        this.currentPrice = price;
        this.currentPriceEl.textContent = '$' + price.toFixed(2);
        
        // Pulse animation
        gsap.fromTo(this.currentPriceEl, 
            { scale: 1.2, color: '#FFD700' },
            { scale: 1, color: '#00FF41', duration: 0.3 }
        );
    }
    
    updatePrediction(pred) {
        this.prediction = pred;
        const { type, score, confidence, reason } = pred;
        
        console.log('[GAME] Prediction update:', pred);
        
        // Signal indicator - show direction even if WAIT
        const isBuyBias = reason.includes('Up20') || reason.includes('Up10');
        const isSellBias = reason.includes('Down20') || reason.includes('Down10');
        
        let signalClass = type.toLowerCase();
        let signalText = 'Analise o gráfico';
        let signalIcon = 'fa-chart-line';
        
        if (type === 'BUY') {
            signalClass = 'buy';
            signalIcon = 'fa-arrow-trend-up';
            signalText = 'Sugestão: COMPRAR';
        } else if (type === 'SELL') {
            signalClass = 'sell';
            signalIcon = 'fa-arrow-trend-down';
            signalText = 'Sugestão: VENDER';
        } else if (isBuyBias && score >= 50) {
            // Show weak buy signal
            signalClass = 'buy';
            signalIcon = 'fa-arrow-trend-up';
            signalText = `Tendência: COMPRA (Score:${score})`;
        } else if (isSellBias && score >= 50) {
            // Show weak sell signal
            signalClass = 'sell';
            signalIcon = 'fa-arrow-trend-down';
            signalText = `Tendência: VENDA (Score:${score})`;
        }
        
        this.signalIndicator.className = 'signal-indicator ' + signalClass;
        this.signalIndicator.innerHTML = `<i class="fas ${signalIcon}"></i><span>${signalText}</span>`;
        
        // Score circle
        const circumference = 283;
        const offset = circumference - (score / 100) * circumference;
        
        console.log('[GAME] Score:', score, 'Offset:', offset);
        
        gsap.to(this.scoreProgress, {
            strokeDashoffset: offset,
            duration: 1,
            ease: 'power2.out'
        });
        
        // Score color
        let scoreColor = '#FF0055';
        if (score >= 80) scoreColor = '#00FF41';
        else if (score >= 60) scoreColor = '#FFD700';
        
        this.scoreProgress.style.stroke = scoreColor;
        
        // Score value - ensure it's a number
        const scoreNum = parseFloat(score) || 0;
        this.animateNumber(this.scoreValue, scoreNum, '');
        
        // Analysis details
        this.analysisDetails.innerHTML = `
            <div><i class="fas fa-chart-bar"></i> ${reason || 'Calculando...'}</div>
            <div><i class="fas fa-percent"></i> Confiança: ${(confidence || 0).toFixed(1)}%</div>
        `;
        
        // Alert sound on high score
        if (score >= 80) {
            this.playSound('alert');
        }
    }
    
    updateChart(candles) {
        if (!candles || candles.length === 0) return;

        this.candles = candles.slice(-20);  // 20 candles para melhor visualizacao
        this.drawChart();
    }
    
    drawChart() {
        const ctx = this.chartCtx;
        const canvas = this.chartCanvas;
        const candles = this.candles;
        
        if (!candles || candles.length === 0) return;
        
        // Clear
        ctx.fillStyle = '#0d001a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Calculate range
        let minPrice = Math.min(...candles.map(c => c.low));
        let maxPrice = Math.max(...candles.map(c => c.high));
        const padding = (maxPrice - minPrice) * 0.1;
        minPrice -= padding;
        maxPrice += padding;
        const priceRange = maxPrice - minPrice;
        
        const chartHeight = canvas.height - 40;
        const chartWidth = canvas.width - 60;
        const candleWidth = chartWidth / candles.length;
        const bodyWidth = candleWidth * 0.6;
        
        // Grid
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 4; i++) {
            const y = 20 + (chartHeight / 4) * i;
            ctx.beginPath();
            ctx.moveTo(40, y);
            ctx.lineTo(canvas.width - 20, y);
            ctx.stroke();
            
            const price = maxPrice - (priceRange / 4) * i;
            ctx.fillStyle = '#666';
            ctx.font = '10px Inter';
            ctx.textAlign = 'right';
            ctx.fillText('$' + price.toFixed(2), 35, y + 3);
        }
        
        // Candles
        candles.forEach((candle, i) => {
            const x = 40 + (i * candleWidth) + (candleWidth / 2);
            const openY = 20 + ((maxPrice - candle.open) / priceRange) * chartHeight;
            const closeY = 20 + ((maxPrice - candle.close) / priceRange) * chartHeight;
            const highY = 20 + ((maxPrice - candle.high) / priceRange) * chartHeight;
            const lowY = 20 + ((maxPrice - candle.low) / priceRange) * chartHeight;
            
            const isBull = candle.close >= candle.open;
            const color = isBull ? '#00FF41' : '#FF0055';
            
            // Wick
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(x, highY);
            ctx.lineTo(x, lowY);
            ctx.stroke();
            
            // Body
            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = 10;
            ctx.fillRect(x - bodyWidth/2, Math.min(openY, closeY), bodyWidth, Math.abs(closeY - openY) || 2);
            ctx.shadowBlur = 0;
        });
        
        // Current price line
        if (this.currentPrice > 0) {
            const y = 20 + ((maxPrice - this.currentPrice) / priceRange) * chartHeight;
            ctx.strokeStyle = '#FFD700';
            ctx.lineWidth = 2;
            ctx.setLineDash([8, 4]);
            ctx.beginPath();
            ctx.moveTo(40, y);
            ctx.lineTo(canvas.width - 20, y);
            ctx.stroke();
            ctx.setLineDash([]);
            
            ctx.fillStyle = '#FFD700';
            ctx.font = 'bold 12px Orbitron';
            ctx.textAlign = 'left';
            ctx.shadowColor = '#FFD700';
            ctx.shadowBlur = 15;
            ctx.fillText('$' + this.currentPrice.toFixed(2), canvas.width - 75, y - 8);
            ctx.shadowBlur = 0;
        }
    }
    
    updateMegaProfit() {
        let totalProfit = 0;
        
        if (this.positions.length > 0) {
            totalProfit = this.positions.reduce((sum, p) => sum + p.profit, 0);
            this.opStatus.textContent = this.positions.length + ' POSIÇÃO(ÕES) ATIVA(S)';
            this.opIcon.className = 'fas fa-circle-dot';
            this.opIcon.style.color = '#00FF41';
        } else {
            this.opStatus.textContent = 'AGUARDANDO';
            this.opIcon.className = 'fas fa-circle';
            this.opIcon.style.color = '#888';
        }
        
        // Animate mega profit
        this.animateNumber(this.profitValue, totalProfit, '');
        
        // Color
        this.profitMega.className = 'profit-mega';
        if (totalProfit > 0) {
            this.profitMega.classList.add('positive');
        } else if (totalProfit < 0) {
            this.profitMega.classList.add('negative');
        }
    }
    
    updatePositionsDisplay() {
        this.positionsCount.textContent = this.positions.length;
        
        if (this.positions.length === 0) {
            this.positionsList.innerHTML = '<div style="text-align:center;padding:30px;color:#888;">Nenhuma posição</div>';
            return;
        }
        
        this.positionsList.innerHTML = this.positions.map(p => `
            <div class="list-item position-item">
                <span class="item-badge ${p.type.toLowerCase()}">${p.type}</span>
                <div class="item-info">
                    <span class="item-label">#${p.ticket} • ${p.volume} lotes</span>
                    <span class="item-value">Entry: $${p.entry_price.toFixed(2)}</span>
                    ${p.trailing_active ? '<span style="color:#00FF41;font-size:10px;"><i class="fas fa-robot"></i> Trailing ON</span>' : ''}
                </div>
                <div class="item-profit ${p.profit >= 0 ? 'positive' : 'negative'}">
                    ${p.profit >= 0 ? '+' : ''}$${p.profit.toFixed(2)}
                </div>
                <button class="btn-close-position" data-ticket="${p.ticket}" title="Fechar posição">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
        
        // Add click listeners to close buttons
        document.querySelectorAll('.btn-close-position').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const ticket = parseInt(btn.dataset.ticket);
                this.closePosition(ticket);
            });
        });
    }
    
    async closePosition(ticket) {
        this.playSound('click');
        
        try {
            const res = await fetch('/api/game/close', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticket })
            });
            
            const data = await res.json();
            
            if (data.success) {
                this.playSound('alert');
                
                // Show profit
                const profit = data.profit || 0;
                const msg = profit >= 0 
                    ? `✅ Posição fechada: +$${profit.toFixed(2)}`
                    : `❌ Posição fechada: -$${Math.abs(profit).toFixed(2)}`;
                
                // Toast notification (simple)
                const toast = document.createElement('div');
                toast.className = 'toast-notification';
                toast.style.cssText = `
                    position: fixed;
                    top: 100px;
                    right: 20px;
                    background: ${profit >= 0 ? '#00FF41' : '#FF0055'};
                    color: ${profit >= 0 ? '#003300' : '#ffffff'};
                    padding: 15px 25px;
                    border-radius: 10px;
                    font-family: 'Orbitron', sans-serif;
                    font-weight: 700;
                    font-size: 14px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    z-index: 10000;
                    animation: slideIn 0.3s;
                `;
                toast.textContent = msg;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.style.animation = 'slideOut 0.3s';
                    setTimeout(() => toast.remove(), 300);
                }, 3000);
                
                // Refresh positions
                await this.fetchPositions();
                await this.fetchHistory();
                
                if (profit > 0) {
                    this.celebrate('win', profit);
                }
            } else {
                alert('❌ Erro: ' + (data.error || 'Desconhecido'));
                this.playSound('lose');
            }
        } catch (e) {
            console.error('Close position error:', e);
            alert('❌ Erro ao fechar posição');
        }
    }
    
    updateHistoryDisplay() {
        if (this.history.length === 0) {
            this.historyList.innerHTML = '<div style="text-align:center;padding:30px;color:#888;">Sem histórico</div>';
            return;
        }
        
        this.historyList.innerHTML = this.history.slice(0, 10).map(t => {
            // Handle different timestamp formats
            let timeString = 'N/A';
            try {
                if (t.close_time) {
                    // Try to parse the timestamp
                    const date = new Date(t.close_time);
                    if (!isNaN(date.getTime())) {
                        timeString = date.toLocaleTimeString();
                    } else {
                        // Fallback: assume it's already a formatted string
                        timeString = t.close_time;
                    }
                }
            } catch (e) {
                console.warn('Error parsing timestamp:', t.close_time, e);
                timeString = 'N/A';
            }
            
            // Ensure profit is a number
            const profit = parseFloat(t.profit) || 0;
            
            return `
                <div class="list-item">
                    <span class="item-badge ${t.type.toLowerCase()}">${t.type}</span>
                    <div class="item-info">
                        <span class="item-label">#${t.ticket}</span>
                        <span class="item-value">${timeString}</span>
                    </div>
                    <div class="item-profit ${profit >= 0 ? 'positive' : 'negative'}">
                        ${profit >= 0 ? '+' : ''}$${profit.toFixed(2)}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    updateStats(stats, prevWins, prevLosses) {
        const { total_profit, wins, losses, streak } = stats;
        
        // Animate profit
        this.animateNumber(this.totalProfitEl, total_profit, '$');
        
        // Win rate
        const totalTrades = wins + losses;
        const winRate = totalTrades > 0 ? (wins / totalTrades * 100) : 0;
        this.winRateEl.textContent = winRate.toFixed(0) + '%';
        
        // Streak
        this.streakEl.textContent = streak;
        
        // Check for new win/loss
        if (wins > prevWins) {
            this.onWin(total_profit - this.totalProfit);
        } else if (losses > prevLosses) {
            this.onLoss();
        }
        
        this.totalProfit = total_profit;
        this.wins = wins;
        this.losses = losses;
        this.streak = streak;
    }
    
    // ============================================
    // EFFECTS & ANIMATIONS
    // ============================================
    
    onWin(amount) {
        this.playSound('win');
        this.celebrate('win', amount);
        
        // Shake total profit
        gsap.to(this.totalProfitEl, {
            scale: 1.5,
            duration: 0.3,
            yoyo: true,
            repeat: 1,
            ease: 'elastic.out(1, 0.3)'
        });
    }
    
    onLoss() {
        this.playSound('lose');
        
        // Shake effect
        gsap.to(this.profitMega, {
            x: -10,
            duration: 0.1,
            yoyo: true,
            repeat: 5
        });
    }
    
    celebrate(type, amount = 0) {
        if (type === 'win') {
            // Big win confetti
            if (amount > 10) {
                confetti({
                    particleCount: 150,
                    spread: 180,
                    origin: { y: 0.5 },
                    colors: ['#FFD700', '#FFA500', '#00FF41'],
                    shapes: ['circle', 'square'],
                    gravity: 0.8,
                    scalar: 1.2
                });
            } else {
                confetti({
                    particleCount: 50,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#FFD700', '#00FF41']
                });
            }
        } else if (type === 'trade') {
            confetti({
                particleCount: 30,
                spread: 50,
                origin: { y: 0.5 },
                colors: ['#FFD700', '#FFA500'],
                startVelocity: 20
            });
        } else if (type === 'start') {
            confetti({
                particleCount: 100,
                spread: 160,
                origin: { y: 0.6 },
                colors: ['#FFD700', '#FFA500', '#B026FF']
            });
        }
    }
    
    animateNumber(element, endValue, prefix = '') {
        const startValue = parseFloat(element.textContent.replace(/[^0-9.-]/g, '')) || 0;
        
        gsap.to({ value: startValue }, {
            value: endValue,
            duration: 1,
            ease: 'power2.out',
            onUpdate: function() {
                element.textContent = prefix + this.targets()[0].value.toFixed(2);
            }
        });
    }
    
    playSound(name) {
        if (!this.soundEnabled) return;
        
        try {
            const sound = this.sounds[name];
            if (sound) {
                sound.play();
            }
        } catch (e) {
            console.warn('Sound error:', e);
        }
    }
    
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        const icon = this.btnSound.querySelector('i');
        icon.className = this.soundEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
        
        gsap.to(this.btnSound, {
            scale: 1.3,
            duration: 0.2,
            yoyo: true,
            repeat: 1
        });
    }
}



// ============================================
// START APP
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    window.goldGame = new GoldGameV2();
});
