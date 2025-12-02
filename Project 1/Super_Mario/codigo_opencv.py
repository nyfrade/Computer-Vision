import cv2
import numpy as np

# Variáveis que definem estados
# São alteradas no main
# São verificadas na função get_user_input do spaceship.py

isMovingLeft = False

isMovingRight = False

isJumping = False


# Cópias globais do cX e cY
cXCopy = -100
cYCopy = -100


# THRESHOLDS MÍNIMO E MÁXIMO SO HSV
# COR VERDE
# S a 70 descobre mais facilmente o objecto verde
threshhold_h_min = 50
threshhold_h_max = 70

threshhold_s_min = 70
threshhold_s_max = 255

threshhold_v_min = 128
threshhold_v_max = 255

# TRACKBARS
def on_trackbar_change_h_min(val):
    global threshhold_h_min
    threshhold_h_min = val

def on_trackbar_change_h_max(val):
    global threshhold_h_max
    threshhold_h_max = val

def on_trackbar_change_s_min(val):
    global threshhold_s_min
    threshhold_s_min = val

def on_trackbar_change_s_max(val):
    global threshhold_s_max
    threshhold_s_max = val

def on_trackbar_change_v_min(val):
    global threshhold_v_min
    threshhold_v_min = val

def on_trackbar_change_v_max(val):
    global threshhold_v_max
    threshhold_v_max = val



def cap_main():
    cap = cv2.VideoCapture(0)

    # MOSTRA AS TRACKBARS NUMA JANELA QUE COPIA A IMAGEM RECEBIDA DA CÂMARA
    cv2.namedWindow("imageshow")
    global threshhold_h_min, threshhold_h_max, threshhold_s_min, threshhold_s_max, threshhold_v_min, threshhold_v_max
    cv2.createTrackbar("H MIN", "imageshow", threshhold_h_min, 180, on_trackbar_change_h_min)
    cv2.createTrackbar("H MAX", "imageshow", threshhold_h_max, 180, on_trackbar_change_h_max)
    cv2.createTrackbar("S MIN", "imageshow", threshhold_s_min, 255, on_trackbar_change_s_min)
    cv2.createTrackbar("S MAX", "imageshow", threshhold_s_max, 255, on_trackbar_change_s_max)
    cv2.createTrackbar("V MIN", "imageshow", threshhold_v_min, 255, on_trackbar_change_v_min)
    cv2.createTrackbar("V MAX", "imageshow", threshhold_v_max, 255, on_trackbar_change_v_max)

    return cap


def open_cv_loop(cap):
    ret, frame = cap.read()

    global isMovingRight, isMovingLeft, isJumping
    global cXCopy,cYCopy

    if ret == True:
        # Espelha a imagem obtida da câmara
        frame_mirror = frame[:, ::-1, :]
        image_HSV = cv2.cvtColor(frame_mirror, cv2.COLOR_BGR2HSV)

        # Segmentação binária - devolve uma matriz binária
        # valores maiores que o threshold são 1 e inferiores são 0
        _, image_thresholded_hmin = cv2.threshold(image_HSV[:, :, 0], threshhold_h_min, 1, cv2.THRESH_BINARY)

        # Segmentação binária inversa
        # devolve uma matriz binária onde os valores maiores que o threshold são 0 e inferiores são 1
        _, image_thresholded_hmax = cv2.threshold(image_HSV[:, :, 0], threshhold_h_max, 1,
                                                  cv2.THRESH_BINARY_INV)

        if (threshhold_h_min < threshhold_h_max):
            # Multiplicação das segmentações devolve uma matriz binária em que só é 1 quando tem 1 nas dois thresholds
            image_thresholded_h = image_thresholded_hmin * image_thresholded_hmax
        else:
            # Adição das segmentações devolve uma matriz binária que devolve os 1s dos dois thresholds
            # Para o caso dos vermelhos (por exemplo)
            # Quando h_min > h_max
            image_thresholded_h = image_thresholded_hmin + image_thresholded_hmax

        # aplicação das mesmas segmentações  no s e no v
        _, image_thresholded_smin = cv2.threshold(image_HSV[:, :, 1], threshhold_s_min, 1, cv2.THRESH_BINARY)
        _, image_thresholded_smax = cv2.threshold(image_HSV[:, :, 1], threshhold_s_max, 1,
                                                  cv2.THRESH_BINARY_INV)
        image_thresholded_s = image_thresholded_smin * image_thresholded_smax

        _, image_thresholded_vmin = cv2.threshold(image_HSV[:, :, 2], threshhold_v_min, 1, cv2.THRESH_BINARY)
        _, image_thresholded_vmax = cv2.threshold(image_HSV[:, :, 2], threshhold_v_max, 1,
                                                  cv2.THRESH_BINARY_INV)
        image_thresholded_v = image_thresholded_vmin * image_thresholded_vmax

        image_thresholded = image_thresholded_h * image_thresholded_s * image_thresholded_v
        image_thresholded = (image_thresholded * 255).astype(np.uint8)

        # devolve apenas os contours externos
        contours, hierarchy = cv2.findContours(image=image_thresholded,
                                               mode=cv2.RETR_EXTERNAL,
                                               method=cv2.CHAIN_APPROX_NONE)

        # Se não houver contours faz reset
        # Resolve o problema de quando entrava no quadrado e saía do ecrã
        if (len(contours) == 0):
            cXCopy = -100
            cYCopy = -100
            isMovingLeft = False
            isMovingRight = False
            isJumping = False

        image_contours = np.zeros(image_thresholded.shape, np.uint8)
        cv2.drawContours(image=image_contours,
                         contours=contours,
                         contourIdx=-1,
                         color=255,
                         thickness=-1)
        # cv2.imshow(winname="image_contours", mat=image_contours)

        # desenhar circulo no centro de massa
        image_circles = np.zeros(frame_mirror.shape, np.uint8)

        for i in range(len(contours)):
            contour = contours[i]
            c_area = cv2.contourArea(contour=contour)
            p = cv2.arcLength(curve=contour, closed=True)
            # print("contour {} area = {}; perimeter={}".format(i, c_area, p))

            # Desenha o contorno do objecto a amarelo
            cv2.drawContours(image=image_circles,
                             contours=contours,
                             contourIdx=i,
                             color=(0, 255, 255),
                             thickness=1)
            M = cv2.moments(array=contour)

            # Verifica se o m00 é diferente de 0
            # para não dividir por zero
            if M['m00'] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                # Desenha um círculo no centro de massa do objecto
                cv2.circle(img=image_circles,
                           center=(cX, cY),
                           radius=5,
                           color=(0, 0, 255),
                           thickness=-1)

        # cv2.imshow("image_circles", image_circles)

        # encontrar o índice e a área do maior objecto
        i_max_area = -1
        max_area = 0

        for i in range(len(contours)):
            contour = contours[i]
            c_area = cv2.contourArea(contour=contour)
            if c_area > max_area:
                max_area = c_area
                i_max_area = i

        print("CONTOUR MAIOR: area = {}".format(max_area))
        print(isJumping)

        # copiar a imagem da câmara
        # não podemos mostrar os contours diretamente na imagem obtida da câmara
        image_show = frame_mirror.copy()

        # image_largest_contour = np.zeros(frame_mirror.shape, np.uint8)

        # Percorremos novamente todos os contours
        # Utilizamos apenas o contour que tem o índice do maior contour descoberto anteriormente
        # Desenhamos o contour e descobrimos  o seu centro de massa

        for i in range(len(contours)):
            contour = contours[i]
            if i == i_max_area:
                cv2.drawContours(image=image_show,
                                 contours=contours,
                                 contourIdx=i,
                                 color=(0, 255, 255),
                                 thickness=1)

                M = cv2.moments(array=contour)
                if M['m00'] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    cXCopy = cX
                    cYCopy = cY
                    # Desenha um círculo no centro de massa do objecto
                    cv2.circle(img=image_show,
                               center=(cX, cY),
                               radius=5,
                               color=(0, 0, 255),
                               thickness=-1)

                    cv2.putText(image_show, f"cX:{cX}  cY:{cY}", (cX - 50, cY + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 255, 255), 2)
                    print(cX, cY)

        # Buffer usado para desviar os retangulos do centro (retangulos = zonas de ação)
        # permite que tenhamos uma zona em que nehuma ação é tomada caso o objecto esteja dentro dessa zona
        buffer_horizontal = 75

        # RETÃNGULOS
        cv2.rectangle(image_show, (0, 0),
                      (int(image_show.shape[1] / 2) - buffer_horizontal, image_show.shape[0]),
                      (0, 0, 255), 2)

        cv2.rectangle(image_show, (int(image_show.shape[1] / 2) + buffer_horizontal, 0),
                      (image_show.shape[1], image_show.shape[0]),
                      (0, 0, 255), 2)

        cv2.rectangle(image_show, (0, 0), (image_show.shape[1], int(image_show.shape[0] / 2)),
                      (0, 0, 255), 2)

        # DESENHA UMA LINHA VERDE PARA SABER QUE ESTÁ COM O OBJECTO NO QUADRADO DA ESQUERDA
        if cXCopy > 0 and cXCopy < int(image_show.shape[1] / 2) - buffer_horizontal:
            cv2.rectangle(image_show, (0, 0),
                          (int(image_show.shape[1] / 2) - buffer_horizontal, image_show.shape[0]),
                          (0, 255, 0), 2)
            isMovingLeft = True
        else:
            isMovingLeft = False

        # Se estiver dentro de um dos retângulos definidos esse retângulo passa a ser verde
        # Para visualmente o utilizador saber onde está posicionado o objecto
        # E saber também ação que vai tomar no jogo
        # Se não não estiver dentro dos limities definidos mete as variáveis de estado a falso
        if cXCopy > int(image_show.shape[1] / 2) + buffer_horizontal and cXCopy < int(image_show.shape[1]):
            cv2.rectangle(image_show, (int(image_show.shape[1] / 2) + buffer_horizontal, 0),
                          (image_show.shape[1], image_show.shape[0]),
                          (0, 255, 0), 2)

            isMovingRight = True
        else:
            isMovingRight = False

        if cYCopy > 0 and cYCopy < int(image_show.shape[0] / 2):
            cv2.rectangle(image_show, (0, 0), (image_show.shape[1], int(image_show.shape[0] / 2)),
                          (0, 255, 0), 2)
            isJumping = True
        else:
            isJumping = False

        # MOSTRAR A JANELA COM A FRAME COPIADA DA CÂMARA
        cv2.imshow("imageshow", image_show)

        # multiplicar a imagem normalizada por 255 para mostrar até 255
        # cv2.imshow("THRESHOLD ", image_thresholded)

        # cv2.imshow("CAM", frame_mirror)

        # C = cv2.waitKey(1)
        # if C == 27:
        #     break
    else:
        return
    # else:
    #     break


def cap_release(cap):
    # FAZ RELEASE DO CAP E FECHA A JANELA EM QUESTÃO
    if cap.isOpened():
        cap.release()
        cv2.destroyWindow("imageshow")

