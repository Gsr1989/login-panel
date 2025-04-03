
from flask import Flask, render_template, request, redirect, session, url_for, send_file
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "clave_secreta"

USUARIO = "admin"
CONTRASENA = "1234"
FOLIO_ACTUAL = 100
REGISTROS_DIR = "documentos"

if not os.path.exists(REGISTROS_DIR):
    os.makedirs(REGISTROS_DIR)

@app.route("/")
def index():
    if "usuario" in session:
        return redirect(url_for("panel"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]
        if usuario == USUARIO and contrasena == CONTRASENA:
            session["usuario"] = usuario
            return redirect(url_for("panel"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)

@app.route("/panel")
def panel():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("panel.html", usuario=session["usuario"])

@app.route("/registro", methods=["GET", "POST"])
def registro():
    global FOLIO_ACTUAL
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        marca = request.form["marca"]
        linea = request.form["linea"]
        anio = request.form["anio"]
        serie = request.form["serie"]
        motor = request.form["motor"]

        folio = f"{FOLIO_ACTUAL:04d}"
        fecha_expedicion = datetime.today()
        fecha_vencimiento = fecha_expedicion + timedelta(days=30)

        data_qr = f"Folio: {folio}\nMarca: {marca}\nLínea: {linea}\nAño: {anio}\nSerie: {serie}\nMotor: {motor}\nExpedición: {fecha_expedicion.strftime('%d/%m/%Y')}\nVigencia: {fecha_vencimiento.strftime('%d/%m/%Y')}"
        qr_img = qrcode.make(data_qr)
        qr_path = os.path.join(REGISTROS_DIR, f"qr_{folio}.png")
        qr_img.save(qr_path)

        # PDF certificado
        pdf_cert_path = os.path.join(REGISTROS_DIR, f"certificado_{folio}.pdf")
        c = canvas.Canvas(pdf_cert_path, pagesize=letter)
        c.drawString(100, 750, f"Folio: {folio}")
        c.drawString(100, 730, f"Marca: {marca}")
        c.drawString(100, 710, f"Línea: {linea}")
        c.drawString(100, 690, f"Año: {anio}")
        c.drawString(100, 670, f"Número de Serie: {serie}")
        c.drawString(100, 650, f"Número de Motor: {motor}")
        c.drawString(100, 630, f"Fecha de Expedición: {fecha_expedicion.strftime('%d/%m/%Y')}")
        c.drawString(100, 610, f"Vigencia: {fecha_vencimiento.strftime('%d/%m/%Y')}")
        c.drawImage(qr_path, 400, 600, width=150, height=150)
        c.save()

        # PDF comprobante de pago
        pdf_pago_path = os.path.join(REGISTROS_DIR, f"pago_{folio}.pdf")
        cp = canvas.Canvas(pdf_pago_path, pagesize=letter)
        cp.drawString(100, 750, f"Referencia: {serie}")
        cp.drawString(100, 730, f"Fecha de Pago: {fecha_expedicion.strftime('%d/%m/%Y')}")
        cp.save()

        FOLIO_ACTUAL += 1
        return render_template("exitoso.html")

    return render_template("registro_vehiculo.html")

@app.route("/error")
def error():
    mensaje = request.args.get("mensaje", "Ha ocurrido un error.")
    return render_template("error.html", mensaje=mensaje)

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
