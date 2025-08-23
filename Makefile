PY=~/.venvs/pds/bin/python
PIP=~/.venvs/pdf/bin/pip
PARQUET=./data/business.parquet \
        ./data/review.parquet \
        ./data/user.parquet \
        ./data/tip.parquet


.PHONY: run
run: $(PARQUET)
	$(PY) processing.py

$(PARQUET):
	echo "Creating parquet files..."
	$(PY) jsons.py

.PHONY: install
install:
	echo "Installing required dependencies..."
	$(PIP) install -r requirements.txt

.PHONY: clean
clean:
	echo "Cleaning parquet files..."
	rm -rf ./data
