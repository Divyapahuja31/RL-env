from env.environment import DisasterEnv

# Initialize environment
env = DisasterEnv()

# Reset and get initial observation
observation = env.reset()
print("\n--- INITIAL STATE ---")
print(observation)

# Dynamically select the first valid zone name
zone_name = observation["zones"][0]["name"]

# Create a valid action
action = {
    "allocations": [
        {
            "resource": "ambulance", 
            "zone": zone_name, 
            "amount": 1
        }
    ]
}

print(f"\n--- PERFORMING STEP (Allocating ambulance to {zone_name}) ---")
result = env.step(action)

print("\n--- STEP RESULT ---")
print(result)