# backend/Makefile
SHELL := /bin/bash

.PHONY: dev worker beat server

dev:
	poetry run uvicorn app.main:app & \
	sleep 3 && \
	poetry run python -m celery -A app.celery_app worker -l info & \
	sleep 3 && \
	poetry run python3 -m  celery -A app.celery_app beat --loglevel=debug