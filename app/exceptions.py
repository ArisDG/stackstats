import datetime
from flask import jsonify


def test_input(since,until):
### Missing fields ############################################################
    # since
    if not since:
        err_message = "ERROR: 'since' field is missing"
        print(err_message)
        return jsonify({'success':False, 'message':err_message}), 400,\
            {'ContentType':'application/json'}

    # until
    if not until:
        
        err_message = "ERROR: 'until' field is missing"
        print(err_message)
        return jsonify({'success':False, 'message':err_message}), 400,\
            {'ContentType':'application/json'}

### Wrong formated values #####################################################
    # since
    try:
        datetime.datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        err_message = "ERROR: 'since' field has wrong format"
        print(err_message)
        return jsonify({'success':False, 'message':err_message}), 400,\
            {'ContentType':'application/json'}

    # until
    try:
        datetime.datetime.strptime(until, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        err_message = "ERROR: 'until' field has wrong format"
        print(err_message)
        return jsonify({'success':False, 'message':err_message}), 400,\
            {'ContentType':'application/json'}

### 'since' more recent than 'until' ##########################################
    if since >= until:
        err_message = "ERROR: Invalid time frame provided"
        print(err_message)
        return jsonify({'success':False, 'message':err_message}), 400,\
            {'ContentType':'application/json'}




def test_response(response):
    # Checks the 'answers' API response for errors
    # In case of errors, returns the response to the client
    if 'error_id' in response:
        return response
    return
