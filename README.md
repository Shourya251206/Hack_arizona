# Hack_arizona
from notion_client import Client

notion = Client(auth="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")

try:
    user = notion.users.list()
    print("Notion client is working!")
except Exception as e:
    print("Error:", e)
