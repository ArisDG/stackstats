from flask import Flask, jsonify, request
from flask_caching import Cache
from exceptions import test_input, test_response
from stackexchange_request import answers_api_request, calculate_statistics


app = Flask(__name__)
app.config.from_object('config.BaseConfig')
cache = Cache(app)


@app.route('/api/v1/stackstats', endpoint='get_statistics', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def get_statistics():
### Parse Values ##############################################################
    # If argument is not provided, request returns None
    since = request.args.get('since')
    until = request.args.get('until')

### Test for exceptions #######################################################
    # Check validity of arguments
    exception_response = test_input(since,until)
    if exception_response:
        return exception_response

### If no exceptions, make the request to StackExchange API ('answers' endpoint)
    # First, make the request
    answers_api_response = answers_api_request(since,until)

    # If anything goes wrong, return the StackExchange API message
    answers_api_exception = test_response(answers_api_response)
    if answers_api_exception:
        return answers_api_exception

### Calculate statistics ######################################################
    response_body = calculate_statistics(answers_api_response['items'])

    return jsonify(response_body), 200, {'ContentType':'application/json'}

if __name__ == "__main__":
    app.run(threaded=True,host='0.0.0.0',port=5000)
