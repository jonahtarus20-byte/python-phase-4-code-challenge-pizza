#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants], 200


class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            return restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas.id', 'restaurant_pizzas.price', 'restaurant_pizzas.pizza_id', 'restaurant_pizzas.restaurant_id', 'restaurant_pizzas.pizza.id', 'restaurant_pizzas.pizza.name', 'restaurant_pizzas.pizza.ingredients')), 200
        else:
            return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        else:
            return {"error": "Restaurant not found"}, 404


class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas], 200


class RestaurantPizzaCreate(Resource):
    def post(self):
        try:
            data = request.get_json()
            price = data.get('price')
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')

            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurant_pizza)
            db.session.commit()

            return restaurant_pizza.to_dict(only=('id', 'price', 'pizza_id', 'restaurant_id', 'pizza.id', 'pizza.name', 'pizza.ingredients', 'restaurant.id', 'restaurant.name', 'restaurant.address')), 201
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400


api.add_resource(RestaurantList, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(PizzaList, '/pizzas')
api.add_resource(RestaurantPizzaCreate, '/restaurant_pizzas')


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
