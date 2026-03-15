# dev shortcuts: make up, make seed, make test

.PHONY: up down seed test

up:
	docker-compose up -d

down:
	docker-compose down

seed:
	cd backend && python3 -m scripts.seed_supabase_demo_places

test:
	cd backend && pytest tests/ -v
