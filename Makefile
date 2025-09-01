VENV:=$(HOME)/.venvs/bi
PY:=$(VENV)/bin/python
PIP:=$(VENV)/bin/pip

#PARQUET:=./data/yelp.parquet

PARQUET:=./data/business.parquet\
		 ./data/business_attributes.parquet\
		 ./data/business_hours.parquet\
		 ./data/business_categories.parquet\
		 ./data/review.parquet\
		 ./data/tip.parquet\
		 ./data/user.parquet

DB:=./data/gyms.db

.PHONY: run
run: $(PARQUET)
	@echo "The future's uncertain, and the end is always near."

$(PARQUET): $(DB)
	@echo "Creating parquet file..."
	$(PY) export.py

$(DB):
	@echo "Creating SQLite3 database files..."
	mkdir ./data
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
