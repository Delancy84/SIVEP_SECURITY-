from flask import Flask, render_template, Response, request, redirect, url_for, session, jsonify
import cv2
from datetime import datetime
from database import oficiales, sesiones, vehiculos 
import easyocr
import threading
import time


app.secret_key = os.environ.get(
    "SECRET_KEY",
    "sivep_security_2026"
)  # nosec B105

reader = None
camara = None

# Variables globales compartidas
vehiculo_actual = {
    "placa": "Esperando escaneo...",
    "propietario": "---",
    "modelo": "---",
    "multas": False
}

frame_actual = None
running = True

# =========================================================
# HILO SECUNDARIO: PROCESA OCR SIN DETENER LA CÁMARA
# =========================================================
def procesar_ocr_background():
    global vehiculo_actual, frame_actual, running
    
    print("Iniciando motor de reconocimiento de placas...")
    while running:
        if frame_actual is not None:
            # Hacemos una copia local para liberar rápido la variable global
            img_procesar = frame_actual.copy()
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(img_procesar, cv2.COLOR_BGR2GRAY)
            
            # Ejecutar OCR (esto toma un par de segundos en CPU)
            resultados = reader.readtext(gray)
            
            for (bbox, texto, prob) in resultados:
                texto_limpio = texto.replace(" ", "").upper()
                
                # Validar longitud mínima de placas estándar
                if 5 <= len(texto_limpio) <= 8 and prob > 0.35:
                    print(f"Detectado en background: {texto_limpio} ({prob:.2f})")
                    
                    # Consulta a Base de Datos
                    info_db = vehiculos.find_one({"placa": texto_limpio})
                    
                    if info_db:
                        vehiculo_actual = {
                            "placa": info_db.get("placa", texto_limpio),
                            "propietario": info_db.get("propietario", "Desconocido"),
                            "modelo": info_db.get("modelo", "Desconocido"),
                            "multas": info_db.get("multas_pendientes", False) 
                        }
                    else:
                        vehiculo_actual = {
                            "placa": texto_limpio,
                            "propietario": "No registrado / Desconocido",
                            "modelo": "---",
                            "multas": False
                        }
                    break
        
        # Pausa para no saturar al 100% el CPU de la computadora
        time.sleep(1.0)

# Iniciar el hilo del OCR de inmediato
hilo_ocr = threading.Thread(target=procesar_ocr_background, daemon=True)
hilo_ocr.start()


# =========================================================
# FLUJO DEL VIDEO EN VIVO (Transmisión fluida instantánea)
# =========================================================
def generar_frames():
    global frame_actual
    while True:
        success, frame = camara.read()
        if not success:
            break

        # Actualizar el frame para que el hilo de OCR lo lea cuando esté libre
        frame_actual = frame

        # Codificar video de inmediato (sin retrasos de procesamiento)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame_bytes +
            b'\r\n'
        )

# ===========================
# RUTA API: DATOS EN TIEMPO REAL
# ===========================
@app.route("/api/vehiculo_actual")
def api_vehiculo_actual():
    global vehiculo_actual
    return jsonify(vehiculo_actual)

# ===========================
# PÁGINA PRINCIPAL
# ===========================
@app.route("/")
def index():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", oficial=session["usuario"])

# ===========================
# STREAMS DE VIDEO
# ===========================
@app.route("/video")
def video():
    return Response(generar_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

# ===========================
# LOGOUT / LOGIN / REGISTRO
# ===========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        numero = request.form["numero"]
        password = request.form["password"]
        oficial = oficiales.find_one({"numero_empleado": numero, "password": password, "estado": "Activo"})
        if oficial:
            session["usuario"] = oficial["nombre"] + " " + oficial["apellido"]
            session["empleado"] = oficial["numero_empleado"]
            sesiones.insert_one({"numero_empleado": oficial["numero_empleado"], "nombre": oficial["nombre"] + " " + oficial["apellido"], "inicio": datetime.now(), "fin": None, "estado": "Activa"})
            return redirect(url_for("index"))
        return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/logout")
def logout():
    if "empleado" in session:
        sesiones.update_one({"numero_empleado": session["empleado"], "estado": "Activa"}, {"$set": {"fin": datetime.now(), "estado": "Finalizada"}})
    session.clear()
    return redirect(url_for("login"))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        numero = request.form["numero"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        rango = request.form["rango"]
        password = request.form["password"]
        if oficiales.find_one({"numero_empleado": numero}):
            return render_template("registro.html", error="El número de empleado ya existe.")
        oficiales.insert_one({"numero_empleado": numero, "nombre": nombre, "apellido": apellido, "rango": rango, "password": password, "estado": "Activo"})
        return redirect(url_for("login"))
    return render_template("registro.html")

if __name__ == "__main__":
    try:
        app.run(debug=False, use_reloader=False) # use_reloader=False evita duplicar hilos en background
    finally:
        running = False
