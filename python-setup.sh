rm -rf pyenv || 1
python3 -m venv pyenv
pyenv/bin/pip install wheel
pyenv/bin/pip install --upgrade pip
pyenv/bin/pip install -r requirements.txt
