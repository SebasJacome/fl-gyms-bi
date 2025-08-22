PY=~/.venvs/pds/bin/python
PIP=~/.venvs/pdf/bin/pip

.PHONY: run
run:
	$(PY) gyms.py

.PHONY: install
install:
	$(PIP) install -r requirements.txt
