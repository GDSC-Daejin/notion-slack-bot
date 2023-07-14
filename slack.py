import os
from slack_sdk import WebClient
from configure import MY_TOKEN
from channel import EVENT


def post_message(
    channel, isToday, title, start_date, end_date, position, url, file_path, threadurl
):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": isToday + " " + title,
                "emoji": True,
            },
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "*🕘* " + start_date + end_date}],
        },
        {"type": "divider"},
    ]
    mention = ""
    if isToday.count("[오늘]"):
        mention = "@channel" + "\n"
        mention_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{mention}",
                },
            },
        ]
        blocks.extend(mention_blocks)

    """슬랙 메시지 전송"""
    client = WebClient(token=MY_TOKEN)

    fields = []

    if position:
        position = "*" + position + "*"
        fields.append({"type": "mrkdwn", "text": position})

    if url:
        fields.append({"type": "mrkdwn", "text": f" <{url}|슬랙 링크> "})
    if threadurl:
        fields.append({"type": "mrkdwn", "text": f" <{threadurl}|[관련 쓰레드]> "})
    thread_blocks = [
        {
            "type": "section",
            "fields": fields,
        }
    ]

    if fields:
        blocks.extend(thread_blocks)
    button_blocks = [
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*참석*\n "},
                {"type": "mrkdwn", "text": "*불참*\n "},
            ],
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "참석",
                    },
                    "style": "primary",
                    "value": "attend",
                    "action_id": "attend",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "emoji": True, "text": "불참"},
                    "style": "danger",
                    "value": "nonattend",
                    "action_id": "nonattend",
                },
            ],
        },
    ]
    # 이전 메시지들을 확인하여 파일 업로드 이전에 메시지를 먼저 보냄
    if isToday.count("[오늘]"):
        #     mention = "@channel"
        if channel != EVENT:
            blocks.extend(button_blocks)
    response = client.chat_postMessage(channel=channel, text="fallback text message", blocks=blocks)
    latest_ts = None
    conversation_history = client.conversations_history(channel=channel)
    for message in conversation_history["messages"]:
        if "ts" in message:
            latest_ts = message["ts"]

        if "bot_id" in message:
            break
    # 파일을 업로드함

    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            response = client.files_upload_v2(
                channel=channel,
                file=file_content,
                filename=title + ".ics",
                thread_ts=latest_ts,
                initial_comment="맥os, 윈도우(일정 설정 必) 밖에 안열려요 ㅠㅠ",
            )

    except FileNotFoundError as e:
        print("Error: %s : %s" % (file_path, e.strerror))
    except UnboundLocalError as e:
        print(e)
    except OSError as e:
        print("Error: %s : %s" % (file_path, e.strerror))
