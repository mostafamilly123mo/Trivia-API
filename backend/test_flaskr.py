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
    def test_get_catagoris(self):
        res = self.client().get('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])
    def test_get_pagginating_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['currentCategory'])
        self.assertTrue(data['total_questions'])
    def test_404_sent_request_beyond_valid(self):
        res = self.client().get('/questions?page=100000')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['messege'], "Not Found")
            
    def test_post_question(self):
        res = self.client().post(
            '/questions', json={'question': 'kk', 'answer': 'hh'})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)

    def test_post_question_beyond_not_valid(self):
        res = self.client().post(
            '/questions/1', json={'question': 'kk', 'answer': 'hh'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['messege'], "method not allowed")
    def test_delete_question(self):
        res=self.client().delete('/questions/8')
        data=json.loads(res.data)
        self.assertAlmostEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
    def test_422_delete_request_not_valid(self):
        res=self.client().post('/questions/132')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
    def test_422_questions_perCategory(self):
        res = self.client().get('/categories/9/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

if __name__ == "__main__":
    unittest.main()
