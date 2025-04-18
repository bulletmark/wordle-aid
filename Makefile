NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))
PYFILES = $(PYNAME).py wordle-test

check:
	ruff check $(PYFILES)
	pyright $(PYFILES)
	vermin -vv --no-tips -i $(PYFILES)

build:
	rm -rf dist
	uv build

upload: build
	uv-publish

doc:
	update-readme-usage

format:
	ruff check --select I --fix $(PYFILES) && ruff format $(PYFILES)

clean:
	@rm -vrf *.egg-info .venv/ build/ dist/ __pycache__/
