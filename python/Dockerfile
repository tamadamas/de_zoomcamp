FROM python:3.14.2-slim-trixie

RUN pip install pandas

RUN useradd -m user
USER user
WORKDIR /app

COPY . .

ENTRYPOINT ["python", "main.py"]
