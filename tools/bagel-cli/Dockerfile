# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app
COPY tools/bagel-cli/dist/*.whl /tmp/
RUN test "$(ls /tmp/*.whl | wc -l)" -eq 1 \
 && pip install --no-cache-dir /tmp/*.whl \
 && rm /tmp/*.whl
ENTRYPOINT [ "bagel" ]
CMD ["--help"]
