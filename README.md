# MoodMentor

MoodMentor is an emotion-analysis application that combines pretrained machine-learning models, sentiment analysis, wellness recommendations, and a Streamlit dashboard backed by a FastAPI API.

## Features

* Emotion and sentiment analysis
* Wellness recommendations
* Interaction history and emotional trend tracking
* User authentication and data deletion
* Python package and command-line interface
* Streamlit dashboard with a FastAPI backend

## Prerequisites

* Python 3.10 or later
* Internet access for the initial pretrained model download
* Sufficient memory to load the PyTorch emotion model

## Installation

### Install the Python Package

Install the package without optional machine-learning dependencies:

```powershell
python -m pip install .
```

Install the package with emotion-analysis support:

```powershell
python -m pip install ".[analysis]"
```

### Install Web Application Dependencies

From the project root, install the dependencies listed for the backend and dashboard:

```powershell
python -m pip install -r backend/requirements.txt
```

## Command-Line Usage

Show help:

```powershell
moodmentor --help
```

Show the package version:

```powershell
moodmentor --version
```

Analyze text:

```powershell
moodmentor analyze "I feel happy and excited today."
```

The first analysis may download a pretrained emotion model from Hugging Face.

## Configuration

### Environment Variables

Create a `.env` file in the project root. Configure the following variables with your own values:

```dotenv
JWT_SECRET=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

USER_001_PASSWORD=replace-with-a-demo-password
USER_002_PASSWORD=replace-with-a-demo-password
USER_003_PASSWORD=replace-with-a-demo-password
```

Replace every placeholder with a strong, unique value. These are example settings, not real credentials.

* `JWT_SECRET` is required by the backend.
* `JWT_ALGORITHM` defaults to `HS256`.
* `JWT_EXPIRE_MINUTES` defaults to `60`.
* The three user password variables supply the demo-user credentials.

Keep `.env` out of version control. For deployment, configure secrets through your hosting provider's environment-variable or secret-management settings. Never commit actual credentials.

### Backend URL

The Streamlit dashboard reads the backend URL from `MOODMENTOR_BACKEND_URL`. If this variable is not set, it uses `http://127.0.0.1:8000`.

For local development in PowerShell:

```powershell
$env:MOODMENTOR_BACKEND_URL = "http://127.0.0.1:8000"
```

## Run the Application Locally

Run these commands from the project root.

### 1. Start the FastAPI Backend

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Keep this terminal running.

### 2. Start the Streamlit Dashboard

Open a second terminal, activate the same virtual environment, and run:

```powershell
streamlit run streamlit_app.py
```

Open the local URL displayed in the terminal.

## Deployment Notes

* Deploy the FastAPI backend and Streamlit dashboard as separate services when required by your hosting platform.
* Set `MOODMENTOR_BACKEND_URL` on the Streamlit service to the reachable backend URL.
* Configure all required secrets in the hosting environment.
* The emotion model is downloaded from Hugging Face when its module loads. Initial startup may be slow and requires network access unless the model is cached.
* Verify memory and startup-time requirements for the selected hosting plan.
* Use persistent storage for databases and other data that must survive restarts. Confirm the application's database paths before deployment.
* The backend currently allows the browser origin `http://localhost:5173` through CORS. Update this configuration if a deployed browser-based frontend needs a different origin. Streamlit's server-side HTTP requests do not require browser CORS permission.
* Test authentication, model loading, API health, data deletion, and restart behavior before public release.

## Testing and Validation

Run the available tests and API checks before release. Record any failing or skipped tests, resolve deployment-specific configuration issues, and verify the application in the target hosting environment before declaring it production-ready.
