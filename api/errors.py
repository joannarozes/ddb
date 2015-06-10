import json

from bottle import error, response

@error(404)
def error404(err):
    error_dict = {
        'error': 404,
        'message': str(err.body)
    }
    response.content_type = 'application/json'
    return json.dumps(error_dict)


@error(400)
def error400(err):
    error_dict = {
        'error': 400,
        'message': str(err.body)
    }
    response.content_type = 'application/json'
    return json.dumps(error_dict)


@error(500)
def error500(err):
    error_dict = {
        'error': 500,
        'message': str(err.body)
    }
    response.content_type = 'application/json'
    return json.dumps(error_dict)