.PHONY: build run

PYTHON=.venv/bin/python
PIP=.venv/bin/pip

build:
	@echo "Building ShiftTimerBot..."
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Build complete."

run:
	@echo "Building ShiftTimerBot..."
	cd src && ../$(PYTHON) run.py
