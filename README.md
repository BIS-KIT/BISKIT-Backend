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
│  ├─ __init__.py
│  ├─ admin : Admin BackOffice 
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  └─ templates
│  │     ├─ _macros.html
│  │     ├─ base.html
│  │     ├─ content_details.html
│  │     ├─ create.html
│  │     ├─ details.html
│  │     ├─ edit.html
│  │     ├─ error.html
│  │     ├─ index.html
│  │     ├─ layout.html
│  │     ├─ list.html
│  │     ├─ modals
│  │     │  ├─ delete.html
│  │     │  ├─ details_action_confirmation.html
│  │     │  └─ list_action_confirmation.html
│  │     ├─ photo_list.html
│  │     ├─ report_list.html
│  │     └─ tag_list.html
│  ├─ alembic : DB Migrations
│  │  ├─ README
│  │  ├─ env.py
│  │  ├─ script.py.mako
│  │  └─ versions
│  │
│  ├─ alembic.ini
│  ├─ api 
│  │  ├─ __init__.py
│  │  └─ v1
│  │     ├─ __init__.py
│  │     ├─ endpoints
│  │     │  ├─ admin.py
│  │     │  ├─ alarm.py
│  │     │  ├─ chat.py
│  │     │  ├─ meeting.py
│  │     │  ├─ profile.py
│  │     │  ├─ system.py
│  │     │  ├─ user.py
│  │     │  └─ utility.py
│  │     └─ router.py
│  ├─ core
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ redis_driver.py
│  │  └─ security.py
│  ├─ crud : Business Logic
│  │  ├─ __init__.py
│  │  ├─ alarm.py
│  │  ├─ base.py
│  │  ├─ chat.py
│  │  ├─ meeting.py
│  │  ├─ profile.py
│  │  ├─ system.py
│  │  ├─ user.py
│  │  └─ utility.py
│  ├─ database : DB Session Management
│  │  ├─ __init__.py
│  │  └─ session.py
│  ├─ init_data.py : Load initial data from excel
│  ├─ main.py
│  ├─ models
│  │  ├─ __init__.py
│  │  ├─ alarm.py
│  │  ├─ base.py
│  │  ├─ chat.py
│  │  ├─ meeting.py
│  │  ├─ profile.py
│  │  ├─ system.py
│  │  ├─ user.py
│  │  └─ utility.py
│  ├─ requirements
│  ├─ scheduler_module.py : Scheduler Jobs
│  ├─ schemas
│  │  ├─ __init__.py
│  │  ├─ alarm.py
│  │  ├─ base.py
│  │  ├─ chat.py
│  │  ├─ enum.py
│  │  ├─ meeting.py
│  │  ├─ profile.py
│  │  ├─ system.py
│  │  ├─ user.py
│  │  └─ utility.py
│  ├─ templates
│  │  └─ email_kr.html
│  ├─ tests
│  │  ├─ confest.py
│  │  ├─ fixtures
│  │  │  ├─ __init__.py
│  │  │  ├─ alarm_fixture.py
│  │  │  ├─ base.py
│  │  │  ├─ meeting_fixture.py
│  │  │  ├─ profile_fixture.py
│  │  │  ├─ system_fixture.py
│  │  │  ├─ user_fixture.py
│  │  │  ├─ utility_fixture.py
│  │  │  └─ utils.py
│  │  └─ v1
│  │     ├─ test_alarm.py
│  │     ├─ test_chat.py
│  │     ├─ test_meeting.py
│  │     ├─ test_profile.py
│  │     ├─ test_system.py
│  │     ├─ test_user.py
│  │     └─ test_utility.py
│
├─ docker-compose.deploy.yml
├─ docker-compose.local.yml
├─ dockerfile
├─ init-user.sh
├─ nginx
│  ├─ dockerfile
│  └─ nginx.conf
└─ requirements
   └─ requirements.txt

```

## ERD

![BisKit](https://github.com/BIS-KIT/BISKIT-Backend/assets/76996686/7050a803-4329-4334-a36a-83cd28c9239d)