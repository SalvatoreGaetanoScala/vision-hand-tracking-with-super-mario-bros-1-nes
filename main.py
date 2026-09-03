import cv2
import mediapipe as mp
import numpy as np
import time
import math
from pynput.keyboard import Controller, KeyCode

# --- 1. Configurazione Tastiera e Controlli ---
keyboard = Controller()

# Mappatura Tasti (WASD per movimento, P per salto)
KEY_LEFT = KeyCode.from_char('a')
KEY_RIGHT = KeyCode.from_char('d')
KEY_JUMP = KeyCode.from_char('p')

is_left_pressed = False
is_right_pressed = False
is_jump_pressed = False

# --- 2. Inizializzazione e Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Estetica: Colore Giallo per scheletro e linee (Formato BGR: 0, 255, 255)
landmark_style = mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=4)
connection_style = mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2)

cap = cv2.VideoCapture(0)
window_name = "Mario Hand Controller"
cv2.namedWindow(window_name)

pTime = 0

# --- 3. Funzioni di Supporto ---
def calculate_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def release_all_keys():
    global is_left_pressed, is_right_pressed, is_jump_pressed
    if is_left_pressed: 
        keyboard.release(KEY_LEFT)
        is_left_pressed = False
    if is_right_pressed: 
        keyboard.release(KEY_RIGHT)
        is_right_pressed = False
    if is_jump_pressed: 
        keyboard.release(KEY_JUMP)
        is_jump_pressed = False

# --- 4. Loop Principale ---
while cap.isOpened():
    success, img = cap.read()
    if not success: 
        break
        
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    
    # Linea di divisione dello schermo (SX: Movimento, DX: Salto)
    cv2.line(img, (w // 2, 0), (w // 2, h), (100, 100, 100), 2)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    action_text = "Fermo"
    jump_text = ""
    
    if not results.multi_hand_landmarks:
        release_all_keys()
    else:
        movement_active = False
        jump_active = False
        
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(
                img, hand_landmarks, mp_hands.HAND_CONNECTIONS, 
                landmark_style, connection_style
            )
            
            # --- CALCOLO BOUNDING BOX E LABEL ESTETICA ---
            x_min, y_min = w, h
            x_max, y_max = 0, 0
            for lm in hand_landmarks.landmark:
                x, y = int(lm.x * w), int(lm.y * h)
                x_min, y_min = min(x_min, x), min(y_min, y)
                x_max, y_max = max(x_max, x), max(y_max, y)
            
            # Margine attorno alla mano
            pad = 20
            x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
            x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)
            
            # Disegna il rettangolo
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 0), 1)
            
            # Identifica Destra/Sinistra e disegna l'etichetta
            label = results.multi_handedness[idx].classification[0].label
            display_label = "Right" if label == "Left" else "Left"
            
            # Sfondo etichetta e testo
            cv2.rectangle(img, (x_min, y_min - 25), (x_min + 55, y_min), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, display_label, (x_min + 5, y_min - 5), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
            
            # --- LOGICA DI CONTROLLO ---
            # Troviamo il centro della mano (basato sul polso) per capire in che metà si trova
            wrist = hand_landmarks.landmark[0]
            cx = int(wrist.x * w)
            
            # --- ZONA SINISTRA (MOVIMENTO) ---
            if cx < w // 2:
                movement_active = True
                middle_mcp = hand_landmarks.landmark[9]
                
                # Inclinazione polso a SX (Cammina a sinistra)
                if middle_mcp.x < wrist.x - 0.05:
                    action_text = "<< SINISTRA ('a')"
                    if not is_left_pressed: 
                        keyboard.press(KEY_LEFT)
                        is_left_pressed = True
                    if is_right_pressed: 
                        keyboard.release(KEY_RIGHT)
                        is_right_pressed = False
                
                # Inclinazione polso a DX (Cammina a destra)
                elif middle_mcp.x > wrist.x + 0.05:
                    action_text = "DESTRA >> ('d')"
                    if not is_right_pressed: 
                        keyboard.press(KEY_RIGHT)
                        is_right_pressed = True
                    if is_left_pressed: 
                        keyboard.release(KEY_LEFT)
                        is_left_pressed = False
                        
                else:
                    if is_left_pressed: 
                        keyboard.release(KEY_LEFT)
                        is_left_pressed = False
                    if is_right_pressed: 
                        keyboard.release(KEY_RIGHT)
                        is_right_pressed = False

            # --- ZONA DESTRA (SALTO) ---
            else:
                jump_active = True
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                
                distance = calculate_distance((tx, ty), (ix, iy))
                circle_x, circle_y = (tx + ix) // 2, (ty + iy) // 2
                
                # Pizzico (Salto)
                if distance < 40:
                    cv2.circle(img, (circle_x, circle_y), 15, (0, 0, 255), cv2.FILLED)
                    jump_text = "SALTO! ('p')"
                    if not is_jump_pressed: 
                        keyboard.press(KEY_JUMP)
                        is_jump_pressed = True
                else:
                    cv2.circle(img, (circle_x, circle_y), 15, (0, 255, 0), 2)
                    if is_jump_pressed: 
                        keyboard.release(KEY_JUMP)
                        is_jump_pressed = False

        # Rilascia i tasti se le mani escono dalla loro zona
        if not movement_active:
            if is_left_pressed: 
                keyboard.release(KEY_LEFT)
                is_left_pressed = False
            if is_right_pressed: 
                keyboard.release(KEY_RIGHT)
                is_right_pressed = False
        if not jump_active:
            if is_jump_pressed: 
                keyboard.release(KEY_JUMP)
                is_jump_pressed = False

    # --- Interfaccia Grafica FPS e Testo Azioni ---
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    
    cv2.rectangle(img, (0, h - 60), (w, h), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, action_text, (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(img, jump_text, (w // 2 + 20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow(window_name, img)
    
    # --- Gestione Chiusura Pulita ---
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
    try:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1: 
            break
    except cv2.error:
        break

# Spegnimento pulito
release_all_keys()
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)