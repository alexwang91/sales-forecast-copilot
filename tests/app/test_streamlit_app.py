from app.streamlit_app import PAGE_REGISTRY, render_page


def test_page_registry_contains_core_pages():
    assert "Executive Overview" in PAGE_REGISTRY
    assert "Forecast Workbench" in PAGE_REGISTRY
    assert "Inventory Recommendation" in PAGE_REGISTRY


def test_render_page_returns_page_payload():
    payload = render_page("Executive Overview")

    assert payload["title"] == "Executive Overview"
    assert "description" in payload
