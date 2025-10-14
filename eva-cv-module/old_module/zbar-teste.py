import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from pyzbar import pyzbar
import cv2

# --- CONFIGURAÇÕES OTIMIZADAS ---
# Use a resolução mais baixa que ainda funcione para a leitura do seu QR Code.
# 640x480 é um bom ponto de partida para a v1.
RES_W, RES_H = 640, 480
FRAME_RATE = 30 # Tente 30. Se o desempenho for lento, reduza para 15.

# 1. Inicializa a Câmera
camera = PiCamera()
camera.resolution = (RES_W, RES_H)
camera.framerate = FRAME_RATE
# Cria um array para armazenar os frames brutos (raw)
rawCapture = PiRGBArray(camera, size=(RES_W, RES_H))

# Pequeno atraso para que a câmera se ajuste ao sensor
time.sleep(0.1)

print("Iniciando leitura de QR Code... Pressione 'q' na janela para sair.")

# Loop para captura contínua de frames
# .capture_continuous usa um gerador, que é mais rápido que um loop while True com .capture()
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    # Obtém o array NumPy da imagem (já no formato BGR do OpenCV)
    image = frame.array
    
    # --- PRÉ-PROCESSAMENTO OTIMIZADO (Escala de Cinza) ---
    # Converte para escala de cinza, pois ZBar só precisa de luminância.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. Decodificação Otimizada com pyzbar
    barcodes = pyzbar.decode(gray)

    # 3. Processamento e Exibição do Resultado
    for barcode in barcodes:
        # Pega a string decodificada (o conteúdo do QR Code)
        data = barcode.data.decode("utf-8")
        type = barcode.type
        
        # Desenha um retângulo ao redor do código
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Exibe o tipo e os dados do código
        text = f"Tipo: {type} | Dados: {data}"
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        print(f"[{time.strftime('%H:%M:%S')}] {text}")

    # 4. Mostra o Frame
    cv2.imshow("QR Code Reader (PiCamera)", image)

    # 5. Limpa o buffer para o próximo frame
    rawCapture.truncate(0)

    # 6. Sair do Loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Limpeza Final ---
cv2.destroyAllWindows()
camera.close()
print("Programa de leitura de QR Code encerrado.")


