# Feup-WSDL
Web Semântica e Dados Ligados.

---

### Setup
The Setup explanation is detailed in [setup](./docs/setup.md) document.

---

### Implementation Details
To further understand how the project is currently working, how it is addressing some conserns of Data Linked Principles, and the structure of every component you may investigate the [project_details](./docs/project_details.md) document.

---

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

## Fuseki
Apache Jena Fuseki server is used to create our Knowledgebase solution for applications/systems related to SmartCity. In scripts folder there is a detailed [explanation](./scripts/README.md) of each script, what data is being collected and the information that it provides.

# Docker Development

Alternatively, you can use `docker compose up --build --force-recreate --watch`, in the `website/` to start the apps.
In this case, the files will be mounted in the containers using volumes, so all changes will be reflected in the running containers (including changes in the PyPI or NPM dependencies).
