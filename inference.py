"""
Inference Script for Disaster Response OpenEnv
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

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or "no-key-set"
BENCHMARK = "disaster-openenv"

SYSTEM_PROMPT = textwrap.dedent("""\
You are an AI Emergency Response Coordinator managing disaster relief.
You must allocate resources (ambulances and food_kits) to disaster zones to reduce urgency.
Respond with valid JSON: {"allocations": [{"resource": "ambulance", "zone": "<name>", "amount": <int>}]}
""").strip()

def _fallback_action(observation: Dict[str, Any]) -> Dict[str, Any]:
    """Simple heuristic fallback when LLM fails."""
    zones = observation["zones"]
    most_urgent = max(zones, key=lambda z: z["urgency"])
    allocations = []
    if observation["resources"]["ambulances"] > 0 and most_urgent["urgency"] > 0:
        allocations.append({"resource": "ambulance", "zone": most_urgent["name"], "amount": 1})
    elif observation["resources"]["food_kits"] > 0 and most_urgent["urgency"] > 0:
        allocations.append({"resource": "food_kits", "zone": most_urgent["name"], "amount": 10})
    return {"allocations": allocations}

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = DisasterEnv()
    task = EasyTask()
    obs = env.reset(task.get_config())
    print("[START] task=easy env=disaster-openenv model=" + MODEL_NAME)
    # Basic loop placeholder
    action = _fallback_action(obs)
    result = env.step(action)
    print(f"[STEP] step=1 action={json.dumps(action)} reward={result['reward']:.2f} done={str(result['done']).lower()} error=null")
    print("[END] success=false steps=1 score=0.000 rewards=" + f"{result['reward']:.2f}")

if __name__ == "__main__":
    main()
