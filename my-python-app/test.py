import os

#folder_path = '/path/to/your/folder'  # 원하는 폴더 경로로 변경
print(os.getcwd())  # 현재 작업 디렉토리 출력
def list_files_in_folder(folder_path):
    if os.path.exists(folder_path):
        print(f"Listing files in folder: {folder_path}")
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                print(file_path)
    else:
        print(f"Folder does not exist: {folder_path}")
        return


def __main__():
    print("This is a test script.")
    list_files_in_folder(f'{os.getcwd()}/information')
if __name__ == "__main__":
    __main__()