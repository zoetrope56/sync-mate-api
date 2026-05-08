# DB 스키마 가이드 — sync-mate-api

> 기준: `alembic/versions/5d9062ac3ceb_initial_schema.py`  
> ORM: SQLAlchemy 2.x Mapped 스타일 / DB: PostgreSQL

---

## 테이블 목록

| 테이블 | 역할 |
|--------|------|
| `users` | 계정 (인증 주체) |
| `characters` | 유저당 1개의 육성 캐릭터 |
| `todos` | 유저의 할 일 목록 |

---

## `users`

**파일:** `app/domain/user/entity.py`

| 컬럼 | 타입 | 제약 | 기본값 |
|------|------|------|--------|
| `id` | `INTEGER` | PK, INDEX | — |
| `email` | `VARCHAR(255)` | UNIQUE, INDEX, NOT NULL | — |
| `hashed_password` | `VARCHAR(255)` | NOT NULL | — |
| `is_active` | `BOOLEAN` | NOT NULL | `true` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` (UTC) |

- 비밀번호는 bcrypt 해시로 저장 (`passlib[bcrypt]`).
- `is_active=false`인 유저는 로그인 불가 (인증 레이어에서 차단).

---

## `characters`

**파일:** `app/domain/character/entity.py`

| 컬럼 | 타입 | 제약 | 기본값 |
|------|------|------|--------|
| `id` | `INTEGER` | PK, INDEX | — |
| `user_id` | `INTEGER` | FK → `users.id`, UNIQUE, NOT NULL | — |
| `name` | `VARCHAR(50)` | NOT NULL | — |
| `level` | `INTEGER` | NOT NULL | `1` |
| `exp` | `INTEGER` | NOT NULL | `0` |
| `happiness` | `INTEGER` | NOT NULL | `50` |
| `hunger` | `INTEGER` | NOT NULL | `50` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` (UTC) |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `now()` (UTC) |

- `user_id`에 UNIQUE 제약 → 유저당 캐릭터 1개만 허용.
- `happiness`, `hunger` 범위: 0~100 (엔티티 메서드에서 클램핑).
- `updated_at`은 SQLAlchemy `onupdate`로 자동 갱신.

### 도메인 상수 (entity.py)

| 상수 | 값 | 용도 |
|------|----|------|
| `EXP_PER_LEVEL` | 100 | 레벨업 필요 경험치 = `level × 100` |
| `TODO_COMPLETE_EXP` | 20 | 투두 완료 시 획득 경험치 |
| `TODO_COMPLETE_HAPPINESS` | 5 | 투두 완료 시 행복도 증가 |
| `INTERACT_EXP` | 5 | 상호작용 시 획득 경험치 |
| `INTERACT_HAPPINESS` | 10 | 상호작용 시 행복도 증가 |

### 도메인 메서드

| 메서드 | 설명 |
|--------|------|
| `apply_todo_complete()` | 투두 완료 처리. exp +20, happiness +5. 레벨업 여부 반환 |
| `apply_interact()` | 상호작용 처리. exp +5, happiness +10. 레벨업 여부 반환 |
| `apply_hunger_decay(amount=5)` | hunger -= amount (최솟값 0). 스케줄러가 30분마다 호출 |

---

## `todos`

**파일:** `app/domain/todo/entity.py`

| 컬럼 | 타입 | 제약 | 기본값 |
|------|------|------|--------|
| `id` | `INTEGER` | PK, INDEX | — |
| `user_id` | `INTEGER` | FK → `users.id`, NOT NULL | — |
| `title` | `VARCHAR(255)` | NOT NULL | — |
| `description` | `TEXT` | NULL 허용 | `null` |
| `is_completed` | `BOOLEAN` | NOT NULL | `false` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `now()` (UTC) |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `now()` (UTC) |

- `characters`와 달리 `user_id`에 UNIQUE 없음 → 유저당 N개.
- 완료 처리(`is_completed=true`) 시 연동 엔드포인트가 `character.apply_todo_complete()` 호출.

---

## ERD (텍스트)

```
users (1) ──── (1) characters
  │
  └──── (N) todos
```

---

## 마이그레이션

```bash
# 현재 상태 적용
alembic upgrade head

# 엔티티 변경 후 마이그레이션 파일 생성
alembic revision --autogenerate -m "설명"
alembic upgrade head
```

새 모델 추가 시 `app/db/base.py`에 entity import를 추가해야 Alembic autogenerate가 감지합니다.
