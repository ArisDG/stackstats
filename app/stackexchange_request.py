from datetime import datetime
from collections import Counter
from requests import get
import time

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
    page = 1
    print("Retrieving answers page: ",page)
    
    data = {'page': str(page),'pagesize':'100','fromdate':  since_total_sec,\
            'todate': until_total_sec, 'site': 'stackoverflow',\
            'order': 'desc', 'sort': 'votes'}

    # Initial GET Request to the StackExchange answers API
    answer_response = get(URL, params = data).json()

    # Check if backoff needed
    backoff = backoff_func(answer_response.get("backoff"))

    # Check for more data
    more_data = answer_response.get("has_more")

    # Count number of retries to avoid throttling    
    retry_n = 0
    
    # Typically 'more_data' is bool
    # When 'more_data' is None (non existent in the reponse dict),
    # then we have backoff violation (even though we already waited).
    # To deal with it we use exponential wait.
    while more_data is None:
        # Advance retry counter + 1
        retry_n += 1

        # Exponentially raise backoff waiting time (backoff violation occured)
        backoff = exp_backoff_func(backoff,retry_n)

        # Resend GET Request to the StackExchange answers API
        answer_response = get(URL, params = data).json()

        # Get more data (In case backoff violation is not active)
        more_data = answer_response.get("has_more")
        
    # We got a reply but we still need to be careful and check for backoff
    backoff = backoff_func(answer_response.get("backoff"))
    
    # While there are more data, retrieve them from the next pages
    while more_data:
        # Update page index
        page += 1
        
        # Page above 25 requires access token or app key
        if page > 25:
            break
        
        # Debug
        print("Retrieving answer page: ",page)
        data.update({'page': str(page)})

        # Get results from new index           
        tmp_response = get(URL, params = data).json()

        # Backoff if needed        
        backoff = backoff_func(tmp_response.get("backoff"))

        # Get more data, if no backoff violation        
        more_data = tmp_response.get("has_more")

        # In case of violation start the exponential routine        
        retry_n = 0

        # Check for violations
        while more_data is None:
            # Advance retry counter + 1
            retry_n += 1

            # Exponentially backoff
            backoff = exp_backoff_func(backoff, retry_n)
            
            # Then retry
            tmp_response = get(URL, params = data).json()

            # Get more data (In case backoff violation is not active)
            more_data = tmp_response.get("has_more")
            
        # Update the response dict by adding the new data
        answer_response.update(tmp_response)

    return answer_response


def calculate_statistics(response_items):
### Create a copy of the template and check for exceptions ####################
    # Get template copy
    response_body = response_template.copy()

    # If no items, return empty response template
    if not response_items:
        return response_body

### Calculate number of accepted answers & their avg score ####################
    total_accepted = len([x for x in response_items if x.get("is_accepted")])
    if total_accepted > 0:
        avg_score = sum([x.get("score") for x in response_items if x.get("is_accepted")])/total_accepted
    else:
        avg_score = 0

### Calculate the average answer count per question ###########################
    # Instead of the pythonic way, it is better to make it readable

    # Get the ids of all the questions that the answers belong to
    question_ids = [x.get("question_id") for x in response_items]

    # Calculate each question's occurences
    question_occurences = Counter(question_ids).values()

    # Average
    avg_answers_per_question = sum(question_occurences)/len(question_occurences)

### Calculate comment count for each of the top 10 answers ####################
    # Again, instead of the pythonic way, it is better to make it readable

    # Get the ids of the top 10 answers (already sorted)
    top_ten_answer_ids = [str(x.get("answer_id")) for x in response_items[:10]]

    # Create the query for the StackExchange API request ('comments' endpoint)
    # This endpoint accepts a list of ids, separated by semicolon (max 100)
    query = '/'+';'.join(top_ten_answer_ids)

    # data is just the required values from the StackExchange API
    page = 1
    
    print("Retrieving comments page:",page)
    data = {'page':str(page), 'pagesize':'100', 'order':'desc','site':'stackoverflow'}

    # GET Request to the StackExchange API ('comments' endpoint)
    comments_response = get(URL+query+'/comments', data = data).json()

    # Check if backoff needed
    backoff = backoff_func(comments_response.get("backoff"))

    # Check for more data
    more_data = comments_response.get("has_more")

    # Count number of retries to avoid throttling    
    retry_n = 0

    # Typically 'more_data' is bool
    # When 'more_data' is None (non existent in the reponse dict),
    # then we have backoff violation.
    # To deal with it we use exponential wait.
    while more_data is None:
        # Advance retry counter + 1
        retry_n += 1

        # Exponentially raise backoff waiting time (backoff violation occured)
        backoff = exp_backoff_func(backoff,retry_n)

        # Resend GET Request to the StackExchange answers API
        comments_response = get(URL+query+'/comments', data = data).json()

        # Get more data (In case backoff violation is not active)
        more_data = comments_response.get("has_more")

    # We got a reply but we still need to be careful and check for backoff
    backoff = backoff_func(comments_response.get("backoff"))
    
    # While there are more data, retrieve them from the next pages
    while more_data:
        # Update Page index
        page += 1

        # Page above 25 requires access token or app key
        if page > 25:
            break

        # Debug
        print("Retrieving comments page:",page)
        data.update({'page': str(page)})

        # Get results from new index
        tmp_response = get(URL+query+'/comments', data = data).json()
        
        # Backoff if needed        
        backoff = backoff_func(tmp_response.get("backoff"))

        # Get more data, if no backoff violation
        more_data = tmp_response.get("has_more")

        # In case of violation start the exponential routine        
        retry_n = 0
        
        # Check for violations
        while more_data is None:
            # Advance retry counter + 1
            retry_n += 1

            # Exponentially wait
            backoff = exp_backoff_func(backoff, retry_n)
            
            # Then retry
            tmp_response = get(URL, params = data).json() 

            # Get more data (In case backoff violation is not active)
            more_data = tmp_response.get("has_more")

        # Update the response dict by adding the new data
        comments_response.update(tmp_response)

    # Get items of response
    comments_items = comments_response.get('items')

    # The post ids reffer to the original answers that have comments
    post_ids = [str(x.get("post_id")) for x in comments_items]

    # Count occurences of each of the top 10 ids in the above list
    # *Note* There is probably a faster way
    top_ten_answers_comment_count = {x:post_ids.count(x) for x in top_ten_answer_ids}

### Fill the response_body ####################################################
    response_body["total_accepted_answers"] = total_accepted
    response_body["accepted_answers_average_score"] = avg_score
    response_body["average_answers_per_question"] = avg_answers_per_question
    response_body["top_ten_answers_comment_count"]  = top_ten_answers_comment_count

    return response_body

def backoff_func(backoff):
    # If API says chill, we chill!
    if backoff:
        print('API asked for backoff')
        print('Waitiing for: '+str(backoff)+' seconds')
        time.sleep(backoff)
        return backoff
    return None    

def exp_backoff_func(backoff, retry_n):
    print('Backoff violation, retrying no:',retry_n)
    # Exponentially wait
    if backoff:
        print('Exponential waitiing for '+str((2^retry_n)*backoff)+' seconds based on previous backof value: '+str(backoff))
        time.sleep((2^retry_n)*backoff)
    else:
        print('Exponential waitiing for: '+str((2^retry_n)*2)+' seconds')
        time.sleep((2^retry_n)*2)
