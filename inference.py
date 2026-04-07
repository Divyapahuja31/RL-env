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
MAX_TOTAL_REWARD = 150.0
TEMPERATURE = 0.7
MAX_TOKENS = 300

SYSTEM_PROMPT = textwrap.dedent("""\
You are an AI Emergency Response Coordinator managing disaster relief.
You must allocate resources (ambulances and food_kits) to disaster zones to reduce urgency.
Rules:
- Ambulances significantly reduce urgency, especially in high-urgency zones.
- Food kits help survival but have less impact on urgency.
- Prioritize high-urgency zones first.
Respond with valid JSON: {"allocations": [{"resource": "ambulance", "zone": "<name>", "amount": <int>}]}
Valid resource types: "ambulance", "food_kits"
""").strip()

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def _fallback_action(observation):
    zones = observation["zones"]
    most_urgent = max(zones, key=lambda z: z["urgency"])
    allocations = []
    if observation["resources"]["ambulances"] > 0 and most_urgent["urgency"] > 0:
        allocations.append({"resource": "ambulance", "zone": most_urgent["name"], "amount": 1})
    elif observation["resources"]["food_kits"] > 0 and most_urgent["urgency"] > 0:
        allocations.append({"resource": "food_kits", "zone": most_urgent["name"], "amount": 10})
    return {"allocations": allocations}

def get_model_action(client, observation):
    zone_names = [z["name"] for z in observation["zones"]]
    amb = observation["resources"]["ambulances"]
    food = observation["resources"]["food_kits"]
    user_prompt = f"Current state:\n{json.dumps(observation, indent=2)}\nResources: {amb} ambulances, {food} food_kits\nValid zones: {zone_names}\nRespond with JSON only."
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
        action_data = json.loads(raw)
        clean = []
        for alloc in action_data.get("allocations", []):
            zone = alloc.get("zone", "")
            if zone not in zone_names:
                zone = zone_names[0]
            resource = alloc.get("resource", "ambulance")
            if resource not in ("ambulance", "food_kits"):
                resource = "ambulance"
            amount = max(1, int(alloc.get("amount", 1)))
            clean.append({"resource": resource, "zone": zone, "amount": amount})
        return {"allocations": clean}
    except Exception:
        return _fallback_action(observation)

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    grader = Grader(max_attainable_reward=MAX_TOTAL_REWARD)
    tasks = {"easy": EasyTask(), "medium": MediumTask(), "hard": HardTask()}

    for task_name, task_instance in tasks.items():
        env = DisasterEnv()
        config = task_instance.get_config()
        max_steps = config.get("max_steps", 5)
        current_obs = env.reset(config)
        rewards = []
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
            total_reward = sum(rewards)
            score = grader.evaluate(total_reward, current_obs)
            score = max(0.0, min(1.0, score))
            success = score >= 0.5
        finally:
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
        print()

if __name__ == "__main__":
    main()
