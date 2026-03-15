# dev shortcuts: make up, make seed, make test

.PHONY: up down seed test install lint build

up:
	docker-compose up -d

down:
	docker-compose down

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
