import os

def upload(folder):
    data = os.walk(os.path.join(os.getcwd(), folder))
    for dir, sub_dirs, files in data:
        for file in files:
            # Construct the mpremote command for uploading
            relative_path = os.path.relpath(dir, os.getcwd())  # Get the relative path
            cmd = f"mpremote fs cp {os.path.join(relative_path, file)} :{os.path.join(relative_path, file)}"
            print(f"Executing: {cmd}")  # Print the command for debugging
            os.system(f"{cmd} 2>&1")  # Execute and capture any errors

def delete(folder):
    data = os.walk(os.path.join(os.getcwd(), folder))
    for dir, sub_dirs, files in data:
        for file in files:
            # Construct the mpremote command for deleting
            relative_path = os.path.relpath(dir, os.getcwd())  # Get the relative path
            cmd = f"mpremote rm :{os.path.join(relative_path, file)}"
            print(f"Executing: {cmd}")  # Print the command for debugging
            os.system(f"{cmd} 2>&1")  # Execute and capture any errors

folder = "lib"
# Print the full path for verification
print(f"Target folder path: {os.path.join(os.getcwd(), folder)}")

# Call the delete and upload functions
delete(folder)
upload(folder)