.PHONY: test data backtest app

test:
	python -m pytest

data:
	python -m src.data.sample_data

backtest:
	@echo "backtest is added in P1 Task 5 after metrics and baseline are implemented"

app:
	python app/streamlit_app.py
