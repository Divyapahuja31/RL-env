from fastapi import FastAPI
import uvicorn
from env.environment import DisasterEnv

app = FastAPI()
env = DisasterEnv()

@app.post("/reset")
def reset():
    state = env.reset()
    return {"observation": state, "reward": 0.0, "done": False, "info": {}}

@app.post("/step")
def step(action: dict):
    result = env.step(action)
    return result

@app.get("/state")
def state():
    return env.state()

if __name__ == "__main__":
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)
