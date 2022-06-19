from datetime import datetime
from collections import Counter
from json import loads
from requests import get


# Response Template
response_template = {
    "total_accepted_answers": 0,
    "accepted_answers_average_score": 0,
    "average_answers_per_question": 0,
    "top_ten_answers_comment_count": {}
}

# StackExchange API URL
URL = 'https://api.stackexchange.com/2.3/answers'


def answers_api_request(since,until):
### Transform input data ######################################################
    # Transform strings to datetime objects
    since_datetime = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    until_datetime = datetime.strptime(until, "%Y-%m-%d %H:%M:%S")

    # *Insert Unix joke here*
    begining_of_time = datetime(1970, 1, 1)

    # Calculate total seconds for each value
    since_total_sec = str(int((since_datetime-begining_of_time).total_seconds()))
    until_total_sec = str(int((until_datetime-begining_of_time).total_seconds()))

### 'answers' API request #####################################################
    # Create the data to be passed to the StackExchange API ('answers' endpoint)
    data = {'fromdate':  since_total_sec, 'todate': until_total_sec, \
            'site': 'stackoverflow', 'order': 'desc', 'sort': 'votes'}

    # GET Request to the StackExchange answers API
    answer_response = get(URL, params = data)

### Return data to the main API thread ########################################
    # Decode/Transform to JSON format
    assert loads(answer_response.content.decode())
    answer_response = answer_response.json()

    return answer_response


def calculate_statistics(response_items):
### Create a copy of the template and check for exceptions ####################
    # Get template copy
    response_body = response_template.copy()

    # If no items, return empty response template
    if not response_items:
        return response_body

### Calculate number of accepted answers & their avg score ####################
    total_accepted = sum([1 for x in response_items if x["is_accepted"]])
    avg_score = sum([x["score"] for x in response_items if x["is_accepted"]])/total_accepted

### Calculate the average answer count per question ###########################
    # Instead of the pythonic way, it is better to make it readable

    # Get the ids of all the questions that the answers belong to
    question_ids = [x["question_id"] for x in response_items]

    # Calculate each question's occurences
    question_occurences = Counter(question_ids).values()

    # Average
    avg_answers_per_question = sum(question_occurences)/len(question_occurences)

### Calculate comment count for each of the top 10 answers ####################
    # Again, instead of the pythonic way, it is better to make it readable

    # Get the ids of the top 10 answers
    top_ten_answer_ids = [str(x["answer_id"]) for x in response_items[:10]]

    # Create the query for the StackExchange API request ('comments' endpoint)
    # This endpoint accepts a list of ids, separated by semicolon (max 100)
    query = '/'+';'.join(top_ten_answer_ids)

    # data is just the required values from the StackExchange API
    data = {'order':'desc','site':'stackoverflow'}

    # GET Request to the StackExchange API ('comments' endpoint)
    comments_response = get(URL+query+'/comments', data = data)

    # Decode/Transform data to JSON format
    assert loads(comments_response.content.decode())
    comments_response = comments_response.json()

    # Get items of response
    comments_items = comments_response['items']

    # The post ids reffer to the original answers that have comments
    post_ids = [str(x["post_id"]) for x in comments_items]

    # Count occurences of each of the top 10 ids in the above list
    # *Note* There is probably a faster way
    top_ten_answers_comment_count = {x:post_ids.count(x) for x in top_ten_answer_ids}

### Fill the response_body ####################################################
    response_body["total_accepted_answers"] = total_accepted
    response_body["accepted_answers_average_score"] = avg_score
    response_body["average_answers_per_question"] = avg_answers_per_question
    response_body["top_ten_answers_comment_count"]  = top_ten_answers_comment_count

    return response_body
