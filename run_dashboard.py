# run_dashboard.py
import streamlit.web.bootstrap as bootstrap

if __name__ == "__main__":
    bootstrap.run(
        "UI/dashboard/peer_review_dashboard.py",
        is_hello=False,
        args=[],
        flag_options={},
    )