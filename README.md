# 🚀 Selenium Scraper Quickstarter

**Selenium Scraper Quickstarter** is a professional template for building robust and scalable web scrapers using Selenium and Flask, with **automatic browser streaming capabilities** for monitoring and debugging your automation tasks.

[![🚀 Docker Build & Publish](https://github.com/Ismola/selenium-scraper-quickstarter/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Ismola/selenium-scraper-quickstarter/actions/workflows/docker-publish.yml)

---

## ✨ Main Features

- **🎯 Selenium Automation:** Advanced interaction with dynamic web pages
- **🌐 RESTful API with Flask:** Secure and customizable endpoint exposure
- **🎥 Automatic Streaming:** Record MP4 videos of browser sessions automatically
- **🔒 Bearer Authentication:** Security via configurable tokens
- **⚙️ Environment Management:** Variables for production, testing, and staging
- **🐳 Docker & Cloud Ready:** Containers and cloud development support
- **📝 Logging System:** Activity and error logging for auditing and debugging
- **📁 File Management:** Automated downloads and temporary directory handling
- **🔧 Extensible & Modular:** Clean architecture for adding actions and endpoints
- **💡 Production Ready:** Optimized for development and production environments

---

## 📁 Project Structure

```bash
├── main.py                   # Flask entry point with streaming support
├── actions/                  # Scraping and automation logic
│   └── web_driver.py        # WebDriver with automatic streaming
├── controller/               # Endpoint controllers
├── utils/                    # Utilities and configuration
│   ├── external_streaming_service.py  # Video recording service
│   └── config.py            # Environment configuration
├── temp_downloads/           # Temporary downloads
├── videos/                   # Streaming video outputs
├── logs/                     # Application logs
├── STREAMING_GUIDE.md        # Comprehensive streaming documentation
└── requirements.txt          # Python dependencies
```

├── requirements.txt          # Python dependencies
├── Dockerfile                # Production-ready Docker image
├── .env.example              # Example environment configuration
└── README.md                 # This file

```

---

## ⚙️ Environment Variables

Configure scraper behavior via variables in the `.env` file. Copy `.env.example` to `.env` and customize as needed.

| Variable           | Required | Possible Values / Example                | Description                                                        |
|--------------------|----------|------------------------------------------|--------------------------------------------------------------------|
| `STAGE`            | Yes      | `production`, `testing`, `staging`       | Execution environment (affects visibility and real actions)        |
| `VALID_TOKEN`      | Yes      | `sample`                                 | Bearer token to authenticate requests                              |
| `HEADLESS_MODE`    | Optional | `auto`, `True`, `False`                  | Controls if the browser is visible or headless                     |
| `AUTO_DELETE_LOGS` | Optional | `True`, `False`                          | Automatically deletes old logs                                     |

### 🎥 Streaming Configuration

| Variable           | Required | Default | Description                                                        |
|--------------------|----------|---------|-------------------------------------------------------------------|
| `STREAMING_ENABLED`| Optional | `false` | Enable/disable real-time browser streaming                       |
| `STREAMING_FPS`    | Optional | `10`    | Frames per second for the stream (5-30 recommended)              |
| `STREAMING_QUALITY`| Optional | `80`    | JPEG quality for stream images (1-100)                           |
| `STREAMING_WIDTH`  | Optional | `1280`  | Browser window width for streaming                                |
| `STREAMING_HEIGHT` | Optional | `720`   | Browser window height for streaming                               |

> **Note:** See `.env.example` for more details and recommendations.
> **Base URL:** The base URL is now set in the constant `BASE_URL` inside `utils/config.py`.  
> To change the target site, edit the value of `BASE_URL` in that file.

---

## 🏁 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Ismola/selenium-scraper-quickstarter.git
cd selenium-scraper-quickstarter
```

### 2. Set up your environment

- Copy `.env.example` to `.env` and edit it as needed.
- Make sure you have Python 3.x and Google Chrome installed.
- **Set the base URL:** Edit the `BASE_URL` constant in `utils/config.py` to point to your target website.

### 3. Choose your development mode

#### Option A: Dev Container (Recommended)

1. Install [VS Code](https://code.visualstudio.com/) and the **Dev Containers** extension.
2. Install [Docker](https://www.docker.com/).
3. Open the project in VS Code and select "Reopen in Container".

#### Option B: GitHub Codespaces

1. Click "Code" > "Open with Codespaces" on GitHub.
2. Wait for the environment to be set up automatically.

#### Option C: Manual

```bash
python3 -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## ▶️ Running

### Local

```bash
python3 main.py
```

### Docker

```bash
docker build -t selenium-scraper .
docker run --env-file .env -p 3000:3000 selenium-scraper
```

### Production (Gunicorn)

```bash
gunicorn -w 2 -b 0.0.0.0:3000 --timeout 600 main:app
```

---

## ⚙️ CI/CD and Workflow Customization

- **Change environment variables for CI/CD:**
  - Go to **Settings > Secrets and variables > Actions** in your GitHub repository.
  - Add or update secrets like `STAGE`, `VALID_TOKEN` as needed.
  - These will be injected into the Docker image during the build and publish process.

> **⚠️ Important:**  
> If you publish the Docker image to a public registry, any environment variable (such as `STAGE`, `VALID_TOKEN`) injected during build may be visible to anyone who downloads the image.  
> **Never use production secrets or sensitive tokens in public images.**  
> For private deployments, always use private registries and restrict access to your images.

- **Change Docker registry or image name:**
  - Edit the `REGISTRY` and `IMAGE_NAME` variables in `.github/workflows/docker-publish.yml`.

- **Trigger the publish workflow:**
  - By default, the Docker image is published only after a successful run of the `Test` workflow.
  - You can change the trigger to run on other branches or events by editing the `on:` section.

> **Tip:** Adjust the port if you change the exposed port in `compose.yaml`.

---

## 🔗 API Usage

### Authentication

All protected routes require the header:

```curl
Authorization: Bearer <VALID_TOKEN>
```

### Default Endpoints

| Method | Route      | Description                        |
|--------|-----------|------------------------------------|
| GET    | `/`        | Server health check                |
| GET    | `/sample`  | Example endpoint (modifiable)      |

### 🎥 Streaming Endpoints

| Method | Route               | Description                                    |
|--------|---------------------|------------------------------------------------|
| POST   | `/stream/start`     | Start browser streaming                        |
| POST   | `/stream/stop`      | Stop browser streaming                         |
| GET    | `/stream/status`    | Get current streaming status                   |
| POST   | `/stream/navigate`  | Navigate to URL during streaming               |
| POST   | `/stream/action`    | Execute actions (click, type, scroll)         |
| GET    | `/stream/video`     | Video stream endpoint (for embedding)         |
| GET    | `/stream/viewer`    | 🌐 **Web interface to view stream**          |

### 🎬 Demo Endpoints

| Method | Route                    | Description                                    |
|--------|--------------------------|------------------------------------------------|
| POST   | `/demo/streaming-search` | Google search demo with streaming              |
| POST   | `/demo/streaming-scraping`| Web scraping demo with streaming              |
| POST   | `/demo/interactive`      | Interactive streaming session                  |

#### Example with `curl`

```bash
curl -H "Authorization: Bearer sample" http://localhost:3000/sample
```

### 🎥 Quick Streaming Example

1. **Enable streaming** in your `.env` file:

   ```env
   STREAMING_ENABLED=true
   ```

2. **Start the server:**

   ```bash
   python3 main.py
   ```

3. **Open the web viewer:**

   Visit <http://localhost:3000/stream/viewer> in your browser

4. **Start streaming:**

   Click "▶️ Start Stream" or use the API:

   ```bash
   curl -X POST -H "Content-Type: application/json" \
        -d '{"url":"https://www.google.com","browser":"chrome"}' \
        http://localhost:3000/stream/start
   ```

5. **Run a demo:**

   Click "🔍 Google Search Demo" or:

   ```bash
   curl -X POST http://localhost:3000/demo/streaming-search
   ```

Now you can watch your browser automation in real-time! 🎬

---

## 🛠️ Customization & Extension

1. **Add your token in `.env`.**
2. **Set the base URL in `utils/config.py` by editing the `BASE_URL` constant.**
3. **Create new endpoints in `main.py`.**
4. **Implement scraping logic in `actions/` and controllers in `controller/`.**
5. **Use utilities from `utils/` for logging, configuration, and helpers.**

---

## 🧩 Architecture & Flow

1. **main.py:** Defines endpoints and starts Flask.
2. **controller/**: Receives the request, validates, and calls the action.
3. **actions/**: Executes scraping logic (Selenium).
4. **utils/**: Configuration, helpers, and shared utilities.  
   - **BASE_URL** is defined in `utils/config.py`.
5. **temp_downloads/**: Stores temporarily downloaded files.

---

## 🚢 Deployment

There are several recommended ways to deploy your scraper in a production or staging environment:

### 1. Gunicorn (Recommended for Production)

The project is ready to be served using [Gunicorn](https://gunicorn.org/), a robust WSGI HTTP server for Python web applications. This is the method used in the provided Dockerfile.

**To run with Gunicorn manually:**

```bash
gunicorn -w 2 -b 0.0.0.0:3000 --timeout 600 main:app
```

- `-w 2`: Number of worker processes (adjust as needed).
- `-b 0.0.0.0:3000`: Binds to all interfaces on port 3000.
- `--timeout 600`: Increases timeout for long scraping tasks.

### 2. Docker (Recommended for Consistency)

You can deploy the application using Docker, ensuring all dependencies and environment settings are consistent across environments.

**Build and run the container:**

```bash
docker build -t selenium-scraper .
docker run --env-file .env -p 3000:3000 selenium-scraper
```

### 3. Docker Compose (For Multi-Service and Volume Management)

The repository includes a `compose.yaml` file for [Docker Compose](https://docs.docker.com/compose/), which simplifies running the application with persistent storage

**To deploy with Docker Compose:**

```bash
docker compose up --build
```

#### Volumes in Compose

- `./logs:/app/logs`: Persists application logs on your host machine for easier debugging and auditing.
- `./temp_downloads:/app/temp_downloads`: Stores downloaded files outside the container, so you don't lose data on container restarts.

> **Tip:** You can customize the exposed ports and volume paths in `compose.yaml` as needed for your infrastructure.

---

## ⚙️ GitHub Actions CI/CD

This project includes a preconfigured GitHub Actions workflow for continuous integration and automated Docker image publishing. You can find the workflow files in `.github/workflows/`.

### Included Workflows

- **Docker Smoke (`docker-smoke.yml`):**
  - Builds the Docker image and verifies that the application starts correctly using Docker Compose.
  - Performs a smoke test by accessing the root endpoint (`/`) to ensure the container responds.

- **CI Test Suite (`ci-test.yml`):**
  - Runs after the smoke test.
  - Installs dependencies and runs automated tests with `pytest` inside the Docker Compose environment.
  - Ensures the application passes tests before continuing the pipeline.

- **Docker Build & Publish (`docker-publish.yml`):**
  - Runs only if the previous workflows are successful.
  - Builds and publishes the Docker image to GitHub Container Registry (`ghcr.io`).
  - Uses environment variables and secrets configured in the repository.

> ⚙️ You can customize or extend these workflows by editing the files in `.github/workflows/` as needed for your CI/CD requirements.

## 🧪 Automated Testing

The project includes automated tests located in the `test/` folder, using `pytest` and Flask's test client.

### 📂 Test Structure

- `test/test_main.py`: Tests for the main endpoints defined in `main.py`.

### ▶️ How to run the tests

1. Install dependencies if you haven't already:

   ```bash
   pip install -r requirements.txt
   pip install pytest
   ```

2. Run the tests:

   ```bash
   pytest --maxfail=1 --disable-warnings -v
   ```

> 💡 **Tip:** You can also run the tests automatically in the CI/CD flow with GitHub Actions.

### ✏️ How to modify or add tests?

- Edit or add files in the `test/` folder following the example in `test_main.py`.
- Use the Flask client to simulate HTTP requests and validate responses.
- To test new endpoints, create functions starting with `test_` and use the `client` fixture.
- See the [pytest documentation](https://docs.pytest.org/) for more options and best practices.

---

## 🤖 Custom instructions for GitHub Copilot

This project uses custom Copilot instructions from [Ismola/personal-copilot-instructions](https://github.com/Ismola/personal-copilot-instructions).  
Each time the devcontainer starts, they are cloned and updated automatically in `.github/instructions`.

---

## 🐞 Troubleshooting

### Common error: `local variable 'driver' referenced before assignment`

- This may be due to incompatibility between Chrome and Chromedriver.
- Quick fix:
    1. Delete the drivers folder: `rm -rf ~/.wdm`
    2. Restart the environment.

### Other issues

- Ensure environment variables are correctly set.
- Check generated logs for more details.

---

## 📚 Resources & Bibliography

- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [Flask Docs](https://flask.palletsprojects.com/en/3.0.x/)
- [Selenium Tutorial (YouTube)](https://youtube.com/playlist?list=PLheIVUbpfWZ17lCcHnoaa1RD59juFR06C)

---

## 🤝 Contributions

Pull requests and suggestions are welcome! Please open an issue to discuss major changes.

---

## 📝 License

MIT License © Ismola

---

## 🎥 Browser Streaming Features

Este proyecto incluye capacidades avanzadas de streaming en tiempo real para visualizar las automatizaciones del navegador mientras se ejecutan.

### ✨ Características del Streaming

- **🎬 Vista en tiempo real:** Observa el navegador mientras automatiza tareas
- **🎮 Control remoto:** Navega y ejecuta acciones desde la interfaz web
- **📱 Interfaz responsive:** Viewer web optimizado para diferentes dispositivos
- **🔍 Destacado de elementos:** Resalta elementos antes de interactuar
- **⚙️ Calidad configurable:** Ajusta FPS y calidad según necesidades
- **🐳 Docker ready:** Funciona en contenedores con display virtual
- **📊 Demos incluidos:** Ejemplos listos para usar

### 🚀 Casos de Uso

- **Debugging:** Ve qué hace tu bot paso a paso
- **Demostraciones:** Muestra automatizaciones a clientes/equipos
- **Monitoreo:** Supervisa bots de larga duración
- **Desarrollo:** Desarrolla scrapers de forma visual
- **Educación:** Enseña automatización web

### 📖 Documentación Completa

Para guías detalladas, ejemplos de código y configuración avanzada, consulta:

- **[STREAMING_GUIDE.md](STREAMING_GUIDE.md)** - Guía completa de streaming
- **Interfaz Web:** <http://localhost:3000/stream/viewer>
- **API Reference:** Endpoints de streaming documentados arriba

---
