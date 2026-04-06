from env.environment import DisasterEnv

env = DisasterEnv()

obs = env.reset()
print("Initial:", obs)

action = {
    "allocations": [
        {"resource": "ambulance", "zone": "Metropolis", "amount": 1}
    ]
}

result = env.step(action)
print("Step result:", result)
