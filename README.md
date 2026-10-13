# API Test Automation
![CI](https://github.com/kishankumar-qa/api-test-automation/actions/workflows/ci.yml/badge.svg)
API test automation with Python (requests + pytest) and Postman/Newman, run against the [ReqRes](https://reqres.in) test API.

## What's inside

- `tests/test_reqres.py`: pytest suite covering GET, POST, PUT and DELETE, a negative case (400 on a bad login), parametrized status checks, and JSON schema validation
- `tests/conftest.py`: shared `api` fixture, a requests session that sends the API key on every call
- `postman/reqres-collection.json`: Postman collection (GET and POST requests with test scripts), runnable from the command line with Newman

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Authentication

ReqRes needs a free API key from app.reqres.in. The key is read from an environment variable and is never stored in the repo.

```
set REQRES_API_KEY=your_key_here
```

## Run the pytest suite

```
pytest -v
```

## Run the Postman collection with Newman

```
npm install -g newman
newman run postman\reqres-collection.json --env-var "base_url=https://reqres.in/api" --env-var "api_key=%REQRES_API_KEY%"
```