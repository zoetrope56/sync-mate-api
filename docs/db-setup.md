# DB 세팅 가이드 — sync-mate-api

> 로컬 개발 환경 기준. PostgreSQL은 Homebrew로 설치된 것을 가정합니다.

---

## 사전 확인

### PostgreSQL 설치 및 실행 확인

```bash
brew services list | grep postgresql   # 실행 중인지 확인
brew services start postgresql@18      # 실행 안 되어 있으면 시작
```

### 현재 존재하는 role 확인

```bash
psql postgres -c "\du"
```

---

## 최초 세팅 (role + DB 생성)

로컬 PostgreSQL은 기본적으로 `trust` 인증을 사용하므로 **비밀번호는 실제로 검증되지 않습니다.** `.env`의 값과 일치시켜두기만 하면 됩니다.

### 1. `.env` 파일 생성

```bash
cp .env.example .env   # .env.example이 없으면 아래 내용으로 직접 생성
```

`.env` 내용:

```
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sync_mate

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=<임의의 긴 문자열>
HUNGER_DECAY_INTERVAL_MINUTES=30
```

`SECRET_KEY` 생성 방법:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. PostgreSQL role 생성

```bash
psql -U $(whoami) postgres -c "CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';"
```

### 3. 데이터베이스 생성

```bash
psql -U $(whoami) postgres -c "CREATE DATABASE sync_mate OWNER postgres;"
```

### 4. 마이그레이션 적용

```bash
source venv/bin/activate   # venv가 없으면 ./start.sh 실행 후 다시 시도
alembic upgrade head
```

---

## 연결 확인

```bash
psql -U postgres -d sync_mate -c "\dt"
```

다음과 같이 세 테이블이 출력되면 정상입니다:

```
 Schema |    Name    | Type  |  Owner
--------+------------+-------+----------
 public | characters | table | postgres
 public | todos      | table | postgres
 public | users      | table | postgres
```

---

## 자주 겪는 오류

### `role "postgres" does not exist`

macOS에서 Homebrew로 PostgreSQL을 설치하면 `postgres` role이 기본 생성되지 않습니다. [위의 role 생성 단계](#2-postgresql-role-생성)를 실행하세요.

### `database "sync_mate" does not exist`

[DB 생성 단계](#3-데이터베이스-생성)를 실행하세요.

### `connection refused` (포트 5432)

PostgreSQL 서비스가 실행 중이 아닙니다:

```bash
brew services start postgresql@18
```

버전이 다를 경우 `postgresql@18` 대신 설치된 버전명으로 교체하세요:

```bash
brew services list | grep postgresql
```

---

## DB 초기화 (개발 중 스키마를 완전히 다시 만들고 싶을 때)

```bash
psql -U postgres -c "DROP DATABASE sync_mate;"
psql -U postgres -c "CREATE DATABASE sync_mate OWNER postgres;"
alembic upgrade head
```

---

## 마이그레이션 관리

```bash
alembic upgrade head                          # 최신 마이그레이션 적용
alembic downgrade -1                          # 마지막 마이그레이션 롤백
alembic revision --autogenerate -m "설명"     # 엔티티 변경 후 마이그레이션 파일 생성
alembic current                               # 현재 적용된 revision 확인
alembic history                               # 마이그레이션 이력 조회
```

새 모델 추가 시 `app/db/base.py`에 entity import를 추가해야 `autogenerate`가 변경을 감지합니다.

---

## 관련 문서

- [db-schema.md](db-schema.md) — 테이블 스키마 및 ERD