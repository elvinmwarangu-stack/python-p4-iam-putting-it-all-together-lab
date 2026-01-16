from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, Recipe


# ======================
# SIGNUP
# ======================
class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()

            user = User(
                username=data['username'],
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            user.password_hash = data['password']

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            return user.to_dict(), 201

        except Exception as e:
            return {'errors': [str(e)]}, 422


# ======================
# CHECK SESSION
# ======================
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.get(user_id)
            return user.to_dict(), 200

        return {'error': 'Unauthorized'}, 401


# ======================
# LOGIN
# ======================
class Login(Resource):
    def post(self):
        data = request.get_json()

        user = User.query.filter_by(username=data['username']).first()

        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {'error': 'Invalid username or password'}, 401


# ======================
# LOGOUT
# ======================
class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return '', 204

        return {'error': 'Unauthorized'}, 401


# ======================
# RECIPES
# ======================
class RecipeIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        try:
            data = request.get_json()

            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=session['user_id']
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201

        except Exception as e:
            return {'errors': [str(e)]}, 422


# ======================
# ROUTES
# ======================
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
