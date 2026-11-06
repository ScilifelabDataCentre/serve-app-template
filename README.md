
# SciLifeLab Serve app template

This repository provides a template that allows you to start creating a application that can be published on [SciLifeLab Serve](https://serve.scilifelab.se/). This template is geared towards those who intend to use AI agents, coding assistants, or chatbots to help with development of the application but it is also suitable in case you are planning to develop the application yourself.

Supported application types:

- Gradio
- Streamlit
- Dash
- Shiny (R)
- Custom Python web apps, with FastAPI as the starter example

**You do not need to know or specify the application type. If you use a chatbot, AI agents or coding assistant, give it the prompt(s) mentioned below. It will create the application for you. However, please keep in mind that as an application creator you are always responsible for the accuracy of the application-content and security (regardless of which tools you use).**

---

## Publish your application on [SciLifeLab Serve](https://serve.scilifelab.se/) in three quick steps!

### Step 1. Choose how you want to start

#### a. I want to use a coding assistant, AI agents, or chatbot to create the application

**i. I only have an idea**

> ⚠️ **“I only have an idea” means the scientific task is well-defined, but the code is not yet written. AI must not decide the research methodology.**

Give this prompt with your idea (see `TO-DO:`) to a coding assistant, AI agents or chatbot:

```text
Use this repository as the reference:
https://github.com/ScilifelabDataCentre/serve-app-template

Create a small working web application for this idea:

<TO-DO: DESCRIBE YOUR IDEA>

Create all files needed to run it locally with Docker and deploy it through
GitHub to SciLifeLab Serve.

Keep the application simple. If you need more information about what I want,
ask me before making an important assumption.

Also create a README with the exact commands I should run to test and deploy it.
```
---

**ii. I already have some code**

Your code can be:

* a GitHub repository;
* a local directory;
* one or more files; or
* code pasted directly into the conversation.

Give this prompt with your code (see `TO-DO:`) to your coding assistant, AI agents, or chatbot:

```text
Use this repository as the reference:
https://github.com/ScilifelabDataCentre/serve-app-template

Here is my existing code:

<TO-DO: REPOSITORY LINK, LOCAL DIRECTORY, CODE PASTED HERE, OR FILES ATTACHED>

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


The coding assistant, AI agents, or chatbot should create a complete project containing the application code, dependencies, Dockerfile, GitHub workflow, and deployment instructions.

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
  https://github.com/ScilifelabDataCentre/serve-app-template \
  <YOUR-APPLICATION-NAME>
```

Copier will ask a few setup questions and create the new directory:

```text
<YOUR-APPLICATION-NAME>/
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
cd <YOUR-APPLICATION-NAME>
```

Put or write your application code inside:

```text
app/
```

Follow the generated `README.md` for any application-specific requirements.

If you are developing the template itself locally, you can test it without GitHub:

```bash
git clone https://github.com/ScilifelabDataCentre/serve-app-template.git
cd serve-app-template
copier copy . ../<YOUR-APPLICATION-NAME>
```

Your complete project should contain the application code, dependencies, Dockerfile, GitHub workflow, and deployment instructions.

---

### Step 2. Choose how you want to build the Docker image

By now you should have your application code ready in a project repository. Follow the generated project's README. The common test steps are described there. Execute them. If all are okay then follow the next steps.


#### a. Build the Docker image locally using Docker Desktop

The generated project and codes should contain the exact command and port for your application. Follow its README in case it differs from the example below.

**Install Docker**

Install and start **Docker Desktop** before continuing.

[Docker Desktop installation guide](https://docs.docker.com/get-started/get-docker/)

**Build the image**

Run in a terminal from the directory containing the `Dockerfile`:

```bash
docker build --platform linux/amd64 -t <YOUR-APPLICATION-NAME>:<VERSION-TAG> .
```

Check that the image exists:

```bash
docker image ls
```

**Run the image**

The generated README should tell you which port the application uses.

Run:

```bash
docker run --rm -p <PORT>:<PORT> <YOUR-APPLICATION-NAME>:<VERSION-TAG>
```

For example, if the application uses port `8000`:

```bash
docker run --rm -p 8000:8000 <YOUR-APPLICATION-NAME>:<VERSION-TAG>
```

Then open:

```text
http://localhost:8000>
```

in your browser. Test it.

Stop the application with `Ctrl+C` in your terminal.

Finally push to the public registry:

```bash
docker push <YOUR-ORGANIZATION OR YOUR-ACCOUNT-NAME>/<YOUR-APPLICATION-NAME>:<VERSION-TAG>
```

---

#### b. Build the Docker image using GitHub Actions workflow


**Put the project on GitHub**

Make sure that `git` is installed. See [installation guide](https://git-scm.com/install/).

Create an empty GitHub repository for your application. Make sure to set it `public`.

Then, from your application project directory, in a terminal, run:

```bash
git init
git add .
git commit -m "Initial application"
git branch -M main
git remote add origin https://github.com/<YOUR-ORGANIZATION OR YOUR-ACCOUNT-NAME>/<YOUR-REPOSITORY-NAME>.git
git push -u origin main
```


**Build the Docker image using GitHub Actions workflow**

Projects created from this template include a GitHub Actions workflow.

After pushing to `main`:

1. Open your repository on GitHub.
2. Open **Actions**.
3. Wait for the build and container tests to finish successfully.
4. Open the generated package under **Packages**.
5. Copy the exact `ghcr.io/...:<tag>` image name.

The image will look similar to:

```text
ghcr.io/<YOUR-ORGANIZATION OR YOUR-ACCOUNT-NAME>/<YOUR-REPOSITORY-NAME>:<VERSION-TAG>
```

Great! Now You have a working application and it is publicly avialable!

---

### Step 3. Deploy the application on [SciLifeLab Serve](https://serve.scilifelab.se/)

1. Sign in to [SciLifeLab Serve](https://serve.scilifelab.se/).
2. Create a project, or open an existing project.
3. Fill out the form so that it accurately describes your application. you will find some suggestions in the README file of your repository. Please make sure to double check the required values there such as correct descriptions, creator list, etc.
4. Paste the public `image value` (see below) into the **Image** field.
5. Enter the port shown in the generated README or Dockerfile.
6. Add the GitHub repository URL as the **Source code URL**.
7. Create the application.

The `image value` should look similar to:

If you followed **step 2a (for example, Docker Hub)**:

```
docker.io/<YOUR-ORGANIZATION OR YOUR-ACCOUNT-NAME>/<YOUR-APPLICATION-NAME>:<VERSION-TAG>
```

If you followed **step 2b (GitHub)**:

```
ghcr.io/<YOUR-ORGANIZATION OR YOUR-ACCOUNT-NAME>/<YOUR-REPOSITORY-NAME>:<VERSION-TAG>
```

Congratulations! Your application is now published and open for all!

---


## Security and data handling

- Do not commit credentials, tokens or secrets.
- Do not report credentials, sensitive data or exploitable security details in public issues.
- Generated applications are intended for [SciLifeLab Serve](https://serve.scilifelab.se/)'s public application model.
- Do not include personal, patient or sensitive data, user databases or committed credentials in generated applications.
- For platform-specific security or data-handling questions, follow the current [SciLifeLab Serve documentation](https://serve.scilifelab.se/docs/).

---

## Contact

 [SciLifeLab Serve](https://serve.scilifelab.se/) team's official email: `serve@scilifelab.se`.

---

## References

- [SciLifeLab Serve documentation](https://serve.scilifelab.se/docs/)
- [Copier documentation](https://copier.readthedocs.io/)

The current [SciLifeLab Serve documentation](https://serve.scilifelab.se/docs/) is the source of truth for deployment requirements. `docs/SERVE_REQUIREMENTS.md` records the rules and framework-specific exceptions used by this template.

---

## License

MIT.

---
