# 구현 로드맵 — sync-mate-api

> 기준일: 2026-05-08  
> 스펙 출처: 프로젝트 기획서 (Overview ~ Tech Stack)  
> 실제 스택: Python / FastAPI / SQLAlchemy / APScheduler / Redis / PostgreSQL

---

## 현재 구현 완료

| 기능 | 파일 |
|------|------|
| 회원가입 / 로그인 (JWT) | `endpoints/users.py` |
| Todo CRUD (목록·생성·수정·삭제) | `endpoints/todos.py` |
| Todo 완료 시 캐릭터 exp·happiness 적용 | `endpoints/todos.py` + `entity.py` |
| 캐릭터 생성 / 조회 / 상호작용(interact) | `endpoints/character.py` |
| Hunger 감소 도메인 메서드 | `domain/character/entity.py` |

---

## 구현 리스트 (우선순위 순)

---

### P0 — 기반 완성 (즉시 처리)

현재 동작 중인 코드에 직접 영향을 주거나 상위 기능의 전제가 되는 항목.

#### P0-1. Hunger Decay 스케줄러 연결
- **작업**: `app/core/scheduler.py` 생성 + `app/main.py` lifespan 패턴 적용
- **근거**: 메서드는 구현됐으나 어디서도 호출되지 않음 (code-review 미결)
- **가이드**: `docs/hunger-decay-scheduler.md` Step 3–4
- **예상 소요**: 30분

#### P0-2. Todo 스키마에 마감 기한 필드 추가
- **작업**: `todos` 테이블에 `due_date (TIMESTAMPTZ, nullable)` 컬럼 추가, Alembic 마이그레이션
- **근거**: 알람 시스템(P1-1)의 전제 조건
- **변경 파일**: `domain/todo/entity.py`, `schemas/todo.py`, Alembic revision 생성
- **예상 소요**: 1시간

#### P0-3. User 테이블에 telegram_id 추가
- **작업**: `users` 테이블에 `telegram_id (VARCHAR, nullable, unique)` 추가, Alembic 마이그레이션
- **근거**: 텔레그램 알림(P1-2)의 전제 조건
- **변경 파일**: `domain/user/entity.py`, `schemas/user.py`, Alembic revision 생성
- **예상 소요**: 1시간

---

### P1 — 핵심 기능 (알람 · 타이머)

프로젝트 차별점인 "알림 정확성"과 "집중 모드"를 구현하는 항목.

#### P1-1. 알람 예약 시스템 (Schedule 테이블 + APScheduler)
- **작업**:
  1. `Schedule` 테이블 생성: `id`, `todo_id (FK)`, `alarm_time (TIMESTAMPTZ)`, `status (ENUM: pending·sent·cancelled)`
  2. Todo 생성/수정 시 `due_date` 기반으로 Schedule 레코드 생성
  3. APScheduler `date` 트리거로 지정 시각에 one-shot job 실행
  4. 알람 발송 후 `status = sent` 업데이트
- **변경 파일**: `domain/schedule/entity.py` (신규), `domain/schedule/repository.py` (신규), `core/scheduler.py` (확장)
- **예상 소요**: 3–4시간
- **의존**: P0-1, P0-2

#### P1-2. 텔레그램 봇 알림
- **작업**:
  1. `python-telegram-bot` 패키지 추가 (`requirements.txt`)
  2. `TELEGRAM_BOT_TOKEN` 설정값 추가 (`config.py`)
  3. `app/core/telegram.py` — 봇 메시지 전송 함수 구현
  4. Schedule job에서 텔레그램 전송 호출 (캐릭터 말투 메시지)
  5. `PUT /api/v1/users/me/telegram` — telegram_id 등록 엔드포인트 추가
- **변경 파일**: `core/telegram.py` (신규), `endpoints/users.py` (확장), `core/config.py`
- **예상 소요**: 2–3시간
- **의존**: P0-3, P1-1

#### P1-3. 타이머 기록 시스템 (Timer 테이블)
- **작업**:
  1. `Timer` 테이블 생성: `id`, `user_id (FK)`, `todo_id (FK, nullable)`, `duration_seconds (INTEGER)`, `started_at (TIMESTAMPTZ)`, `ended_at (TIMESTAMPTZ, nullable)`
  2. `POST /api/v1/timers/start` — 타이머 시작
  3. `POST /api/v1/timers/{id}/stop` — 타이머 종료 + 경험치 산정 (30분 = +10 EXP 등 규칙 정의 필요)
  4. 타이머 완료 시 `character.apply_timer_complete(duration)` 호출
- **변경 파일**: `domain/timer/entity.py` (신규), `domain/timer/repository.py` (신규), `endpoints/timer.py` (신규), `domain/character/entity.py` (메서드 추가)
- **예상 소요**: 3시간
- **의존**: P0-1 (캐릭터 상태 변경)

---

### P2 — 실시간 동기화

멀티 디바이스 실시간 반응 기능. FastAPI WebSocket으로 구현.

#### P2-1. WebSocket 연결 관리
- **작업**:
  1. `app/core/ws_manager.py` — 접속 중인 유저별 WebSocket 연결 관리 (`ConnectionManager`)
  2. `GET /api/v1/ws` — WebSocket 엔드포인트 (JWT 인증 포함)
- **변경 파일**: `core/ws_manager.py` (신규), `api/v1/api.py` (라우터 등록)
- **예상 소요**: 2시간

#### P2-2. 이벤트 브로드캐스트
- **작업**: Todo 완료·생성, 캐릭터 레벨업, 타이머 완료 시 해당 유저의 모든 연결에 이벤트 메시지 전송
- **변경 파일**: `endpoints/todos.py`, `endpoints/character.py`, `endpoints/timer.py`
- **예상 소요**: 2시간
- **의존**: P2-1

---

### P3 — 확장 기능 (백로그)

우선순위가 낮거나 별도 설계가 필요한 항목.

| 항목 | 설명 |
|------|------|
| 캘린더 뷰 API | `GET /todos?date=YYYY-MM-DD` 날짜별 필터링 |
| 블로그 위젯 API | 인증 없이 공개 가능한 read-only 캐릭터 상태 엔드포인트 |
| 코스튬 시스템 | `characters`에 `current_skin` 추가, 코스튬 상점 테이블 |
| 친구 캐릭터 상호작용 | 공유 Todo 리스트, 친구 관계 테이블 |

---

## DB 변경 누적 계획

```
현재 스키마
  users / characters / todos

P0 완료 후
  users          ← +telegram_id
  todos          ← +due_date

P1 완료 후
  +schedules     (todo_id FK, alarm_time, status)
  +timers        (user_id FK, todo_id FK, duration_seconds, started_at, ended_at)
```

---

## 패키지 추가 예정

| 패키지 | 용도 | 단계 |
|--------|------|------|
| `python-telegram-bot>=20.0` | 텔레그램 봇 메시지 전송 | P1-2 |
| `websockets>=12.0` | FastAPI WebSocket 지원 (uvicorn 표준 포함) | P2-1 |

---

## 작업 순서 요약

```
P0-1 스케줄러 연결
  → P0-2 due_date 추가
  → P0-3 telegram_id 추가
    → P1-1 알람 예약 시스템
      → P1-2 텔레그램 봇 연동
  → P1-3 타이머 시스템
    → P2-1 WebSocket 연결 관리
      → P2-2 이벤트 브로드캐스트
```
