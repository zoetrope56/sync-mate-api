# SyncMate API

> "내 할 일을 함께 관리하고 성장하는 다마고치형 데스크톱 메이트"

사용자의 할 일 상태에 따라 실시간으로 반응하는 캐릭터 기반 Todo 관리 시스템의 백엔드 API 서버입니다.

---

## 📋 구현 목록

### 사용자 인증
- [x] 회원가입 / 로그인
- [x] JWT 기반 인증 (Bearer Token)
- [ ] 텔레그램 ID 연동 (알림 수신용)

### Todo 관리
- [x] 할 일 생성 / 조회 / 수정 / 삭제
- [x] 완료 상태 토글 (`is_completed`)
- [ ] 마감 기한(Due Date) 설정
- [ ] 알람 시간 설정 (10분 전, 정각 등)

### 캐릭터 시스템 (다마고치)
- [x] 캐릭터 상태 조회 (경험치, 행복도, 스킨)
- [ ] 할 일 완료 시 경험치 / 친밀도 상승
- [ ] 레벨업 계산 및 스킨 해금
- [ ] 집중 모드 상태 연동 (타이머 API)

### 알림 시스템
- [ ] 알람 스케줄 등록 / 취소 (Schedule 테이블)
- [ ] BullMQ + Redis 기반 작업 큐 연동
- [ ] 텔레그램 봇으로 캐릭터 말투 알림 발송

### 타이머
- [ ] 집중 타이머 시작 / 종료 기록
- [ ] 집중 시간 기반 캐릭터 경험치 산정

### 실시간 동기화
- [ ] Socket.io를 통한 멀티 디바이스 상태 동기화
- [ ] 할 일 완료 이벤트 → 클라이언트 캐릭터 애니메이션 트리거

---

## 🗄️ 데이터베이스 스키마

| 테이블 | 주요 필드 | 설명 |
|--------|-----------|------|
| **User** | id, email, password, telegram_id | 사용자 정보 및 알람 수신 ID |
| **Todo** | id, user_id, content, is_completed, due_date | 할 일 내용 및 마감 기한 |
| **MateStatus** | user_id, exp, happiness, current_skin | 캐릭터 레벨, 기분 상태 |
| **Schedule** | id, todo_id, alarm_time, status | 알람 예약 시간 및 발송 상태 |
| **Timer** | id, todo_id, duration, started_at | 집중 시간 기록 및 경험치 산정 |

---

## 🏗️ 프로젝트 구조

```
sync-mate-api/
├── app/
│   ├── main.py                  # FastAPI 초기화 및 앱 실행
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── users.py     # 회원가입, 로그인
│   │       │   ├── todos.py     # 할 일 CRUD
│   │       │   └── character.py # 캐릭터 상태, 레벨업
│   │       ├── api.py           # 라우터 통합
│   │       └── deps.py          # 공통 의존성 (get_current_user)
│   ├── core/
│   │   ├── config.py            # 환경변수 설정 (pydantic-settings)
│   │   └── security.py          # JWT 생성/검증, 비밀번호 해싱
│   ├── crud/
│   │   ├── crud_todo.py
│   │   ├── crud_character.py
│   │   └── crud_user.py
│   ├── models/                  # SQLAlchemy ORM 테이블 정의
│   │   ├── user.py
│   │   ├── todo.py
│   │   └── character.py
│   ├── schemas/                 # Pydantic 입출력 모델
│   │   ├── user.py
│   │   ├── todo.py
│   │   └── character.py
│   ├── db/
│   │   ├── session.py           # DB 엔진 및 세션
│   │   └── base.py              # Alembic 모델 등록
│   └── services/
│       └── character_logic.py   # 경험치, 레벨업 계산 규칙
├── tests/
├── alembic/
├── .env
├── requirements.txt
└── README.md
```

---

## ⚙️ 핵심 로직 흐름

1. **할 일 등록**: 클라이언트 → Todo 생성 API → DB 저장 → 캐릭터 기분 업데이트
2. **알람 예약**: Todo 생성 시 Schedule 등록 → BullMQ가 Redis에 작업 큐 등록
3. **알람 발송**: 예약 시각 도달 → 서버 워커가 텔레그램 봇으로 캐릭터 말투 메시지 전송
4. **실시간 교감**: 모바일에서 완료 체크 → Socket.io 이벤트 → PC 앱 캐릭터 즉시 반응

---

## 🛠️ 기술 스택

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Migrations**: Alembic
- **Cache / Queue**: Redis + BullMQ
- **Auth**: JWT (`python-jose`, `passlib[bcrypt]`)
- **Notifications**: Telegram Bot API

---

## 🚀 로컬 실행

```bash
# 1. 가상환경 설정 (WSL2/Ubuntu)
sudo apt install -y python3.12-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 환경변수 설정 (.env 파일 생성)
POSTGRES_SERVER=
POSTGRES_PORT=5432
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=

# 3. DB 마이그레이션
alembic upgrade head

# 4. 서버 실행
uvicorn app.main:app --reload
```
