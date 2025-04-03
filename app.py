
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Usuario por defecto
USUARIOS = {
    'admin': '1234'
}

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('panel'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if usuario in USUARIOS and USUARIOS[usuario] == contrasena:
            session['usuario'] = usuario
            return redirect(url_for('panel'))
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/panel')
def panel():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('panel.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
