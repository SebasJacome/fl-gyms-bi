PY=~/.venvs/pds/bin/python
PIP=~/.venvs/pdf/bin/pip
PARQUET=./data/business.parquet \
        ./data/review.parquet \
        ./data/user.parquet \
        ./data/tip.parquet
DB=./gyms.db \
   ./gyms.db-journal

.PHONY: run
run: $(DB)
	$(PY) processing.py

$(DB):
	@echo "Creating SQLite3 database files..."
	$(PY) jsons.py

.PHONY: install
install:
	@echo "Installing required dependencies..."
	$(PIP) install -r requirements.txt

.PHONY: clean
clean:
	@echo "Cleaning parquet files..."
	rm -rf ./data gyms.db
