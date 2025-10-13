[![Dynamic DevOps Roadmap](https://img.shields.io/badge/Dynamic_DevOps_Roadmap-559e11?style=for-the-badge&logo=Vercel&logoColor=white)](https://devopsroadmap.io/getting-started/)
[![Community](https://img.shields.io/badge/Join_Community-%23FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://newsletter.devopsroadmap.io/subscribe)
[![Telegram Group](https://img.shields.io/badge/Telegram_Group-%232ca5e0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/DevOpsHive/985)
[![Fork on GitHub](https://img.shields.io/badge/Fork_On_GitHub-%2336465D?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DevOpsHiveHQ/devops-hands-on-project-hivebox/fork)

# HiveBox - DevOps End-to-End Hands-On Project

<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox" style="display: block; padding: .5em 0; text-align: center;">
    <img alt="HiveBox - DevOps End-to-End Hands-On Project" border="0" width="90%" src="https://devopsroadmap.io/img/projects/hivebox-devops-end-to-end-project.png" />
  </a>
</p>

> [!TIP]
> If you are looking for the full roadmap, including this project, go back to the [getting started](https://devopsroadmap.io/getting-started) page.

This repository is the starting point for [HiveBox](https://devopsroadmap.io/projects/hivebox/), the end-to-end hands-on project.

You can fork this repository and start implementing the [HiveBox](https://devopsroadmap.io/projects/hivebox/) project. HiveBox project follows the same Dynamic MVP-style mindset used in the [roadmap](https://devopsroadmap.io/).

The project aims to cover the whole Software Development Life Cycle (SDLC). That means each phase will cover all aspects of DevOps, such as planning, coding, containers, testing, continuous integration, continuous delivery, infrastructure, etc.

Happy DevOpsing ♾️

<br/>
<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox/" imageanchor="1">
    <img src="https://img.shields.io/badge/Get_Started_Now-559e11?style=for-the-badge&logo=Vercel&logoColor=white" />
  </a><br/>
</p>

---

## Implementation

### Phase 1

- [x] Fork HiveBox repo
- [x] Create Kanban board
- [x] Save openSenseMap ids
- [x] Write implementation doc

### Phase 2

- [x] Create version.sh that outputs version
- [x] Choose semantic version 0.1.0 as reccomended at [Semantic Versioning 2.0.0 | Semantic Versioning](https://semver.org/)
- [x] Create a Dockerfile
- [x] Test locally
- [x] Write how-to-test in documentation

#### How to test

```bash
git clone https://github.com/Aldeimeter/devops-hands-on-project-hivebox.git

cd devops-hands-on-project-hivebox

docker build -t hivebox:0.1.0 .

docker run hivebox:0.1.0
```

### Phase 3

#### Preparation p.1

##### Why choose Ruff over Pylint?

**Primary reason:** Ruff is significantly faster than Pylint.

However, Pylint is more comprehensive in its analysis. My approach:

- **Ruff:** For quick, real-time feedback during development
- **Pylint:** For thorough analysis in CI/CD pipelines and periodic manual checks

##### Why choose uv over pip?

**Context:** Running Arch Linux (btw) with Neovim as my editor.

**Practical benefits of uv:**

- Simpler dependency installation and virtual environment management on Arch
- Faster dependency resolution compared to pip
- Better developer experience for running apps in virtual environments
- Native support for dependency groups (production vs dev dependencies)

##### Steps

- [x] Install [Hadolint CLI](https://github.com/hadolint/hadolint)
- [x] Configure Hadolint in neovim
- [x] Install ~~Pylint~~ [Ruff](https://docs.astral.sh/ruff/)
- [x] Configure Ruff in neovim
- [x] Install uv
- [x] Init uv project

#### Security Hardening

- [x] Configure OSSF Scorecard workflow for supply-chain security
- [x] Set up Dependabot for automated dependency updates (Python + Docker)
- [x] Pin GitHub Actions to SHA hashes
- [x] Pin Docker base images with SHA256 digests
- [x] Configure least-privilege token permissions in CI workflows
- [x] Document security posture and practices

#### Preparation p.2

##### FastApi vs Flask

I'd prefer to go with [FastApi](https://fastapi.tiangolo.com/) as I've used it in the past.

##### API Architecture

**Objective:** Fetch N openSenseMap boxes and calculate average temperature from sensors with data no older than 1 hour.

**Configuration:**

- Store senseBox IDs in `sensebox_ids.txt` (one ID per line)
- Decouple box IDs from source code for easy updates

**API Endpoint:** `GET https://api.opensensemap.org/boxes/:senseBoxId`

Returns full box metadata including latest measurements for all sensors.

**Implementation Flow:**

```
For each box ID in configuration:
1. Fetch box data from OpenSenseMap API
2. Find temperature sensor(s):
- Match by phenomenon: "Temperatur"
- OR match by unit: "°C"
3. Validate data freshness:
- Parse lastMeasurement.createdAt timestamp
- Check if timestamp is within last 1 hour
4. If valid:
- Extract temperature value
- Add to calculation pool
5. If invalid:
- Skip this box (log reason)

Calculate average temperature from all valid readings
```

**Data Validation Rules:**

Include reading if:

- Box has temperature sensor
- `lastMeasurement.createdAt` is within last 60 minutes
- Temperature value is not null/missing

Exclude reading if:

- No temperature sensor on box
- Data older than 1 hour
- Temperature value is null/empty
- API request fails

**Response Structure:**

```json
{
  "average_temperature": 23.5,
  "unit": "°C",
  "timestamp": "2025-10-07T14:30:00Z",
  "statistics": {
    "boxes_checked": 3,
    "valid_readings": 2,
    "excluded_boxes": 1
  },
  "excluded_reasons": [
    {
      "box_id": "abc123",
      "reason": "data_too_old",
      "last_measurement": "2025-10-07T12:00:00Z"
    }
  ]
}
```

**Error Handling:**

- **No valid readings:** Return HTTP 503 or 200 with null average + explanation
- **API failures:** Skip box if request fails
- **Rate limiting:** Implement delays between requests if needed
- **Invalid box IDs:** Log warning, continue with remaining boxes

**Temperature Sensor Identification:**

OpenSenseMap boxes may have multiple sensors. Identify air temperature by:

1. `sensor.phenomenon === "Temperatur"` (German)

##### Testing

I want to follow **Test-Driven Development** (TDD) principles for this project.

**Testing Framework Setup:**

- FastAPI provides excellent testing support via `pytest` and `httpx` using `TestClient`
- Test dependencies are added to the `[dependency-groups]` dev group in `pyproject.toml`
- Using `uv` dev dependencies keeps the final Docker image smaller (dev deps excluded from production)
- Created initial test to verify pytest integration works correctly

##### Steps

- [x] Init FastApi project
- [x] Look into [openSenseMap API](https://docs.opensensemap.org/)
- [x] Add testing framework
- [x] Test testing framework

#### Code implementation

##### /version Endpoint Architecture

**Objective:** Return the application version from environment configuration

**Project Structure:**

```
hivebox-python/
├── app/
│   ├── __init__.py
│   ├── config.py            # Configuration management (reads .env)
│   ├── routers/             # API route modules
│   │   ├── __init__.py
│   │   └── version.py       # /version endpoint
├── tests/                   # Test modules
│   ├── __init__.py
│   └── test_version.py      # Tests for /version endpoint
├── .env                     # Environment variables (not in git)
├── .env.example             # Example env file (in git)
├── pyproject.toml           # Project metadata and dependencies
└── main.py                  # Application factory and FastAPI instance
```

**Architectural Principles:**

1. **Separation of Concerns:**
   - `app/config.py` - Configuration management (environment variables)
   - `app/routers/version.py` - Route handlers (API layer)
   - `tests/test_version.py` - Test suite

2. **Modular Design:**
   - Use FastAPI's `APIRouter` for route organization
   - Each router handles a specific domain (version, sensors, health, etc.)
   - Routers are included in main app via `app.include_router()`

3. **Configuration as Code:**
   - Version stored in `.env` file (12-factor app principle)
   - Easy to update without code changes
   - Works well with Docker/Kubernetes deployments

**Configuration Management:**

Use `pydantic-settings` (included with FastAPI) to read environment variables:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_version: str = "0.0.0"  # default value


settings = Settings()
```

**.env file:**

```
APP_VERSION=0.2.0
```

**Test Cases for /version endpoint:**

1. **Happy Path:**
   - GET /version returns 200 status code
   - Version is the same as in .env
   - Response structure is `{"version": "X.Y.Z"}`

**API Response Example:**

```json
{
  "version": "0.2.0"
}
```

##### /temperature Endpoint Architecture

**Objective:** Return current average temperature based on all senseBox data no older than 1 hour

**Project Structure Updates:**

```
hivebox-python/
├── app/
│   ├── __init__.py
│   ├── config.py                # Configuration management (reads .env)
│   ├── routers/                 # API route modules
│   │   ├── __init__.py
│   │   ├── version.py           # /version endpoint
│   │   └── temperature.py       # /temperature endpoint
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── opensensemap.py      # OpenSenseMap API client
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py
│   │   └── temperature.py       # Temperature response models
├── tests/                       # Test modules
│   ├── __init__.py
│   ├── test_version.py          # Tests for /version endpoint
│   └── test_temperature.py      # Tests for /temperature endpoint
├── sensebox_ids.txt             # SenseBox IDs (one per line)
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example env file (in git)
├── pyproject.toml               # Project metadata and dependencies
└── main.py                      # Application factory and FastAPI instance
```

**Architectural Layers:**

1. **Router Layer (`app/routers/temperature.py`):**
   - Handles HTTP request/response
   - Delegates business logic to service layer
   - Returns formatted API response

2. **Service Layer (`app/services/opensensemap.py`):**
   - Fetches data from OpenSenseMap API
   - Identifies temperature sensors
   - Validates data freshness (within 1 hour)
   - Calculates average temperature
   - Handles API failures gracefully

3. **Model Layer (`app/models/temperature.py`):**
   - Pydantic models for response validation
   - Type safety for temperature data structures

**Data Flow:**

```
Application Startup:
- Read sensebox_ids.txt once
- Store IDs in memory (config.py Settings)

Request Flow:
1. Client → GET /temperature
2. Router → Service Layer
3. Service gets box IDs from in-memory config
4. For each box ID:
   - Fetch box data from OpenSenseMap API
   - Identify temperature sensor(s)
   - Validate data freshness (<1 hour)
   - Extract valid temperature values
5. Calculate average from valid readings
6. Build response with statistics
7. Router → Client (JSON response)
```

**Temperature Sensor Identification Strategy:**

Simple exact match:

- `sensor.title === "Temperatur"` (air temperature only, excludes soil/ground temperature)

**Data Validation Rules:**

Include reading if:

- Box has temperature sensor
- `lastMeasurement.createdAt` is within last 60 minutes
- Temperature value is not null/missing

Exclude reading if:

- No temperature sensor on box
- Data older than 1 hour
- Temperature value is null/empty
- API request fails

**API Response Structure:**

```json
{
  "average_temperature": 23.5,
  "unit": "°C",
  "timestamp": "2025-10-09T14:30:00Z",
  "statistics": {
    "boxes_checked": 3,
    "valid_readings": 2,
    "excluded_boxes": 1
  },
  "excluded_reasons": [
    {
      "box_id": "5eba5fbad46fb8001b799786",
      "reason": "data_too_old",
      "last_measurement": "2025-10-09T12:00:00Z"
    }
  ]
}
```

**Error Handling:**

- **No valid readings:** If all senseBoxes have stale data (>1 hour old) or no temperature sensors, return HTTP 200 with `average_temperature: null` and explain why in the response (e.g., "No valid temperature data available within the last hour")
- **API failures:** If fetching data from OpenSenseMap fails for one box (network error, timeout, 500 error), skip that box but continue processing the remaining boxes. Don't fail the entire request.
- **Invalid box IDs:** If a senseBox ID doesn't exist (404), log a warning and exclude it from the calculation. Continue with valid boxes.
- **Empty configuration:** If `sensebox_ids.txt` is empty or missing, return HTTP 503 (Service Unavailable) since the service can't function without configured boxes.

**Test-Driven Development Approach:**

Test cases organized by category:

1. Happy path tests
2. Data freshness validation tests
3. Sensor identification tests
4. Data validation tests
5. Multiple boxes scenarios
6. Edge cases (no valid readings, single reading)
7. API failure handling tests
8. Calculation precision tests
9. Statistics accuracy tests
10. Timestamp validation tests

All tests implemented before endpoint code

#### Docker Updates

- [x] Refactor Dockerfile to multi-stage build
- [x] Add .dockerignore for optimized builds
- [x] Implement Docker best practices (non-root user, labels, security)
- [x] Create separate test and production stages

**Multi-stage Dockerfile Architecture:**

- **Base stage:** Shared dependencies and configuration
- **Test stage:** Includes dev dependencies and test suite
- **Production stage:** Minimal, security-hardened image with non-root user

**Build and test:**

Run tests in Docker:

```bash
docker build --target test -t hivebox:test .
docker run --rm hivebox:test
```

Build production image:

```bash
docker build --target production -t hivebox:0.2.0 .
docker run -p 8000:80 hivebox:0.2.0
```

Quick production build (default):

```bash
docker build -t hivebox:latest .
docker run -p 8000:80 hivebox:latest
```

#### CI/CD Pipeline

**GitHub Actions Workflow:**

Implemented comprehensive CI/CD pipeline in `.github/workflows/ci.yml` with the following stages:

**1. Lint Job:**

- Python code linting with `pylint`
- Dockerfile linting with `hadolint`
- Runs on Python 3.13 with `uv` for dependency management
- Uses GitHub Actions cache for faster dependency installation

**2. Build & Test Job:**

- Builds Docker test image with all dev dependencies
- Runs unit tests inside Docker container
- Builds production Docker image
- Starts production container and runs integration tests
- Tests `/version` endpoint to verify correct version (0.2.0)
- Uses Docker layer caching (GitHub Actions cache) for faster builds
- Cleans up containers after tests

**Workflow Triggers:**

- Push to `main` branch
- Pull requests to `main` branch

**Pipeline Benefits:**

- Early detection of code quality issues
- Dockerfile best practices enforcement
- Automated testing in isolated Docker environment
- Integration testing with actual container
- Fast builds with multi-layer caching

**Local Testing:**

Run the same checks locally before pushing:

```bash
# Lint Python code
cd hivebox-python
uv run pylint app/ main.py

# Lint Dockerfile
hadolint Dockerfile

# Run tests in Docker
docker build --target test -t hivebox:test .
docker run --rm hivebox:test

# Test production container
docker build --target production -t hivebox:prod .
docker run -d --name hivebox-test -p 8000:80 hivebox:prod
curl http://localhost:8000/version
docker stop hivebox-test && docker rm hivebox-test
```

#### Security and Dependency Management

**OSSF Scorecard Integration:**

Implemented OpenSSF Scorecard for supply-chain security monitoring in `.github/workflows/scorecard.yml`:

- **Automated Security Analysis:** Runs weekly and on every push to `main` branch
- **Supply-Chain Security Checks:** Evaluates 18+ security checks including:
  - Branch protection configuration
  - Dependency update tools
  - Code review practices
  - Dangerous workflow patterns
  - Token permissions
  - Pinned dependencies
- **SARIF Integration:** Results uploaded to GitHub Security tab for visibility
- **Public Badge:** Project security posture visible via OpenSSF badge

**Dependabot Configuration:**

Automated dependency updates configured in `.github/dependabot.yml`:

- **Python Dependencies:** Weekly updates for `uv`-managed packages in `/hivebox-python`
- **Docker Base Images:** Weekly updates for Docker base images
- **Automatic PRs:** Creates pull requests for security patches and version updates
- **Ecosystem Coverage:** Monitors both application dependencies and container images

**Action and Image Pinning:**

Enhanced CI/CD security by pinning all external dependencies to SHA hashes:

- **GitHub Actions:** All actions pinned to specific SHA commits (e.g., `actions/checkout@08eba0b2...`)
- **Docker Base Images:** Python and other base images include SHA256 digests
- **Supply Chain Integrity:** Prevents unauthorized modifications to CI/CD dependencies
- **Automated Updates:** Dependabot manages updates to pinned versions

**Security Benefits:**

- Automated vulnerability detection and patching
- Supply-chain attack prevention through pinned dependencies
- Continuous security posture monitoring
- Proactive dependency maintenance
- GitHub Security Dashboard integration

**CI Token Permissions:**

Implemented least-privilege token permissions in GitHub Actions:

- **Default Read-Only:** `permissions: contents: read` in CI workflow
- **Specific Grants:** Security events and ID tokens only where needed (Scorecard workflow)
- **Reduced Attack Surface:** Minimizes potential damage from compromised workflows
