# 🎬 BoxOffice Insight

## 📌 프로젝트 소개

**“숫자와 그래프로 영화 산업을 읽는다”**

> 본 프로젝트는 한국 영화 시장에 대한 공공 통계 데이터를 기반으로 다양한 관점에서 분석하고 시각화하여, 사용자가 영화 산업의 흐름과 트렌드를 직관적으로 이해할 수 있도록 도와주는 데이터 기반 영화 분석 웹 애플리케이션입니다.
> 
> 제가 참여했던 프로그래머스 데이터 엔지니어링 데브코스 1차 팀 프로젝트의 기능을 축소하고, AWS 인프라 배포를 진행한 축소판 프로젝트입니다.

**진행 기간**: `2025.05.08 ~ 2025.05.11`

<!-- ## 배포 주소 -->

## 📌 시작 가이드

- Python 3.x
- Django 5.2
- mysql 8.0
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
python manage.py makemigrations

```
```bash
python manage.py migrate

```

4. 데이터 크롤링

```bash
cd utils

```
```bash
python crawl_10days.py

```
```bash
python crawl_info.py

```

5. 개발 서버 실행

```bash
python manage.py runserver

```

## 🛠️ 기술 스택

### Frontend

<img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"><img src="https://img.shields.io/badge/plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white">
<img src="https://img.shields.io/badge/chartjs-FF6384?style=for-the-badge&logo=chartjs&logoColor=white">

### Backend

<img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white"><img src="https://img.shields.io/badge/sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white">

<!-- ### Infra -->

### Cooperation

<img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white"><img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">
<img src="https://img.shields.io/badge/slack-4A154B?style=for-the-badge&logo=slack&logoColor=white">


## 📌 주요 기능
|  | 설명 |
| --- | --- |
| 📊 **누적 흥행 추이 분석** | 영화별 개봉 이후 10일 간의 **누적 관객 수, 매출액, 스크린 수 변화**를 선형 그래프로 시각화 |
| 🌎 **동기간 경쟁작과 비교 분석** | 박스오피스 데이터에서 **관객 수**를 기반으로 연도별로 묶어 파이차트로 시각화 |


### **영화별 성과 데이터 시각화**

1. **데이터로 영화 성과 간략하게 확인하기**
    - 개요
        - 국내 박스오피스 TOP 200 영화 데이터를 활용하여, 각 영화의 흥행 성과를 시각적으로 쉽게 파악할 수 있도록 나타냈습니다.
        - 성과 분석에 유용한 주요 지표를 시각화함으로써 흥행 성적을 직관적으로 이해할 수 있도록 하였습니다.
    - 기능
        - 영화 목록 제공 : 기본 페이지에서는 국내 박스오피스 상위 200편의 영화 목록을 확인할 수 있습니다.
          ![스크린샷 2025-04-24 오전 1 42 21](https://github.com/user-attachments/assets/3ef90220-9597-4a7f-84a7-02039ed9b552)

        - 검색 기능 : 관심 있는 영화를 검색하여 빠르게 찾을 수 있도록 검색 기능을 제공합니다.
          ![image (1)](https://github.com/user-attachments/assets/733fec39-ae33-4aab-a497-c3ff54274e9a)


        - 성과 지표 시각화 : 여기서 개봉 후 10일 동안 `관객 수`와 `스크린 수`, `매출액` 지표를 가져와 어떤 그래프를 띄우는지 한 눈에 볼 수 있습니다.
          ![image](https://github.com/user-attachments/assets/f01cdc62-3d57-4fd8-bb3b-adcec9e21965)

            - 좌측 그래프 ****: `스크린 수`와 `관객 수`를 함께 나타내어, 개봉 초반 마케팅 투자(스크린 수)에 비해 실제 관객 유입이 어떻게 이루어졌는지를 시각적으로 확인할 수 있습니다.
            - 우측 그래프 : `일일 매출액`과 `누적 매출액`을 함께 시각화하여, 영화의 매출 성과가 시간이 지남에 따라 어떻게 변화했는지(증감 추이)를 파악할 수 있습니다.
              
2. **같은 시기 다른 영화들과의 비교**
    - 개요
        - 국내 박스오피스 TOP 200 영화 중 상영된 시기와 같은 연도에 개봉한 다른 영화들의 데이터를 불러와 원형 그래프로 나타냅니다.
        - 이를 통해 해당 영화가 어떤 작품들과 경쟁했는지, 또 그 경쟁 속에서 어느 정도의 흥행 성과를 거두었는지를 직관적으로 비교해볼 수 있습니다.
    - 기능
        - 연도별 관객수 파이 차트 제공 : 기본페이지에는 2005년부터 2024년까지의 연도별 `관객수` 파이차트가 있습니다.
          ![image (3)](https://github.com/user-attachments/assets/f536acc0-999c-43d5-9ae7-a333ba4757ba)

        - 이를 통해 연도별 영화 산업의 흐름을 살펴보고, 특정 연도의 흥행 강세 및 약세를 한눈에 확인할 수 있습니다.
            
            예를 들어 코로나19가 유행하던 2020년과 2021년의 파이차트를 살펴보면, 다른 연도에 비해 개봉 영화의 수와 총 관객 수가 현저히 낮았음을 시각적으로 확인할 수 있습니다.
            
        - 검색기능 : 검색해서 원하는 데이터의 파이차트를 확인할 수 있습니다. 찾고자 하는 영화의 흥행 성적은 어느 정도였는지 확인해보세요!
          ![image (4)](https://github.com/user-attachments/assets/00c40723-d9f2-4c2f-90a8-4b063d1ee693)



## 📌 프로젝트 구조

```
boxoffice/
├── boxoffice/          # 프로젝트 설정 디렉토리
│   ├── __init__.py
│   ├── settings.py     # 프로젝트 설정 파일
│   ├── router/
│   |  ├── urls.py        # URL 설정
│   ├── asgi.py        # ASGI 설정
│   └── wsgi.py        # WSGI 설정
├── manage.py          # Django 관리 스크립트
├── requirements.txt   # 의존성 패키지 목록
└── README.md         # 프로젝트 문서

```

## 🌱 향후 확장 방향

- 데이터 수집 자동화 시스템 구축
- 외부 API 연동 확장
- 사용자 맞춤형 시각화 기능 제공

---

## ⚠️ 한계 및 개선점

- **데이터의 양 부족**
    
    역대 박스오피스 Top 200의 영화 데이터를 사용함
    → 더 많은 양의 영화 데이터 수집 시스템 필요
    
- **실시간 크롤링 요청 의존성**
    
    → 정기 수집 및 데이터 누적 시스템 필요
    
    
