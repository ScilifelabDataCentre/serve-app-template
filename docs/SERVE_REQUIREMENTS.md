# SciLifeLab Serve requirement audit

**Last manual verification:** 2026-09-08  
**Serve version shown in the checked documentation:** 2026-07-29 (v5.2.0-beta)

This is the source map used to maintain the template and its generated `AGENTS.md` files. It separates **Serve requirements** from **template policy**.

## Common Serve requirements

| Topic | Current requirement used by this template | Source |
| --- | --- | --- |
| Packaging | Apps are hosted as Docker container images. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Public material | Data and code behind hosted apps need to be publicly available. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Port | Server port must be 3000–9999. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Compute | Default 2 vCPU / 4 GB RAM; up to 12 vCPU / 48 GB can be requested with demonstrated need. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Image architecture | Documentation builds with `--platform linux/amd64`. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Image tag | Every deployed version needs a unique tag; reusing a deployed tag does not update the app. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Image availability | Registry image must remain available; GHCR packages may need to be made public. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Storage | Configure mount paths in Project Settings → Storage, then select a mount path in the app form. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/), [Files](https://serve.scilifelab.se/docs/files/) |
| Managed database | Not provided. SQLite on project storage is allowed if it contains no user/sensitive data. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Accounts/state | User registration and user databases are not allowed; next visit should return to default state. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Sensitive data | Apps with sensitive data are not supported. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Logs | Only the past 24 hours are shown; logs are for debugging and must not track users. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Permissions | Private/Project are temporary; Link is suitable for review; apps should eventually be public. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Upload size | Generic app upload limit is 100 MB unless otherwise arranged. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |
| Source URL | App submission includes a source-code URL. | [Other app types](https://serve.scilifelab.se/docs/application-hosting/other/) |

The current file-management documentation should be rechecked whenever storage defaults change. This template's generated guidance states the current documented project storage model: a small initial allocation with automatic extension up to 5 GB when enabled, and larger requests through Serve support.

## FAIR and research-output recommendations

The Serve FAIR-applications page adds publication/reproducibility guidance. This template treats these as **recommendations**, separate from deployment requirements:

- deposit code/data in repositories supporting persistent identifiers and durable availability; the guide uses Zenodo as a general example and describes GitHub–Zenodo release archiving;
- use clear project structure, a README and launch instructions;
- use an appropriate software license and an appropriate data license for research data;
- lock language/package versions and specify data versions;
- provide citation guidance such as `CITATION.cff`;
- researchers must also consider applicable funder, institutional, open-access/open-data and ethical-approval obligations.

Source: https://serve.scilifelab.se/docs/application-hosting/fair/

## Framework profiles

### Gradio

Current guide assumptions encoded here:

- entry point: `main.py`;
- port: 7860;
- non-root user: UID 1000 in the documented Docker example;
- bind to `0.0.0.0` using `GRADIO_SERVER_NAME`;
- temp files should live in a writable application temp directory;
- current Serve guide warns that Gradio deployments have a known issue with Private/Project permissions, so use Link/Public;
- current guide notes upload/temp-file pressure around the 5 GB storage boundary and a 100 MB upload limit.

Source: https://serve.scilifelab.se/docs/application-hosting/gradio/

### Streamlit

Current guide assumptions encoded here:

- entry point: `app.py` in `WORKDIR`;
- port: 8501;
- documented Docker example creates UID 1000;
- server binds `0.0.0.0`;
- health endpoint: `/_stcore/health` is used by the template.

Source: https://serve.scilifelab.se/docs/application-hosting/streamlit/

### Dash

Current guide assumptions encoded here:

- example production server: Gunicorn;
- `app:server` application target;
- example port: 8000;
- server binds `0.0.0.0:8000`;
- Docker image is built for `linux/amd64`.

Source: https://serve.scilifelab.se/docs/application-hosting/dash/

**Template policy:** the Dash profile also runs as non-root UID 1000. The Dash page's example does not itself state that requirement; this template applies UID 1000 as a conservative common container policy.

### Shiny

Current guide assumptions encoded here:

- `rocker/shiny` / Shiny Server model;
- app copied under `/srv/shiny-server`;
- port: 3838;
- current documented Docker example normalizes the `shiny` user to UID 999 and runs as that user.

Source: https://serve.scilifelab.se/docs/application-hosting/shiny/

**Important conflict:** the general custom-app guide says non-root UID 1000 and a startup script in `WORKDIR`, while the current Shiny guide explicitly uses UID 999 and Shiny Server. The Shiny profile follows the Shiny-specific guide. If Serve resolves this discrepancy, change the profile and this audit together.

### Custom Python

The custom profile follows the general contract directly:

- UID 1000;
- startup script placed in `WORKDIR`;
- port within 3000–9999 (this starter uses 8000);
- binds to `0.0.0.0`;
- build for `linux/amd64`.

The starter uses FastAPI/Uvicorn only to provide a small working example; FastAPI is not a Serve requirement.

Source: https://serve.scilifelab.se/docs/application-hosting/other/

## Template-only policies

These are deliberate maintainability choices, not claims about mandatory Serve behavior:

- exact `==` pins in starter Python requirements;
- telemetry disabled where trivial;
- application source protected from Copier updates using `_skip_if_exists`;
- stdlib-only preflight validator;
- GHCR workflow emits timestamp + short SHA + workflow run/attempt tags and never publishes `latest`;
- Dash runs as UID 1000;
- FastAPI/Uvicorn used as the Custom Python starter.

## Drift review checklist

When the Serve documentation changes, compare at least:

1. allowed ports;
2. required runtime UID/startup mechanism;
3. `linux/amd64` requirement/examples;
4. registry visibility and tag rules;
5. storage/mount-path behavior and size limits;
6. account/state/database/sensitive-data restrictions;
7. logs and tracking restrictions;
8. upload limits;
9. permissions lifecycle;
10. each framework's port, entry point and startup command;
11. Gradio permission caveat;
12. Shiny UID exception.

Generated projects also include `scripts/docs_drift.py`, which performs a lightweight string check against the current documentation. It is an alarm, not a substitute for human review.
