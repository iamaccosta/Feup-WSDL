# Feup-WSDL
Web Semântica e Dados Ligados

---

# Local Development

1. Clone the repository

## Backend

1. Go into the `website/backend/` directory, with `cd website/backend`
2. Create a virtual environment, with `python3 -m venv .venv`
3. [Activate the environment](https://docs.python.org/3/library/venv.html#how-venvs-work), with `source .venv/bin/activate` on bash/zsh.
4. Install the project's dependencies using `pip install -r requirements.txt` 
5. Run `flask --app app run --debug` to start the app.

## Frontend

1. Go into the `website/frontend/` directory, with `cd website/frontend`
2. Run `npm install` to install the dependencies
3. Run `npm run dev` to start the app.

# Docker Development

Alternatively, you can use `docker compose up --build --force-recreate`, in the `website/` to start the apps.
In this case, the files will be mounted in the containers using volumes, so all changes will be reflected in the running containers (except changes in the PyPI or NPM dependencies).