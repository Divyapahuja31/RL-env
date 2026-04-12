---
title: Disaster Response OpenEnv
emoji: 🚨
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 7860
tags:
  - openenv
pinned: false
license: mit
---

# 🚨 Disaster Response Environment (OpenEnv)

[![OpenEnv Support](https://img.shields.io/badge/OpenEnv-Compliant-blue.svg)](https://github.com/openenv)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-fidelity, deterministic resource allocation environment designed for evaluating AI agents in critical disaster relief coordination.

## 📖 Problem Description

In the immediate aftermath of a disaster, the window for effective intervention is extremely narrow. Decision-makers must allocate scarce resources—such as ambulances and food supplies—across multiple geographically dispersed zones. Each zone presents unique challenges: varying population densities and fluctuating levels of urgency. The core challenge is the **constrained multi-objective optimization problem**: minimizing overall urgency across all zones while managing depleting resources under a strict time limit.

## 🌍 Real-World Impact

Effective disaster response logistics can save thousands of lives. However, human coordination under extreme stress is often prone to error or delay. This environment provides a safe, reproducible benchmark for developing AI agents capable of:
- **Prioritizing Criticality**: Identifying and addressing "Danger Zones" before they escalate.
- **Resource Efficiency**: Reducing waste by ensuring every ambulance and food kit is deployed where its marginal impact is highest.
- **Strategic Planning**: Balancing short-term relief (food) with long-term stabilization (medical intervention).

---

## 🔍 Environment Specification

### 📡 Observation Space
The agent receives a comprehensive snapshot of the crisis at every step:
- **Zones**: A list of urban/rural areas, each containing:
  - `name`: Identifier.
  - `people`: Current population count.
  - `urgency`: A floating-point value [0.0 - 1.0] representing the severity of the situation.
- **Resources**: Remaining counts for `ambulances` and `food_kits`.
- **Time Remaining**: Integer steps before the response window closes.

### 🎮 Action Space
Agencies interact with the environment via a list of **Allocations**:
- `resource`: The type of supply to deploy (`ambulance` or `food_kits`).
- `zone`: The target zone's name.
- `amount`: The quantity to deploy.

### 🏆 Reward Design
The reward system is continuous and deterministic, designed to guide agents toward optimal behavior:
- **Urgency Reduction**: Primary reward is proportional to the reduction in urgency, weighted by the zone's current severity (saving a person in a 0.9 urgency zone is worth more than in a 0.2 zone).
- **Resource Discipline**: Penalties are applied for attempting to allocate resources that are not in stock (Waste Penalty).
- **Inactivity Penalty**: A baseline penalty is charged if no valid actions are taken, reflecting the cost of time in a crisis.

---

## 🛠️ Tasks

| Difficulty | Task Name | Key Challenge | Success Criteria |
| :--- | :--- | :--- | :--- |
| **Easy** | Urgency Intervention | Single-zone focus | Reduce Danger Zone urgency by 50% |
| **Medium**| Food Distribution | Balanced allocation | Achieve >0.3 aggregate urgency reduction |
| **Hard** | Survival Optimization | Extreme scarcity | Total reduction >1.0 and stabilize 1+ zone |

---

## 🚀 Setup Instructions

### Local Installation
1. Ensure Python 3.10+ is installed.
2. Install dependencies (recommended):
   ```bash
   pip install uv
   uv sync
   ```
   *Alternatively:* `pip install -r requirements.txt`

### Local Testing
Verify your environment and grader logic using the included test scripts:
1. **Quick Test**: `python3 test_env.py` (Basic functionality check)
2. **Comprehensive Test**: `python3 test_all_tasks.py` (Runs all 3 tasks with reports)

### Docker Setup
Build the minimal image for containerized runs or deployment to Hugging Face Spaces:
```bash
docker build -t disaster-env .
```

---

## 🤖 Running Inference

The project includes an LLM-driven inference script that uses OpenAI-compatible APIs to generate coordination strategies.

```bash
# Set your environment variables
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="your_api_key_here"

# Execute simulation
python3 inference.py
```

### Logging Format
The script follows a strict lifecycle logging format:
- `[START]`: Initialization and task loading.
- `[STEP]`: Action generation and environment execution.
- `[END]`: Final scoring and reward visualization.

---

## 📈 Expected Baseline Behavior

- **Greedy Agents**: Typically perform well on the Easy task by saturating the highest urgency zone first, but often fail the Hard task due to premature resource depletion.
- **Strategic Agents**: Should demonstrate "triage" logic—allocating just enough food to stabilize moderate zones while committing medical units to the most critical sectors.
- **Score Range**: A "Passing" grade represents a normalized score of **>0.5**, indicating high efficiency and no significant resource waste.

| Task | Baseline Score | Baseline Reward |
|:---|:---:|:---:|
| Easy | 0.210 | 46.49 |
| Medium | 0.162 | 24.25 |
| Hard | 0.338 | 65.65 |

| Average Score | 0.236 |
|---|---|

---
*Built with ❤️ for the OpenEnv Community.*
