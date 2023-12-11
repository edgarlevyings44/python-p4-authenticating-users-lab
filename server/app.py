#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401
    
class Login(Resource):
    def post(self):
        # Get the username from request's JSON
        username = request.json.get('username')

        # Retrieve the user by username
        user = User.query.filter_by(username=username).first()

        if user:
            # Set the session's user_id value to the user's id
            session['user_id'] = user.id

            # Return the user as JSON with a 200 status code
            response = make_response(jsonify(user.to_dict()), 200)
            response.headers['Content-Type'] = 'application/json'  # Set content type to application/json
            return response
        else:
            # Return an error message with a 404 status code
            return {'message': 'User not found'}, 404
        
class Logout(Resource):
    def delete(self):
        # Remove the user_id value from the session
        session['user_id'] = None

          # Return no data and a 204 status code
        return {}, 204  

class CheckSession(Resource):
    def get(self):
        # Get the user_id value from the session
        user_id = session.get('user_id')

        # Retrieve the user by id
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        
        # Return an error message with a 401 status code
        return {}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
