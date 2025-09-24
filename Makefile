
.PHONY: all auth-service product-catalog-service cart-service frontend stop

all: auth-service product-catalog-service cart-service frontend

auth-service:
	@echo "Starting auth-service..."
	@cd services/auth-service && uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload &

product-catalog-service:
	@echo "Starting product-catalog-service..."
	@cd services/product-catalog-service && uv run uvicorn src.main:app --reload --port 8004 &

cart-service:
	@echo "Starting cart-service..."
	@cd services/cart-service && yarn dev &

frontend:
	@echo "Starting frontend..."
	@cd frontend && npm run dev &

stop:
	@echo "Stopping all services..."
	@killall -9 uvicorn || true
	@fuser -k 3000/tcp || true
	@fuser -k 8007/tcp || true
