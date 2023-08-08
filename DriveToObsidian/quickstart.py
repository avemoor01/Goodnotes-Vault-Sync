import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import json



current_directory = os.getcwd()
local_folder = os.path.join(current_directory, "temp")




dataFile = os.path.join(os.path.dirname(current_directory), "data.json")

with open(dataFile, 'r') as file:
    data = json.load(file)


output_root = current_directory
for _ in range(4):
    output_root = os.path.dirname(output_root)
output_root = os.path.join(output_root, "GoodNotes")


import pdfsplit


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']
service = None
items = []


def delete_folder_contents(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)  # Delete files
        elif os.path.isdir(item_path):
            delete_folder_contents(item_path)  # Recursively delete subfolders
            os.rmdir(item_path)  # Delete empty subfolders

def download_file(service, file_id, local_folder):
    file = service.files().get(fileId=file_id).execute()
    file_name = file['name']
    request = service.files().get_media(fileId=file_id)

    with open(os.path.join(local_folder, file_name), "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print("Download progress: %d%%" % int(status.progress() * 100))

def getFiles(index, local_folder):

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
    delete_folder_contents(local_folder)
    global items
    print(items[index])
    if 0 <= index < len(items):
        folder_id = items[index][0]
        folder_name = items[index][1]
        print(f"Downloading files from folder '{folder_name}' (ID: {folder_id})")

        # Get the children of the specified folder
        children = get_children(service, folder_id)

        print(children)

        if children:


            subdir = os.path.join(output_root, folder_name)
            print(subdir)
            if not os.path.exists(subdir):
                os.makedirs(subdir)

            delete_folder_contents(subdir)

            print("Downloading files...")
            for child_id, child_name, child_mimeType in children:
                if child_mimeType != "application/vnd.google-apps.folder":
                    download_file(service, child_id, local_folder)
                    print(child_name + " downloaded.")
                else:
                    print(f"Skipping folder '{child_name}' (ID: {child_id}), currently supporting only files.")
            print("Download completed.")
            pdfsplit.main(folder_name)
        else:
            print("The folder has no children.")
    else:
        print("Invalid index.")



def search(service, query):
    # search for the file
    result = []
    page_token = None
    while True:
        response = service.files().list(q=query,
                                        spaces="drive",
                                        fields="nextPageToken, files(id, name, mimeType)",
                                        pageToken=page_token).execute()
        # iterate over filtered files
        for file in response.get("files", []):
            result.append((file["id"], file["name"], file["mimeType"]))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            # no more files
            break
    return result

def get_children(service, folder_id):
    result = []
    page_token = None
    while True:
        response = service.files().list(q=f"'{folder_id}' in parents",
                                        spaces="drive",
                                        fields="nextPageToken, files(id, name, mimeType)",
                                        pageToken=page_token).execute()
        # iterate over children files
        for file in response.get("files", []):
            result.append((file["id"], file["name"], file["mimeType"]))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            # no more children
            break
    return result

def main():

    global service, items  # Add this line to access the global items list

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # Search for the folder named "GoodNotes"
        folder_name = data["driveFolder"]
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        search_results = search(service, query=query)

        if search_results:
            folder_id = search_results[0][0]  # Take the first match (there may be multiple)
            print("Found GoodNotes folder with ID:", folder_id)

            # Call the get_children function with the found folder ID
            children = get_children(service, folder_id)
            if children:
                print("Children of GoodNotes folder:")
                print(children)
                items = children
            else:
                print("GoodNotes folder has no children.")
        else:
            print("GoodNotes folder not found.")
    except Exception as e:
        print("Error occurred:", str(e))

    #sending list of folders to GUI
    books = []
    if items:
        for i in range(len(items)):
            books.append(items[i][1])
        return books  # Return the list of books

if __name__ == '__main__':
    main()
