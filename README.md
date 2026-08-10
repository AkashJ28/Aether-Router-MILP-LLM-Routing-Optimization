# Aether Router: MILP LLM Routing Optimization

Aether Router is a mathematical optimization framework that formulates Large Language Model (LLM) query routing as a **Mixed Integer Linear Programming (MILP)** assignment problem. 

Instead of routing queries using brittle heuristic if-else rules or incurring the overhead of expensive "always-run-strongest" strategies, Aether Router dynamically evaluates the complexity of a batch of user queries and distributes them across a heterogeneous set of local and cloud-based LLM providers. The framework minimizes total service latency while strictly satisfying rate-limit capacity (Requests-Per-Minute) and capability constraints.

---

## 1. Project Overview & Mathematical Formulation

In a multi-model environment, developers face trade-offs between speed, cost, rate limits, and reasoning capability. Aether Router models this choice as a resource allocation problem, solved optimally per batch using the **PuLP** optimization library.

### Decision Variable
$$x_{ij} \in \{0, 1\} \quad \text{representing if task } i \text{ is assigned to backend } j$$

### Objective
Minimize total service latency:
$$\min \sum_{i \in I} \sum_{j \in J} L_j x_{ij}$$
Where $L_j$ is the calibrated wall-clock response latency of backend $j$.

### Constraints
1. **Uniqueness**: Each task is assigned to exactly one backend:
   $$\sum_{j \in J} x_{ij} = 1 \quad \forall i \in I$$
2. **Capability Satisfaction**: A backend $j$ can only receive task $i$ if its capability score matches or exceeds the task's required complexity:
   $$x_{ij} = 0 \quad \text{whenever } \text{Cap}_j < R_i$$
   *(Complexity is categorized as Low ($R_i=1$), Medium ($R_i=3$), or High ($R_i=5$))*
3. **Rate Limit Enforcements**: The number of queries dispatched to a backend within a batch cannot exceed its Requests-Per-Minute (RPM) capacity:
   $$\sum_{i \in I} x_{ij} \le \text{RPM}_j \quad \forall j \in J \text{ with finite RPM}$$

---

## 2. System Architecture

Aether Router utilizes a modern, split-stack architecture designed for high-density developer telemetry and real-time visualization:

```text
                        Incoming Query Batch
                                │
                                ▼
                 Rule-Based Complexity Classifier
                                │
                                ▼
                   MILP Optimization Engine (PuLP)
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
      Local Ollama           Groq API           Gemini API
     (llama3.2:1b)     (llama-3.1-8b-instant) (gemini-2.5-flash)
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │
                                ▼
                       Aggregated Telemetry
```

### Backends Profile (Calibrated Free-Tier Config)
*   **Local Ollama (`llama3.2:1b`)**: Capability 1, Calibrated Latency: `1.98s`, RPM Limit: Unlimited. Runs locally on device (optimized for RTX 4060 laptops).
*   **Groq API (`llama-3.1-8b-instant`)**: Capability 2, Calibrated Latency: `0.36s`, RPM Limit: `30`. Ultra-fast cloud tier.
*   **Gemini API (`gemini-2.5-flash`)**: Capability 5, Calibrated Latency: `1.53s`, RPM Limit: Unlimited (modeled on daily free quota).

### Tech Stack
*   **Backend**: Python, FastAPI, PuLP (CBC Solver), OpenAI SDK (compatible client interfaces), pytest.
*   **Frontend**: Next.js (App Router, TS), Tailwind CSS v4, Recharts (dark mode visualizations), shadcn/ui.

---

## 3. Installation & Setup

### Prerequisites
*   [Python 3.10+](https://www.python.org/downloads/)
*   [Node.js 18+](https://nodejs.org/)
*   [Ollama](https://ollama.com/) (for local model hosting)

---

### Step A: Start the Local Ollama Model
1. Open a terminal and start the Ollama service:
   ```bash
   ollama serve
   ```
2. Pull the lightweight `llama3.2:1b` model:
   ```bash
   ollama pull llama3.2:1b
   ```

---

### Step B: Set Up the Backend
1. Navigate to the root directory and create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   *   **PowerShell**:
       ```powershell
       .venv\Scripts\Activate.ps1
       ```
   *   **Git Bash / macOS / Linux**:
       ```bash
       source .venv/bin/activate
       ```
   *   **Command Prompt**:
       ```cmd
       .venv\Scripts\activate.bat
       ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Copy the environment variables template and configure your keys:
   ```bash
   cp env.example .env
   ```
   Open the `.env` file and insert your API keys for **Groq** and **Gemini**.

---

### Step C: Set Up the Frontend
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```

---

## 4. Running the Project

To experience the full capability of the system, run both the backend API and Next.js frontend developer dashboard simultaneously.

### 1. Boot the FastAPI Backend Server
From the project root (with your virtual environment activated):
```bash
python -m uvicorn backend.api.main:app --reload --port 8000
```
The backend API is now running at `http://localhost:8000`. You can inspect the interactive OpenAPI docs at `http://localhost:8000/docs`.

### 2. Boot the Next.js Frontend Dashboard
From the `frontend/` directory:
```bash
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 5. Testing and Validation

### Run Automated Tests
Aether Router has a comprehensive suite of unit and integration tests verifying the rule-based classifier, the MILP mathematical logic (including Groq's RPM boundary overflow/spillover), and FastAPI routes.

From the project root:
```bash
.venv\Scripts\python -m pytest backend/tests/
```

### Run Latency Calibration Script
To recalibrate the latencies of your backends with fresh live requests, run the following command:
```bash
.venv\Scripts\python backend/experiments/measure_latency.py
```

---

## 6. Security Note

> [!IMPORTANT]
> **CRITICAL SECURITY NOTE:** 
> Do not under any circumstances hardcode your provider API keys (Groq/Gemini) in the code files or commit them to source control. Always place keys inside the root `.env` file. The `.gitignore` file has been configured to block `.env` from ever being staged or pushed to GitHub.
