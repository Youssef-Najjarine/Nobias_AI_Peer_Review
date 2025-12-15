# Config/__init__.py
"""
Nobias Configuration Package

Centralized configuration loading.
Usage:
    from Config import settings
    print(settings.scoring_weights["statistics"])
"""

from pathlib import Path
import yaml

CONFIG_DIR = Path(__file__).parent

def load_yaml(file_name: str) -> dict:
    path = CONFIG_DIR / file_name
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Load all configs on import
model_config = load_yaml("model_config.yaml")
scoring_weights = load_yaml("scoring_weights.yaml")
api_config = load_yaml("api_config.yaml")
security_config = load_yaml("security_config.yaml")
datasets = load_yaml("datasets.yaml")

# Unified settings object (optional convenience)
settings = {
    "model": model_config,
    "scoring_weights": scoring_weights,
    "api": api_config,
    "security": security_config,
    "datasets": datasets,
}