import os
import random
import platform
import argparse
from time import sleep
import smtplib
from email.message import EmailMessage
import queue
import json
import threading

import requests
from plyer import notification
import logging
import colorlog
from bs4 import BeautifulSoup

USER_AGENT_LIST = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
]
USER_AGENT = random.choice(USER_AGENT_LIST)
headers = {"user-agent": USER_AGENT}
s = requests.Session()
s.trust_env = False

log_colors_config = {
    "DEBUG": "white",  # cyan white
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

logger = logging.getLogger("logger_name")

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(
    filename="UniversityAdmissions.txt", mode="a", encoding="utf8"
)

logger.setLevel(logging.DEBUG)
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
    fmt="[%(asctime)s] : %(message)s", datefmt="%b-%d %H:%M"
)
console_formatter = colorlog.ColoredFormatter(
    fmt="%(log_color)s[%(asctime)s] : %(message)s",
    datefmt="%b-%d %H:%M",
    log_colors=log_colors_config,
)
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

parser = argparse.ArgumentParser(description="University Admissions Crawler")
parser.add_argument(
    "--mail",
    help="Notify via email if status changes",
    action="store_true",
)
parser.add_argument(
    "--interval",
    help="Interval between checks, defaults to 300 seconds",
    type=int,
    default=300,
    required=False,
    metavar="SECONDS",
)


class Config:
    def __init__(self, mail_mode):
        try:
            self.__config = {
                "username": os.environ["UA_USERNAME"],
                "password": os.environ["UA_PASSWORD"],
                "smtp": {
                    "host": os.environ["SMTP_HOST"],
                    "port": int(os.environ["SMTP_PORT"]),
                    "username": os.environ["SMTP_USERNAME"],
                    "token": os.environ["SMTP_TOKEN"],
                    "from": os.environ["SMTP_FROM"],
                    "to": os.environ["SMTP_TO"],
                },
            }
            logger.info("Using environment variables")
        except KeyError:
            try:
                self.__config = json.load(open("./config.local.json", "r"))
                logger.info("Using local config file")
            except FileNotFoundError:
                self.__config = json.load(open("./config.json", "r"))
            try:
                assert "username" in self.__config
                self.__str_check(self.__config["username"])
                assert "password" in self.__config
                self.__str_check(self.__config["password"])
                if mail_mode:
                    assert "smtp" in self.__config
                    assert "host" in self.__config["smtp"]
                    self.__str_check(self.__config["smtp"]["host"])
                    assert "port" in self.__config["smtp"]
                    self.__int_check(self.__config["smtp"]["port"])
                    assert "username" in self.__config["smtp"]
                    self.__str_check(self.__config["smtp"]["username"])
                    assert "token" in self.__config["smtp"]
                    self.__str_check(self.__config["smtp"]["token"])
                    assert "from" in self.__config["smtp"]
                    self.__str_check(self.__config["smtp"]["from"])
                    assert "to" in self.__config["smtp"]
                    self.__str_check(self.__config["smtp"]["to"])
            except AssertionError:
                logger.error(f"Invalid config file, {self.__config}")
                exit(1)

    def __str_check(self, value):
        assert isinstance(value, str) and bool(value) is True

    def __int_check(self, value):
        assert isinstance(value, int)

    @property
    def username(self):
        return self.__config["username"]

    @property
    def password(self):
        return self.__config["password"]

    @property
    def smtp(self):
        return self.__config["smtp"]


class DesktopNotifier:
    def __init__(self):
        self.__system = platform.system()
        if self.__system == "Darwin":
            self.__title_part = 'with title "UA Crawler"'
            self.__subtitle_part = 'subtitle "STATUS CHANGED!!!"'
            self.__sound_part = 'sound name "Glass"'

    def send(self, message):
        if platform.system() == "Darwin":
            applescript = f'display notification "{message}" {self.__title_part} {self.__subtitle_part} {self.__sound_part}'
            os.system(f"osascript -e '{applescript}'")
            return
        try:
            assert notification.notify is not None
            notification.notify(
                title="STATUS CHANGED!!!",
                message=message,
                app_icon=None,
                timeout=300,
            )
        except Exception:
            logger.error("Desktop notification failed")


class MailNotifier:
    def __init__(self, config):
        self.__config = config
        try:
            self.__server = smtplib.SMTP(
                self.__config["host"], self.__config["port"], timeout=30
            )
            self.__server.starttls()
            self.__server.login(self.__config["username"], self.__config["token"])
        except Exception as e:
            logger.error("SMTP login failed")
            logger.error(e)
            exit(1)

    def send(self, message):
        content = EmailMessage()
        content.set_content(message)
        content["Subject"] = "University Admissions Monitor"
        content["From"] = self.__config["from"]
        content["To"] = self.__config["to"]
        try:
            self.__server.sendmail(
                self.__config["from"], self.__config["to"], content.as_string()
            )
            logger.info("SMTP sent successed")
        except Exception:
            logger.error("SMTP send failed")

    def __del__(self):
        try:
            self.__server.quit()
        except Exception:
            pass


def clear():
    sys = platform.system()
    if sys == "Windows":
        os.system("cls")
    elif sys == "Linux" or sys == "Darwin":
        os.system("clear")


def producer(q, username, password, interval):
    params = {
        "username": username,
        "password": password,
        "url": "/intl/mypages",
    }
    application_info = {}
    while 42:
        response = s.post(
            "https://www.universityadmissions.se/intl/loginajax",
            headers=headers,
            params=params,
            verify=False,
        )
        if response.text != "/intl/mypages":
            logger.error(response.text)
            input("Press Any Key to Exit...")
            exit(0)
        else:
            logger.info("Login Success!")
        response = s.get(
            "https://www.universityadmissions.se/intl/mypages",
            headers=headers,
            verify=False,
        )
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.head is None:
            continue
        if soup.head.title is None:
            continue
        if soup.head.title.text != "My applications - Universityadmissions.se":
            continue
        courses = soup.find_all("div", class_="course")
        q.put("STARTED MONITORING... \nTEST MAIL")
        for course in courses:
            course_name = course.find(
                "h3", class_="coursehead_desktop heading4 coursename moreinfolink"
            ).text.strip()[2:]
            course_uni = (
                course.find("span", class_="appl_fontsmall").text.split(",")[1].strip()
            )
            course_status = course.find("div", class_="statusblock").text.strip()
            try:
                if application_info[course_name]["status"] != course_status:
                    logger.warning("STATUS CHANGED!!!")
                    msg = course_status + ", " + course_name + " | " + course_uni
                    q.put(msg)
            except KeyError:
                application_info[course_name] = {}
            finally:
                logger.info(course_name)
                logger.info("\t" + course_uni)
                for course_status_lines in course_status.split("\n"):
                    logger.info("\t" + course_status_lines)
                print()
                application_info[course_name]["status"] = course_status
                application_info[course_name]["uni"] = course_uni
        sleep(interval)


def consumer(q, notifier):
    while 42:
        message = q.get()
        notifier.send(message)
        sleep(10)


if __name__ == "__main__":
    # clear()
    args = parser.parse_args()
    config = Config(args.mail)
    if args.mail:
        logger.info("Mail Notifier Enabled")
        notifier = MailNotifier(config.smtp)
    else:
        notifier = DesktopNotifier()
    q = queue.Queue(20)

    pt = threading.Thread(
        target=producer,
        args=(q, config.username, config.password, args.interval),
        daemon=True,
    )
    ct = threading.Thread(target=consumer, args=(q, notifier), daemon=True)

    pt.start()
    ct.start()
    pt.join()
    ct.join()
