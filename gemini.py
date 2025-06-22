import os
import google.generativeai as genai
import concurrent.futures
import re
from dotenv import load_dotenv
import hashlib
load_dotenv()

# Gemini API 키를 설정합니다.
# 실제 배포 시에는 환경 변수를 사용하는 것이 보안상 안전합니다.
# 예: os.getenv("GEMINI_API_KEY")
# 개발 단계에서는 여기에 직접 API 키를 붙여넣을 수도 있습니다.
# const apiKey = "" // Canvas 환경에서 API 키가 자동으로 제공되므로 빈 문자열로 둡니다.
# 하지만 Python 스크립트에서는 실제 키가 필요합니다.
# 여기에 YOUR_API_KEY_HERE 대신 실제 Gemini API 키를 입력하세요.
API_KEY =  os.getenv("secrets.GEMINI_API_KEY") 
# 모델에 보낼 프롬프트를 정의합니다.
# 모델에게 HTML 파일을 생성하도록 명시적으로 지시하는 것이 중요합니다.
template_prompt_text = """
당신은 웹 페이지를 생성하는 데 능숙한 AI입니다.
아래의 요구 사항에 따라 HTML 파일을 생성해 주세요:
1. 제목은 "<title>"로 설정합니다.
3. HTML 문서 구조를 준수합니다.
생성된 HTML은 웹 브라우저에서 올바르게 표시되어야 합니다.
research the following question and generate an HTML file according to the above conditions:
아래의 질문에 대한 내용을 연구하여 위의 조건에 따라 html 파일을 생성해 주세요:
추가 적으로 예제나 관련 연구 학술 논문도 있으면 같이 링크도 하단에 reference로 추가 해줘.
<contents>
"""
def call_generate_content(prompt_text: str):
    """
    주어진 프롬프트 텍스트를 사용하여 Gemini API를 호출하고 콘텐츠를 생성합니다.
    :param prompt_text: 생성할 콘텐츠의 프롬프트 텍스트
    :return: 생성된 콘텐츠
    """
    # API 키를 설정합니다.
    genai.configure(api_key=API_KEY)
    # 사용할 모델을 초기화합니다. 'gemini-pro' 모델을 사용합니다.
    model = genai.GenerativeModel('gemini-2.5-flash')

    print("Gemini API 호출 중... 응답을 기다려 주세요.\n")

    try:
        # Gemini API를 호출하여 콘텐츠를 생성합니다.
        response = model.generate_content(prompt_text)
        print(response)
        return response
    except Exception as e:
        print(f"API 호출 중 오류가 발생했습니다: {e}")
def execute_get_html(api_key: str, prompt_text: str, output_file_path: str):
    # API 키를 설정합니다.
    genai.configure(api_key=api_key)
    # 사용할 모델을 초기화합니다. 'gemini-pro' 모델을 사용합니다.
    # 'Deep Research'는 특정 모델 이름이 아니며, '2.5 pro'는 'gemini-pro'로 해석했습니다.
    model = genai.GenerativeModel('gemini-2.5-flash')

    print("Gemini API 호출 중... 응답을 기다려 주세요.\n")

    try:
        # Gemini API를 호출하여 콘텐츠를 생성합니다.
        # response.candidates[0].content.parts[0].text 를 사용하여
        # 모델이 반환한 HTML 텍스트를 직접 추출합니다.
        response = None
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(call_generate_content, prompt_text)
            try:
                response = future.result(timeout=300)  # 300초(5분) 타임아웃
                if response.candidates and len(response.candidates) > 0 and \
                    response.candidates[0].content and len(response.candidates[0].content.parts) > 0:
                        generated_html_content = response.candidates[0].content.parts[0].text
                        match = re.search(r'<!DOCTYPE html>.*?</html>', generated_html_content, re.DOTALL | re.IGNORECASE)
                        if match:
                            html_content = match.group(0)
                            # 생성된 HTML 내용을 파일로 저장하는 예시
                            with open(output_file_path, "w", encoding="utf-8") as f:
                                f.write(html_content)
                            print(f"\n생성된 HTML 내용이 '{output_file_path}' 파일로 저장되었습니다.")
                            print(f"이 파일을 웹 브라우저로 열어 결과를 확인하세요.")
                else:
                    print("API 응답에서 유효한 HTML 콘텐츠를 찾을 수 없습니다.")
                    print(response) # 디버깅을 위해 전체 응답 출력
            except concurrent.futures.TimeoutError:
                print("타임아웃이 발생했습니다.")   
    except Exception as e:
        print(f"API 호출 중 오류가 발생했습니다: {e}")
        # 자세한 오류 메시지를 보려면 response.prompt_feedback 또는 response.text를 확인할 수 있습니다.
def get_html_file(title, contents):
    mytext = template_prompt_text.replace('<title>', title).replace('<contents>', contents)
    hash_object = hashlib.sha256(title.encode('utf-8'))
    html_path = f'pages/{hash_object.hexdigest()[:10]}.html'
    execute_get_html(API_KEY, mytext, html_path)
    return html_path
def __main__():
    # 이 스크립트는 직접 실행될 때만 작동합니다.
    # test code 
    if not API_KEY:
        print("API 키가 설정되지 않았습니다. API_KEY 변수를 확인하세요.")
        return
    else:
        print("API 키가 설정되었습니다. Gemini API를 호출합니다.")
        mytext = template_prompt_text.replace('<title>', 'My Web Page').replace('<contents>', 'html의 역사 및 최신 트렌드에 대해 연구 해줘')
        execute_get_html(API_KEY, mytext, 'template.html')
    pass
if __name__ == "__main__":
    __main__()