import pygame
import sys
import random
import numpy as np
import platform
import math
import os

pygame.init()

system = platform.system()
if system == "Windows":
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
elif system == "Darwin":
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
elif system == "Linux":
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
else:
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)

pygame.mixer.init()
print(f"Sistema rilevato: {system}")

LARGHEZZA = 800
ALTEZZA = 600
BIANCO = (255, 255, 255)
NERO = (0, 0, 0)
GRIGIO = (128, 128, 128)
GRIGIO_SCURO = (64, 64, 64)
FPS = 60

PADDLE_LARGHEZZA = 15
PADDLE_ALTEZZA = 90
PADDLE_VELOCITA = 7

PALLA_RAGGIO = 8
PALLA_VELOCITA_BASE = 6

def crea_suono_beep(frequenza, durata, volume=0.3):
    try:
        sample_rate = pygame.mixer.get_init()[0]
        if sample_rate is None:
            sample_rate = 44100
        
        frames = int(durata * sample_rate)
        
        t = np.linspace(0, durata, frames, False)
        wave = np.sin(2 * np.pi * frequenza * t)

        fade_frames = int(0.01 * sample_rate)
        fade_in = np.linspace(0, 1, fade_frames)
        fade_out = np.linspace(1, 0, fade_frames)
        
        wave[:fade_frames] *= fade_in
        wave[-fade_frames:] *= fade_out
        
        wave = (wave * volume * 32767).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        
        return pygame.sndarray.make_sound(stereo_wave)
    except Exception as e:
        print(f"Errore creazione suono beep: {e}")
        return None

def crea_suono_goal():
    try:
        sample_rate = pygame.mixer.get_init()[0]
        if sample_rate is None:
            sample_rate = 44100
            
        durata = 0.8
        t = np.linspace(0, durata, int(durata * sample_rate), False)
        
        freq_start = 600
        freq_end = 200
        freq = freq_start - (freq_start - freq_end) * (t / durata)
        
        vibrato = 1 + 0.1 * np.sin(2 * np.pi * 8 * t)
        wave = 0.4 * np.sin(2 * np.pi * freq * vibrato * t)
        
        envelope = np.exp(-t * 2)
        wave *= envelope
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        
        return pygame.sndarray.make_sound(stereo_wave)
    except Exception as e:
        print(f"Errore creazione suono goal: {e}")
        return None

def carica_suono_mp3(nome_file):
    percorsi = [f"sounds/{nome_file}", nome_file]
    
    for percorso in percorsi:
        try:
            if os.path.exists(percorso):
                return pygame.mixer.Sound(percorso)
        except (pygame.error, FileNotFoundError):
            continue
    return None

suono_paddle = carica_suono_mp3("paddle.mp3")
suono_parete = carica_suono_mp3("wall.mp3") 
suono_goal = carica_suono_mp3("goal.mp3")

if not suono_paddle or not suono_parete or not suono_goal:
    print("File MP3 non trovati, generando suoni sintetici...")
    try:
        if not suono_paddle:
            suono_paddle = crea_suono_beep(523, 0.1, 0.6)
        if not suono_parete:
            suono_parete = crea_suono_beep(330, 0.15, 0.5)
        if not suono_goal:
            suono_goal = crea_suono_goal()
        
        audio_disponibile = all([suono_paddle, suono_parete, suono_goal])
        
        if audio_disponibile:
            print("Audio sintetico inizializzato!")
        else:
            raise Exception("Errore nella creazione dei suoni")
            
    except Exception as e:
        print(f"Errore nell'inizializzazione audio: {e}")
        print("Il gioco funzionerà senza suoni.")
        audio_disponibile = False
        
        class SuonoDummy:
            def play(self): pass
            def set_volume(self, vol): pass
        
        suono_paddle = SuonoDummy()
        suono_parete = SuonoDummy()
        suono_goal = SuonoDummy()
else:
    audio_disponibile = True
    print("File MP3 personalizzati caricati con successo!")
    print("- sounds/paddle.mp3 per il rimbalzo sul paddle")
    print("- sounds/wall.mp3 per il rimbalzo sulla parete")  
    print("- sounds/goal.mp3 per i goal")

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.larghezza = PADDLE_LARGHEZZA
        self.altezza = PADDLE_ALTEZZA
        self.velocita = PADDLE_VELOCITA
        self.rect = pygame.Rect(x, y, self.larghezza, self.altezza)

        self.target_y = y
        self.velocita_attuale = 0.0
        self.ultima_predizione = ALTEZZA // 2
        self.frame_senza_aggiornamento = 0 
    
    def muovi_su(self):
        if self.y > 0:
            self.y -= self.velocita
            self.rect.y = self.y
    
    def muovi_giu(self):
        if self.y < ALTEZZA - self.altezza:
            self.y += self.velocita
            self.rect.y = self.y
    
    def ai_muovi(self, palla_x, palla_y, palla_velocita_x, palla_velocita_y, difficolta=0.85):

        if palla_velocita_x > 0:
            tempo_impatto = max(0.1, (self.x - palla_x) / abs(palla_velocita_x))
            predizione_y = palla_y + palla_velocita_y * tempo_impatto
            
            while predizione_y < 0 or predizione_y > ALTEZZA:
                if predizione_y < 0:
                    predizione_y = -predizione_y
                elif predizione_y > ALTEZZA:
                    predizione_y = 2 * ALTEZZA - predizione_y
            
            if abs(predizione_y - self.ultima_predizione) > 15:
                self.ultima_predizione = predizione_y
                self.frame_senza_aggiornamento = 0
            else:
                self.frame_senza_aggiornamento += 1
                predizione_y = self.ultima_predizione
            
            self.target_y = predizione_y
        else:
            centro = ALTEZZA // 2
            self.target_y = centro
        
        centro_paddle = self.y + self.altezza // 2
        
        if palla_velocita_x > 0 and palla_x > LARGHEZZA * 0.6:
            if random.random() < 0.1:
                offset_strategia = 10 if palla_y > ALTEZZA // 2 else -10
                self.target_y += offset_strategia
        
        if self.frame_senza_aggiornamento <= 5:
            errore_base = (1 - difficolta) * 15
            errore = random.gauss(0, errore_base) * 0.5
            self.target_y += errore
        
        distanza_target = self.target_y - (self.y + self.altezza // 2)

        zona_morta = 8
        
        if abs(distanza_target) > zona_morta:

            max_velocita = self.velocita * difficolta

            if abs(distanza_target) > 50:
                velocita_desiderata = max_velocita
            else:
                velocita_desiderata = max_velocita * (abs(distanza_target) / 50)
            
            fattore_smooth = 0.15 
            if distanza_target > 0:
                self.velocita_attuale += (velocita_desiderata - abs(self.velocita_attuale)) * fattore_smooth
                movimento = min(self.velocita_attuale, abs(distanza_target))
            else:
                self.velocita_attuale += (velocita_desiderata - abs(self.velocita_attuale)) * fattore_smooth
                movimento = min(self.velocita_attuale, abs(distanza_target))
            
            if distanza_target > zona_morta:
                nuovo_y = self.y + movimento
                if nuovo_y <= ALTEZZA - self.altezza:
                    self.y = nuovo_y
            elif distanza_target < -zona_morta:
                nuovo_y = self.y - movimento
                if nuovo_y >= 0:
                    self.y = nuovo_y
        else:
            self.velocita_attuale *= 0.8
        
        if random.random() < (1 - difficolta) * 0.005:
            piccolo_errore = random.randint(-8, 8)
            nuovo_y = max(0, min(ALTEZZA - self.altezza, self.y + piccolo_errore))
            self.y = nuovo_y
        
        self.rect.y = int(self.y)
    
    def disegna(self, schermo):
        pygame.draw.rect(schermo, BIANCO, self.rect)
        pygame.draw.rect(schermo, (200, 200, 255), self.rect, 1)

class Palla:
    def __init__(self):
        self.velocita_base = PALLA_VELOCITA_BASE
        self.velocita_massima = 12
        self.reset()
    
    def muovi(self):
        self.x += self.velocita_x
        self.y += self.velocita_y
        
        if self.y - self.raggio <= 0 or self.y + self.raggio >= ALTEZZA:
            self.velocita_y = -self.velocita_y
            self.y = max(self.raggio, min(ALTEZZA - self.raggio, self.y))
            if audio_disponibile:
                try:
                    suono_parete.play()
                except:
                    pass
    
    def rimbalza_paddle(self, paddle):
        self.velocita_x = -self.velocita_x
        
        centro_paddle = paddle.y + paddle.altezza / 2
        hit_pos = (self.y - centro_paddle) / (paddle.altezza / 2)
        hit_pos = max(-1, min(1, hit_pos))
        
        self.velocita_y += hit_pos * 3
        
        self.velocita_x *= 1.05
        self.velocita_y *= 1.02
        
        velocita_totale = math.sqrt(self.velocita_x**2 + self.velocita_y**2)
        if velocita_totale > self.velocita_massima:
            fattore = self.velocita_massima / velocita_totale
            self.velocita_x *= fattore
            self.velocita_y *= fattore
        
        if abs(self.velocita_y) > 8:
            self.velocita_y = 8 if self.velocita_y > 0 else -8
        
        if audio_disponibile:
            try:
                suono_paddle.play()
            except:
                pass
    
    def reset(self):
        self.x = float(LARGHEZZA // 2)
        self.y = float(ALTEZZA // 2)
        self.raggio = PALLA_RAGGIO
        
        angolo = random.uniform(-math.pi/4, math.pi/4)
        if random.choice([True, False]):
            angolo += math.pi
        
        self.velocita_x = self.velocita_base * math.cos(angolo)
        self.velocita_y = self.velocita_base * math.sin(angolo)
    
    def disegna(self, schermo):
        pygame.draw.circle(schermo, BIANCO, (int(self.x), int(self.y)), self.raggio)
        pygame.draw.circle(schermo, (255, 255, 200), (int(self.x - 2), int(self.y - 2)), max(1, self.raggio - 4))

class Gioco:
    def __init__(self):
        self.schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
        pygame.display.set_caption("Pong Game - ESC per pausa")
        self.clock = pygame.time.Clock()
        
        self.giocatore = Paddle(50, ALTEZZA // 2 - PADDLE_ALTEZZA // 2)
        self.ai = Paddle(LARGHEZZA - 50 - PADDLE_LARGHEZZA, ALTEZZA // 2 - PADDLE_ALTEZZA // 2)
        self.palla = Palla()
        
        self.punteggio_giocatore = 0
        self.punteggio_ai = 0
        self.font = pygame.font.Font(None, 74)
        self.font_piccolo = pygame.font.Font(None, 28)
        self.font_menu = pygame.font.Font(None, 60)
        self.font_opzioni = pygame.font.Font(None, 40)
        
        self.stato = "gioco" 
        
        self.difficolta_base = 0.70
        self.max_difficolta = 0.90 
        self.adattamento_ai = True
    
    def reset_punteggio(self):
        """Resetta solo il punteggio"""
        self.punteggio_giocatore = 0
        self.punteggio_ai = 0
        self.palla.reset()
    
    def gestisci_input_gioco(self):
        tasti = pygame.key.get_pressed()
        if tasti[pygame.K_w] or tasti[pygame.K_UP]:
            self.giocatore.muovi_su()
        if tasti[pygame.K_s] or tasti[pygame.K_DOWN]:
            self.giocatore.muovi_giu()
    
    def aggiorna_logica(self):
        self.palla.muovi()
        
        if self.adattamento_ai:
            punteggio_totale = self.punteggio_giocatore + self.punteggio_ai
            differenza_punteggio = self.punteggio_giocatore - self.punteggio_ai
            velocita_palla = math.sqrt(self.palla.velocita_x**2 + self.palla.velocita_y**2)
            
            difficolta_punteggio = min(0.10, punteggio_totale * 0.015) 
            difficolta_equilibrio = min(0.08, differenza_punteggio * 0.02) 
            difficolta_velocita = min(0.03, (velocita_palla - 6) * 0.015) 
            
            difficolta_attuale = self.difficolta_base + difficolta_punteggio + difficolta_equilibrio + difficolta_velocita
            difficolta_attuale = min(self.max_difficolta, difficolta_attuale)
        else:
            difficolta_attuale = self.difficolta_base
    
        self.ai.punteggio_ai = self.punteggio_ai
        self.ai.punteggio_giocatore = self.punteggio_giocatore
        
        self.ai.ai_muovi(
            self.palla.x, self.palla.y, 
            self.palla.velocita_x, self.palla.velocita_y, 
            difficolta_attuale
        )
        
        if (self.palla.x - self.palla.raggio <= self.giocatore.rect.right and
            self.palla.x + self.palla.raggio >= self.giocatore.rect.left and
            self.palla.y + self.palla.raggio >= self.giocatore.rect.top and
            self.palla.y - self.palla.raggio <= self.giocatore.rect.bottom and
            self.palla.velocita_x < 0):
            
            self.palla.x = self.giocatore.rect.right + self.palla.raggio
            self.palla.rimbalza_paddle(self.giocatore)
        
        if (self.palla.x + self.palla.raggio >= self.ai.rect.left and
            self.palla.x - self.palla.raggio <= self.ai.rect.right and
            self.palla.y + self.palla.raggio >= self.ai.rect.top and
            self.palla.y - self.palla.raggio <= self.ai.rect.bottom and
            self.palla.velocita_x > 0):
            
            self.palla.x = self.ai.rect.left - self.palla.raggio
            self.palla.rimbalza_paddle(self.ai)
        
        if self.palla.x < -self.palla.raggio:
            self.punteggio_ai += 1
            if audio_disponibile:
                try:
                    suono_goal.play()
                except:
                    pass
            self.palla.reset()
        elif self.palla.x > LARGHEZZA + self.palla.raggio:
            self.punteggio_giocatore += 1
            if audio_disponibile:
                try:
                    suono_goal.play()
                except:
                    pass
            self.palla.reset()
    
    def disegna_linea_centrale(self):
        for y in range(0, ALTEZZA, 25):
            pygame.draw.rect(self.schermo, (150, 150, 150), 
                           (LARGHEZZA // 2 - 2, y, 4, 15))
    
    def disegna_punteggio(self):
        punteggio_giocatore_testo = self.font.render(str(self.punteggio_giocatore), True, BIANCO)
        punteggio_ai_testo = self.font.render(str(self.punteggio_ai), True, BIANCO)
        
        self.schermo.blit(punteggio_giocatore_testo, (LARGHEZZA // 4 - 30, 30))
        self.schermo.blit(punteggio_ai_testo, (3 * LARGHEZZA // 4 - 30, 30))
        
        giocatore_label = self.font_piccolo.render("GIOCATORE", True, (180, 180, 180))
        ai_label = self.font_piccolo.render("AI", True, (180, 180, 180))
        
        self.schermo.blit(giocatore_label, (50, ALTEZZA - 30))
        self.schermo.blit(ai_label, (LARGHEZZA - 120, ALTEZZA - 30))
        
        if hasattr(self, 'adattamento_ai') and self.adattamento_ai:
            punteggio_totale = self.punteggio_giocatore + self.punteggio_ai
            differenza_punteggio = self.punteggio_giocatore - self.punteggio_ai
            
            difficolta_punteggio = min(0.10, punteggio_totale * 0.015)
            difficolta_equilibrio = min(0.08, differenza_punteggio * 0.02)
            difficolta_attuale = self.difficolta_base + difficolta_punteggio + difficolta_equilibrio
            difficolta_attuale = min(self.max_difficolta, difficolta_attuale)
            
            difficolta_display = f"AI: {difficolta_attuale:.0%}"
            difficolta_testo = self.font_piccolo.render(difficolta_display, True, (100, 255, 100))
            self.schermo.blit(difficolta_testo, (LARGHEZZA // 2 - 30, ALTEZZA - 60))
    
    def disegna(self):
        self.schermo.fill(NERO)
        
        self.disegna_linea_centrale()
        self.disegna_punteggio()
        self.giocatore.disegna(self.schermo)
        self.ai.disegna(self.schermo)
        self.palla.disegna(self.schermo)
        
        istruzioni = self.font_piccolo.render("W/S o Frecce per muoversi - ESC per uscire", True, (120, 120, 120))
        self.schermo.blit(istruzioni, (10, 10))
        
        pygame.display.flip()
    
    def esegui(self):
        running = True
        
        print("=== PONG GAME (AI FLUIDA) ===")
        print("Controlli:")
        print("W o Freccia Su - Muovi paddle su")
        print("S o Freccia Giù - Muovi paddle giù")
        print("ESC - Esci dal gioco")
        print("\nFile audio supportati (opzionali):")
        print("- sounds/paddle.mp3 (suono rimbalzo paddle)")
        print("- sounds/wall.mp3 (suono rimbalzo parete)")
        print("- sounds/goal.mp3 (suono goal)")
        if audio_disponibile:
            print("🔊 Audio attivato!")
        else:
            print("🔇 Modalità silenziosa")
        print("✨ AI con movimento fluido senza tremolii!")
        print("Buona fortuna!\n")
        
        while running:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    running = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        running = False
            
            self.gestisci_input_gioco()
            
            self.aggiorna_logica()
            
            self.disegna()
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gioco = Gioco()
    gioco.esegui()