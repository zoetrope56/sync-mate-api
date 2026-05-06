# 코드 리뷰 — sync-mate-api

> 리뷰 일자: 2026-04-29  
> 대상 브랜치: develop  
> 조치 완료: 2026-04-30

---

## 개요

FastAPI + PostgreSQL + Redis 기반의 투두 앱 + 육성 캐릭터 API.  
레이어 구분(models / schemas / crud / services / endpoints)이 명확하고 전반적인 구조는 양호합니다.

---

## 미결 사항

### `apply_hunger_decay` 스케줄링 미구현

**파일:** `app/services/character_logic.py`

함수는 구현되어 있으나 어디서도 호출되지 않습니다.  
APScheduler 또는 Redis 기반 백그라운드 태스크로 주기적으로 호출하는 전략이 필요합니다.


### 날짜 형식 가독성 개선
**파일** `app/schemas/todo.py`, `app/schemas/character.py`

ISO 8601 형식(2026-04-29T10:00:00Z)으로 반환되는 날짜 형식을 클라이언트 가독성을 위해 일반적인 형식(YYYY-MM-DD HH:mm:ss)으로 변경이 필요합니다.


### 도메인 중심 설계(DDD)로의 전환 제안

**파일:** `app/services/character_logic.py`, `app/models/character.py`

현재 서비스 레이어(`character_logic.py`)에 집중된 비즈니스 로직을 도메인 모델(`models/character.py`)로 이전하는 리팩토링을 제안합니다.

- **데이터 중심에서 행위 중심으로 변경:** `Character` 엔티티 내부에 `eat()`, `play()`, `level_up()` 등의 메서드를 구현하여 객체 스스로 상태를 제어하도록 변경.
- **Service 레이어 역할 축소:** 서비스 레이어는 DB 조회, 도메인 메서드 호출, 트랜잭션 관리만 담당하는 'Thin Service' 지향.
- **장점:** 핵심 비즈니스 규칙의 응집도를 높이고, 외부 의존성 없는 순수 도메인 단위 테스트 가능.


---

## 조치 완료 항목

| 항목 | 파일 | 내용 |
|------|------|------|
| `apply_interact` EXP 미부여 버그 수정 | `services/character_logic.py` | 쓰다듬기 시 EXP +5 추가, 레벨업 반환값 정상화 |
| 응답 스키마에서 `user_id` 제거 | `schemas/todo.py`, `schemas/character.py` | 불필요한 내부 필드 노출 차단 |
| pydantic-settings v2 Config 스타일 적용 | `core/config.py` | `class Config` → `model_config = SettingsConfigDict(...)` |
| 캐릭터 초기 happiness/hunger 기본값 수정 | `models/character.py` | 100 → 50 (API 문서 기준 일치) |
| 테스트 추가 | `tests/` | 인증·Todo CRUD·캐릭터 24개 테스트 (SQLite in-memory) |
