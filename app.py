from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

# Configurations for the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/product_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

SECRET_TOKEN = "1234"  # You should use a more secure method to store this

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace("Bearer ", "")

        if not token or token != SECRET_TOKEN:
            return jsonify({'message': 'Token is missing or invalid'}), 401

        return f(*args, **kwargs)
    return decorated

# Define the table model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

@app.route('/products', methods=['GET'])
@token_required
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

@app.route('/product', methods=['POST'])
@token_required
def add_product():
    product_name = request.json.get('name')
    new_product = Product(name=product_name)
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201

if __name__ == '__main__':
    app.run(debug=True)
