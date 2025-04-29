import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://cc5002:programacionweb@localhost:3306/tarea2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-local'
