from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def pagginate_question(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type , Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET , POST ,PATCH ,DELETE , OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if (len(categories) == 0):
            abort(404)
        else:
            current_categories = [categorie.format()['type']
                                  for categorie in categories]
            return jsonify({
                'success': True,
                'categories': current_categories,
                'total_categories': len(categories)
            })

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        if (len(questions) == 0):
            abort(404)
        current_questions = pagginate_question(request, questions)
        if (len(current_questions) == 0):
            abort(404)
        else:
            try:
                current_categories = [question['category']
                                      for question in current_questions]
                categerois = Category.query.order_by(Category.id).all()
                ct = [cat.type for cat in categerois]
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions),
                    'currentCategory': current_categories,
                    'categories': ct
                })
            except Exception:
                abort(422)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            qustion = Question.query.filter(Question.id == question_id).first()
            qustion.delete()
            questions = Question.query.order_by(Question.id).all()
            current_question = pagginate_question(request, questions)
            return jsonify({
                'success': True,
                'question': current_question,
                'number of questions': len(questions),
            })
        except Exception:
            abort(422)

    @app.route('/questions', methods=["POST"])
    def insert_questions():
        body = request.get_json()
        question = body.get('question', 'none')
        answer = body.get('answer', 'none')
        difficulty = body.get('difficulty', 0)
        category = body.get('category')
        search = body.get('searchTerm', 0)
        try:
            if search:
                questions = Question.query.filter(
                    Question.question.ilike('%{}%'.format(search))).all()
                current_questions = pagginate_question(request, questions)
                current_categories = [qs['category']
                                      for qs in current_questions]
                if (len(current_questions) == 0):
                    abort(404)
                else:
                    return jsonify({
                        'success': True,
                        'questions': current_questions,
                        'total_questions': len(questions),
                        'currentCategory': current_categories,
                    })
            else:
                question = Question(
                    question=question, answer=answer, difficulty=difficulty,
                    category=category)
                question.insert()
                return jsonify({
                    'success': True
                })
        except Exception:
            abort(422)

    @app.route('/categories/<int:categorie_id>/questions')
    def get_by_categorie(categorie_id):
        try:
            questions = Question.query.filter(
                Question.category == categorie_id).all()
            if (len(questions) == 0):
                abort(404)
            else:
                current_questions = pagginate_question(request, questions)
                current_categories = [qs['category']
                                      for qs in current_questions]
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions),
                    'currentCategory': current_categories,
                })
        except Exception:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def make_quiz():
        body = request.get_json()
        previousQuestions = body.get('previous_questions', [])
        quizCategory = body.get('quiz_category')
        try:
            check = Question.category == quizCategory['id']
            question = Question.query.filter(
                check).order_by(func.random()).first()
            while (question in previousQuestions):
                question = Question.query.order_by(func.random()).all()
            return jsonify({
                'success': True,
                'question': question.format()})
        except Exception:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'messege': "Not Found"
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'messege': "method not allowed"
        }), 405

    @app.errorhandler(422)
    def Unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'messege': "Unprocessable Entity"
        }), 422
    return app
