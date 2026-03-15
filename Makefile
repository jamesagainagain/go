# dev shortcuts: make up, make seed, make test

.PHONY: up down seed test

up:
	docker-compose up -d

down:
	docker-compose down

seed:
	# TODO: Run seed script to load london_venues.json and sample_events.json

test:
	cd backend && pytest tests/ -v
