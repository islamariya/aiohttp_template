FROM python:3.10.9-slim-buster

ENV PYTHONPATH="/usr/src/app:${PYTHONPATH}"

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install pydantic[email]

COPY . .

CMD ["python", "app.main.py"]
