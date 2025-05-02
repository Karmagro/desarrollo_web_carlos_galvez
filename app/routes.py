from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/agregar')
def agregar():
    return render_template('agregar.html')

@main.route('/listado')
def listado():
    return render_template('listado.html')

@main.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')
