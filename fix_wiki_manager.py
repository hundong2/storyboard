#!/usr/bin/env python3
"""
파일 경로 문제 해결을 위한 수정된 위키 매니저
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path

class WikiManager:
    def __init__(self, html_file=None, data_file="wiki_data.json"):
        # HTML 파일 자동 감지
        if html_file is None:
            if Path("index.html").exists():
                self.html_file = Path("index.html")
                print("✅ index.html을 메인 파일로 사용합니다.")
            elif Path("wiki.html").exists():
                self.html_file = Path("wiki.html")
                print("✅ wiki.html을 메인 파일로 사용합니다.")
            else:
                print("❌ index.html 또는 wiki.html 파일을 찾을 수 없습니다.")
                return
        else:
            self.html_file = Path(html_file)
        
        self.data_file = Path(data_file)
        self.pages = self._load_pages()
        
        # HTML 파일에 필요한 JavaScript 코드가 있는지 확인
        self._check_html_structure()
    
    def _check_html_structure(self):
        """HTML 파일에 필요한 구조가 있는지 확인"""
        if not self.html_file.exists():
            print(f"❌ {self.html_file} 파일이 존재하지 않습니다.")
            return False
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # wikiPages 변수가 있는지 확인
        if 'wikiPages' not in content:
            print(f"⚠️  {self.html_file}에 wikiPages 변수가 없습니다.")
            print("HTML 파일을 위키 형태로 변환하시겠습니까? (y/N): ", end="")
            
            try:
                response = input()
                if response.lower() == 'y':
                    self._convert_to_wiki_format(content)
                    return True
            except:
                pass
            
            return False
        
        return True
    
    def _convert_to_wiki_format(self, existing_content):
        """기존 HTML을 위키 형태로 변환"""
        # 간단한 위키 스타일 HTML 생성
        wiki_html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Storyboard Wiki</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 6px; }}
        .header h1 {{ color: #333; margin: 0; }}
        .search-box {{ margin-bottom: 20px; }}
        .search-input {{ width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; }}
        .wiki-item {{ margin: 10px 0; padding: 15px; border: 1px solid #eee; border-radius: 6px; background: white; }}
        .wiki-item:hover {{ background: #f8f9fa; }}
        .wiki-link {{ text-decoration: none; color: #0066cc; display: block; }}
        .wiki-title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 5px; }}
        .wiki-path {{ font-size: 0.9em; color: #666; font-family: monospace; }}
        .wiki-date {{ font-size: 0.8em; color: #999; float: right; }}
        .category-header {{ background: #e9ecef; padding: 8px 12px; margin: 20px 0 10px 0; font-weight: bold; border-radius: 4px; }}
        .no-results {{ text-align: center; color: #666; font-style: italic; padding: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Storyboard Wiki</h1>
            <p>페이지 목록</p>
        </div>

        <div class="search-box">
            <input type="text" class="search-input" id="search-input" placeholder="🔍 페이지 검색..." onkeyup="filterPages()">
        </div>

        <div id="wiki-content">
            <!-- 페이지 목록이 여기에 표시됩니다 -->
        </div>
    </div>

    <script>
        let wikiPages = [];

        document.addEventListener('DOMContentLoaded', function() {{
            renderPages();
        }});

        function renderPages(filteredPages = null) {{
            const pages = filteredPages || wikiPages;
            const content = document.getElementById('wiki-content');
            
            if (pages.length === 0) {{
                content.innerHTML = '<div class="no-results">📝 아직 등록된 페이지가 없습니다.</div>';
                return;
            }}

            const categories = {{}};
            pages.forEach(page => {{
                const category = page.category || '기타';
                if (!categories[category]) categories[category] = [];
                categories[category].push(page);
            }});

            let html = '';
            Object.keys(categories).sort().forEach(category => {{
                html += `<div class="category-header">${{category}}</div>`;
                categories[category].sort((a, b) => a.title.localeCompare(b.title)).forEach(page => {{
                    html += `
                        <div class="wiki-item">
                            <a href="${{page.path}}" class="wiki-link">
                                <div class="wiki-date">${{page.created_at}}</div>
                                <div class="wiki-title">${{page.title}}</div>
                                <div class="wiki-path">${{page.path}}</div>
                            </a>
                        </div>
                    `;
                }});
            }});

            content.innerHTML = html;
        }}

        function filterPages() {{
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            if (searchTerm === '') {{
                renderPages();
                return;
            }}

            const filteredPages = wikiPages.filter(page => 
                page.title.toLowerCase().includes(searchTerm) ||
                page.path.toLowerCase().includes(searchTerm) ||
                (page.category && page.category.toLowerCase().includes(searchTerm))
            );

            renderPages(filteredPages);
        }}
    </script>
</body>
</html>'''
        
        # 기존 파일 백업
        backup_file = self.html_file.with_suffix('.bak')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(existing_content)
        print(f"✅ 기존 파일을 {backup_file}로 백업했습니다.")
        
        # 새 위키 형태로 저장
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(wiki_html)
        print(f"✅ {self.html_file}을 위키 형태로 변환했습니다.")
    
    def _load_pages(self):
        """저장된 페이지 데이터 로드"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️  데이터 파일이 손상되었습니다. 새로 시작합니다.")
        return []
    
    def add_page(self, title, path, category="기타"):
        """새 페이지 추가"""
        # 중복 체크
        for page in self.pages:
            if page['title'] == title:
                print(f"❌ 이미 존재하는 제목입니다: {title}")
                return False
        
        new_page = {
            "title": title,
            "path": path,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": self._generate_id(title)
        }
        
        self.pages.append(new_page)
        self._save_pages()
        
        print(f"✅ 페이지 추가 완료: {title}")
        return True
    
    def _save_pages(self):
        """페이지 데이터 저장 및 HTML 업데이트"""
        # JSON 파일에 저장
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.pages, f, indent=2, ensure_ascii=False)
        
        # HTML 파일 업데이트
        self._update_html()
    
    def _update_html(self):
        """HTML 파일의 JavaScript 데이터 업데이트"""
        if not self.html_file.exists():
            print(f"❌ {self.html_file} 파일을 찾을 수 없습니다.")
            return
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # JavaScript 데이터 생성
        js_data = json.dumps(self.pages, indent=8, ensure_ascii=False)
        
        # wikiPages 배열 교체
        pattern = r'let wikiPages = \[.*?\];'
        replacement = f'let wikiPages = {js_data};'
        
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 변경사항이 있는지 확인
        if updated_content == content:
            print("⚠️  HTML 파일에서 wikiPages를 찾을 수 없습니다.")
            return
        
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ {self.html_file} 업데이트 완료!")
    
    def _generate_id(self, title):
        """고유 ID 생성"""
        clean_title = re.sub(r'[^\w가-힣]', '', title).lower()[:15]
        base_id = clean_title if clean_title else "page"
        
        existing_ids = [page['id'] for page in self.pages]
        unique_id = base_id
        counter = 1
        
        while unique_id in existing_ids:
            unique_id = f"{base_id}_{counter}"
            counter += 1
        
        return unique_id

def quick_test():
    """빠른 테스트 함수"""
    manager = WikiManager()
    
    # 테스트 페이지 추가
    test_pages = [
        ("홈페이지", "index.html", "메인"),
        ("GitHub 저장소", "https://github.com/hundong2/storyboard", "링크"),
        ("README", "README.md", "문서")
    ]
    
    print("🧪 테스트 페이지들을 추가합니다...")
    for title, path, category in test_pages:
        manager.add_page(title, path, category)
    
    print(f"\n✅ 총 {len(manager.pages)}개의 페이지가 등록되었습니다.")
    print(f"📄 {manager.html_file}에서 확인하세요.")

if __name__ == "__main__":
    print("🔧 Wiki Manager 문제 해결 도구")
    print("1. 빠른 테스트 실행")
    print("2. 수동으로 페이지 추가")
    
    choice = input("선택하세요 (1-2): ").strip()
    
    if choice == '1':
        quick_test()
    elif choice == '2':
        manager = WikiManager()
        title = input("페이지 제목: ")
        path = input("페이지 경로: ")
        category = input("카테고리 [기본값: 기타]: ") or "기타"
        manager.add_page(title, path, category)