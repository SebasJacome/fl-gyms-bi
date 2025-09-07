VENV:=$(HOME)/.venvs/bi
PY:=$(VENV)/bin/python
PIP:=$(VENV)/bin/pip

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
	$(PY) atlas.py

$(PARQUET): $(DB)
	@echo "Creating parquet file..."
	$(PY) export.py
	rm business_hours_merge.parquet business.parquet business_attributes.parquet business_categories.parquet business_hours.parquet gyms.db
	mv business_merge.parquet business.parquet

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
