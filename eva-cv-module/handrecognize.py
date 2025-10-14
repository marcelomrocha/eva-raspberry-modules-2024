# import cv2
# import numpy as np
# import math
# import time

# from picamera.array import PiRGBArray
# from picamera import PiCamera

# # --- DEFINIÇÃO DA REGIÃO DE INTERESSE (ROI) ---
# ROI_Y_START, ROI_Y_END = 20, 400
# ROI_X_START, ROI_X_END = 320, 620
# MIN_CONTOUR_AREA = 1000 # Área mínima para ser considerada uma mão

# # --- PARÂMETROS PARA DETECÇÃO DE COR DA PELE (YCrCb) ---
# # Y: Luminância, Cr: Crominância Vermelha, Cb: Crominância Azul
# # Intervalos considerados robustos para a maioria dos tons de pele
# lower_skin = np.array([0, 133, 77], dtype=np.uint8)
# upper_skin = np.array([255, 173, 127], dtype=np.uint8)


# print("Inicializando a câmera (modo legado)...")
# camera = PiCamera()
# camera.resolution = (640, 480)
# camera.framerate = 30
# rawCapture = PiRGBArray(camera, size=(640, 480))

# # --- MELHORIA 1: ESTABILIZAÇÃO DA CÂMERA ---
# # Permite que o AWB (Auto White Balance) se ajuste e, em seguida, o trava.
# try:
#     time.sleep(2.0)
#     camera.shutter_speed = camera.exposure_speed
#     camera.exposure_mode = 'off'
#     g = camera.awb_gains
#     camera.awb_mode = 'off'
#     camera.awb_gains = g
# except Exception as e:
#     # Se der erro (por exemplo, em um ambiente que não seja RPi), avisa e segue
#     print(f"Aviso: Não foi possível estabilizar a exposição da câmera. Erro: {e}")
    
# time.sleep(0.1)
# print("Câmera inicializada e estabilizada.")


# for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
#     image = frame.array
#     image = cv2.flip(image, 1)

#     # 1. RECORTAR A REGIÃO DE INTERESSE
#     roi_image = image[ROI_Y_START:ROI_Y_END, ROI_X_START:ROI_X_END]
#     cv2.rectangle(image, (ROI_X_START, ROI_Y_START), (ROI_X_END, ROI_Y_END), (0, 255, 0), 2)

#     # --- MELHORIA 2: SEGMENTAÇÃO POR COR DA PELE (YCBCR) ---
#     ycbcr_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2YCrCb)
#     thresh = cv2.inRange(ycbcr_roi, lower_skin, upper_skin)
    
#     cv2.imshow("Skin Mask (YCrCb)", thresh) 
    
#     # 2. PRÉ-PROCESSAMENTO REFINADO
#     thresh = cv2.GaussianBlur(thresh, (11, 11), 0) # Desfoque menor
    
#     # Operação Morfológica de FECHAMENTO (fecha buracos na mão)
#     kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
#     thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel) 
    
#     # 3. ENCONTRAR CONTORNOS
#     try:
#         _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     except ValueError:
#         contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#     gesture_name = "SEARCHING"

#     if len(contours) > 0:
#         hand_contour = max(contours, key=cv2.contourArea)
#         area = cv2.contourArea(hand_contour)

#         if area < MIN_CONTOUR_AREA:
#              # O gesto continua como "SEARCHING"
#              pass
#         else:
#             # 4. TRADUZIR O CONTORNO PARA AS COORDENADAS DA IMAGEM ORIGINAL
#             hand_contour_original = hand_contour.copy()
#             hand_contour_original[:, 0, 0] += ROI_X_START
#             hand_contour_original[:, 0, 1] += ROI_Y_START
#             cv2.drawContours(image, [hand_contour_original], -1, (0, 255, 255), 2)
    
#             # 5. CÁLCULO DE SOLIDARIEDADE (MELHORIA 3A)
#             hull = cv2.convexHull(hand_contour, returnPoints=False)
#             hull_pts = cv2.convexHull(hand_contour, returnPoints=True)
#             hull_area = cv2.contourArea(hull_pts)

#             solidity = 0.0
#             if hull_area > 0:
#                  solidity = float(area) / hull_area 
            
#             finger_count = 0
            
#             if hull is not None and len(hull) > 3 and len(hand_contour) > 3:
#                 defects = cv2.convexityDefects(hand_contour, hull)
                
#                 if defects is not None:
#                     for i in range(defects.shape[0]):
#                         s, e, f, d = defects[i, 0]
#                         start = tuple(hand_contour[s][0])
#                         end = tuple(hand_contour[e][0])
#                         far = tuple(hand_contour[f][0])
                        
#                         a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
#                         b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
#                         c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                        
#                         try:
#                             if b > 0 and c > 0:
#                                 # Ângulo entre os lados do defeito de convexidade
#                                 angle = math.acos((b**2 + c**2 - a**2) / (2*b*c))
#                             else:
#                                 continue
#                         except ValueError:
#                             continue
    
#                         if angle <= math.pi / 2: # Contamos apenas ângulos agudos (vales entre os dedos)
#                             finger_count += 1
    
#                     finger_count += 1 # Compensamos para o primeiro dedo ou polegar
    
#                     # Encontra o centro e os pontos extremos (na ROI)
#                     M = cv2.moments(hand_contour)
#                     if M["m00"] != 0:
#                         cY_roi = int(M["m01"] / M["m00"])
#                     else: 
#                         cY_roi = 0
                        
#                     topmost_roi = tuple(hand_contour[hand_contour[:, :, 1].argmin()][0])
#                     bottommost_roi = tuple(hand_contour[hand_contour[:, :, 1].argmax()][0])
    
#                     # --- MELHORIA 3B: LÓGICA DE CLASSIFICAÇÃO COM SOLIDARIEDADE ---
                    
#                     if solidity > 0.90 and finger_count <= 2:
#                         # Se for quase um círculo (alta solidariedade) e poucos dedos, é um punho.
#                         gesture_name = "CLOSE"
#                     elif finger_count >= 5:
#                         gesture_name = "OPEN"
#                     elif finger_count == 3:
#                         gesture_name = "THREE"
#                     elif finger_count == 2:
#                         gesture_name = "PEACE"
#                     elif finger_count == 1:
#                         # Só consideramos THUMBS UP/DOWN se a mão não for muito 'redonda' (evita punhos disfarçados)
#                         if solidity > 0.70: 
#                              if (cY_roi - topmost_roi[1]) > 50:
#                                 gesture_name = "THUMBS_UP"
#                              elif (bottommost_roi[1] - cY_roi) > 50:
#                                 gesture_name = "THUMBS_DOWN"
#                         else:
#                             gesture_name = "ONE" # Gesto de um dedo, mas sem ser Thumbs Up/Down claro


#     cv2.putText(image, gesture_name, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
#     print(gesture_name)
#     cv2.imshow("HandPose", image)

#     rawCapture.truncate(0)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cv2.destroyAllWindows()
# camera.close()


########### SEM ROI - A TELA TODA #######################################################################

import cv2
import numpy as np
import math
import time

from picamera.array import PiRGBArray
from picamera import PiCamera

# --- PARÂMETROS GLOBAIS ---
MIN_CONTOUR_AREA = 1500 # Aumentei um pouco a área mínima para contornos de tela cheia

# --- PARÂMETROS PARA DETECÇÃO DE COR DA PELE (YCrCb) ---
# Y: Luminância, Cr: Crominância Vermelha, Cb: Crominância Azul
lower_skin = np.array([0, 133, 77], dtype=np.uint8)
upper_skin = np.array([255, 173, 127], dtype=np.uint8)


print("Inicializando a câmera (modo legado)...")
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))

# --- ESTABILIZAÇÃO DA CÂMERA (Mantida para consistência de cor) ---
try:
    time.sleep(2.0)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g
except Exception as e:
    print(f"Aviso: Não foi possível estabilizar a exposição da câmera. Erro: {e}")
    
time.sleep(0.1)
print("Câmera inicializada e estabilizada.")


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    image = cv2.flip(image, 1) # Imagem original (640x480)

    # 1. PRÉ-PROCESSAMENTO: TELA CHEIA
    
    # a) SEGMENTAÇÃO POR COR DA PELE (YCBCR)
    ycbcr_full = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    thresh = cv2.inRange(ycbcr_full, lower_skin, upper_skin)
    
    cv2.imshow("Skin Mask (YCrCb)", thresh) 
    
    # b) FILTROS MORFOLÓGICOS REFINADOS
    thresh = cv2.GaussianBlur(thresh, (11, 11), 0)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel) 
    
    # 2. ENCONTRAR CONTORNOS
    try:
        # Procuramos contornos em toda a imagem
        _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    gesture_name = "SEARCHING"

    if len(contours) > 0:
        hand_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(hand_contour)

        if area < MIN_CONTOUR_AREA:
             pass
        else:
            # Não precisamos de offset, desenhamos direto no contorno
            cv2.drawContours(image, [hand_contour], -1, (0, 255, 255), 2)
    
            # 3. CÁLCULO DE SOLIDARIEDADE E DEFEITOS
            hull = cv2.convexHull(hand_contour, returnPoints=False)
            hull_pts = cv2.convexHull(hand_contour, returnPoints=True)
            hull_area = cv2.contourArea(hull_pts)

            solidity = 0.0
            if hull_area > 0:
                 solidity = float(area) / hull_area 
            
            finger_count = 0
            
            if hull is not None and len(hull) > 3 and len(hand_contour) > 3:
                defects = cv2.convexityDefects(hand_contour, hull)
                
                if defects is not None:
                    for i in range(defects.shape[0]):
                        s, e, f, d = defects[i, 0]
                        start = tuple(hand_contour[s][0])
                        end = tuple(hand_contour[e][0])
                        far = tuple(hand_contour[f][0])
                        
                        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                        
                        try:
                            if b > 0 and c > 0:
                                angle = math.acos((b**2 + c**2 - a**2) / (2*b*c))
                            else:
                                continue
                        except ValueError:
                            continue
    
                        if angle <= math.pi / 2:
                            finger_count += 1
    
                    finger_count += 1
    
                    # Encontra o centro e os pontos extremos (agora na tela cheia)
                    M = cv2.moments(hand_contour)
                    if M["m00"] != 0:
                        cY = int(M["m01"] / M["m00"])
                    else: 
                        cY = 0
                        
                    topmost = tuple(hand_contour[hand_contour[:, :, 1].argmin()][0])
                    bottommost = tuple(hand_contour[hand_contour[:, :, 1].argmax()][0])
    
                    # 4. LÓGICA DE CLASSIFICAÇÃO COM SOLIDARIEDADE
                    if solidity > 0.90 and finger_count <= 2:
                        gesture_name = "CLOSE"
                    elif finger_count >= 5:
                        gesture_name = "OPEN"
                    elif finger_count == 3:
                        gesture_name = "THREE"
                    elif finger_count == 2:
                        gesture_name = "PEACE"
                    elif finger_count == 1:
                        if solidity > 0.70: 
                             # Usa os pontos e o centro na tela cheia
                             if (cY - topmost[1]) > 50:
                                gesture_name = "THUMBS_UP"
                             elif (bottommost[1] - cY) > 50:
                                gesture_name = "THUMBS_DOWN"
                        else:
                            gesture_name = "ONE"

    # Exibe o resultado
    cv2.putText(image, gesture_name, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    print(gesture_name)
    cv2.imshow("HandPose", image)

    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
camera.close()