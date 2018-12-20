# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from selenium import webdriver
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-502761537154-503752319332-E8fzsYXGVKWpm3vuVITO7f0g"
slack_client_id = "502761537154.503315380337"
slack_client_secret = "867a15378878e693699c6e59c9d7e41e"
slack_verification = "867a15378878e693699c6e59c9d7e41e"
sc = SlackClient(slack_token)

driver = webdriver.Chrome(r'C:\Users\student\Desktop\chromedriver.exe')
# 사용자 호출 전에 실행되어야 할 것

# 크롤링 함수
def _crawl_portal_keywords(text):

    # 사용자 호출 후 실행되어야 할 것
    text = re.sub(r'^<@\S+> ', '', text)

    # url = "http://www.10000recipe.com/recipe/list.html"
    # driver.get(url)
    # # req = urllib.request.Request(url)
    # # sourcecode = urllib.request.urlopen(url).read()
    # sourcecode = driver.page_source
    # soup = BeautifulSoup(sourcecode, "html.parser")
    #
    # links = []
    # # 함수를 구현해 주세요
    # for i in soup.find_all("div", class_="col-xs-4"):
    #     links.append("http://www.10000recipe.com"+i.find("a")["href"])
    # links = links[:-1]
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return text


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        msg = {}
        msg["text"] = "hey!"
        msg["image_url"] = "https://dispatch.cdnser.be/wp-content/uploads/2018/04/20180410162922_28430063_188843508382637_3514609031517831168_n.jpg"
        msg["color"] = "#F36F81"

        keywords = _crawl_portal_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords,
            attachments = json.dumps([msg])
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)