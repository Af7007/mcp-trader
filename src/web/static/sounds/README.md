# 🎵 Sound Effects for Gold Loss Zero Game

## Required Sound Files

Place the following MP3 files in this directory:

### 1. `win.mp3`
- **Trigger**: When a position closes with profit
- **Duration**: 1-2 seconds
- **Style**: Celebratory, positive (coins, bell, cheer)
- **Example**: Casino win sound, cash register, "cha-ching"

### 2. `lose.mp3`
- **Trigger**: When a position closes with loss
- **Duration**: 1-2 seconds
- **Style**: Negative feedback (buzzer, sad tone)
- **Example**: Buzzer, "aww" sound, game over tone

### 3. `trade.mp3`
- **Trigger**: When opening a new position
- **Duration**: 0.5-1 seconds
- **Style**: Action, confirmation (click, beep)
- **Example**: Button click, confirmation beep, snap

### 4. `alert.mp3`
- **Trigger**: When a strong signal appears (score >= 70)
- **Duration**: 0.5-1 seconds
- **Style**: Attention grabber (ding, notification)
- **Example**: Notification sound, bell ding, alert tone

## How to Get Sound Effects

### Free Sources
- **Freesound.org**: https://freesound.org (CC-licensed sounds)
- **Zapsplat**: https://www.zapsplat.com (Free sound effects)
- **Mixkit**: https://mixkit.co/free-sound-effects/ (Free sounds)
- **Soundbible**: http://soundbible.com (Public domain sounds)

### Search Terms
- Win: "coin", "cash register", "success", "victory"
- Lose: "buzzer", "fail", "error", "negative"
- Trade: "click", "button", "confirm", "beep"
- Alert: "notification", "ding", "bell", "alert"

## Format Requirements
- **Format**: MP3 (recommended) or OGG
- **Size**: < 100KB per file (preferably < 50KB)
- **Quality**: 128kbps is sufficient
- **Channels**: Mono or Stereo

## Creating Placeholder Sounds

If you don't have sounds yet, the game will work silently. You can add them later.

### Using Text-to-Speech (Temporary)
Use online TTS to generate temporary placeholders:
- Win: "Congratulations! You won!"
- Lose: "Better luck next time"
- Trade: "Order placed"
- Alert: "Signal detected"

### Using Beep Sounds
Generate simple beeps at different frequencies:
- Win: High pitch beep (1000Hz)
- Lose: Low pitch beep (200Hz)
- Trade: Mid pitch beep (500Hz)
- Alert: Double beep (800Hz)

## Testing Sounds

To test sounds in the game:
1. Open browser console (F12)
2. Type: `window.goldGame.playSound('win')`
3. Check if sound plays
4. Repeat for 'lose', 'trade', 'alert'

## Disabling Sounds

To disable sounds temporarily, edit `game.js`:

```javascript
playSound(type) {
    return; // Disable all sounds
    
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
```

## Volume Control

To adjust volume, add this to `game.js` constructor:

```javascript
// Set volume (0.0 to 1.0)
Object.values(this.sounds).forEach(sound => {
    sound.volume = 0.5; // 50% volume
});
```

## Browser Autoplay Policy

Modern browsers require user interaction before playing sounds. The game handles this automatically - sounds will only play after the user interacts with the page (clicking a button, etc.).

If sounds don't play:
1. Click anywhere on the page first
2. Check browser console for errors
3. Verify audio files exist in this directory
4. Check file names match exactly (case-sensitive)

## License Note

When using sound effects from free sources:
- Read and follow the license terms
- Provide attribution if required
- Don't use sounds marked "commercial use prohibited" in commercial projects
- For personal/educational use, most free sounds are fine
