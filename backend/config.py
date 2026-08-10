import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# config.py
# Provider limits captured on 2026-08-10; verify before final experiments.

BACKENDS = {
    "local": {
        "cost_per_1k_tokens": 0.0,
        "latency_s": 1.98,
        "rpm_limit": None,       # unlimited for this project model
        "tpm_limit": None,
        "rpd_limit": None,
        "capability": 1,
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.2:1b",
    },
    "groq": {
        "cost_per_1k_tokens": 0.0,
        "latency_s": 0.36,
        "rpm_limit": 30,
        "tpm_limit": 6000,
        "rpd_limit": 14400,
        "capability": 2,
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",
    },
    "gemini": {
        "cost_per_1k_tokens": 0.0,
        "latency_s": 1.53,
        "rpm_limit": None,       # not modeled because a stable RPM value is not used
        "tpm_limit": 250000,
        "rpd_limit": 1500,
        "capability": 5,
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash",
    },
}
