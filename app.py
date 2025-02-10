from flask import Flask
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import time
from redis_helper import get_product_redis


app = Flask(__name__)

# Set the secret key for JWTs (this can be stored in an environment variable)
app.config['JWT_SECRET_KEY'] = 'mysecretkey'  # Change this to a strong key in production

# Initialize JWTManager
jwt = JWTManager(app)

# Dummy user data
users = {
    "user1": {"password": "password1", "role": "user"},
    "user2": {"password": "adminpass", "role": "admin"}
}


load_dotenv()

@app.route("/")
def home():
    return "Hello from Flask on AWS EC2!"

@app.route('/login', methods= ['POST'])
def login():
    username = request.json.get('username',None)
    password = request.json.get('password',None)

    if username not in users or users[username]['password'] != password:
        return jsonify ({"msg" : "Bad Username or password"}), 401

    access_token = create_access_token(identity={"username":username,"role":users[username]["role"]})
    return jsonify(access_token=access_token)

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/admin', methods=['GET'])
@jwt_required()
def admin_route():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "Admins only!"}),403
    return jsonify({"message": "Welcome to the admin route!"}),200


@app.route('/products/<product_id>', methods=['GET'])
def get_product_details(product_id):
    print(product_id)
    product = get_product(product_id)

    if product:
        return jsonify({"product": product }),200
    else:
        return jsonify({"error": "product_not_fount" }),404

cache= {}
print(cache)
mock_db={"1": {"name": "echo","price": "100" },
            "2": {"name": "echo2","price": "200" },
            "3": {"name": "echo3","price": "300" }
        }
TTL=10

def get_product(product_id):
    current_time =  time.time()

    if product_id in cache:
        if cache[product_id]["ttl"] > current_time:
            print('cache hit')
            cache_to_return= cache[product_id].copy()
            del cache_to_return["ttl"]
            return cache_to_return
        else:
            print('Del Entry Cache')
            del cache[product_id]

    if product_id in mock_db:    
        print('cache miss')
        product= mock_db[product_id].copy()
        product.update({"ttl" : current_time + TTL})
        cache[product_id] = product
        print('cache : ', cache[product_id])
        product_to_return= product.copy()
        del product_to_return["ttl"] 
        return product_to_return
    
    else:
        return None
    
@app.route('/redis/products/<product_id>', methods = ['GET'])
def get_product_details_redis(product_id) :
    product, source=  get_product_redis(product_id)
    if product:
        return jsonify({"product": product, "source" : source}),200
    return jsonify({"error": "product not found"}),404




if __name__ == "__main__":
    port= int(os.getenv(("FLASK_PORT"),5000))
    app.run(host="0.0.0.0", port=port)