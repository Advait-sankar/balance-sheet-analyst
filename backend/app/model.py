import json
from pathlib import Path

def load_data(path="data/reliance_2024.json"):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{path} not found. Place cleaned JSON there.")
    return json.loads(p.read_text())

# Dummy users for demonstration
USERS = {
    "analyst@company.com": {"password": "analyst123", "role": "analyst", "companies": ["Reliance"]},
    "ceo@reliance.com": {"password": "ceo123", "role": "ceo", "companies": ["Reliance"]},
    "group_owner@ambi.com": {"password": "group123", "role": "group_owner", "companies": ["ALL"]}
}
