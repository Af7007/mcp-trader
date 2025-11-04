#!/usr/bin/env python3
"""
Script para corrigir a função de predição no game_api.py
"""

import re

# Nova função de predição focada em M1
new_prediction_function = '''
def _predict_next_candle(mt5) -> Dict:
    """
    Prediction system aligned with M1 chart data displayed in game
    Uses EXACTLY the same candles and data shown in the chart
    
    Returns:
        {
            "type": "BUY" | "SELL" | "WAIT",
            "score": 0-100,
            "confidence": 0-100,
            "reason": "explanation"
        }
    """
    try:
        print("[PREDICTION] Starting M1-aligned analysis...")
        
        # === M1 Data (EXACT SAME as chart) ===
        rates_m1 = mt5.copy_rates_from_pos(
            symbol="XAUUSDc",
            timeframe="M1",
            start_pos=0,
            count=20  # SAME as chart display
        )
        
        print(f"[PREDICTION] M1 candles: {len(rates_m1) if rates_m1 else 0}")
        
        if not rates_m1 or len(rates_m1) < 15:
            print("[PREDICTION] ERROR: Insufficient M1 data")
            return {"type": "WAIT", "score": 0, "confidence": 0, "reason": "Insufficient M1 data"}
        
        # Extract same data structure as chart
        closes = [float(r['close']) for r in rates_m1[:15]]  # Last 15 candles (same as chart)
        highs = [float(r['high']) for r in rates_m1[:15]]
        lows = [float(r['low']) for r in rates_m1[:15]]
        volumes = [float(r.get('tick_volume', 1000)) for r in rates_m1[:15]]
        
        current = closes[0]
        
        print(f"[PREDICTION] Current price: ${current:.2f}")
        print(f"[PREDICTION] Chart data range: ${min(closes):.2f} - ${max(closes):.2f}")
        
        # === ANALYSIS BASED ON EXACT CHART DATA ===
        
        # 1. Simple Trend Analysis (based on chart candles)
        last_5 = closes[:5]
        last_3 = closes[:3]
        last_2 = closes[:2]
        
        # Recent direction
        up_2 = last_2[0] < last_2[1] if len(last_2) >= 2 else False
        up_3 = sum([1 for i in range(len(last_3)-1) if last_3[i] < last_3[i+1]]) >= 2
        up_5 = sum([1 for i in range(len(last_5)-1) if last_5[i] < last_5[i+1]]) >= 3
        
        # 2. Support/Resistance from chart data
        recent_high = max(closes[:5])
        recent_low = min(closes[:5])
        price_position = (current - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
        
        # 3. Volume analysis (if available)
        avg_volume = sum(volumes) / len(volumes)
        recent_volume = sum(volumes[:3]) / 3
        volume_trend = "normal" if recent_volume >= avg_volume * 0.8 else "low"
        
        # 4. Momentum from chart movement
        momentum_1 = ((closes[0] - closes[1]) / closes[1]) * 100 if len(closes) > 1 else 0
        momentum_3 = ((closes[0] - closes[3]) / closes[3]) * 100 if len(closes) > 3 else 0
        momentum_5 = ((closes[0] - closes[5]) / closes[5]) * 100 if len(closes) > 5 else 0
        
        print(f"[PREDICTION] Momentum: 1c={momentum_1:.3f}%, 3c={momentum_3:.3f}%, 5c={momentum_5:.3f}%")
        
        # 5. Volatility check (from chart candles)
        candle_ranges = [highs[i] - lows[i] for i in range(min(5, len(highs)))]
        avg_range = sum(candle_ranges) / len(candle_ranges)
        current_range = highs[0] - lows[0]
        volatility = current_range / avg_range if avg_range > 0 else 1
        
        print(f"[PREDICTION] Volatility: {volatility:.2f}x average")
        
        # === SIGNAL GENERATION ===
        score = 0
        signal_factors = []
        
        # BUY CONDITIONS (based on chart data)
        if up_2 or up_3:
            score += 20
            signal_factors.append(f"Trend:{up_3 and 'Up3' or 'Up2'}")
            
        if momentum_3 > 0.001:  # Positive momentum
            score += 15
            signal_factors.append(f"Momentum:+{momentum_3:.3f}%")
        elif momentum_3 < -0.001:  # Negative momentum hurts buy signal
            score -= 10
            signal_factors.append(f"Momentum:{momentum_3:.3f}%")
            
        if price_position > 0.6:  # Near resistance
            score += 10
            signal_factors.append("Near resistance")
        elif price_position < 0.4:  # Near support  
            score += 5
            signal_factors.append("Near support")
            
        if volatility > 2.0:  # High volatility
            score -= 15
            signal_factors.append("High volatility")
        elif volatility < 0.7:  # Low volatility (consolidation)
            score += 10
            signal_factors.append("Low volatility")
            
        if volume_trend == "normal":
            score += 5
            signal_factors.append("Normal volume")
        
        # SELL CONDITIONS (opposite of buy)
        sell_score = 0
        sell_factors = []
        
        # Check for sell signals
        down_trend = not up_3 and momentum_3 < -0.001
        if down_trend:
            sell_score += 20
            sell_factors.append(f"Trend:Down3")
            
        if momentum_3 < -0.001:
            sell_score += 15
            sell_factors.append(f"Momentum:{momentum_3:.3f}%")
            
        if price_position < 0.4:  # Near support (vulnerable to breakdown)
            sell_score += 10
            sell_factors.append("Near support")
            
        if volatility > 2.0:
            sell_score -= 10  # High volatility hurts sell signal too
            
        # === FINAL SIGNAL ===
        confidence = min(abs(momentum_5) * 100, 100)  # Based on actual movement
        
        # Determine final signal
        if score >= 30 and score > sell_score:
            signal_type = "BUY"
            final_score = min(score, 100)
            reason = f"M1 Chart | {' | '.join(signal_factors)} | Score:{final_score}"
            print(f"[PREDICTION] BUY signal: score={final_score}, confidence={confidence:.1f}")
            
        elif sell_score >= 30 and sell_score > score:
            signal_type = "SELL"
            final_score = min(sell_score, 100)
            reason = f"M1 Chart | {' | '.join(sell_factors)} | Score:{final_score}"
            print(f"[PREDICTION] SELL signal: score={final_score}, confidence={confidence:.1f}")
            
        else:
            signal_type = "WAIT"
            final_score = max(score, sell_score)
            reason = f"M1 Chart | {up_3 and 'Up3' or down_trend and 'Down3' or 'Neutral'} | Score:{final_score}"
            print(f"[PREDICTION] WAIT signal: score={final_score}")
        
        return {
            "type": signal_type,
            "score": final_score,
            "confidence": confidence,
            "reason": reason
        }
        
    except Exception as e:
        print(f"[PREDICTION] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"type": "WAIT", "score": 0, "confidence": 0, "reason": f"Error: {str(e)}"}
'''

print("Nova função de predição criada!")
print("Aguardando aplicação manual...")
