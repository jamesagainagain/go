# go! — Hackathon TODO

## Backend

- [ ] Read `02_system_architecture.pdf` for full spec — data model, agent architecture, API design, deployment
- [ ] Implement the activation endpoint that accepts a user ID + location, runs the agent pipeline, and returns an activation card
- [ ] Implement the 5-agent LangGraph pipeline (Context → Discovery → Social Proof → Commitment → Momentum) as described in the architecture doc
- [ ] Implement agent log streaming (SSE or WebSocket) so the frontend can display real-time pipeline progress
- [ ] Set up PostgreSQL + PostGIS with the schema from the architecture doc
- [ ] Set up Redis for session/location caching
- [ ] Seed the database with London events (200+ real events), venues, and a demo user with preferences
- [ ] Docker-compose for local dev (api, db, redis)
- [ ] `.env.example` with all required variables

## Frontend

- [x] `/demo` route — tabbed UI shell with 6 tabs, keyboard navigation
- [x] Tab 1: Title screen
- [x] Tab 2: 7 friction points + "See go! fix this" transition button
- [x] Tab 3: Doom timeline
- [x] Tab 4: Split view — phone mockup (left) + agent terminal (right), wired to live backend
- [x] Tab 5: Agent pipeline diagram
- [x] Tab 6: Closing tagline
- [x] PhoneMockup component (pure CSS/Tailwind iPhone frame, no iframe)
- [x] ActivationCard component (slides up inside phone from backend data)
- [x] MapDetail component (Mapbox walking route inside phone after tap)
- [x] AgentLogPanel component (terminal log, live from SSE or simulated)
- [x] Fallback activation card (5s timeout, realistic hardcoded London data)
- [ ] Test at 1920×1080 projector resolution

## Data & APIs

- [ ] Mapbox account + access token
- [ ] OpenAI API key
- [ ] Curated seed data: real London events as JSON

## Pre-Demo Checklist

- [ ] `docker-compose up` starts backend cleanly
- [ ] `npm run dev` starts frontend cleanly
- [ ] Tab 4 returns a live activation card from the backend in <8s
- [ ] Fallback card works when backend is killed
- [ ] Agent log panel displays correctly
- [ ] Mapbox route renders inside phone after tap
- [ ] All 6 tabs render correctly at 1920×1080
- [ ] Keyboard shortcuts work
- [ ] Chrome full-screen mode (F11) tested
- [ ] Rehearsed 90-second flow at least 3 times
- [ ] Backup: screen recording of full demo saved as .mp4
