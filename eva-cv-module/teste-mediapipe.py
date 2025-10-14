import cv2
import mediapipe as mp
import time

# --- Configurações da Câmera (OpenCV) ---
# Em muitos sistemas Raspberry Pi, a PiCamera é acessada como índice 0 ou -1.
# Se estiver usando PiCamera, o melhor é usar a API padrão do OpenCV para V4L2.
CAP_WIDTH = 640
CAP_HEIGHT = 480
CAP_FPS = 30
CAMERA_INDEX = 0 # Tente 0. Se não funcionar, tente 1 ou -1.

cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, CAP_FPS)

if not cap.isOpened():
    print("ERRO: Não foi possível abrir a câmera. Verifique a conexão e o índice.")
    exit()

# --- Inicialização do MediaPipe Hands ---
# Inicializa as soluções de desenho e rastreamento de mãos
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Cria o objeto Hands com parâmetros básicos
# min_detection_confidence: Confiança mínima para detectar uma mão
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- Variáveis de Controle de FPS ---
pTime = 0

print("Iniciando reconhecimento de gestos... Pressione 'q' para sair.")

# --- Loop Principal ---
while True:
    # 1. Captura do Frame
    success, image = cap.read()
    if not success:
        print("A câmera não conseguiu ler o frame.")
        break

    # 2. Pré-processamento e Processamento do MediaPipe
    # Converte o frame de BGR (OpenCV) para RGB (MediaPipe)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Processa o frame com o modelo Hands
    results = hands.process(image_rgb)

    # 3. Desenho e Detecção Simples
    # Verifica se alguma mão foi detectada
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            # Desenha os 21 pontos da mão no frame original (BGR)
            mp_drawing.draw_landmarks(
                image, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2), # Cor dos pontos (Verde)
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)  # Cor das conexões (Azul)
            )

            # --- DETECÇÃO DE GESTO SIMPLES (Mão Aberta vs. Mão Fechada) ---
            # Verifica se a ponta do dedo indicador (ponto 8) está acima do dedo do meio (ponto 5)
            # Este é um teste heurístico bem simples e nem sempre 100% preciso.
            
            # Ponto 5 (Metacarpo do Indicador) e Ponto 8 (Ponta do Indicador)
            y_ponto_5 = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y
            y_ponto_8 = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

            # Se a ponta do indicador (y_ponto_8) for *menor* que o metacarpo (y_ponto_5),
            # o dedo está esticado (pois o eixo Y cresce para baixo na imagem).
            if y_ponto_8 < y_ponto_5 - 0.05: # Adiciona um pequeno offset
                gesture_text = "MAO ABERTA / GESTO DETECTADO"
                text_color = (0, 255, 0) # Verde
            else:
                gesture_text = "MAO FECHADA / NENHUM GESTO"
                text_color = (0, 0, 255) # Vermelho
            
            # Exibe o texto do gesto
            cv2.putText(image, gesture_text, (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)


    # 4. Cálculo e Exibição do FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    cv2.putText(image, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # 5. Exibição do Frame
    cv2.imshow("MediaPipe Hands Test (Raspberry Pi)", image)

    # 6. Sair
    # Pressione 'q' para sair do loop
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# --- Finalização ---
hands.close()
cap.release()
cv2.destroyAllWindows()
print("Programa encerrado.")