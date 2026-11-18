# Project Mazassumnida

Github 프로필에서 boj 프로필을 이쁘게 보여주는 프로젝트


## 주의사항
- **V1, V2는 1시간, mini는 하루 간격으로 업데이트됩니다.**
- 만약 로드된 후 애니메이션을 다시 보고싶으시면 `ctrl + shift + R` 을 눌러서 강력 새로고침을 하시면 다시 보실 수 있습니다!

[![Solved.ac
프로필](https://mazassumnida.wtf/api/mini/generate_badge?handle=koosaga)](https://github.com/mazassumnida/mazassumnida)

[![Solved.ac
프로필](https://mazassumnida.wtf/api/v2/generate_badge?handle=Malkoring)](https://solved.ac/malkoring)
[![Solved.ac
프로필](https://mazassumnida.wtf/api/generate_badge?handle=ccoco&c=c)](https://solved.ac/ccoco)
[![Solved.ac
프로필](https://mazassumnida.wtf/api/v2/generate_badge?handle=strawJI)](https://solved.ac/strawji)


## install

Python 3.12를 사용합니다. 로컬 개발용 서명 키는 서버를 실행할 셸에서 생성하세요.

```sh
export DJANGO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')"
```

운영 환경에서는 새로 생성한 키를 배포 플랫폼의 비밀 설정에 한 번 저장하고 모든 워커와 재시작에서 같은 값을 사용하세요. Git 기록에 있던 키는 폐기하고 폴백 키로도 등록하지 마세요. 기존 키로 서명한 값은 교체 후 검증에 실패할 수 있습니다.

기본 허용 호스트는 `mazassumnida.wtf`와 로컬 주소입니다. 다른 도메인으로 서비스하면 `DJANGO_ALLOWED_HOSTS`에 사용할 호스트 전체를 쉼표로 구분해 지정하세요. 디버그 모드가 필요한 로컬 개발에서만 `DJANGO_DEBUG=1`을 설정하세요.

HTTPS를 종료하는 프록시에서 HTTP 리디렉션과 HSTS를 설정할 수 있습니다. Django가 직접 처리할 경우 HTTPS 요청을 `request.is_secure()`가 올바르게 인식하는지 먼저 확인한 뒤 `DJANGO_SECURE_SSL_REDIRECT=1`과 `DJANGO_SECURE_HSTS_SECONDS`(초)를 설정하세요.

### solved.ac v4 설정

[Backstage](https://backstage.solved.ac/developer/apps)에 등록한 앱의 값을 서버 환경변수로 설정합니다.

| 환경변수 | 값 |
| --- | --- |
| `SOLVED_AC_CLIENT_ID` | 앱의 Client ID |
| `SOLVED_AC_CLIENT_SECRET` | 앱의 Client Secret |
| `REDIS_URL` | 공유 캐시의 `redis://` 또는 `rediss://` 연결 주소 |

Heroku에서는 앱 Settings의 Config Vars에서 설정합니다. Client Secret은 서버의 요청 헤더에만 사용됩니다. 설정이 빠지면 API를 호출하지 않고 Unknown 배지를 반환합니다.

운영에서 여러 워커 또는 dyno를 실행하면 `REDIS_URL`을 같은 Redis에 연결하세요. 설정하면 모든 워커가 프로필 캐시와 호출 제한을 공유합니다. 설정하지 않은 로컬 개발에서는 프로세스별 메모리 캐시를 사용합니다. Redis의 TLS 인증서 검증은 활성화되어 있으며, 캐시 연결 실패 시 외부 API 호출도 중단합니다.

- 프로필은 핸들별로 1시간 캐시하며 네 가지 배지가 공유합니다. 정상 프로필의 보관 기간은 조회 시점부터 최대 24시간입니다.
- 앱별 기본 한도에 맞춰 600회 용량의 토큰 버킷을 사용하고 초당 2회씩 보충합니다. 동일 핸들의 동시 갱신도 제한합니다. 다른 서비스에서도 동일한 앱 인증정보를 사용하면 solved.ac의 공유 한도에 함께 포함됩니다.
- 429 응답의 `Retry-After`만큼 앱 전체 요청을 중단합니다. 인증 오류는 60초, 개별 조회 장애는 30초 동안 재호출을 억제합니다.
- 일시적인 장애 또는 호출 제한 중에는 보관된 정상 프로필을 사용합니다. 이 응답과 Unknown 배지는 `no-store`로 반환합니다. 404는 이전 데이터를 지우고 60초 동안 재조회하지 않습니다.
- 외부 캐시의 유효시간에서는 서버 캐시에 머문 시간을 빼서 V1·V2·pastel의 1시간과 mini의 24시간 갱신 주기가 누적되지 않도록 합니다.

새 URL은 `?handle=solved.ac핸들`을 사용합니다. 기존 `?boj=`도 같은 solved.ac 핸들을 조회하는 별칭으로 받으며, 두 값이 모두 있으면 `handle`을 사용합니다. BOJ와 solved.ac 핸들이 달라진 사용자는 URL을 새 핸들로 수정해야 합니다. 기본 핸들은 `ccoco`입니다. 핸들은 1~64자까지 받고 공백·제어문자와 경로 세그먼트 `.`, `..`는 거부합니다.

배지 티어에는 API의 `tier`를 사용합니다. `tier=null`은 Unknown으로 표시하면서 유효한 통계는 보여줍니다. 진행률 구간은 기존 티어 기준표를 사용하며, API 티어와 레이팅 구간이 일치하지 않으면 진행률을 생략합니다. CLASS는 `classPlus=true`일 때 `+`를 표시합니다.

[공식 API 문서](https://backstage.solved.ac/developer/docs)와 [v4 계정 변경 공지](https://solved.ac/notices/v4)를 참고하세요.

검증은 다음 명령으로 실행합니다. 테스트의 API 응답과 캐시는 격리됩니다.

```sh
python manage.py test
python -m gunicorn --check-config mazassumnida.wsgi
```

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
프로필](https://mazassumnida.wtf/api/generate_badge?handle={handle})](https://solved.ac/{handle})
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
프로필](https://mazassumnida.wtf/api/v2/generate_badge?handle={handle})](https://solved.ac/{handle})
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
프로필](https://mazassumnida.wtf/api/mini/generate_badge?handle={handle})](https://solved.ac/{handle})
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
