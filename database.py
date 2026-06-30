from pymongo import MongoClient

cliente = MongoClient("mongodb+srv://marlenezacarias50:Marlene84@cluster1.colm6.mongodb.net/")

db = cliente["sivep_security"]

# Colecciones

vehiculos = db["vehiculos"]

oficiales = db["oficiales"]

sesiones = db["sesiones"]

historial = db["historial"]