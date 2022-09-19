FROM python:3.8.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /CHEAP.P

RUN apt update
RUN apt install -y postgresql-server-dev-all gcc python3-dev musl-dev
RUN apt -y install netcat

COPY requirements.txt .

RUN pip install pip==20.2.4
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /CHEAP.P/entrypoint.sh
RUN mkdir /CHEAP.P/CheapSh0p/cache
RUN chmod +rwx /CHEAP.P/CheapSh0p/cache

RUN sed -i.bak 's/\r$//' /CHEAP.P/entrypoint.sh
ENTRYPOINT ["bash", "/CHEAP.P/entrypoint.sh"]
