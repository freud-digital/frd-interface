# frd-interface

## DEV
* create virtual python environment e.g. `python -m venv env`
* update pip `pip install -U pip`
* install dependencies `pip install -r requirements.txt`

## run

`gunicorn app.main:app --reload`

### build & run

* `docker build -t frd-int .`
* `docker run -d --name frd-int -p 80:80 frd-int`

or just run `./build_and_run.sh`

### use published image

docker run -d --name frd-int -p 80:80 ghcr.io/freud-digital/frd-interface:latest
