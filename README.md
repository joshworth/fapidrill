# Asynchronous Tasks with FastAPI and Celery

Example of how to handle background processes with FastAPI, Celery, and Docker.

### Quick Start

Spin up the containers:

```sh
$ docker-compose up -d --build
```

Open your browser to [http://localhost:8004](http://localhost:8004)



Run that test individually:

$ docker-compose exec web python -m pytest -k "test_task and not test_home"

$ docker-compose exec web python -m pytest -k "test_mock_task"
