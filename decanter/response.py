from flask import current_app, request, json

def json_response(response_object, status):
    resp_j = json.dumps(response_object, indent=None if request.is_xhr else 2)
    return current_app.response_class(resp_j,
                                      mimetype='application/json',
                                      status=status)
