PYTHON_FILE=bot.py
EXE_NAME=DiscordBot
OUTPUT_DIR=./output
SPEC_FILE=$(EXE_NAME).spec
ENV_FILE=.env

# Default target
all: build clean

run:
	python3 bot.py

# Build the .exe using pyinstaller
build:
	pyinstaller --onefile --name $(EXE_NAME) --distpath $(OUTPUT_DIR) --add-data "$(ENV_FILE):." $(PYTHON_FILE)

# Clean up temporary files
clean:
	rm -rf dist build .cache music $(SPEC_FILE) __pycache__

# Phony targets
.PHONY: all run build clean