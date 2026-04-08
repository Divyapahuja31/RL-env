"""
Inference Script for Disaster Response OpenEnv
================================================
Runs all 3 tasks (easy, medium, hard) using an LLM agent via OpenAI client.

Required environment variables:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.

STDOUT FORMAT:
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import os
import json
import textwrap
from typing import List, Dict, Any, Optional

from openai import OpenAI

from env.environment import DisasterEnv
from env.models import Action
from graders.grader import Grader
from tasks.easy import EasyTask
from tasks.medium import MediumTask
from tasks.hard import HardTask

# ── Configuration ──────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN") or "no-key-set"

BENCHMARK = "disaster-openenv"
MAX_TOTAL_REWARD = 150.0  # Used for score normalization
TEMPERATURE = 0.7
MAX_TOKENS = 300

TASKS = {
    "easy": EasyTask(),
    "medium": MediumTask(),
    "hard": HardTask(),
}

SYSTEM_PROMPT = textwrap.dedent("""\
You are an AI Emergency Response Coordinator managing disaster relief.
You must allocate resources (ambulances and food_kits) to disaster zones to reduce urgency.

Rules:
- Ambulances significantly reduce urgency, especially in high-urgency zones.
- Food kits help survival but have less impact on urgency.
- You cannot allocate more resources than are available.
- Prioritize high-urgency zones first.

You MUST respond with valid JSON matching this exact structure:
{
    "allocations": [
        {"resource": "ambulance", "zone": "<zone_name>", "amount": <int>},
        {"resource": "food_kits", "zone": "<zone_name>", "amount": <int>}
    ]
}

Only use zone names and resource types from the current observation.
Valid resource types: "ambulance", "food_kits"
""").strip()


# ── Logging helpers (strict format) ────────────────────────────────────────────
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ── LLM action generation ─────────────────────────────────────────────────────
def get_model_action(client: OpenAI, observation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends the current observation to the LLM and returns a clean action dict.
    Dynamically identifies valid zones and ensures the most urgent zone is used as a fallback.
    """
    zones = observation["zones"]
    zone_names = [z["name"] for z in zones]
    
    # Identify the highest urgency zone for strategic fallback
    most_urgent_zone = max(zones, key=lambda z: z["urgency"])["name"]
    
    amb = observation["resources"]["ambulances"]
    food = observation["resources"]["food_kits"]

    user_prompt = f"""Current disaster state:
{json.dumps(observation, indent=2)}

Available resources: {amb} ambulances, {food} food_kits
Valid zone names: {zone_names}
Time remaining: {observation['time_remaining']} steps

Decide your resource allocations now. Respond with JSON only."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        raw = (response.choices[0].message.content or "").strip()

        # Parse the JSON response
        action_data = json.loads(raw)

        # Validate and sanitize zone names
        clean_allocations = []
        for alloc in action_data.get("allocations", []):
            zone = alloc.get("zone", "")
            # DYNAMIC FIX: If zone is invalid or hardcoded wrong, pick the most urgent one
            if zone not in zone_names:
                zone = most_urgent_zone 
                
            resource = alloc.get("resource", "ambulance")
            if resource not in ("ambulance", "food_kits"):
                resource = "ambulance"
                
            amount = max(1, int(alloc.get("amount", 1)))
            clean_allocations.append({
                "resource": resource,
                "zone": zone,
                "amount": amount,
            })

        return {"allocations": clean_allocations}

    except Exception:
        # Fallback: allocate 1 ambulance to highest urgency zone
        return _fallback_action(observation)


def _fallback_action(observation: Dict[str, Any]) -> Dict[str, Any]:
    """Simple heuristic fallback when LLM fails."""
    zones = observation["zones"]
    most_urgent = max(zones, key=lambda z: z["urgency"])
    allocations = []

    if observation["resources"]["ambulances"] > 0 and most_urgent["urgency"] > 0:
        allocations.append({
            "resource": "ambulance",
            "zone": most_urgent["name"],
            "amount": 1,
        })
    elif observation["resources"]["food_kits"] > 0 and most_urgent["urgency"] > 0:
        allocations.append({
            "resource": "food_kits",
            "zone": most_urgent["name"],
            "amount": 10,
        })

    return {"allocations": allocations}


# ── Run a single task ──────────────────────────────────────────────────────────
def run_task(client: OpenAI, task_name: str, task_instance, grader: Grader) -> float:
    """
    Runs one full episode for a given task.
    Returns the normalized score in [0, 1].
    """
    env = DisasterEnv()
    config = task_instance.get_config()
    max_steps = config.get("max_steps", 5)

    current_obs = env.reset(config)
    rewards: List[float] = []
    steps_taken = 0
    done = False
    score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        for step in range(1, max_steps + 1):
            if done:
                break

            action = get_model_action(client, current_obs)
            action_str = json.dumps(action)
            error = None

            try:
                result = env.step(action)
                current_obs = result["observation"]
                reward = float(result["reward"])
                done = bool(result["done"])

                # Check for env-level errors
                if "error" in result.get("info", {}):
                    error = result["info"]["error"]

            except Exception as e:
                reward = 0.0
                done = True
                error = str(e)

            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=action_str, reward=reward, done=done, error=error)

            if done:
                break

        # Compute normalized score in [0, 1]
        total_reward = sum(rewards)
        score = grader.evaluate(total_reward, current_obs)
        score = max(0.0, min(1.0, score))
        success = score >= 0.5

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    grader = Grader(max_attainable_reward=MAX_TOTAL_REWARD)

    scores = {}
    for task_name, task_instance in TASKS.items():
        score = run_task(client, task_name, task_instance, grader)
        scores[task_name] = score
        print()  # blank line between tasks

    # Summary
    print("=" * 50)
    print("FINAL SCORES:")
    for name, s in scores.items():
        print(f"  {name}: {s:.3f}")
    avg = sum(scores.values()) / len(scores)
    print(f"  AVERAGE: {avg:.3f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
