.PHONY: all backend frontend

all: backend frontend

backend:
	$(MAKE) -C backend/app dev &

frontend:
	$(MAKE) -C frontend dev &

stop:
	@echo "Stopping all services…"
	-@pkill -f "uvicorn app.main:app"   || true
	-@pkill -f "celery"                 || true
	-@pkill -f "streamlit run dashboard"|| true
	@echo "Done."