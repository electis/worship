import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def get_creads():
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'cred.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def create_stream(config):
    creds = get_creads()
    youtube = build('youtube', 'v3', credentials=creds)
    insert_broadcast_response = youtube.liveBroadcasts().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title='broadcast_title',
                scheduledStartTime='start_time',
                scheduledEndTime='end_time'
            ),
            status=dict(
                privacyStatus='private'
            )
        )
    ).execute()
    broadcast_id = insert_broadcast_response["id"]
    insert_stream_response = youtube.liveStreams().insert(
        part="snippet,cdn",
        body=dict(
            snippet=dict(
                title='stream_title'
            ),
            cdn=dict(
                format="1080p",
                ingestionType="rtmp"
            )
        )
    ).execute()
    stream_id = insert_stream_response["id"]
    bind_broadcast_response = youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id
    ).execute()

# if not create_stream(config):
#     raise Exception('Could not create stream')