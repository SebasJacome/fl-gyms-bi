VENV:=$(HOME)/.venvs/bi
PY:=$(VENV)/bin/python
PIP:=$(VENV)/bin/pip

PARQUET:=./data/business.parquet \
        ./data/review.parquet \
        ./data/user.parquet \
        ./data/tip.parquet
DB:=./data/gyms.db

.PHONY: run
run: $(DB)
	$(PY) export.py

$(DB):
	@echo "Creating SQLite3 database files..."
	$(PY) jsons.py
	@echo "Removing unused rows..."
	$(PY) processing.py


.PHONY: install
install:$(VENV)
	@echo "Installing required dependencies..."
	$(PIP) install -r requirements.txt

$(VENV):
	@echo "Creating python virtual environment at $(VENV)..."
	python3 -m venv $(VENV)

.PHONY: clean
clean:
	@echo "Cleaning data directory..."
	rm -rf ./data .ropeproject
