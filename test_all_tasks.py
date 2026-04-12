
import json
from env.environment import DisasterEnv
from tasks.easy import EasyTask
from tasks.medium import MediumTask
from tasks.hard import HardTask
from graders.grader import Grader

def test_task(name, task_instance):
    print(f"\n{'='*20} TESTING TASK: {name.upper()} {'='*20}")
    env = DisasterEnv()
    grader = Grader(max_attainable_reward=150.0)
    
    config = task_instance.get_config()
    obs = env.reset(config)
    print(f"Initial Obs: {json.dumps(obs, indent=2)}")
    
    total_reward = 0
    done = False
    step = 0
    
    # Simple heuristic policy for testing
    while not done and step < config.get("max_steps", 5):
        step += 1
        # Strategy: find highest urgency zone and allocate resources
        zones_sorted = sorted(obs["zones"], key=lambda z: z["urgency"], reverse=True)
        target_zone = zones_sorted[0]["name"]
        
        allocations = []
        if obs["resources"]["ambulances"] > 0:
            allocations.append({"resource": "ambulance", "zone": target_zone, "amount": 1})
        elif obs["resources"]["food_kits"] > 0:
            # Allocate 10% of food kits
            amount = max(1, obs["resources"]["food_kits"] // 5)
            allocations.append({"resource": "food_kits", "zone": target_zone, "amount": amount})
        
        action = {"allocations": allocations}
        print(f"\nStep {step} Action: {json.dumps(action)}")
        
        result = env.step(action)
        obs = result["observation"]
        reward = result["reward"]
        done = result["done"]
        total_reward += reward
        
        print(f"Step {step} Reward: {reward}")
        print(f"Step {step} Info: {result['info']['logs']}")
        print(f"Remaining Resources: {obs['resources']}")
    
    report = grader.get_grade_report(total_reward, obs)
    print(f"\n{name.upper()} TASK REPORT:")
    print(json.dumps(report, indent=2))
    return report["passing"]

if __name__ == "__main__":
    tasks = {
        "easy": EasyTask(),
        "medium": MediumTask(),
        "hard": HardTask()
    }
    
    results = {}
    for name, task in tasks.items():
        results[name] = test_task(name, task)
    
    print("\n" + "#"*50)
    print("FINAL SUMMARY")
    for name, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{name.upper()}: {status}")
    print("#"*50)
