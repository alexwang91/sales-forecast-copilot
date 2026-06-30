PAGE_REGISTRY = {
    "Executive Overview": "FVA, accuracy, risk, and weekly movement summary.",
    "Forecast Workbench": "SKU-level forecast inspection and model comparison.",
    "Inventory Recommendation": "Inventory coverage, sell-in recommendation, and risk flags.",
    "Promotion Simulator": "Scenario planning for known future commercial events.",
    "Launch Planner": "New product analog planning and launch curve review.",
}


def render_page(page_name: str) -> dict:
    if page_name not in PAGE_REGISTRY:
        raise KeyError(f"unknown page: {page_name}")
    return {"title": page_name, "description": PAGE_REGISTRY[page_name]}


def main() -> dict:
    return render_page("Executive Overview")


if __name__ == "__main__":
    main()
