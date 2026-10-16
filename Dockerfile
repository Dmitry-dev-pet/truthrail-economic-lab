FROM python:3.12-slim
ARG SOURCE_TAG=v1.0
ARG SOURCE_SHA=d4703b6ae0d19dca08fbde11a25c218fa4c7b7a6
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && git clone --depth 1 --branch "$SOURCE_TAG" \
       https://github.com/fhoces/opa-ai-macro-econ-scenarios.git /opt/opa-model \
    && test "$(git -C /opt/opa-model rev-parse HEAD)" = "$SOURCE_SHA" \
    && rm -rf /opt/opa-model/.git
WORKDIR /app
COPY lab/ /app/lab/
COPY ui/ /app/ui/
COPY tests/ /app/tests/
ENV PYTHONPATH=/opt/opa-model:/app \
    LAB_UPSTREAM_DIR=/opt/opa-model \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN python -m unittest discover -s /app/tests -v
USER 65534:65534
EXPOSE 8000
CMD ["python", "-m", "lab.api"]
