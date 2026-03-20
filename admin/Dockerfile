FROM docker.io/python:slim

LABEL org.opencontainers.image.source="https://github.com/herheliuk/rust-dedicated"
LABEL org.opencontainers.image.authors="Andrii Herheliuk <andrii@herheliuk.com>"
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends rsync \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m user \
    && mkdir -p /home/user/server_data_backups \
    && chown -R user:user /home/user/server_data_backups

WORKDIR /home/user/

COPY --chown=user:user requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user . .

RUN chmod +x *.py *.sh

USER user

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
