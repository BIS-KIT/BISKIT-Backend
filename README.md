# BISKIT-Backend

## Project Introduction

[App Introduction Page - KR](https://landing.teambiskit.com/ko)

BISKIT은 대학 내 한국인, 외국인 학생이 캠퍼스를 기반으로 편하고 안전하게 교류할 수 있도록 돕는 소모임 서비스입니다.

[App Introduction Page - EN](https://landing.teambiskit.com/en)


BISKIT is a consumable service that helps Korean and foreign students in colleges and universities to interact comfortably and safely on campus.

## Project Structure 

```
BISKIT-Backend
├─ README.md
├─ apps
│  ├─ admin : Admin BackOffice 
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  └─ templates
│  ├─ alembic : DB Migrations
│  ├─ api  : EndPoint
│  │  └─ v1
│  │     ├─ endpoints
│  │     └─ router.py
│  ├─ core
│  ├─ crud : Business Logic
│  ├─ database : DB Session Management
│  ├─ init_data.py : Load initial data from excel
│  ├─ main.py
│  ├─ models : DB Schema
│  ├─ requirements
│  ├─ scheduler_module.py : Scheduler Jobs
│  ├─ schemas : Pydantic Schema
│  ├─ tests
│  │  ├─ confest.py
│  │  ├─ fixtures
│  │  └─ v1
├─ docker-compose.deploy.yml : Dev & Prod Server
├─ docker-compose.local.yml : Local Server
├─ dockerfile
├─ nginx
│  ├─ dockerfile
│  └─ nginx.conf
└─ requirements
   └─ requirements.txt
```

## Main Feature

### 회원 가입 및 로그인

- JWT 기반
- 외국인은 휴대폰 인증 불가하여 학생증 및 생년월일 인증
- 다중 국적 및 사용 언어 선택 지원

### 모임

- 모임 검색 : 다양한 필터링 조건, Full Text Search 구현 & Redis cache
- 모임 생성, 수정, 삭제
- 모임 참여 신청, 승인 및 거절
- 모임 채팅 : FireStore
- 모임 후기

### 알림

- FCM 기반 알림 기능 구현
   - 모임 생성 및 삭제
   - 모임 남은 시간 1시간 전
   - 모임 참여 승인 및 거절
   - 학생증 인증 승인 및 거절
   - 신고 및 누적횟수
   - 공지 사항
- 중요 & 기타 알림 설정 및 해제

### 신고

- 유저, 모임, 후기 신고
- 유저 차단 시 해당 유저 관련 모임 및 후기 필터링

## CI / CD

- Gibhub Action 활용
   - release/dev or release/prod 브랜치에 PR 시 WorkFlows 트리거 작동

```yml
jobs:
  test: # 환경 세팅 및 pytest
    services:
      maindb:
        image: postgres:13
        env:
          POSTGRES_USER: ${{ secrets.DB_USER }}
          POSTGRES_PASSWORD: ${{ secrets.DB_ROOT_PASSWORD }}
          POSTGRES_DB: ${{ secrets.TEST_DB }}
        ports:
          - 5432:5432
      redis:
        image: redis:6.2.6
        ports: 
          - 6379:6379

      - name: checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Create .env file
        run: |

      - name: Install dependencies
        run: |

      - name: Run test
        run: |


  push: # Docker Image Build & Push to DockerHub
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: checkout code
        uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/biskit:${{ env.DATE }}


  deploy: # Access server with SSH and pull docker image
    needs: push

    steps:
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Remote ssh connect
        uses: appleboy/ssh-action@v0.1.9
        with:
          host: ${{ secrets.DEV_REMOTE_IP }}
          username: ${{ secrets.DEV_REMOTE_USER }}
          password: ${{ secrets.DEV_REMOTE_PASSWORD }}
          port: ${{ secrets.DEV_REMOTE_PORT }}
          script: |
```

## ERD

![BisKit](https://github.com/BIS-KIT/BISKIT-Backend/assets/76996686/7050a803-4329-4334-a36a-83cd28c9239d)