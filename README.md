# BoxOffice Insight

BoxOffice Insight는 영화 박스오피스 정보를 제공하는 웹 애플리케이션입니다.

## 기술 스택
- Python 3.11
- Django 5.2
- SQLite (개발용 DB)

## 설치 방법

1. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
```

2. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

3. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

4. 개발 서버 실행
```bash
python manage.py runserver
```

## 프로젝트 구조
```
boxoffice/
├── boxoffice/          # 프로젝트 설정 디렉토리
│   ├── __init__.py
│   ├── settings.py     # 프로젝트 설정 파일
│   ├── urls.py        # URL 설정
│   ├── asgi.py        # ASGI 설정
│   └── wsgi.py        # WSGI 설정
├── manage.py          # Django 관리 스크립트
├── requirements.txt   # 의존성 패키지 목록
└── README.md         # 프로젝트 문서
```
