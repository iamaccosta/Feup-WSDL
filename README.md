# Feup-WSDL
Web Semântica e Dados Ligados

---

# Local Development

1. Clone the repository
2. Go into the `website` directory, with `cd website`
3. Create a virtual environment, with `python3 -m venv .venv`
4. [Activate the environment](https://docs.python.org/3/library/venv.html#how-venvs-work), with `source .venv/bin/activate` on bash/zsh.
5. Install the project's dependencies using `pip install -r requirements.txt` 
6. Run `flask --app app run --debug` to start the app.

# Docker Development

Alternatively, you can use `docker compose up --build --force-recreate` to start the apps.
In this case, the files will be mounted in the containers using volumes, so all changes will be reflected in the running containers (except changes in the PyPI dependencies).