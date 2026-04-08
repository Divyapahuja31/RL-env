from fastapi import FastAPI, Body
import uvicorn
from env.environment import DisasterEnv
from tasks.easy import EasyTask
from tasks.medium import MediumTask
from tasks.hard import HardTask
from graders.grader import Grader

app = FastAPI(title="Disaster Response OpenEnv")

# One env instance per task for isolation
envs = {}
grader = Grader(max_attainable_reward=150.0)

TASKS = {
    "easy": EasyTask(),
    "medium": MediumTask(),
    "hard": HardTask(),
}


@app.post("/reset")
def reset(body: dict = Body(default={})):
    """Resets the environment. Optionally accepts {"task": "easy|medium|hard"}."""
    task_name = body.get("task", "easy")
    task = TASKS.get(task_name, TASKS["easy"])
    env = DisasterEnv()
    envs["current"] = env
    envs["task_name"] = task_name
    state = env.reset(task.get_config())
    return {
        "observation": state,
        "reward": 0.0,
        "done": False,
        "info": {"task": task_name}
    }


@app.post("/step")
def step(action: dict = Body(...)):
    """Processes one step. Accepts action dict with 'allocations' list."""
    env = envs.get("current")
    if env is None:
        return {"error": "Environment not reset. Call /reset first."}
    result = env.step(action)
    return result


@app.get("/state")
def state():
    """Returns current environment state."""
    env = envs.get("current")
    if env is None:
        return {"error": "Environment not reset. Call /reset first."}
    return env.state()


@app.get("/tasks")
def list_tasks():
    """Lists available tasks."""
    return {"tasks": list(TASKS.keys())}


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "name": "Disaster Response OpenEnv", "version": "1.1.0"}


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()