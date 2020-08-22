# Project Mazassumnida

Github 프로필에서 boj 프로필을 이쁘게 보여주는 프로젝트

## install

### Poetry를 이용할 경우

```sh
poetry install             # 의존성 설치
poetry shell               # 가상환경에 진입
python manage.py runserver # 서버 실행
```

### requirements.txt를 이용할 경우

```sh
pip install -r requirements.txt
python manage.py runserver # 서버 실행
```

## Usage

html 파일을 아무거나 만들어서 img 태그로 테스트 해보시면 됩니다.

```html
<img src="http://localhost:8000/api/generate_badge?boj=ccoco">
```
