# Tests/test_replication_engine.py
from Core.replication_simulator import ReplicationSimulator


def test_replication_simulator_scores_in_range():
    sim = ReplicationSimulator()
    text = """
    We preregistered the study, share all data and analysis code on GitHub,
    and ran 10,000 bootstrap replications plus Monte Carlo simulations
    to assess robustness. Sensitivity analyses across parameter settings
    are also reported.
    """
    result = sim.analyze_replication(text)
    assert "overall_replicability_score" in result
    score = result["overall_replicability_score"]
    assert 0.0 <= score <= 1.0
    assert any(isinstance(v, dict) for v in result.values())


def test_replication_simulator_distinguishes_weak_and_strong():
    sim = ReplicationSimulator()
    weak_text = """
    We propose a theoretical framework but provide no replication,
    no open data, and no mention of robustness checks or preregistration.
    """
    strong_text = """
    This work explicitly replicates prior findings. The protocol was preregistered
    on OSF, all raw data and analysis code are publicly available, and we run
    extensive robustness checks including bootstrapping and Monte Carlo simulations.
    """
    weak_result = sim.analyze_replication(weak_text)
    strong_result = sim.analyze_replication(strong_text)

    weak_score = weak_result["overall_replicability_score"]
    strong_score = strong_result["overall_replicability_score"]

    assert 0.0 <= weak_score <= 1.0
    assert 0.0 <= strong_score <= 1.0
    assert strong_score >= weak_score

    # Strong should have positive openness/robustness signals
    assert any(strong_result["openness"].values())
    assert any(strong_result["robustness"].values())