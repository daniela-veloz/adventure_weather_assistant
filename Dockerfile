FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (without problematic packages)
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 user
USER user

# Make sure the user owns the app directory
USER root
RUN chown -R user:user /app
USER user

# Set environment variables
ENV HOME=/app
ENV PATH=$HOME/.local/bin:$PATH

# Expose Streamlit port
EXPOSE 7860

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]