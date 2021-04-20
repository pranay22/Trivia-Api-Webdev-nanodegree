import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Success Test: GET /questions Endpoint
    def test_get_all_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
     
    # Error Test: GET /questions?page=5555 endpoint - Intentional - Does not exist
    def test_failed_sent_requesting_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=5555')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # Success Test: GET /categories endpoint - get categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    # Error Test: GET /categories/5555 endpoint - Intentional - 5555 ivalid category
    def test_failed_sent_requesting_non_existing_category(self):
        res = self.client().get('/categories/5555')
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # Success Test: DELETE /questions/13 - Deleting successful question
    def test_delete_question(self):
        res = self.client().delete('/questions/13')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], '13')

    # Error Test: DELETE /questions/abc endpoint - invalid question
    def test_failed_sent_deleting_non_existing_question(self):
        res = self.client().delete('/questions/abc')
        self.assertEqual(res.status_code, 500)
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # Success Test: POST /questions endpoint - to add question successfully
    def test_add_question(self):
        new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        total_questions_before = len(Question.query.all())
        res = self.client().post('/questions', json=new_question)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        total_questions_after = len(Question.query.all())
        self.assertEqual(data["success"], True)
        self.assertEqual(total_number_of_questions_after, total_number_of_questions_before + 1)

    # Error Test: POST /questions/question endpoint - invalid question path
    def test_invalid_add_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    # Success Test: POST /questions/search endpoint .. test successful serach of a question
    def test_search_questions(self):
        new_search = {'searchTerm': 'abc'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    # Error Test: POST /questions/search endpoint - question not found while saerching
    def test_failed_search_question(self):
        new_search = {
            'searchTerm': '',
        }
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        
    # Success Test: GET /categories/1/questions endpoint - valid question
    def test_get_questions_per_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    # Error test: GET /categories/a/questions endpoint - invalid question in questions endpoint
    def test_failed_get_questions_per_category(self):
        res = self.client().get('/categories/a/questions')
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # Success Test: POST /quizzes endpoint
    def test_play_quiz(self):
        new_quiz_round = {'previous_questions': [],'quiz_category': {'type': 'Science', 'id': 1}}
        res = self.client().post('/quizzes', json=new_quiz_round)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # Error Test: POST /quizzes endpoint - error
    def test_error_play_quiz(self):
        new_quiz_round = {'previous_questions': []}
        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()