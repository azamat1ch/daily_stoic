# 1. Base Image
FROM python:3.12-slim

# 2. Environment Variables
ENV PYTHONUNBUFFERED=1

# 3. Working Directory
WORKDIR /app

# 4. Copy Requirements
COPY requirements.txt .

# 5. Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Application Code
COPY src/ ./src/

# 7. Copy Assets
COPY assets/ ./assets/

# 8. Entry Point/Command
CMD ["python", "-m", "src.main"]