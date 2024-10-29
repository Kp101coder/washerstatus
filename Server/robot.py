from __future__ import print_function
import os
from pynput.keyboard import Key, Controller
keyboard = Controller()
from pynput.mouse import Button, Controller
mouse = Controller()
import time
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import io
import time

'''
while(True):
    print("Mouse pos: {0}".format(mouse.position))
'''

SCOPES = ['https://www.googleapis.com/auth/drive']

def search_for_file(service, name = None, type = None, parents = None, full = False):
    print("Searching for File")
    #application/vnd.google-apps.folder
    #text/plain
    files = []
    page_token = None
    while True:
        if parents != None:
            response = service.files().list(q="parents in '" + parents + "' and trashed=false", spaces='drive', fields='nextPageToken, ''files(id, name)',pageToken=page_token).execute()
        else:
            response = service.files().list(q="mimeType='" + type + "' and name contains '" + name + "' and trashed=false", spaces='drive', fields='nextPageToken, ''files(id, name)',pageToken=page_token).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    if full:
        return files
    else:
        return files[0].get('id')

def download_file(service, file_id, filepath):
    print("Downloading File")
    file = service.files().get_media(fileId=file_id).execute()
    # Write the content to a file
    with io.open(filepath, "w", encoding="utf-8") as j:
        for character in file.decode("utf-8"):
            j.write(character)

def delete_file(service, file_id):
    service.files().delete(fileId=file_id).execute()

def mouseKeyboard():
    mouse.position = 143,18
    mouse.click(Button.left)
    mouse.release(Button.left)

    time.sleep(5)

    mouse.position = 804,89
    mouse.click(Button.left)
    mouse.release(Button.left)

    time.sleep(3)

    mouse.position = 480,280
    mouse.click(Button.left)
    mouse.release(Button.left)

    time.sleep(3)

    # Press and release space

    keyboard.type("cd \"Desktop/UHD\"")
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

    time.sleep(3)

    keyboard.type("uvicorn main:app --reload --host 0.0.0.0 --port 7106")
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

def search(service, pid, doDownload = True):

    items = search_for_file(service, parents=pid, full=True)

    if not items:
        print('No files found.')
        return False
    else:
        print('Files:')
        if not doDownload:
            return True
        for item in items:
            print(f"{item['name']} ({item['id']})")
            if os.path.exists(item['name']):
                os.remove(item['name'])
            download_file(service, item['id'], item['name'])
            delete_file(service, item['id'])

print("Starting Server")
creds = None
service = None

try:
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0) 
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
except:
    print("Failed to init api")
    time.sleep(1800)
    os.system("sudo reboot")

pid = search_for_file(service, name="Server Update", type="application/vnd.google-apps.folder")

search(service, pid, True)

mouseKeyboard()

while(True):
    try:
        if search(service, pid, True):
            print("Found update, and downloaded")
        else:
            print("Nothing found")
        time.sleep(900)
    except:
        os.system("sudo reboot")