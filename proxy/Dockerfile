FROM python:3.7-alpine
WORKDIR /app
COPY app.py app.py
RUN pip install art
ENTRYPOINT [ "python3", "app.py" ]