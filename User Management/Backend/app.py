from flask import request, jsonify
from flask_ldap3_login import AuthenticationResponseStatus
from datetime import datetime

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    response = ldap_manager.authenticate(data['username'], data['password'])
    if response.status == AuthenticationResponseStatus.success:
        return jsonify(message='Login successful'), 200
    return jsonify(message='Login failed'), 401

@app.route('/scenarios', methods=['GET'])
def get_scenarios():
    scenarios = Scenario.query.all()
    return jsonify([s.to_dict() for s in scenarios])

@app.route('/schedule', methods=['POST'])
def schedule_scenario():
    data = request.json
    scenario_id = data['scenario_id']
    time_str = data['time']
    time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

    scenario = Scenario.query.get(scenario_id)
    if not scenario:
        return jsonify(message='Scenario not found'), 404

    schedule = Schedule(scenario_id=scenario_id, time=time_obj)
    db.session.add(schedule)
    db.session.commit()

    return jsonify(message='Scenario scheduled successfully')

if __name__ == '__main__':
    app.run(debug=True)
