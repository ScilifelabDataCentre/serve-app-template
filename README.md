
# SciLifeLab Serve multi-app template

This repository helps you turn an idea or existing code into a web application that can be deployed on [SciLifeLab Serve](https://serve.scilifelab.se/). You can also use AI agents, coding assistants, or chatbots to help with development.

Supported application types:

- Gradio
- Streamlit
- Dash
- Shiny (R)
- Custom Python web apps, with FastAPI as the starter example

**You do not need to know or specify the application type. If you use a chatbot, AI or coding assistant, give it the prompt(s) mentioned below. It will create the application for you.**

---

## Deploy your application on [SciLifeLab Serve](https://serve.scilifelab.se/) in three quick steps!

### Step 1. Choose how you want to start

#### a. I want to use a coding assistant, AI, or chatbot to create the application

##### i. I only have an idea

Give this prompt with your idea to a coding assistant, AI or chatbot:

```text
Use this repository as the reference:
https://github.com/ScilifelabDataCentre/serve-template-multi-app

Create a small working web application for this idea:

<DESCRIBE YOUR IDEA>

Create all files needed to run it locally with Docker and deploy it through
GitHub to SciLifeLab Serve.

Keep the application simple. If you need more information about what I want,
ask me before making an important assumption.

Also create a README with the exact commands I should run to test and deploy it.
```
---

##### ii. I already have some code

Your code can be:

* a GitHub repository;
* a local directory;
* one or more files; or
* code pasted directly into the conversation.

Give this prompt with your code to your coding assistant, AI, or chatbot:

```text
Use this repository as the reference:
https://github.com/ScilifelabDataCentre/serve-template-multi-app

Here is my existing code:

<REPOSITORY LINK, LOCAL DIRECTORY, CODE PASTED HERE, OR FILES ATTACHED>

Turn this into a working web application that I can run with Docker and deploy
to SciLifeLab Serve.

Preserve my existing application logic.

Inspect the code and decide the appropriate setup yourself. If the code does
not make the intended application clear, ask me what I want the application
to do before deciding.

Create all files needed to run it locally with Docker and deploy it through
GitHub to SciLifeLab Serve.

Keep the application simple. If you need more information about what I want,
ask me before making an important assumption.

Also create a README with the exact commands I should run to test and deploy it.
```


The coding assistant, AI, or chatbot should create a complete project containing the application code, dependencies, Dockerfile, GitHub workflow, and deployment instructions.

---

#### b. I want to create a starter project to code by myself

Use this option if you want a clean starter repository template and plan to write or copy the application code yourself.

Install Copier:

```bash
pipx install copier
```

Create a new project:

```bash
copier copy --vcs-ref v0.1.0 \
  https://github.com/ScilifelabDataCentre/serve-template-multi-app \
  my-apps
```

Copier will ask a few setup questions and create the new directory:

```text
my-app/
├── app/
├── Dockerfile
├── README.md
├── AGENTS.md
├── .github/
├── scripts/
└── ...
```

Then:

```bash
cd my-app
```

Put or write your application code inside:

```text
app/
```

Follow the generated `README.md` for any application-specific requirements.

If you are developing the template itself locally, you can test it without GitHub:

```bash
cd serve-template-multi-app
copier copy . ../my-app
```

Your complete project should contain the application code, dependencies, Dockerfile, GitHub workflow, and deployment instructions.

---

### Step 2. Build the Docker image using GitHub

By now you should have your application codes ready in a project repository. Follow the generated project's README. The common test and deployment steps are also described there. Execute them. If all okay then follow the next steps.


#### a. Put the project on GitHub

Create an empty GitHub repository for your application.

Then, from your application project directory:

```bash
git init
git add .
git commit -m "Initial application"
git branch -M main
git remote add origin https://github.com/<YOUR-USER-OR-ORG>/<YOUR-REPOSITORY>.git
git push -u origin main
```


#### b. Build the Docker image

Projects created from this template include a GitHub Actions workflow.

After pushing to `main`:

1. Open your repository on GitHub.
2. Open **Actions**.
3. Wait for the build and container tests to finish successfully.
4. Open the generated package under **Packages**.
5. Copy the exact `ghcr.io/...:<tag>` image name.

The image will look similar to:

```text
ghcr.io/<organization>/<repository>:<unique-tag>
```

#### c. Make the container image public

[SciLifeLab Serve](https://serve.scilifelab.se/) must be able to download the image.

On GitHub:

**Package → Package settings → Change visibility → Public**

---

### Step 3. Deploy on [SciLifeLab Serve](https://serve.scilifelab.se/)

Once the Docker image is available publicly:

1. Sign in to [SciLifeLab Serve](https://serve.scilifelab.se/).
2. Create a project, or open an existing project.
3. Follow the generated application's README for the appropriate app creation form.
4. Paste the public GHCR image address into the **Image** field.
5. Enter the port shown in the generated README or Dockerfile.
6. Add the GitHub repository URL as the **Source code URL**.
7. Fill in the title, description, permissions, and other application information.
8. Create the app.

The image value should look similar to:

```text
ghcr.io/<organization>/<repository>:<unique-tag>
```

Congratulations! Your application is now published and open for all!

---

## (Optional) Run your application locally

The generated project and codes should contain the exact command and port for your application. Follow its README in case it differs from the example below.

#### a. Install Docker

Install and start **Docker Desktop** before continuing.

Docker Desktop installation: `DOCKER_DESKTOP_INSTALL_LINK`

#### Build the image

From the directory containing the `Dockerfile`:

```bash
docker build --platform linux/amd64 -t my-app:local .
```

Check that the image exists:

```bash
docker image ls
```

#### Run the image

The generated README should tell you which port the application uses.

Run:

```bash
docker run --rm -p <PORT>:<PORT> my-app:local
```

For example, if the application uses port `8000`:

```bash
docker run --rm -p 8000:8000 my-app:local
```

Then open:

```text
http://localhost:<PORT>
```

in your browser.

Stop the application with `Ctrl+C`.

---

## Repository structure and design

```text
.
├── README.md                  # Main guide
├── AGENTS.md                  # Detailed adaptation and maintenance rules
├── copier.yml                 # Copier questions and framework settings
├── profiles/                  # Plain Dockerfile references
│   ├── gradio/
│   ├── streamlit/
│   ├── dash/
│   ├── shiny/
│   └── custom/
├── template/                  # Files generated by Copier
├── tests/                     # Template checks
├── scripts/                   # Maintenance checks
└── docs/
    └── SERVE_REQUIREMENTS.md  # Serve requirements and source audit
```

Specialized [SciLifeLab Serve](https://serve.scilifelab.se/) products such as TissUUmaps and Depictio are intentionally outside this template because they have separate deployment workflows.

### Adding another framework

1. Confirm it fits the current [SciLifeLab Serve](https://serve.scilifelab.se/) container requirements.
2. Record its entry point, startup command, port, runtime user, architecture, storage needs and health check.
3. Add `profiles/<framework>/Dockerfile`.
4. Add the framework to `copier.yml`.
5. Add its Copier Dockerfile and starter application files.
6. Add framework-specific validation and tests.
7. Update `AGENTS.md` and `docs/SERVE_REQUIREMENTS.md`.

---

## Development, contribution and release

1. read `AGENTS.md`;
2. verify any changed [SciLifeLab Serve](https://serve.scilifelab.se/) assumption against the current documentation;
3. update `docs/SERVE_REQUIREMENTS.md` when needed;
4. run the template tests and render checks; and
5. build affected profiles for `linux/amd64` when Docker is available.

```bash
python -m pytest -q
python tests/render_smoke.py
python tests/copier_smoke.py
```

For a generated project:

```bash
python scripts/preflight.py --strict
python -m unittest discover -s tests -v
docker build --platform linux/amd64 -t serve-template-smoke:test .
```

### Release sequence

1. Verify the current [SciLifeLab Serve](https://serve.scilifelab.se/) documentation.
2. Update `docs/SERVE_REQUIREMENTS.md` if needed.
3. Run the tests and render checks.
4. Bump `template_version` in `template/.serve-template.json.jinja`.
5. Update `CHANGELOG.md`.
6. Commit and merge the release state.
7. Create and push a PEP 440-compatible tag such as `v0.2.0`.
8. Generate one project from the released Git URL and run an end-to-end Docker smoke test.

Versioned Git tags are important because Copier uses them when comparing template versions during `copier update`.

---

## Security and data handling

- Do not commit credentials, tokens or secrets.
- Do not report credentials, sensitive data or exploitable security details in public issues.
- Generated applications are intended for [SciLifeLab Serve](https://serve.scilifelab.se/)'s public application model.
- Do not include personal or sensitive data, user databases or committed credentials in generated applications.
- For platform-specific security or data-handling questions, follow the current [SciLifeLab Serve](https://serve.scilifelab.se/) documentation and use the [SciLifeLab Serve](https://serve.scilifelab.se/) team's published support channel when clarification is needed.

## References and license

---

- [SciLifeLab Serve documentation](https://serve.scilifelab.se/docs/)
- [Copier documentation](https://copier.readthedocs.io/)

The current [SciLifeLab Serve documentation](https://serve.scilifelab.se/docs/) is the source of truth for deployment requirements. `docs/SERVE_REQUIREMENTS.md` records the rules and framework-specific exceptions used by this template.

License: MIT.
