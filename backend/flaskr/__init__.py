import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Questions pagination
def paginateQuestions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    currentQuestions = questions[start:end]
    return currentQuestions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  # @TODO: Set up CORS. Allow '*' for origins.
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=["GET"])
  def retrieve_all_categories():
    try:
      categories = Category.query.order_by(Category.type).all()
      if len(categories) == 0:
        abort(404)
      result = {'success': True,
        'categories': {category.id: category.type for category in categories}
      }
      return jsonify(result)
    except Exception as e:
      print(str(e))
      abort(500)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=["GET"])
  def retrieve_all_questions():
    try:
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginateQuestions(request, questions)
      categories = Category.query.order_by(Category.type).all()
      if len(current_questions) == 0:
        abort(404)
      result = {
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'categories': {category.id: category.type for category in categories},
        'current_category': None
      }
      return jsonify(result)
    except Exception as e:
      print(str(e))
      abort(500)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<question_id>", methods=['DELETE'])
  def delete_question(question_id):
    try:
      question_to_be_deleted = Question.query.get(question_id)
      question_to_be_deleted = Question.query.filter(Question.id == question_id).one_or_none()
      if (question_to_be_deleted is None):
        return jsonify({
          'success': False,
          'message': 'Invalid question_id'
        })
      question_to_be_deleted.delete()
      result = {
          'success': True,
          'deleted': question_id
      }
      return jsonify(result)
    except Exception as e:
      print(str(e))
      abort(500)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods=['POST'])
  def add_new_question():
    try:
      body = request.get_json()
      if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
        abort(422)
      question = body.get('question', None)
      answer = body.get('answer', None)
      difficulty = body.get('difficulty', None)
      category = body.get('category', None)
      question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      question.insert()
      result = {
        'success': True,
        'created': question.id,
      }
      return jsonify(result)
    except Exception as e:
      print(str(e))
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    try:
      body = request.get_json()
      search_phrase = body.get('searchTerm', None)
      if (search_phrase is not None):
        search_results = Question.query.filter(Question.question.ilike(f'%{search_phrase}%')).all()
        formatted_questions = [question.format() for question in search_results]
        result = {
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(search_results),
          'current_category': None
        }
        return jsonify(result)
      else:
        abort(404)
    except Exception as e:
      print(str(e))
      abort(500)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
        questions = Question.query.filter(Question.category == str(category_id)).order_by(Question.id).all()
        current_category = Category.query.filter(Category.id == category_id).first()
        formatted_category = current_category.format()
        formatted_questions = [question.format() for question in questions]
        result = 
        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(questions),
          'current_category': formatted_category
        })
    except Exception as e:
      print(str(e))
      abort(404)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      body = request.get_json()
      category = body.get('quiz_category', None)
      previous_questions = body.get('previous_questions', [])

      if not ('quiz_category' in body and 'previous_questions' in body):
        abort(422)
      
      if category['type'] == 'click':
        available_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      else:
        available_questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()
      if len(available_questions):
        new_question = available_questions[random.randrange(0, len(available_questions))].format()
      else:
        new_question = None
      result = {
        'success': True,
        'question': new_question,
        "timestamp": time()
      }
      return jsonify(result)
    except Exception as e:
      print(str(e))
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422
  
  return app

    