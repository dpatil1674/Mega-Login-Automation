FROM hrishi2861/megalogin:latest
WORKDIR /app

COPY requirements.txt .
RUN uv venv
RUN uv pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "login:app"]
