# install just to use this justfile: https://github.com/casey/just

uv_installed := `command -v uv`
uv_install_cmd := "curl -LsSf https://astral.sh/uv/install.sh | sh"

default:
    @just -l

install-uv:
    @# visit https://docs.astral.sh/uv/getting-started/installation/ for more installation options.
    @# cargo install --git https://github.com/astral-sh/uv uv
    @{{ if uv_installed != "" { "echo uv already installed" } else { "echo installing uv... && " + uv_install_cmd } }}
    
install-python:
    uv python install

venv:
    uv venv

install: install-uv install-python venv

test:
    uv run python -m unittest src/django_records/tests.py
