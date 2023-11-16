# Docker


Dockerfile
```dockerfile
FROM python:3.12
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
```

This copies the src folder on your machine to the /code in the docker container.

I find it easier using docker-compose for these things.

compose.yml

```yaml
services:
  api:
    build:
      context: ./
      dockerfile: Dockerfile
    container_name: "api"
    depends_on:
      - database
    ports:
      - "80:80"
```