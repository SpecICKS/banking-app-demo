ifeq ($(OS),Windows_NT)
    PYTHON = python
else
    PYTHON = python3
endif

all: compile run

compile:
	@javac -d java_backend/bin java_backend/src/Read/Key.java java_backend/src/Controller/Controller.java

run:
	@cd python_frontend/src && $(PYTHON) launch.py

# Curățarea fișierelor compilate (opțional, util pentru reset)
clean:
	@rm -rf java_backend/bin/*