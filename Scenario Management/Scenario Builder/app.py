from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scenarios.db'
db = SQLAlchemy(app)

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    attack_vectors = db.Column(db.String(200), nullable=False)

@app.route('/scenarios', methods=['POST'])
def create_scenario():
    data = request.json
    scenario = Scenario(
        name=data['name'],
        description=data['description'],
        attack_vectors=data['attack_vectors']
    )
    db.session.add(scenario)
    db.session.commit()
    return jsonify({'message': 'Scenario created', 'scenario_id': scenario.id}), 201

@app.route('/scenarios', methods=['GET'])
def list_scenarios():
    scenarios = Scenario.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'description': s.description, 'attack_vectors': s.attack_vectors} for s in scenarios])

@app.route('/scenarios/<int:scenario_id>', methods=['GET'])
def get_scenario(scenario_id):
    scenario = Scenario.query.get(scenario_id)
    if scenario:
        return jsonify({'id': scenario.id, 'name': scenario.name, 'description': scenario.description, 'attack_vectors': scenario.attack_vectors})
    return jsonify({'message': 'Scenario not found'}), 404

if __name__ == '__main__':
    db.create_all()  # Create tables on startup
    app.run(debug=True, host='0.0.0.0')  # Host on all available network interfaces
