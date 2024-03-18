# UniversityAdmissionsSE_Monitor
A monitoring programme for application status changing on Universityadmissions.se

## Usage(Python)

```
❯ python ua_crawler.py --help
usage: ua_crawler.py [-h] [--mail] [--interval SECONDS]

University Admissions Crawler

options:
  -h, --help          show this help message and exit
  --mail              Notify via email if status changes
  --interval SECONDS  Interval between checks, defaults to 300 seconds
```

### Desktop mode

1.   Edit `username`  and  `password`  fields in `config.json`
2.   Run with
	```
	pip install -r requirements.txt
	python ua_crawler.py
	```

### Mail mode

1.   Edit all fields in `config.json`

2.   Run with

     ```
     pip install -r requirements.txt
     python ua_crawler.py --mail
     ```

## Usage(Docker)

1.   Edit all fileds under `environment` in `docker-compose.yml`

     ```yaml
     version: "3.3"
     
     services:
       app:
         container_name: ua_crawler
         build: .
         restart: unless-stopped
         environment: # <-- HERE
           UA_USERNAME: "lihua@outlook.com"
           UA_PASSWORD: "abcd"
           SMTP_HOST: "smtp.resend.com"
           SMTP_PORT: "465"
           SMTP_USERNAME: "resend"
           SMTP_TOKEN: "1234"
           SMTP_FROM: "from@where.com"
           SMTP_TO: "your@address.com"
     ```

2.   Run with

     ```
     docker compose up -d
     ```

     
