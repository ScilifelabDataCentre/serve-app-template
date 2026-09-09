# AGENTS.md — agent contract for this multi-app template

This file is the first reference for an AI agent using this repository. It covers both the primary **Dockerize existing code** workflow and template maintenance. Generated Copier projects receive their own root `AGENTS.md` plus a framework-specific `app/AGENTS.md`.

## Default agent use: Dockerize existing user code from this template link

This is the **primary consumer workflow**. A user may give you only:

- a link to this template repository; and
- pasted application code, a local code folder, or a code repository URL.

They may simply say:

> Create a Dockerfile for my code based on this template repository.

The user does **not** need to mention SciLifeLab Serve, Copier, the framework, the port, the runtime user, or the deployment rules. By referring to this repository, they are asking you to apply the container contract encoded here.

### What you must do

1. **Inspect the supplied application first.** Read the main code, dependency files, README/run commands, local modules, assets/data, environment usage, and any existing Docker-related files. If the code is given by URL, inspect that repository rather than guessing from its name.
2. **Determine the app type only when the evidence is sufficient.** An explicit user statement wins. Otherwise inspect the code, dependencies, documented run command, and web entry point. If these give a clear answer, infer the app type. If they do not, ask one short clarification such as which kind of app the user wants or which command/file is supposed to launch the web app. Do not force an uncertain project into a profile just to avoid asking.

   | Profile | Strong signals |
   | --- | --- |
   | Gradio | `import gradio`, `gr.Interface`, `gr.Blocks`, `.launch()` |
   | Streamlit | `import streamlit as st`, `streamlit run`, substantial `st.*` usage |
   | Dash | `from dash import ...`, `Dash(...)`, callbacks, `dcc`/`html` |
   | Shiny | R code using `library(shiny)`, `shinyApp(...)`, Shiny UI/server objects |
   | Custom Python | FastAPI, Flask, or another Python web server not covered above |

   Do not classify from one incidental dependency if the repository clearly launches another framework. Use the actual web entry point and documented run command. Ask a targeted clarification whenever the evidence is weak, contradictory, or multiple launch targets remain plausible. Proceed without a question only when the framework/runtime is clear enough to choose the profile safely.
3. **Use the matching reference profile** under `profiles/<app-type>/Dockerfile`. These are plain, agent-readable mirrors of the Copier Dockerfile templates. Do not require the user to run Copier for an existing codebase.
4. **Adapt the Dockerfile to the user's repository instead of forcing the repository into this template's demo layout.** Adjust `COPY` source paths, dependency paths, entry-point mapping, required assets/models, and genuine OS packages. Preserve the user's application behavior.
5. **Keep the platform/container invariants from the selected profile.** In particular, keep the externally visible profile port, reachable bind address, expected non-root runtime identity, and production startup model. Build for `linux/amd64` when producing the image.
6. **Create only minimal supporting files or code adapters when necessary.** Examples:
   - If Streamlit source is `dashboard.py`, the Dockerfile may copy it into the required in-container `app.py` rather than reorganizing the user's repository.
   - If Dash code does not expose a Gunicorn-loadable WSGI callable, add the smallest safe adapter or minimal `server = app.server` change. Do not rewrite callbacks/business logic.
   - If no dependency metadata exists, derive the needed runtime packages from the code and verify compatible versions rather than inventing pins.
7. **Validate what you can.** Build and run the container when Docker is available. If not, statically verify the Dockerfile, startup command, paths, framework import target, port/bind, and dependencies.
8. **Report the inference.** Tell the user which app type you detected, which profile you used, what you adapted, and any assumption that could not be verified.

### What not to do

- Do not tell the user they must first create a Copier project.
- Do not require the user to know or state the framework when the code makes it clear. Conversely, do not pretend the framework is clear when it is not; ask a short clarification instead.
- Do not generate a Dockerfile from generic Docker memory while ignoring this repository's profile.
- Do not unnecessarily move or rename the user's source tree just to resemble the starter project. Map paths in the Dockerfile when that is sufficient.
- Do not silently choose when the app type or launch target is genuinely unclear; ask the smallest useful clarification.

### Role of Copier

Copier is **optional for this workflow**. Use it only when the user asks for a **new repository/project generated from this template**. Then Copier selects a clean framework-specific starter and update metadata.

So there are three distinct jobs:

1. **Dockerize existing code using this repository as reference** — default consumer use; no Copier required.
2. **Generate a new starter repository** — use Copier.
3. **Maintain this template repository** — edit `copier.yml`, `template/`, tests, profiles, or shared documentation.

When changing a Dockerfile profile as a maintainer, update both its Copier template and the matching plain reference under `profiles/`; tests enforce that the default reference mirrors stay synchronized.

## First principle

Do not guess SciLifeLab Serve requirements. Before changing deployment, Docker, validation, CI, storage, permissions, or framework defaults, check the current Serve documentation and update `docs/SERVE_REQUIREMENTS.md` when the contract changes.

Source priority:

1. Current framework-specific Serve guide for framework-specific behavior.
2. Current Serve "Other app types" guide for the cross-framework/custom contract.
3. Current Serve file-management guide for persistent storage.
4. Current Serve FAIR-application guidance for publication/reproducibility recommendations.
5. This repository's template policy where Serve is silent.

If sources disagree, do not silently normalize them. Record the conflict, keep the framework-specific exception explicit, and make validation profile-aware.

## Verified Serve contract

Documentation was last manually audited on **2026-09-08** against Serve version **2026-07-29 (v5.2.0-beta)**.

Cross-framework rules to preserve in generated projects:

- Apps are deployed as Docker container images.
- App code/data/model material required by the hosted app must be publishable; Serve requires code and data behind apps to be publicly available.
- The application server must use an allowed port in the range 3000–9999.
- Build/publish for `linux/amd64`.
- Use a new, unique container image tag for every deployment; never rely on a mutable `latest` tag.
- The container image must remain available while Serve hosts the app. For GHCR, make the package public.
- Do not host personal or sensitive data.
- Do not implement user registration or a user database. A returning visitor should see the default application state.
- Serve does not provide a managed database. File-based SQLite can live on project storage only when it contains no user/personal/sensitive data.
- Project storage is mounted through paths configured in Project Settings → Storage.
- Serve application logs cover the previous 24 hours and are for debugging, not user tracking.
- Private/Project permissions are temporary; Link is suitable for unlisted review; apps are expected to become Public.
- Generic app upload limit is 100 MB unless Serve agrees otherwise.
- Default compute is 2 vCPU and 4 GB RAM; larger allocations can be requested with demonstrated need.

Framework profile table:

| Profile | Entry point | Port | Runtime identity | Important startup rule |
| --- | --- | ---: | ---: | --- |
| Gradio | `app/main.py` | 7860 | UID 1000 | bind `0.0.0.0`; no share/auth; manage Gradio temp files |
| Streamlit | `app/app.py` | 8501 | UID 1000 | `app.py` in WORKDIR; bind `0.0.0.0` |
| Dash | `app/app.py` | 8000 | UID 1000 **template policy** | expose `server`; run Gunicorn bound to `0.0.0.0:8000` |
| Shiny | `app/app.R` | 3838 | UID 999 | use Shiny Server; current Shiny guide explicitly normalizes `shiny` to UID 999 |
| Custom Python | `app/app.py` | 8000 | UID 1000 | startup script must be in WORKDIR |

### Known documentation exception

The general custom-app guide says non-root UID 1000 and a startup script in `WORKDIR`. The current Shiny guide explicitly uses the `shiny` user with UID 999 and Shiny Server. Preserve UID 999 for the Shiny profile unless Serve updates/clarifies the guide. Do not make a global UID assertion that breaks Shiny.

The current Dash guide demonstrates Gunicorn on port 8000 but does not explicitly show a non-root user. This template uses UID 1000 for Dash as a conservative shared security/compatibility policy; label it as template policy rather than a Dash-page quotation.

### Gradio exception

The current Gradio guide reports a known deployment bug with Private and Project permissions. Generated Gradio deployment guidance must recommend Link or Public until the Serve documentation says otherwise.


## FAIR/reproducibility guidance to preserve as recommendations

Do not turn these into hard container preflight failures; the current Serve FAIR page presents them as research-output recommendations:

- publish/archive code and data in a repository that supports persistent identifiers and long-term availability; Serve gives Zenodo as a general example and describes GitHub–Zenodo release archiving;
- keep a useful README with structure and launch instructions;
- apply an appropriate software license, and a separate appropriate data license where research data is distributed;
- lock language/package versions and identify the data version used by each app release;
- provide citation guidance such as `CITATION.cff`;
- project owners remain responsible for applicable funder, institutional and ethical requirements.

## Template policy where Serve is silent

- Pin starter runtime dependencies exactly with `==` so generated examples are reproducible.
- Never put credentials, API keys, tokens, private keys, `.env` files, or secrets in the starter.
- Disable framework analytics/telemetry where a simple documented switch exists.
- Keep starter applications deliberately small. Do not add demo databases, login systems, tracking, external infrastructure, or large assets.
- Use only standard-library code in `scripts/preflight.py` so users can validate before installing app dependencies.

## Change procedure

When changing a profile:

1. Re-read the relevant current Serve framework page and common requirements.
2. Update `docs/SERVE_REQUIREMENTS.md` if the source contract changed.
3. Update the generated root `AGENTS.md` and the profile `app/AGENTS.md` together.
4. Update `scripts/preflight.py` if a machine-checkable invariant changed.
5. Update `DEPLOY.md` if a Serve form/deployment step changed.
6. Update CI if the image build/run contract changed.
7. Run `python -m pytest -q` and `python tests/render_smoke.py`.
8. If Copier is installed, run `python tests/copier_smoke.py`.
9. If Docker is available, build and smoke-run each changed profile for `linux/amd64`.

Do not add a framework by scattering `if framework == ...` through every common file. Add a profile-specific Dockerfile/app skeleton and keep shared rules shared.

## Authoritative references

- Serve docs: https://serve.scilifelab.se/docs/
- Other app types: https://serve.scilifelab.se/docs/application-hosting/other/
- Gradio: https://serve.scilifelab.se/docs/application-hosting/gradio/
- Streamlit: https://serve.scilifelab.se/docs/application-hosting/streamlit/
- Dash: https://serve.scilifelab.se/docs/application-hosting/dash/
- Shiny: https://serve.scilifelab.se/docs/application-hosting/shiny/
- File management: https://serve.scilifelab.se/docs/files/
- FAIR applications: https://serve.scilifelab.se/docs/application-hosting/fair/
- Copier configuration: https://copier.readthedocs.io/en/stable/configuring/
- Copier updates: https://copier.readthedocs.io/en/stable/updating/
