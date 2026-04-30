# 코드 리뷰 — sync-mate-api

> 리뷰 일자: 2026-04-29  
> 대상 브랜치: develop

---

## 개요

FastAPI + PostgreSQL + Redis 기반의 투두 앱 + 육성 캐릭터 API.  
레이어 구분(models / schemas / crud / services / endpoints)이 명확하고 전반적인 구조는 양호합니다.

---

## 기능 버그

### 1. `apply_interact`가 경험치를 부여하지 않음

**파일:** `app/services/character_logic.py:36-39`

쓰다듬기 상호작용이 happiness만 올리고 exp는 0입니다. Todo 완료만이 유일한 exp 획득 경로입니다. 설계 의도라면 주석으로 명시 필요.

### 2. `apply_hunger_decay` 미호출

**파일:** `app/services/character_logic.py:42-44`

함수는 구현되어 있으나 어디서도 호출되지 않습니다. Redis 또는 APScheduler 등을 이용한 백그라운드 주기 실행 전략이 필요합니다.

---

## 코드 품질

### 3. 응답 스키마에 `user_id` 노출

**파일:** `app/schemas/todo.py:19`, `app/schemas/character.py:11`

`TodoResponse`와 `CharacterResponse` 모두 `user_id`를 클라이언트에 노출합니다. 인증된 사용자는 자신의 리소스만 접근 가능하므로 불필요한 정보입니다. 제거를 권장합니다.

### 4. pydantic-settings v2 Config 스타일

**파일:** `app/core/config.py:28-29`

pydantic-settings v2에서는 내부 `Config` 클래스 대신 `model_config`를 사용합니다.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ...
    model_config = SettingsConfigDict(env_file=".env")
```

---

## 테스트

`tests/` 디렉토리에 `__init__.py`만 존재하고 실제 테스트 파일이 없습니다.  
`httpx`와 `pytest`가 이미 requirements에 포함되어 있으므로 아래 영역에 대한 테스트 추가가 필요합니다.

- 회원가입 / 로그인 / 인증 실패
- Todo CRUD (생성, 조회, 수정, 삭제, 권한 검증)
- 캐릭터 생성 / 상호작용 / 레벨업

---

## 우선순위 요약

| 우선순위 | 항목 | 파일 |
|----------|------|------|
| 낮음 | 응답에서 `user_id` 제거 | `schemas/todo.py`, `schemas/character.py` |
| 낮음 | pydantic-settings v2 config 업그레이드 | `core/config.py` |
| 낮음 | hunger decay 스케줄링 전략 결정 | `services/character_logic.py` |
