.PHONY: help install run docker-build docker-up test

help:
	@echo "make install      -> create venv and install dependencies"
	@echo "make run          -> run streamlit locally"
	@echo "make docker-build -> build docker image"
	@echo "make docker-up    -> docker-compose up"
	@echo "make test         -> run pytest"

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	streamlit run app.py

docker-build:
	docker build -t ihras:v1 .

docker-up:
	docker-compose up --build

test:
	pytest -q
