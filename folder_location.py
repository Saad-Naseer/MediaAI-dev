import os

def find_folder(start_dir, folder_name):
    for root, dirs, files in os.walk(start_dir):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return None

# Define the drive or directory to search in
start_dir = 'C:\\'
folder_name = 'vosk'

# Find the folder
folder_location = find_folder(start_dir, folder_name)

if folder_location:
    print(f"Folder '{folder_name}' found at: {folder_location}")
    # Or return folder_location if you are using this in a function
else:
    print(f"Folder '{folder_name}' not found in '{start_dir}'")
