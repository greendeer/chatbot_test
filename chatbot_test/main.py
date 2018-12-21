# -*- coding: utf-8 -*-
import json
from operator_garam import FourCal
from formatter import opp_printing
import os
import re
import urllib.request

from selenium import webdriver
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = ""
slack_client_id = ""
slack_client_secret = ""
slack_verification = ""
sc = SlackClient(slack_token)

#driver = webdriver.Chrome(r'C:\Users\student\Desktop\chromedriver.exe')
# 사용자 호출 전에 실행되어야 할 것

pre_timestamp = ""
# 크롤링 함수
def make_message(text):

    # 사용자 호출 후 실행되어야 할 것
    result = re.sub(r'^<@\S+> ', '', text)

    pattern = re.compile(r"(\d+)(\D+)(\d+)").match(result)
    if pattern:
        s = (pattern.group(1), pattern.group(2), pattern.group(3))
        answer = FourCal().operator[s[1]](int(s[0]), int(s[2]))
        formatted = opp_printing[s[1]]
        if answer:
            formatted["msg"]["text"] = s[0]+" "+opp_printing[s[1]]["printing"]+" "+s[2]+"는 "+str(answer)+"입니다."
            return formatted["msg"]
        else:
            formatted["msg"]["text"] = "0으로 나눌 수는 없습니다."
            return formatted["msg"]
    else:
        formatted = opp_printing["error"]
        formatted["msg"]["text"] = "잘못된 입력입니다.\n245+323와 같이 입력해 주세요.\n연산자는 +,-,*,/가 있습니다."
        return formatted["msg"]

def callList(chan, call_list):
    for i in call_list:
        sc.api_call("chat.postMessage",
                    channel=chan,
                    #text=keywords,
                    attachments = json.dumps([i]))

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]
        list = []
        list.append(make_message(text))
        foott = {"color": "#FA8B8B","title":"연속 메세지","text":"이건 그냥 토끼가 귀여움\n귀여우면 됐음\n아무튼 귀여움", "thumb_url":"https://dispatch.cdnser.be/wp-content/uploads/2018/04/20180410162922_28430063_188843508382637_3514609031517831168_n.jpg"}
        list.append(foott)

        callList(channel,list)

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

        global pre_timestamp

        if pre_timestamp < slack_event["event"]["ts"]:
            event_type = slack_event["event"]["type"]
            pre_timestamp = slack_event["event"]["ts"]
            return _event_handler(event_type, slack_event)
        else:
            print("Duplicated message : "+slack_event["event"]["ts"])
            return make_response("duplicated message", 200, )

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=2000)