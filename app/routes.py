from flask import request, Response, jsonify
from bson import json_util
from bson.objectid import ObjectId
from bson.json_util import dumps
from main import app, mongo
import random
import json

@app.route('/addQuestions', methods= ['POST'])
def create_questions():
    #receive_data
    description = request.json['description']
    materialId = request.json['material_id']
    alternatives = request.json['alternatives']
    correct = request.json['correct']

    if description and materialId and correct:
        id = mongo.db.questions.insert(
                {
                'description' : description,
                'materialId' : materialId,
                'alternatives' : alternatives,
                'answerCorrect' : correct 
                }
            ) 
        """ for item in alternatives:
            mongo.db.alternatives.insert(
                {
                    'questionId': id ,
                    'alternative': item['description'],
                    'feedback' : item['feedback'],
                    'isCorrect' : item['isCorrect']
               }
           ) """
        response = {'id': str(id),'materialId' : materialId}
        return response
    else:
        return not_found()


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
        new_list = random.sample(list(total_questions), 2) 
        for it in new_list:
            questions.append(it)
    if len(questions) > 20 :
        final_questions = random.sample(questions, 20)
    else:
        final_questions = questions

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
        lista_corrects = list()
        lista_incorrects = list()
        for item in evaluation:
            question = mongo.db.questions.find_one({'_id': ObjectId(item['questionId'])})
            if item['result'] == item['isCorrect']:
                questions_response = { 
                    "questionId": item["questionId"],
                    "materialId": question['materialId']
                }
                lista_corrects.append(questions_response)
                corrects = corrects + 1
            else:
                questions_response = { 
                    "questionId": item["questionId"],
                    "materialId": question['materialId'],
                    "feedback": item['feedback_result'],
                }
                lista_incorrects.append(questions_response)
                incorrects = incorrects + 1

        puntaje = (corrects*100)/len(evaluation)        

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


@app.errorhandler(404)
def not_found(error = None):
    response = jsonify({
        'message': 'Ingrese todos los campos correctamente',
        'status' : 404
    })
    response.status_code = 404
    return response
