ifeq ($(OS),Windows_NT)
    PYTHON = python.exe
else
    PYTHON = python3.exe
endif

all: compile run

compile:
	javac.exe -d java_backend/bin java_backend/src/**/*.java

run:
	cd python_frontend/src && $(PYTHON) launch.py

# Clean up compiled Java classes (optional, useful for reset)
clean:
	@rm -rf java_backend/bin/*
	