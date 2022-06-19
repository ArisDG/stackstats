
## stackstats

A Python service that retrieves data from the `StackExchange API` and calculates some simple statistics.




## Overview

This application runs as a long-running service. It provides a `REST API` written in `python 3.6`, using the `flask` module.

The complete service is running as a `dockerized` container.

The API supports caching, utilizing the `redis` framework for faster response times when making the same requests within a short period of time.

It accepts two string parameters following a specific datetime format pattern ('`%Y-%m-%d %H:%M:%S`'), namely `since` and `until`, as input and retrieves data from the `StackExchange API`, calculates some statistics and reports them back to the user.




## StackExchange API

The application requests data from two StackExchange API endpoints:
- `answers` (<https://api.stackexchange.com/docs/answers>), and
- `/answers/{ids}/comments` (<https://api.stackexchange.com/docs/comments-on-answers>).




## Objective

The service communicates with the `StackExchange API` and performs the following tasks:
- Retrieves the StackOverflow answer data for the given date/time range (`answers` endpoint).
- Retrieves the comment data for this set of answers (`/answers/{ids}/comments` endpoint).
- Finally, calculates the following statistics:
    - the total number of accepted answers.
    - the average score for all the accepted answers.
    - the average answer count per question.
    - the comment count for each of the 10 answers with the highest score.

When installed properly the service is accesible in the host machine via <http://localhost:5000/api/v1/stackstats>.




## Example usage

Response body example for input `since = 2020-10-02 10:00:00` & `until = 020-10-02 11:00:00` :

```
{
    "total_accepted_answers": 15,
    "accepted_answers_average_score": 3.8,
    "average_answers_per_question": 1.0714285714285714,
    "top_ten_answers_comment_count": {
        "64169696":0,
        "64169736":0,
        "64169856":2,
        "64169877":6,
        "64169929":3,
        "64169981":1,
        "64170070":2,
        "64170246":0,
        "64170260":0,
        "64170281":0}
}
```

To run this example from terminal, run: 
```
curl -G --url http://localhost:5000/api/v1/stackstats?since=2020-10-02%2010:00:00\&until=2020-10-02%2011:00:00
```

Or with any browser, access: <http://localhost:5000/api/v1/stackstats?since=2020-10-02%2010:00:00\&until=2020-10-02%2011:00:00>

Additionally, you can set your own values for `since` & `until` and get the results, as previously.




## Installation & Requirements

The module dependecies for the `API` are defined in the `requirements.txt` file and are automatically installed during the container's build process. These dependencies are namely:

```
Flask
Flask-Caching
redis
requests
```

To install and run the service you need `docker` & `docker-compose`.

- First, clone the repo.
- cd into the `app` folder
    ```
    cd app
    ```
- Then run:
    ```
    docker compose build
    ```

- And finally, run: 
    ```
    docker compose up
    ```




## Testing

To test the service, there are two methods provided, within the `test` folder.

The first method is an export of `postman` collections, that sends various sanity checks to the `API` in order to test the exception handling capabilities.

The second method is written natively as a `python` script that can be executed to perform the same tests as the 'Postman' collections export.