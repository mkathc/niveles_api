from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

#app.config["MONGO_URI"]= "mongodb://localhost/tesisdb"
app.config["MONGO_URI"]= "mongodb://niveleskath:kath1234@nivelesaprendizajeclust-shard-00-00.ljfao.mongodb.net:27017,nivelesaprendizajeclust-shard-00-01.ljfao.mongodb.net:27017,nivelesaprendizajeclust-shard-00-02.ljfao.mongodb.net:27017/tesis_db?ssl=true&replicaSet=atlas-hp89jh-shard-0&authSource=admin&retryWrites=true&w=majority"

mongo = PyMongo(app)

from router import routes