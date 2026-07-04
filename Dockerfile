# WebStaffr Angel service -- FastAPI app serving /chat and /webhooks/ghl.
# Minimal, single-stage build: this is for local testing (per the current
# scope), not yet a production deployment decision (none has been made --
# see DECISIONS.md).

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webstaffr ./webstaffr

# SQLite file lives on a mounted volume (see docker-compose.yml) so data
# survives container restarts and rebuilds.
ENV WEBSTAFFR_DB_PATH=/data/webstaffr.db
VOLUME ["/data"]

EXPOSE 8000

CMD ["uvicorn", "webstaffr.workers.angel.router:app", "--host", "0.0.0.0", "--port", "8000"]
