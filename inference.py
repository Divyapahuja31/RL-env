"""
Inference Script for Disaster Response OpenEnv
"""
import os
import json
from openai import OpenAI

from env.environment import DisasterEnv
from tasks.easy import EasyTask

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or "no-key-set"

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = DisasterEnv()
    task = EasyTask()
    obs = env.reset(task.get_config())
    print("[START]")
    print("Environment initialized with EasyTask")
    print("[END]")

if __name__ == "__main__":
    main()
