# Test Environment for Package

### Tox

```
pip install tox
```

### Pyenv
```
brew install pyenv
brew install pyenv-virtualenv
```

### System setup for local folder

```
pyenv install 3.7.x
pyenv install 3.8.x
pyenv install 3.9.x
pyenv install 3.10.x

pyenv local 3.7.x 3.8.x 3.9.x 3.10.x
tox
```