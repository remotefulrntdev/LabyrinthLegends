from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import json
import dotenv
import os
import time
dotenv.load_dotenv()

api_key = os.environ.get("KEY")
api_service_name = 'youtube'
api_version = 'v3'
credentials = service_account.Credentials.from_service_account_file(
    'retube-game-a3a6720e6302.json')
youtube = build(api_service_name, api_version, credentials=credentials)

live_chat_id = 'KicKGFVDV0RJYmhKbmUtazUybnVrQWtqOENIZxILc25YU1RvcHl1dkE'


# def listen_to_chat():
#     messages = []
#     while True:
#         try:
#             request = youtube.liveChatMessages().list(
#                 liveChatId=live_chat_id,
#                 part='snippet,authorDetails'
#             )
#             response = request.execute()

#             for item in response['items']:
#                 author = item['authorDetails']['displayName']
#                 message = item['snippet']['displayMessage']
#                 message_data = [author, message]
#                 if message_data not in messages:
#                     messages.append(message_data)
#                     print(
#                         f"New message from {message_data[0]}: {message_data[1]}")

#         except HttpError as e:
#             print(f'An error occurred: {e}')
#         time.sleep(0.3)

# # Call the listen_to_chat function to start listening to live chat


def setup_webhook_subscription():
    try:
       request = youtube.liveChatMessages().insert(
           part='snippet',
           body={
               'snippet': {
                   'liveChatId': live_chat_id,
                   'type': 'textMessageEvent'
               }
           }
       )
       response = request.execute()
       print('Webhook subscription created successfully.')

    except HttpError as e:
       print(f'An error occurred: {e}')


# Call the setup_webhook_subscription function to create the subscription
setup_webhook_subscription()
