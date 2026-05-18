PYFILES := `echo */*.py` + " wordle-test"

check:
  ruff check {{PYFILES}}
  ty check {{PYFILES}}
  vermin -vv --no-tips -i {{PYFILES}}

build:
  rm -rf dist
  uv build

upload: build
  uv-publish

doc:
  update-readme-usage

format:
  ruff check --select I --fix {{PYFILES}} && ruff format {{PYFILES}}

clean:
  @rm -vrf *.egg-info build/ dist/ __pycache__/ */__pycache__/
