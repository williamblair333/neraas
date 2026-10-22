# neraas — run `just` for this list.
# Each recipe is one line; the logic lives in the Python scripts.

# list recipes
default:
    @just --list

# create .venv (uv) and install requirements plus pytest
setup:
    uv venv --allow-existing .venv && uv pip install --python .venv/bin/python -r requirements.txt pytest

# run the tests
test *args:
    .venv/bin/python -m pytest tests -q {{args}}

# predict one moment: just run --date "1859-09-01" --time "11:18" --zone 0
run *args:
    .venv/bin/python main.py {{args}}

# CSV over a range: just generate --start_year 1859 --end_year 1859 --interval days --csv_output results.csv
generate *args:
    .venv/bin/python generate_data.py {{args}}
