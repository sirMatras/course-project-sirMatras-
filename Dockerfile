FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir pip==24.2

COPY pyproject.toml /app/
RUN python - <<'PY'
import tomllib, subprocess
with open('pyproject.toml','rb') as f:
    data = tomllib.load(f)
deps = data['project']['dependencies']
subprocess.check_call(['pip','install',*deps])
PY

COPY src /app/src

EXPOSE 8000

ENV PYTHONPATH=/app/src
CMD ["python", "-m", "uvicorn", "app.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]


