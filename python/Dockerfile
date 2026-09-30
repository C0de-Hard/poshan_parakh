FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV TORCH_HOME=/opt/torch-cache
RUN python -c "from torchvision.models import MobileNet_V3_Small_Weights; MobileNet_V3_Small_Weights.DEFAULT.get_state_dict(progress=True)"

COPY . .

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}"]