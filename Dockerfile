FROM python:3.11.8-alpine3.19

RUN mkdir /uasem && chmod 777 /uasem

WORKDIR /uasem

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "ua_crawler.py", "--mail"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD pgrep python || exit 1
