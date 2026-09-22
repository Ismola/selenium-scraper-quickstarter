FROM ghcr.io/ismola/selenium-scraper-runtime:v0.2.2

USER root
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=scraper:scraper . .
RUN chmod +x /app/docker-entrypoint.sh
USER scraper

ENTRYPOINT ["/app/docker-entrypoint.sh"]
