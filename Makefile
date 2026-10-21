ifeq ($(OS),Windows_NT)
    PYTHON = python
else
    PYTHON = python3
endif

all: compile run

compile:
	javac -d java_backend/bin java_backend/src/**/*.java

run:
	cd python_frontend/src && $(PYTHON) launch.py

# Clean up compiled Java classes (optional, useful for reset)
clean:
	@rm -rf java_backend/bin/*