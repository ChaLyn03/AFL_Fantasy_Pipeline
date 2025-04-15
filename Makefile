# AFLFantasy Pipeline Makefile

# Define directories
RAW_DATA_DIR := data/raw
INTERIM_DATA_DIR := data/interim
PROCESSED_DATA_DIR := data/processed

# Python environment
PYTHON := .venv/bin/python

# Default: run full pipeline
.PHONY: all
all: scrape collate derive team

# --- INDIVIDUAL STAGES ---

.PHONY: scrape
scrape:
	@echo "🔄 Scraping player and coach data..."
	$(PYTHON) scripts/1PlayerScrape.py
	$(PYTHON) scripts/2CoachScrape.py

.PHONY: collate
collate:
	@echo "🧩 Collating raw data into SQLite..."
	$(PYTHON) scripts/5StatCollate.py

.PHONY: derive
derive:
	@echo "📈 Generating derived statistics..."
	$(PYTHON) scripts/7StatDerivatives.py

.PHONY: team
team:
	@echo "📋 Extracting current AFL Fantasy team data..."
	$(PYTHON) scripts/9TeamStats.py

# --- CLEANUP TASKS ---

.PHONY: clean
clean:
	@echo "🧹 Removing generated databases and outputs..."
	rm -f $(INTERIM_DATA_DIR)/*.db
	rm -f $(PROCESSED_DATA_DIR)/*.db
	rm -f $(PROCESSED_DATA_DIR)/*.csv

.PHONY: deep-clean
deep-clean: clean
	@echo "⚠️  You're about to remove your raw scraped JSON files (data/raw/*.json)."
	@echo "💥 These are your fundamental files — it’ll suck if you still need them"
	@read -p "❓ Are you sure you want to continue? (y/N) " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "🧼 Deep cleaning raw files..."; \
		rm -f $(RAW_DATA_DIR)/*.json; \
	else \
		echo "❌ Deep clean cancelled."; \
	fi

# --- ENVIRONMENT ---

.PHONY: install
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

.PHONY: venv
venv:
	@echo "🐍 Creating virtual environment..."
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

# --- TESTING ---

.PHONY: test
test:
	@echo "🧪 Running tests with pytest..."
	pytest tests/