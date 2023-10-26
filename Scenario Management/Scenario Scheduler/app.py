from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scenarios.db'
db = SQLAlchemy(app)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

celery = make_celery(app)

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    attack_vectors = db.Column(db.String(200), nullable=False)
    schedule_time = db.Column(db.DateTime, nullable=True)

@celery.task
def run_scenario(scenario_id):
    scenario = Scenario.query.get(scenario_id)
    if scenario:
        print(f"Running scenario {scenario.name}")
        # Logic for running the scenario
    else:
        print(f"Scenario {scenario_id} not found")

@app.route('/schedule', methods=['POST'])
def schedule_scenario():
    data = request.json
    scenario_id = data['scenario_id']
    time = data['time']  # Time format: 'YYYY-MM-DD HH:MM:SS'
    schedule_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    scenario = Scenario.query.get(scenario_id)
    if scenario:
        scenario.schedule_time = schedule_time
        db.session.commit()
        run_scenario.apply_async(args=[scenario_id], eta=schedule_time)
        return jsonify({'message': 'Scenario scheduled'}), 200
    return jsonify({'message': 'Scenario not found'}), 404

if __name__ == '__main__':
    db.create_all()  # Create tables on startup
    app.run(debug=True, host='0.0.0.0')  # Host on all available network interfaces
