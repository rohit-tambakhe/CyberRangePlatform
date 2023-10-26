@app.errorhandler(400)
def bad_request(e):
    return jsonify(message='Bad Request'), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify(message='Not Found'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify(message='Server Error'), 500
