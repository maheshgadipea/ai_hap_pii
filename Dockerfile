FROM python:3.13.3-slim

ENV HF_HUB_DISABLE_IMPLICIT_TOKEN=1 \
    TRANSFORMERS_VERBOSITY=error \
    HF_HUB_VERBOSITY=error

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Pre-download toxic-bert model weights into the image
RUN python -c "from detoxify import Detoxify; Detoxify('original')"

COPY pii_detector.py hap_detector.py detector.py ./

ENTRYPOINT ["python", "detector.py"]
