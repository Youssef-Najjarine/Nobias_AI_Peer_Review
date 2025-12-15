# run_dashboard.py
import streamlit.web.bootstrap as bootstrap
from pathlib import Path

app_dir = Path("UI/dashboard")

if __name__ == "__main__":
    bootstrap.run(
        str(app_dir / "app.py"),  # Main page
        is_hello=False,
        args=[],
        flag_options={},
    )