# Dockerfile này tạo container image cho Researcher service.
# Image cuối dùng cho AWS Lambda container runtime và cũng có thể chạy local để debug.
FROM public.ecr.aws/awsguru/aws-lambda-adapter:1.0.0 AS lambda-adapter
FROM python:3.12-slim

# Build arg này cho phép local build linh hoạt hơn khi cần thêm tool biên dịch.
ARG INSTALL_BUILD_ESSENTIAL=false

WORKDIR /app

# Các biến môi trường này định hướng nơi Playwright lưu browser và cache.
# HOME/XDG_CACHE_HOME được đưa về vùng an toàn hơn cho container.
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache

# Install Node.js, build tools, and the Playwright MCP server.
RUN apt-get update \
    && apt-get install -y curl \
    && if [ "$INSTALL_BUILD_ESSENTIAL" = "true" ]; then apt-get install -y build-essential; fi \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @playwright/mcp@0.0.75 \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium and its Linux dependencies for Playwright.
RUN npx -y playwright install --with-deps chromium

# Install uv for Python dependency management inside the container.
RUN pip install uv

# Copy dependency metadata first so Docker can cache the install layer.
COPY pyproject.toml uv.lock ./
# Chỉ sync dependency trước để tận dụng cache Docker khi code thay đổi nhưng dependency chưa đổi.
RUN uv sync --frozen --no-install-project
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code.
COPY *.py ./

# Add the Lambda Web Adapter so Lambda can proxy HTTP requests to uvicorn.
COPY --from=lambda-adapter /lambda-adapter /opt/extensions/lambda-adapter

# The FastAPI app listens on port 8000 inside the container.
ENV AWS_LWA_PORT=8000

# Expose the app port and run the web server.
EXPOSE 8000
# Lambda Web Adapter sẽ chuyển request Lambda Function URL vào uvicorn process này.
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
