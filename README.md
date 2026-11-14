# Project Mazassumnida

Github 프로필에서 boj 프로필을 이쁘게 보여주는 프로젝트


## 주의사항
- **V1, V2는 1시간, mini는 하루 간격으로 업데이트됩니다.**
- 만약 로드된 후 애니메이션을 다시 보고싶으시면 `ctrl + shift + R` 을 눌러서 강력 새로고침을 하시면 다시 보실 수 있습니다!

[![Solved.ac
프로필](https://mazassumnida.wtf/api/mini/generate_badge?boj=koosaga)](https://github.com/mazassumnida/mazassumnida)

[![Solved.ac
프로필](https://mazassumnida.wtf/api/v2/generate_badge?boj=Malkoring)](https://solved.ac/malkoring)
[![Solved.ac
프로필](https://mazassumnida.wtf/api/generate_badge?boj=ccoco&c=c)](https://solved.ac/ccoco)
[![Solved.ac
프로필](https://mazassumnida.wtf/api/v2/generate_badge?boj=strawJI)](https://solved.ac/strawji)


## install

Python 3.12를 사용합니다. 로컬 개발용 서명 키는 서버를 실행할 셸에서 생성하세요.

```sh
export DJANGO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')"
```

운영 환경에서는 새로 생성한 키를 배포 플랫폼의 비밀 설정에 한 번 저장하고 모든 워커와 재시작에서 같은 값을 사용하세요. Git 기록에 있던 키는 폐기하고 폴백 키로도 등록하지 마세요. 기존 키로 서명한 값은 교체 후 검증에 실패할 수 있습니다.

기본 허용 호스트는 `mazassumnida.wtf`와 로컬 주소입니다. 다른 도메인으로 서비스하면 `DJANGO_ALLOWED_HOSTS`에 사용할 호스트 전체를 쉼표로 구분해 지정하세요. 디버그 모드가 필요한 로컬 개발에서만 `DJANGO_DEBUG=1`을 설정하세요.

HTTPS를 종료하는 프록시에서 HTTP 리디렉션과 HSTS를 설정할 수 있습니다. Django가 직접 처리할 경우 HTTPS 요청을 `request.is_secure()`가 올바르게 인식하는지 먼저 확인한 뒤 `DJANGO_SECURE_SSL_REDIRECT=1`과 `DJANGO_SECURE_HSTS_SECONDS`(초)를 설정하세요.

### Poetry를 이용할 경우

```sh
poetry install
poetry run python manage.py runserver
```

### requirements.txt를 이용할 경우

```sh
python -m pip install --require-hashes -r requirements.txt
python manage.py runserver # 서버 실행
```

## Mazassumnida v.1.0

### Usage

```html
[![Solved.ac
프로필](https://mazassumnida.wtf/api/generate_badge?boj={handle})](https://solved.ac/{handle})
```

### Screenshots

#### Ruby 🍒
<img src="https://i.ibb.co/LZGnH5R/2020-08-26-2-02-58.png" alt="2020-08-26-2-02-58" border="0">

#### Diamond 💎
<img src="https://i.ibb.co/0cjvjGn/2020-08-26-2-03-10.png" alt="2020-08-26-2-03-10" border="0">

#### Platinum 💚
<img src="https://i.ibb.co/4VnmL99/2020-08-26-2-10-40.png" alt="2020-08-26-2-10-40" border="0">

#### Gold 🏅
<img src="https://i.ibb.co/88n5MR4/2020-08-26-2-03-56.png" alt="2020-08-26-2-03-56" border="0">

#### Silver 💍
<img src="https://i.ibb.co/mXhLMHJ/2020-08-26-2-03-30.png" alt="2020-08-26-2-03-30" border="0">

#### Bronze 🍂
<img src="https://i.ibb.co/4tpFkR5/2020-08-26-2-03-40.png" alt="2020-08-26-2-03-40" border="0">



## Mazassumnida v.2.0

### Usage

```html
[![Solved.ac
프로필](https://mazassumnida.wtf/api/v2/generate_badge?boj={handle})](https://solved.ac/{handle})
```

### Screenshots

#### Ruby 🍒
<img src="https://i.ibb.co/C6gc9jD/chrome-h1796lob-Nu.png" alt="chrome-h1796lob-Nu" border="0">

#### Diamond 💎
<img src="https://i.ibb.co/W0DTqfF/chrome-0s-RCb-MPg-Ia.png" alt="chrome-s-Xr44t-S85-B" border="0">

#### Platinum 💚
<img src="https://i.ibb.co/HpHCVXG/chrome-0-LDwg6-Mgw-Y.png" alt="chrome-0-LDwg6-Mgw-Y" border="0">

#### Gold 🏅
<img src="https://i.ibb.co/WfkLNRQ/chrome-y-AXSQ9j-Z9t.png" alt="chrome-y-AXSQ9j-Z9t" border="0">

#### Silver 💍
<img src="https://i.ibb.co/0rvb2LZ/chrome-q-Fhu-Ge92-Jp.png" alt="chrome-PZp-C0lw-NXK" border="0">

#### Bronze 🍂
<img src="https://i.ibb.co/Vg2NcZH/chrome-VBCSLd8v-HF.png" alt="chrome-VBCSLd8v-HF" border="0">


## Mazassumnida v.mini

### Usage

```html
[![Solved.ac
프로필](https://mazassumnida.wtf/api/mini/generate_badge?boj={handle})](https://solved.ac/{handle})
```

### Screenshots

#### Ruby 🍒
<img src="https://i.ibb.co/JKncFX1/20200830-00-03-45.png" alt="20200830-00-03-45" border="0">

#### Diamond 💎
<img src="https://i.ibb.co/tJg1mMV/20200830-00-04-09.png" alt="20200830-00-04-09" border="0">

#### Platinum 💚
<img src="https://i.ibb.co/16SYvHd/20200830-00-04-24.png" alt="20200830-00-04-24" border="0">

#### Gold 🏅
<img src="https://i.ibb.co/nfJDBKY/20200830-00-03-26.png" alt="20200830-00-03-26" border="0">

#### Silver 💍
<img src="https://i.ibb.co/Q6SRDZ4/20200830-00-04-37.png" alt="20200830-00-04-37" border="0">

#### Bronze 🍂
<img src="https://i.ibb.co/tBW5WbQ/20200830-00-04-51.png" alt="20200830-00-04-51" border="0">
