#!/usr/bin/env python3
"""
위키 페이지 링크 관리자
사용법: 
    - 대화형: python wiki_manager.py
    - 직접 추가: wiki_manager.add_page("제목", "경로", "카테고리")
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path

class WikiManager:
    def __init__(self, wiki_file="index.html", data_file="wiki_data.json"):
        self.wiki_file = Path(wiki_file)
        self.data_file = Path(data_file)
        self.pages = self._load_pages()
    
    def _load_pages(self):
        """저장된 페이지 데이터 로드"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️  데이터 파일이 손상되었습니다. 새로 시작합니다.")
        return []
    
    def _save_pages(self):
        """페이지 데이터 저장"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.pages, f, indent=2, ensure_ascii=False)
        self._update_wiki_html()
    
    def add_page(self, title, path, category="기타"):
        """
        새 페이지 추가
        
        Args:
            title (str): 페이지 제목
            path (str): 페이지 경로 또는 URL
            category (str): 카테고리 (기본값: "기타")
        
        Returns:
            bool: 성공 여부
        """
        # 중복 체크
        for page in self.pages:
            if page['title'] == title or page['path'] == path:
                print(f"❌ 이미 존재하는 페이지입니다: {title}")
                return False
        
        # 새 페이지 정보
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
        print(f"   경로: {path}")
        print(f"   카테고리: {category}")
        
        return True
    
    def remove_page(self, identifier):
        """
        페이지 제거 (제목 또는 ID로)
        
        Args:
            identifier (str): 페이지 제목 또는 ID
        
        Returns:
            bool: 성공 여부
        """
        page_to_remove = None
        
        for page in self.pages:
            if page['title'] == identifier or page['id'] == identifier:
                page_to_remove = page
                break
        
        if not page_to_remove:
            print(f"❌ 페이지를 찾을 수 없습니다: {identifier}")
            return False
        
        self.pages.remove(page_to_remove)
        self._save_pages()
        
        print(f"✅ 페이지 삭제 완료: {page_to_remove['title']}")
        return True
    
    def list_pages(self):
        """현재 페이지 목록 출력"""
        if not self.pages:
            print("📝 등록된 페이지가 없습니다.")
            return
        
        # 카테고리별로 그룹화
        categories = {}
        for page in self.pages:
            category = page.get('category', '기타')
            if category not in categories:
                categories[category] = []
            categories[category].append(page)
        
        print(f"\n📚 위키 페이지 목록 (총 {len(self.pages)}개)")
        print("=" * 60)
        
        for category in sorted(categories.keys()):
            print(f"\n📁 {category}")
            print("-" * 40)
            
            for i, page in enumerate(sorted(categories[category], key=lambda x: x['title']), 1):
                print(f"{i:2d}. {page['title']}")
                print(f"     📄 {page['path']}")
                print(f"     🕐 {page['created_at']}")
                print(f"     🆔 {page['id']}")
                print()
    
    def search_pages(self, query):
        """페이지 검색"""
        query = query.lower()
        results = []
        
        for page in self.pages:
            if (query in page['title'].lower() or 
                query in page['path'].lower() or 
                query in page.get('category', '').lower()):
                results.append(page)
        
        if not results:
            print(f"🔍 '{query}'에 대한 검색 결과가 없습니다.")
            return
        
        print(f"\n🔍 '{query}' 검색 결과 ({len(results)}개)")
        print("=" * 50)
        
        for i, page in enumerate(results, 1):
            print(f"{i}. {page['title']} ({page['category']})")
            print(f"   📄 {page['path']}")
            print()
    
    def update_category(self, identifier, new_category):
        """페이지 카테고리 업데이트"""
        for page in self.pages:
            if page['title'] == identifier or page['id'] == identifier:
                old_category = page.get('category', '기타')
                page['category'] = new_category
                self._save_pages()
                print(f"✅ 카테고리 변경: {page['title']}")
                print(f"   {old_category} → {new_category}")
                return True
        
        print(f"❌ 페이지를 찾을 수 없습니다: {identifier}")
        return False
    
    def _generate_id(self, title):
        """제목을 기반으로 고유 ID 생성"""
        # 특수문자 제거하고 소문자로 변환
        clean_title = re.sub(r'[^\w가-힣]', '', title).lower()
        
        # 기존 ID와 중복되지 않도록 체크
        base_id = clean_title[:20] if clean_title else "page"
        unique_id = base_id
        counter = 1
        
        existing_ids = [page['id'] for page in self.pages]
        while unique_id in existing_ids:
            unique_id = f"{base_id}_{counter}"
            counter += 1
        
        return unique_id
    
    def _update_wiki_html(self):
        """wiki.html 파일의 JavaScript 데이터 부분 업데이트"""
        if not self.wiki_file.exists():
            print("⚠️  wiki.html 파일을 찾을 수 없습니다.")
            return
        
        # HTML 파일 읽기
        with open(self.wiki_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # JavaScript 데이터 생성
        js_data = json.dumps(self.pages, indent=12, ensure_ascii=False)
        
        # wikiPages 배열 교체
        pattern = r'let wikiPages = \[(.*?)\];'
        replacement = f'let wikiPages = {js_data};'
        
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 마지막 업데이트 시간 갱신
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_content = re.sub(
            r'<span id="footer-date">.*?</span>',
            f'<span id="footer-date">{current_time}</span>',
            updated_content
        )
        
        # 파일 저장
        with open(self.wiki_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"📄 {self.wiki_file} 업데이트 완료")
    
    def export_data(self, format_type="json"):
        """데이터 내보내기"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "json":
            filename = f"wiki_backup_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.pages, f, indent=2, ensure_ascii=False)
        
        elif format_type == "markdown":
            filename = f"wiki_export_{timestamp}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Wiki 페이지 목록\n\n")
                
                categories = {}
                for page in self.pages:
                    category = page.get('category', '기타')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(page)
                
                for category in sorted(categories.keys()):
                    f.write(f"## {category}\n\n")
                    for page in sorted(categories[category], key=lambda x: x['title']):
                        f.write(f"- [{page['title']}]({page['path']}) - {page['created_at']}\n")
                    f.write("\n")
        
        print(f"✅ 데이터 내보내기 완료: {filename}")


def main():
    """메인 실행 함수"""
    manager = WikiManager()
    
    while True:
        print("\n" + "="*50)
        print("📚 Storyboard Wiki 관리자")
        print("="*50)
        print("1. 페이지 추가")
        print("2. 페이지 삭제")
        print("3. 페이지 목록 보기")
        print("4. 페이지 검색")
        print("5. 카테고리 변경")
        print("6. 데이터 내보내기")
        print("7. 종료")
        print("-"*50)
        
        choice = input("선택하세요 (1-7): ").strip()
        
        if choice == '1':
            print("\n📝 새 페이지 추가")
            title = input("페이지 제목: ").strip()
            if not title:
                print("❌ 제목을 입력해주세요.")
                continue
            
            path = input("페이지 경로/URL: ").strip()
            if not path:
                print("❌ 경로를 입력해주세요.")
                continue
            
            category = input("카테고리 [기본값: 기타]: ").strip()
            if not category:
                category = "기타"
            
            manager.add_page(title, path, category)
        
        elif choice == '2':
            print("\n🗑️  페이지 삭제")
            manager.list_pages()
            identifier = input("삭제할 페이지 제목 또는 ID: ").strip()
            if identifier:
                confirm = input(f"정말 '{identifier}'를 삭제하시겠습니까? (y/N): ")
                if confirm.lower() == 'y':
                    manager.remove_page(identifier)
        
        elif choice == '3':
            manager.list_pages()
        
        elif choice == '4':
            print("\n🔍 페이지 검색")
            query = input("검색어: ").strip()
            if query:
                manager.search_pages(query)
        
        elif choice == '5':
            print("\n📁 카테고리 변경")
            manager.list_pages()
            identifier = input("변경할 페이지 제목 또는 ID: ").strip()
            if identifier:
                new_category = input("새 카테고리: ").strip()
                if new_category:
                    manager.update_category(identifier, new_category)
        
        elif choice == '6':
            print("\n💾 데이터 내보내기")
            print("1. JSON 형식")
            print("2. Markdown 형식")
            format_choice = input("형식 선택 (1-2): ").strip()
            
            if format_choice == '1':
                manager.export_data("json")
            elif format_choice == '2':
                manager.export_data("markdown")
            else:
                print("❌ 잘못된 선택입니다.")
        
        elif choice == '7':
            print("👋 프로그램을 종료합니다.")
            break
        
        else:
            print("❌ 잘못된 선택입니다. 1-7 사이의 숫자를 입력해주세요.")


# 직접 호출을 위한 함수들
def add_page(title, path, category="기타"):
    """외부에서 직접 페이지 추가"""
    manager = WikiManager()
    return manager.add_page(title, path, category)

def remove_page(identifier):
    """외부에서 직접 페이지 삭제"""
    manager = WikiManager()
    return manager.remove_page(identifier)


if __name__ == "__main__":
    main()