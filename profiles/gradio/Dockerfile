FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=appuser \
    HOME=/home/appuser

RUN useradd -m -u 1000 "$USER"
WORKDIR $HOME/app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=1000:1000 app/ ./
RUN mkdir -p "$HOME/app/tmp" && chown -R 1000:1000 "$HOME/app"

ENV GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    GRADIO_TEMP_DIR=/home/appuser/app/tmp \
    GRADIO_ANALYTICS_ENABLED=False

USER appuser
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/', timeout=3)" || exit 1
CMD ["python", "main.py"]
