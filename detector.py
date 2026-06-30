import cv2
import easyocr

# Inicializar lector OCR
reader = easyocr.Reader(['en'])

# Abrir cámara
camara = cv2.VideoCapture(0)

while True:

    ret, frame = camara.read()

    # Leer texto de la imagen
    resultados = reader.readtext(frame)

    for resultado in resultados:

        texto = resultado[1]

        # Mostrar texto detectado
        cv2.putText(
            frame,
            texto,
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        print("TEXTO DETECTADO:", texto)

    # Mostrar ventana
    cv2.imshow("SIVEP SECURITY", frame)

    # Salir con ESC
    if cv2.waitKey(1) == 27:
        break

camara.release()
cv2.destroyAllWindows()
