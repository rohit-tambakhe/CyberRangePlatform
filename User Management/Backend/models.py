from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    attack_vectors = db.Column(db.Text, nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenario.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    scenario = db.relationship('Scenario', back_populates='schedules')

Scenario.schedules = db.relationship('Schedule', order_by=Schedule.id, back_populates='scenario')

db.create_all()
