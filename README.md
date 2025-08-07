# 🏓 Pong Game - AI Fluida

Un classico gioco Pong implementato in Python con Pygame, caratterizzato da un'intelligenza artificiale fluida e avanzata senza tremolii.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Caratteristiche

- **AI Fluida**: Movimento dell'AI senza scatti o tremolii
- **Audio Dinamico**: Supporto per file MP3 personalizzati o generazione di suoni sintetici
- **Adattamento Dinamico**: L'AI si adatta automaticamente alla difficoltà in base al punteggio
- **Cross-Platform**: Ottimizzazioni audio specifiche per Windows, macOS e Linux
- **Controlli Intuitivi**: Supporto sia per WASD che per le frecce direzionali

## 🎮 Controlli

- **W** / **Freccia Su**: Muovi il paddle verso l'alto
- **S** / **Freccia Giù**: Muovi il paddle verso il basso
- **ESC**: Esci dal gioco

## 🛠️ Requisiti

### Dipendenze Python
```bash
pip install pygame numpy
```

**Versioni testate:**
- Python 3.7+
- Pygame 2.0+
- NumPy 1.19+

### File Audio (Opzionali)
Per un'esperienza audio personalizzata, crea una cartella `sounds/` con i seguenti file:
- `sounds/paddle.mp3` - Suono rimbalzo sul paddle
- `sounds/wall.mp3` - Suono rimbalzo sulla parete
- `sounds/goal.mp3` - Suono quando si segna un goal

**Nota**: Se i file MP3 non sono presenti, il gioco genererà automaticamente suoni sintetici.

## 🚀 Installazione e Avvio

1. **Clona il repository**:
   ```bash
   git clone https://github.com/EventExecutor/Pong-Game.git
   cd pong-game
   ```

2. **Installa le dipendenze**:
   ```bash
   pip install pygame numpy
   ```
   
   Oppure usando requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

3. **Avvia il gioco**:
   ```bash
   python main.py
   ```

## 🎯 Caratteristiche dell'AI

### Sistema di Predizione
- **Predizione traiettoria**: L'AI calcola dove la palla colpirà il suo paddle
- **Gestione rimbalzi**: Simula i rimbalzi contro le pareti per predizioni accurate
- **Movimento strategico**: Posizionamento intelligente quando la palla si allontana

### Adattamento Dinamico
- **Difficoltà basata sul punteggio**: L'AI diventa più forte con l'avanzare del gioco
- **Bilanciamento automatico**: Se il giocatore è in svantaggio, l'AI rallenta leggermente
- **Velocità variabile**: L'AI reagisce alla velocità della palla

### Anti-Tremolo
- **Zona morta**: Previene micro-movimenti quando il paddle è già posizionato
- **Movimento fluido**: Accelerazione e decelerazione graduali
- **Stabilizzazione predizioni**: Evita cambi continui di direzione

## ⚙️ Configurazione

### Parametri principali modificabili in `main.py`:

```python
# Dimensioni schermo
LARGHEZZA = 800
ALTEZZA = 600

# Paddle
PADDLE_VELOCITA = 7
PADDLE_LARGHEZZA = 15
PADDLE_ALTEZZA = 90

# Palla
PALLA_VELOCITA_BASE = 6
PALLA_RAGGIO = 8

# AI
difficolta_base = 0.70      # Difficoltà base (0.0 - 1.0)
max_difficolta = 0.90       # Difficoltà massima
adattamento_ai = True       # Abilita adattamento dinamico
```

## 🖥️ Compatibilità

- **Windows**: Ottimizzazioni buffer audio (512)
- **macOS**: Ottimizzazioni buffer audio (256)  
- **Linux**: Ottimizzazioni buffer audio (1024)

## 🎵 Sistema Audio

### Audio MP3 Personalizzato
Posiziona i file nella cartella `sounds/`:
```
sounds/
├── paddle.mp3
├── wall.mp3
└── goal.mp3
```

### Audio Sintetico (Fallback)
Se i file MP3 non sono disponibili:
- **Paddle**: Beep a 523 Hz (Do)
- **Parete**: Beep a 330 Hz (Mi)
- **Goal**: Suono discendente con vibrato

## 📊 Sistema di Punteggio

- **Display in tempo reale**: Punteggi mostrati in alto
- **Etichette giocatori**: "GIOCATORE" vs "AI"
- **Indicatore difficoltà**: Mostra la difficoltà attuale dell'AI (quando abilitata)

## 🐛 Risoluzione Problemi

### Audio non funziona
- Verifica che i file MP3 siano nella cartella `sounds/`
- Controlla i permessi della cartella
- Il gioco funziona anche senza audio

### Performance scarse
- Riduci FPS modificando `FPS = 60`
- Chiudi altre applicazioni che usano audio
- Su Linux, prova buffer audio diversi

### Controlli non responsivi
- Verifica che la finestra del gioco sia attiva
- Controlla che pygame sia installato correttamente

## 🔧 Sviluppo

### Struttura del codice
- **Classe Paddle**: Gestisce movimento giocatore e AI
- **Classe Palla**: Fisica e collisioni della palla
- **Classe Gioco**: Loop principale e gestione stati
- **Sistema Audio**: Generazione e riproduzione suoni

### Aggiungere nuove funzionalità
1. **Nuovi suoni**: Aggiungi file nella cartella `sounds/`
2. **Modificare AI**: Regola parametri in `ai_muovi()`
3. **Nuovi controlli**: Modifica `gestisci_input_gioco()`

## 📝 Licenza

Questo progetto è rilasciato sotto [Licenza MIT](LICENSE).

## 🚀 Contribuire

I contributi sono benvenuti! Per contribuire:

1. **Fork** del repository
2. **Crea** un branch per le tue modifiche (`git checkout -b feature/nuova-funzionalita`)
3. **Commit** delle modifiche (`git commit -m 'Aggiungi nuova funzionalità'`)
4. **Push** al branch (`git push origin feature/nuova-funzionalita`)
5. **Apri** una Pull Request

### Idee per contributi
- 🎨 Nuovi temi grafici
- 🔊 Più effetti sonori
- 🤖 Modalità AI diverse
- 🏆 Sistema di achievement
- 🌐 Modalità multiplayer online

## 🙏 Crediti

Sviluppato con Python e Pygame. Suoni sintetici generati con NumPy.
