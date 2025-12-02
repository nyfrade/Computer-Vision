import cv2
import numpy as np
#-----OpenCv----
isMovingLeft = False
isMovingRight = False
isShooting = False

#Coordenadas do centro de massa do objeto, quando não há objeto são definidos como -100
cXCopy = -100
cYCopy = -100

# Thresholds min e max
#intervalos de cor em HSV
# COR VERMELHA
threshhold_h_min = 50
threshhold_h_max = 70

threshhold_s_min = 70
threshhold_s_max = 255

threshhold_v_min = 128
threshhold_v_max = 255

#Trackbars que permitem ajustar os limites de cor ao vivo, as funções
#atualizam as variáveis globais quando o utilizador mexe as barras
# Trackbar Threshold Min
def on_trackbar_change_h_min(val):
    global threshhold_h_min
    threshhold_h_min = val

# Trackbar Threshold Max
def on_trackbar_change_h_max(val):
    global threshhold_h_max
    threshhold_h_max = val

def on_trackbar_change_s_min(val):
    global threshhold_s_min
    threshhold_s_min = val

# Trackbar Threshold Max
def on_trackbar_change_s_max(val):
    global threshhold_s_max
    threshhold_s_max = val

def on_trackbar_change_v_min(val):
    global threshhold_v_min
    threshhold_v_min = val

# Trackbar Threshold Max
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
    global cXCopy,cYCopy
    global isMovingRight, isMovingLeft, isShooting

    if ret == True:
        #inverte horizontalmente ("espelho")
        frame_mirror = frame[:, ::-1, :]
        image_HSV = cv2.cvtColor(frame_mirror, cv2.COLOR_BGR2HSV)

        #criar máscaras binárias (preto e branco) que irão indicar onde o pixel está dentro dos limites
        # Segmentação binária - devolve uma matriz binária onde os valores maiores que o threshold são 1 e inferiores são 0
        _, image_thresholded_hmin = cv2.threshold(image_HSV[:, :, 0], threshhold_h_min, 1, cv2.THRESH_BINARY)
        # Segmentação binária invera
        # devolve uma matriz binária onde os valores maiores que o threshold são 0 e inferiores são 1
        _, image_thresholded_hmax = cv2.threshold(image_HSV[:, :, 0], threshhold_h_max, 1, cv2.THRESH_BINARY_INV)

        if (threshhold_h_min < threshhold_h_max):
            # Multiplicação das segmentações devolve uma matriz binária em que só é 1 quando tem 1 nas dois thresholds
            image_thresholded_h = image_thresholded_hmin * image_thresholded_hmax
        else:
            # Adição das segmentações devolve uma matriz binária que devolve os 1s dos dois thresholds
            # Para o caso dos vermelhos
            # Quando h_min > h_max
            image_thresholded_h = image_thresholded_hmin + image_thresholded_hmax

        _, image_thresholded_smin = cv2.threshold(image_HSV[:, :, 1], threshhold_s_min, 1, cv2.THRESH_BINARY)
        _, image_thresholded_smax = cv2.threshold(image_HSV[:, :, 1], threshhold_s_max, 1, cv2.THRESH_BINARY_INV)
        image_thresholded_s = image_thresholded_smin * image_thresholded_smax

        _, image_thresholded_vmin = cv2.threshold(image_HSV[:, :, 2], threshhold_v_min, 1, cv2.THRESH_BINARY)
        _, image_thresholded_vmax = cv2.threshold(image_HSV[:, :, 2], threshhold_v_max, 1, cv2.THRESH_BINARY_INV)
        image_thresholded_v = image_thresholded_vmin * image_thresholded_vmax

        #máscara final em preto e branco, o objeto desejado é branco
        image_thresholded = image_thresholded_h * image_thresholded_s * image_thresholded_v
        image_thresholded = (image_thresholded * 255).astype(np.uint8)

        # devolve apenas os contours externos
        contours, hierarchy = cv2.findContours(image=image_thresholded,
                                               mode=cv2.RETR_EXTERNAL,#apenas contornos externos
                                               method=cv2.CHAIN_APPROX_NONE)#guarda todos os pontos do contorno
        #no caso de não houver contornos, ou seja, nenhum objeto detetado
        if(len(contours) == 0):
            cXCopy = -100
            cYCopy = -100

        image_contours = np.zeros(image_thresholded.shape, np.uint8)
        cv2.drawContours(image=image_contours,
                         contours=contours,
                         contourIdx=-1,
                         color=255,
                         thickness=-1)


        # desenhar circulo no centro de massa
        image_circles = np.zeros(frame_mirror.shape, np.uint8)

        for i in range(len(contours)):
            contour = contours[i]
            c_area = cv2.contourArea(contour=contour)
            p = cv2.arcLength(curve=contour, closed=True)


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
                # Desenha um círculo no centro de massa do objeto
                cv2.circle(img=image_circles,
                           center=(cX, cY),
                           radius=5,
                           color=(0, 0, 255),
                           thickness=-1)



        # encontrar o índice e a área do maior objeto
        i_max_area = -1
        max_area = 0

        for i in range(len(contours)):
            contour = contours[i]
            c_area = cv2.contourArea(contour=contour)
            if c_area > max_area:
                max_area = c_area
                i_max_area = i

        #print("CONTOUR MAIOR: area = {}".format(max_area))

        # copiar a imagem da câmara
        # não podemos mostrar os contours diretamente na imagem obtida da câmara
        image_show = frame_mirror.copy()

        image_largest_contour = np.zeros(frame_mirror.shape, np.uint8)

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
                    # Using cv2.putText() method
                    # Este código desenha o contorno do maior objeto a amarelo
                    #o centro a vermelho e a área do objeto com texto
                    #Também atualiza cXCopy e cYCopy para o centro encontrado
                    cv2.putText(image_show, f"Area: {max_area}", (cX - 50, cY + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 255, 255), 2)
                    print(cX, cY)

        #adicionei
        # ----- movimento com base na posição -----
        # Estes valores dependem da resolução da câmara e obtém a largura e altura do frame da câmara
        #frame_mirror é a imagem captada, já invertida horizontalmente
        frame_width = frame_mirror.shape[1] #número de colunas (largura)
        frame_height = frame_mirror.shape[0] #número de linhas (altura)

        # Limite horizontal para deslocar para a esquerda/direita
        #definir uma zona neutra para que quando o objeto está no meio, a nave não se move
        #a nave só se vai mover se o objeto estiver claramente à esquerda ou à direita
        center_zone = frame_width // 3  # zona central “morta”

        #inicializar as variáveis de controlo
        #mover para a esquerda/direita de acordo com a posição horizontal (cXCopy)
        isMovingLeft = False
        isMovingRight = False
        #disparar quando o objeto sobe (cYCopy diminui)
        isShooting = False

        #verificar se há um objeto a ser detetado e em que parte da tela se encontra
        if cXCopy != -100:
            # Mover para a esquerda se o centro do objeto (cXCopy) está à esquerda da zona central
            #ativar o movimento à esquerda
            if cXCopy < frame_width // 2 - center_zone // 2:
                cv2.putText(image_show, "Esquerda", (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                isMovingLeft = True
            # Mover para a direita se o centro do objeto (cXCopy) está à direita da zona central
            elif cXCopy > frame_width // 2 + center_zone // 2:
                cv2.putText(image_show, "Direita", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                isMovingRight = True

            # Disparo quando o objeto vai para cima (menor Y → mais alto)
            #se o objeto estiver no centro superior da imagem ativa o disparo
            if cYCopy < frame_height // 3:
                cv2.putText(image_show, "Cima", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                isShooting = True

        cv2.imshow("imageshow", image_show)

    else:
        return None, False, False, False

    return frame, isMovingLeft, isMovingRight, isShooting
#-----OpenCv----
def cap_release(cap):
    # FAZ RELEASE DO CAP E FECHA A JANELA EM QUESTÃO
    if cap.isOpened():
        cap.release()
        cv2.destroyWindow("imageshow")