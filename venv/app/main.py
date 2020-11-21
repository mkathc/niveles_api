from flask import Flask, request, Response, jsonify
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask_cors import CORS
import random
import json

app= Flask(__name__)
CORS(app)

#app.config["MONGO_URI"]= "mongodb://localhost/tesisdb"
app.config["MONGO_URI"]= "mongodb://niveleskath:kath1234@nivelesaprendizajeclust-shard-00-00.ljfao.mongodb.net:27017,nivelesaprendizajeclust-shard-00-01.ljfao.mongodb.net:27017,nivelesaprendizajeclust-shard-00-02.ljfao.mongodb.net:27017/tesis_db?ssl=true&replicaSet=atlas-hp89jh-shard-0&authSource=admin&retryWrites=true&w=majority"

mongo = PyMongo(app)

@app.route('/')
def index():
  return "<h1>Welcome to Niveles API</h1>"


@app.route('/addQuestions', methods= ['POST'])
def create_questions():
    #receive_data
    question_list = request.json['question']
    questions_id = list()
    for item in question_list:
        try:
            description = item['description']
            materialId = item['material_id']
            alternatives = item['alternatives']
            correct = item['answerCorrect']

            if description and materialId:
                id = mongo.db.questions.insert(
                        {
                        'description' : description,
                        'materialId' : materialId,
                        'alternatives' : alternatives,
                        'answerCorrect' : correct 
                        }
                    ) 
                questions_id.append(str(id))
        except:
            Response = not_found()

    if (len(questions_id)):
        response = {'questionsId' : questions_id}
    else: 
        response = not_found() 
    return response
     


@app.route('/getAllQuestions', methods= ['GET'])
def get_all_questions():
    questions = mongo.db.questions.find()
    res = {
        "questions": questions
    }
    return Response(res, mimetype = 'application/json')


@app.route('/getQuestionsByMaterial/<material_id>', methods= ['GET'])
def get_questions_by_material(material_id):
    questions = mongo.db.questions.find({'materialId' : material_id})

    res = {
        "questions":  questions
    }

    return dumps(res, ensure_ascii=False)

   # return Response(res, mimetype = 'application/json')


@app.route('/createEvaluation', methods= ['POST'])
def create_evaluation():
    material_list = request.json['material_list']
    questions = list()
    for item in material_list:
        total_questions = mongo.db.questions.find({'materialId' : item})
        total_list = list(total_questions)
        if (len(total_list)>0):
            new_list = random.sample(total_list, 2) 
            if (len(new_list)>0):
                for it in new_list:
                    questions.append(it)
    if len(questions) > 20 :
        final_questions = random.sample(questions, 20)
    else:
        final_questions = questions
    for q in final_questions:
        random.shuffle(q['alternatives'])
        
    res = {
        "evaluation":  final_questions
    }

    return dumps(res, ensure_ascii=False)


@app.route('/sendEvaluation', methods= ['POST'])
def send_evaluation():
    #receive_data
    evaluation = request.json['evaluation']
    if evaluation:
        corrects = 0
        incorrects = 0
        lista_corrects = []
        lista_incorrects = []
        for item in evaluation:
            #question = mongo.db.questions.find_one({'_id': ObjectId(item['questionId'])})
            if item['selected'] == item['answerCorrect']:
        
                questions_response = { 
                    "materialId": item['materialId']
                }
                lista_corrects.append(questions_response)
                corrects = corrects + 1
            else:
                questions_response = { 
                    "materialId": item['materialId'],
                }
                lista_incorrects.append(questions_response)
                incorrects = incorrects + 1

        puntaje = (corrects*100)/len(evaluation)   

        intersection = [x for x in lista_corrects if x in lista_incorrects]

        for item in intersection:
            for correct in lista_corrects:
                if item == correct:
                    lista_corrects.remove(correct)

        res = {
            "corrects": {
                "total_corrects" : corrects,
                "lista_corrects" : lista_corrects,
            },
            "incorrects":{
                "total_incorrects" : incorrects,
                "lista_incorrects" : lista_incorrects
            }, 
            "puntaje": puntaje        
        }

        return  dumps(res, ensure_ascii=False)
    else:
        return not_found()

def intersect(*d):
       sets = iter(map(set, d))
       result = sets.next()
       for s in sets:
           result = result.intersection(s)
       return result

@app.errorhandler(404)
def not_found(error = None):
    response = jsonify({
        'message': 'Ingrese todos los campos correctamente',
        'status' : 404
    })
    response.status_code = 404
    return response

