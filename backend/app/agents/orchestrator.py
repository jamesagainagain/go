from __future__ import annotations

from pathlib import Path

from app.agents.commitment_agent import run_commitment_agent
from app.agents.context_agent import run_context_agent
from app.agents.discovery_agent import run_discovery_agent
from app.agents.momentum_agent import run_momentum_agent
from app.agents.social_proof_agent import run_social_proof_agent
from app.agents.types import ActivationState

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
PROMPT_FALLBACKS = {
    "context.txt": "Identify whether this is a high-leverage intervention moment.",
    "discovery.txt": "Score and filter opportunities based on context and preferences.",
    "social_proof.txt": "Add confidence-building social proof for each opportunity.",
    "commitment.txt": "Reduce commitment friction with one clear action.",
    "momentum.txt": "Prioritize opportunities that are likely to convert.",
}


def load_prompt(prompt_name: str) -> str:
    prompt_path = PROMPTS_DIR / prompt_name
    try:
        prompt_text = prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        prompt_text = ""
    if prompt_text:
        return prompt_text
    return PROMPT_FALLBACKS.get(prompt_name, "No prompt configured.")


def run_activation_pipeline(state: ActivationState) -> ActivationState:
    _ = {
        "context": load_prompt("context.txt"),
        "discovery": load_prompt("discovery.txt"),
        "social_proof": load_prompt("social_proof.txt"),
        "commitment": load_prompt("commitment.txt"),
        "momentum": load_prompt("momentum.txt"),
    }

    state = run_context_agent(state)
    if not state.should_intervene:
        return state

    state = run_discovery_agent(state)
    if not state.candidates:
        return state

    state = run_social_proof_agent(state)
    state = run_commitment_agent(state)
    state = run_momentum_agent(state)
    return state
