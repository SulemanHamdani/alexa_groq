# Simple Makefile for packaging the Alexa Groq Lambda

LAMBDA_DIR := alexa_groq
ZIP_NAME   := alexa_groq.zip

.PHONY: all package clean check tree

all: package

package: ## Create deployment ZIP from $(LAMBDA_DIR)
	cd $(LAMBDA_DIR) && \
	zip -r ../$(ZIP_NAME) . \
	    -x "*/__pycache__/*" "*.pyc" \
	    -x ".DS_Store" \
	    -x "*.dist-info/__pycache__/*"
	@echo "Built $(ZIP_NAME)"

check: ## Byte-compile to catch syntax errors
	python -m compileall -q $(LAMBDA_DIR)

tree: ## Show packaged file listing (without creating a new zip)
	unzip -l $(ZIP_NAME) | sed -e '1,3d' -e '$$d'

clean: ## Remove build artifacts
	rm -f $(ZIP_NAME)
	find $(LAMBDA_DIR) -name "__pycache__" -type d -prune -exec rm -rf {} +
	find $(LAMBDA_DIR) -name "*.pyc" -delete

# Help: list targets with descriptions
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_\-]+:.*##/ {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

