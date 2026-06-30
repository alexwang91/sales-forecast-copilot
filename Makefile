.PHONY: test data backtest app

test:
	python -m pytest

data:
	python -m src.data.sample_data

backtest:
	python -m src.evaluation.run_backtest

app:
	python app/streamlit_app.py
