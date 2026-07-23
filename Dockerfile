# Use Python 3.12 to satisfy requirements pinned for Python >= 3.12
FROM python:3.12-slim

# Create a non-root user for security best practices
RUN useradd -m -u 1000 user
USER user

# Set home and working directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY --chown=user . .

# Run the FastAPI server, listening to Render's dynamic PORT variable (defaulting to 10000)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}