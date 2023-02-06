from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carros.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(20), nullable=False)
    marca = db.Column(db.String(20), nullable=False)
    ano = db.Column(db.String(10), nullable=False)
    observacoes = db.Column(db.String(100), nullable=True)
    vDiaria = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# GET request to retrieve all carros
@app.route('/carros', methods=['GET'])
def get_carros(): 
    carros = Carro.query.all()
    return jsonify({'carros':[carro.as_dict() for carro in carros]}), 200

# GET request to retrieve one carros
@app.route('/carros/<int:id>', methods=['get'])
def get_carro(id):
    carro = Carro.query.get_or_404(id)
    return jsonify({'carro': carro.as_dict()}),200

@app.route('/carros/filtro', methods=['get'])
def get_carro_status():
    if 'ordem' in request.args:
        ordem = int(request.args.get('ordem'))
        if ordem == 1:
            carros = Carro.query.order_by(Carro.vDiaria).all()
        else:
            carros = Carro.query.order_by(desc(Carro.vDiaria)).all()
    elif 'status' in request.args:
        status = str(request.args.get('status'))
        carros = Carro.query.filter_by(status=status).all()
    else:
        return jsonify({'message': 'error 404, bad request'}),404

    return jsonify({'carros': [carro.as_dict() for carro in carros]}),200

# POST request to add a new carro with data of the new carro on a json file
@app.route('/carros', methods=['POST'])
def add_carro():
    if not request.is_json:
        return jsonify({'message':'body is not a json'}), 415
    data = request.get_json()
    if not data or not all(key in data for key in ('modelo', 'marca', 'ano', 'observacoes', 'vDiaria')):
        return jsonify({'message':'bad request'}), 400
    carro = Carro(modelo=data['modelo'], marca=data['marca'], ano=data['ano'], observacoes=data['observacoes'], vDiaria=data['vDiaria'], status='livre')
    db.session.add(carro)
    db.session.commit()
    return jsonify({'carro': carro.as_dict()}), 201

# PUT request to update a carro
@app.route('/carros/<int:id>', methods=['PUT'])
def update_carro(id):
    if not request.is_json:
        return jsonify({'message':'body is not a json'}), 415
    data = request.get_json()
    if not data or not all(key in data for key in ('modelo', 'marca', 'ano', 'observacoes', 'vDiaria', 'status')):
        return jsonify({'message':'bad request'}), 400
    carro = Carro.query.get_or_404(id)
    carro.modelo = data['modelo']
    carro.marca = data['marca']
    carro.ano = data['ano']
    carro.observacoes = data['observacoes']
    carro.vDiaria = data['vDiaria']
    carro.status = data['status']
    db.session.commit()
    return jsonify({'carro': carro.as_dict()}), 200

# DELETE request to delete a carro
@app.route('/carros/<int:id>', methods=['DELETE'])
def delete_carro(id):
    try:
        carro = Carro.query.get_or_404(id)
        db.session.delete(carro)
        db.session.commit()
        return jsonify({'message': 'Carro has been deleted.'}), 200
    except:
        return jsonify({'message':'carro not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
