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

OpenSenseMap boxes may have multiple sensors. Identify temperature by:

1. `sensor.phenomenon === "Temperatur"` (German)
2. `sensor.unit === "°C"`
3. Fallback to `sensor.title` containing "temp" (case-insensitive)

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
