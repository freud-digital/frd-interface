FROM python:3.8-buster

WORKDIR /code

RUN pip install -U pip --no-cache-dir

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8020"]