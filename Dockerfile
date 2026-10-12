# genealogy-mcp in a container: an MCP server over stdio (Glama, other MCP hosts, CI).
#   docker build -t genealogy-mcp .
#   docker run -i --rm genealogy-mcp                          # stdio
#   docker run --rm -p 8000:8000 genealogy-mcp --http --host 0.0.0.0   # Streamable HTTP at /mcp
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    GENEALOGY_MCP_HOME=/data
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install . && useradd --create-home --uid 1000 app && mkdir -p /data && chown app /data
USER app
VOLUME /data
ENTRYPOINT ["genealogy-mcp"]
