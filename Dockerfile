FROM python:3.11

WORKDIR /previewer

COPY . .

RUN python3 -m pip install -r requirements.txt

CMD python3 run.py