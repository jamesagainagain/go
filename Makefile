# dev shortcuts: make up, make seed, make test

.PHONY: up down seed test install lint build verify-demo

up:
	docker-compose up -d

down:
	docker-compose down

verify-demo:
	@echo "Checking demo API..."
	@curl -sf "http://localhost:8001/api/v1/events/demo/nearby?lat=51.5274&lng=-0.0777&limit=3" | python3 -c "import json,sys; d=json.load(sys.stdin); n=len(d.get('events',[])); print(f'OK: {n} demo events'); sys.exit(0 if n else 1)" || (echo "Run: make down && make up  (then retry)"; exit 1)

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

seed:
	cd backend && ( [ -d .venv ] && . .venv/bin/activate; python3 -m scripts.seed_supabase_demo_places )

test:
	cd backend && ( [ -d .venv ] && . .venv/bin/activate; pytest tests/ -v )

lint:
	cd frontend && npm run lint

build:
	cd frontend && npm run build
