# Hunger Decay 스케줄러 구현 가이드

> 목표: `Character.apply_hunger_decay()`를 30분마다 자동 호출

---

## 1. 패키지 설치

`requirements.txt`에 추가:

```
apscheduler>=3.10.0
```

```bash
pip install apscheduler
```

---

## 2. 설정값 추가

**`app/core/config.py`** — `Settings` 클래스 안에 추가:

```python
HUNGER_DECAY_INTERVAL_MINUTES: int = 30
```

`.env`에서 `HUNGER_DECAY_INTERVAL_MINUTES=30`으로 재정의 가능.

---

## 3. 스케줄러 모듈 생성

**`app/core/scheduler.py`** 신규 파일:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.session import SessionLocal
from app.domain.character.entity import Character

scheduler = BackgroundScheduler()


def _run_hunger_decay() -> None:
    db = SessionLocal()
    try:
        characters = db.query(Character).all()
        for character in characters:
            character.apply_hunger_decay()
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def start_scheduler(interval_minutes: int) -> None:
    scheduler.add_job(_run_hunger_decay, "interval", minutes=interval_minutes, id="hunger_decay")
    scheduler.start()


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
```

---

## 4. FastAPI lifespan에 등록

**`app/main.py`** 전체 교체:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler(settings.HUNGER_DECAY_INTERVAL_MINUTES)
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

---

## 동작 흐름

```
uvicorn 시작
  └─ lifespan 진입
       └─ BackgroundScheduler 시작 (별도 스레드)
            └─ 30분마다 _run_hunger_decay() 실행
                 └─ 모든 캐릭터 hunger -= 5, DB commit
uvicorn 종료
  └─ lifespan 종료
       └─ scheduler.shutdown()
```

---

## 주의사항

- `BackgroundScheduler`는 별도 스레드에서 동작하므로 SQLAlchemy 세션을 공유하면 안 됩니다. `_run_hunger_decay` 안에서 `SessionLocal()`을 직접 열고 닫는 이유입니다.
- `uvicorn --workers 2` 이상으로 실행하면 각 워커마다 스케줄러가 독립 실행되어 decay가 중복 적용됩니다. 단일 워커(`--workers 1`)로 운영하세요.
