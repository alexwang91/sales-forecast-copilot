from src.agent.summary import build_weekly_summary


def test_build_weekly_summary_returns_json_and_markdown():
    overview = {"best_model": "system", "fva_vs_baseline": 0.05}
    risks = [{"sku": "S1", "risk": "stockout"}]

    out = build_weekly_summary(overview, risks=risks)

    assert out["json"]["best_model"] == "system"
    assert out["json"]["fva_vs_baseline"] == 0.05
    assert out["json"]["risk_skus"] == ["S1"]
    assert "system" in out["markdown"]
    assert "S1" in out["markdown"]
