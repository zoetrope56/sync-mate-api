# 코드 리뷰 — sync-mate-api

> 최초 리뷰: 2026-04-29  
> 최종 점검: 2026-05-08  
> 대상 브랜치: develop

---

## 개요

FastAPI + PostgreSQL + Redis 기반의 투두 앱 + 육성 캐릭터 API.  
DDD 기반 레이어 구조(domain / schemas / repository / endpoints)로 리팩토링 완료.

---

## 현재 구현 상태

| 항목 | 상태 |
|------|------|
| 회원가입 / 로그인 (JWT) | 완료 |
| Todo CRUD | 완료 |
| Todo 완료 시 캐릭터 exp · happiness 적용 | 완료 |
| 캐릭터 생성 / 조회 / 상호작용 | 완료 |
| `apply_hunger_decay()` 도메인 메서드 | 완료 (호출 미연결) |
| DB 스키마 / Alembic 마이그레이션 | 완료 (초기 스키마) |
| 단위 · 통합 테스트 | 완료 (users, todos, character) |

---

## 미결 사항

### 1. Hunger Decay 스케줄러 미연결 (P0-1)

**파일:** `app/main.py`, `app/core/scheduler.py` (파일 없음)

`Character.apply_hunger_decay()`는 구현됐으나 어디서도 호출되지 않습니다.  
`app/core/scheduler.py` 생성 및 `app/main.py` lifespan 패턴 적용이 필요합니다.

**구현 가이드:** `docs/hunger-decay-scheduler.md` Step 3–4

---

### 2. `todos.due_date` 필드 없음 (P0-2)

**파일:** `app/domain/todo/entity.py`, `app/schemas/todo.py`

알람 예약 시스템(P1-1)의 전제 조건입니다.

- `Todo` 엔티티에 `due_date: Mapped[datetime | None]` 컬럼 추가
- `TodoCreate` · `TodoUpdate` · `TodoResponse` 스키마에 `due_date: datetime | None` 추가
- Alembic 마이그레이션 생성

---

### 3. `users.telegram_id` 필드 없음 (P0-3)

**파일:** `app/domain/user/entity.py`, `app/schemas/user.py`

텔레그램 알림(P1-2)의 전제 조건입니다.

- `User` 엔티티에 `telegram_id: Mapped[str | None]` (`VARCHAR(100)`, UNIQUE) 컬럼 추가
- `UserResponse`에 `telegram_id: str | None` 추가
- Alembic 마이그레이션 생성

---

## 코드 품질 이슈

### 4. `todos.user_id` 컬럼 인덱스 없음

**파일:** `app/domain/todo/entity.py`

`TodoRepository.get_list(user_id=...)` · `get(user_id=...)` 등 모든 조회가 `user_id` 필터를 사용하지만,  
초기 마이그레이션에서 `todos.user_id`에 인덱스가 생성되지 않았습니다.

```python
# entity.py — user_id에 index=True 추가
user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
```

Alembic 마이그레이션으로 `CREATE INDEX ix_todos_user_id ON todos (user_id)` 적용 필요.

---

### 5. 캐릭터 없는 유저의 Todo 완료 시 묵시적 스킵

**파일:** `app/api/v1/endpoints/todos.py:44`

```python
character = char_repo.get_by_user(user_id=current_user.id)
if character:          # 캐릭터 없으면 조용히 스킵
    character.apply_todo_complete()
    char_repo.save(character)
```

캐릭터 없는 유저가 Todo를 완료해도 응답에 `exp_applied: false` 같은 힌트가 없어  
클라이언트가 exp 미적용 사실을 알 수 없습니다.

현재 기획서 기준으로 캐릭터는 필수이므로, 캐릭터 없는 경우 `404`를 반환하거나  
응답 스키마에 `exp_applied: bool` 필드를 추가하는 방식 중 선택이 필요합니다.

---

## 향후 구현 예정

전체 우선순위 및 작업 범위: `docs/implementation-roadmap.md` 참고.

```
P0-1 스케줄러 연결
  → P0-2 due_date 추가
  → P0-3 telegram_id 추가
    → P1-1 알람 예약 시스템
      → P1-2 텔레그램 봇 연동
  → P1-3 타이머 시스템
    → P2-1 WebSocket
      → P2-2 이벤트 브로드캐스트
```
