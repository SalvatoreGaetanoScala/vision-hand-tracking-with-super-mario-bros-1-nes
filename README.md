# Mario Hand Controller

Un controller virtuale basato sul tracciamento delle mani tramite webcam, sviluppato in Python con OpenCV e MediaPipe. Questo script trasforma i movimenti delle tue mani in input della tastiera, permettendoti di giocare a titoli classici come Super Mario Bros senza usare un controller fisico.

## 🎮 Come Funziona
Lo schermo della webcam è diviso verticalmente in due metà:
- **Zona Sinistra (Movimento):** Inclinando il polso a sinistra si attiva il tasto `A` (sinistra), inclinandolo a destra si attiva il tasto `D` (destra).
- **Zona Destra (Salto):** Facendo il gesto del "pizzico" (avvicinando la punta del pollice a quella dell'indice) si attiva il tasto `P` (salto).

## 🐍 Requisiti e Versioni Python
Il progetto richiede **Python 3**. È supportato ufficialmente sulle versioni da **Python 3.8 a Python 3.11** (la versione **3.10** è quella consigliata per una perfetta compatibilità con MediaPipe).

Le dipendenze necessarie sono:
- `opencv-python`
- `mediapipe`
- `numpy`
- `pynput`

Per installarle, apri il terminale ed esegui:
```bash
pip install opencv-python mediapipe numpy pynput
```

## 👾 Test
Il controller è stato configurato e testato con successo con i seguenti parametri:
- **ROM / Gioco:** `super Mario bros(world).nes`
- **Emulatore:** Nestopia v1.4.5 (Mac)

*(Nota: puoi adattarlo facilmente ad altri giochi o emulatori cambiando la mappatura dei tasti `KEY_LEFT`, `KEY_RIGHT` e `KEY_JUMP` all'interno del file `main.py`).*

## 🚀 Avvio rapido
1. Apri Nestopia, vai nelle impostazioni dei controlli e assicurati che Sinistra sia mappato su `A`, Destra su `D` e il tasto per Saltare su `P`.
2. Carica la ROM e avvia il gioco.
3. Apri il terminale ed esegui lo script:
   ```bash
   python main.py
   ```
4. Fai clic sulla finestra dell'emulatore per assicurarti che sia in primo piano (così riceverà i comandi della tastiera virtuale).
5. Per spegnere correttamente il controller, porta la finestra della webcam in primo piano e premi il tasto `q`.
