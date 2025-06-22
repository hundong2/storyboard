import os 
import json
from gemini import get_html_file
from add_page import WikiManager
def search_module(folder_name: str):
    print("This is a search module script.")
    # 여기에 검색 모듈의 주요 기능을 구현합니다.
    # 특정 폴더에 있는 모든 md파일을 검색하는 기능
    # 예시로 현재 작업 디렉토리의 'information' 폴더를 검색합니다.
    folder_path = f'{os.getcwd()}/{folder_name}'
    if os.path.exists(folder_path):
        print(f"Listing markdown files in folder: {folder_path}")
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    get_json_file(file_path)
                    print(file_path)
    else:
        print(f"Folder does not exist: {folder_path}")
        return 
def get_json_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(data)  # data는 dict 타입입니다.
        if 'is_done' not in data or not data['is_done']:    
            html_path = get_html_file(data['title'], data['contents'])
            data['is_done'] = True
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            add_page(data['title'], html_path, data.get('category', 'daily'))
def add_page(title: str, path: str, category: str = 'daily'):
    manager = WikiManager()
    manager.add_page(title, path, category)
def __main__():
    search_module("information")
if __name__ == "__main__":
    __main__() 

