# 코드 리뷰 — sync-mate-api

> 리뷰 일자: 2026-04-29  
> 대상 브랜치: develop  
> 최종 조치 완료: 2026-05-06

---

## 개요

FastAPI + PostgreSQL + Redis 기반의 투두 앱 + 육성 캐릭터 API.  
DDD 기반 레이어 구조(domain / schemas / repository / endpoints)로 리팩토링 완료.

---

## 미결 사항

### `apply_hunger_decay` 스케줄링 미구현

**파일:** `app/domain/character/entity.py`

메서드는 `Character` 엔티티에 구현되어 있으나 어디서도 호출되지 않습니다.  
APScheduler 또는 Redis 기반 백그라운드 태스크로 주기적으로 호출하는 전략이 필요합니다.

---

## 조치 완료 항목

| 항목 | 파일 | 내용 |
|------|------|------|
| `apply_interact` EXP 미부여 버그 수정 | `domain/character/entity.py` | 쓰다듬기 시 EXP +5 추가, 레벨업 반환값 정상화 |
| 응답 스키마에서 `user_id` 제거 | `schemas/todo.py`, `schemas/character.py` | 불필요한 내부 필드 노출 차단 |
| pydantic-settings v2 Config 스타일 적용 | `core/config.py` | `class Config` → `model_config = SettingsConfigDict(...)` |
| 캐릭터 초기 happiness/hunger 기본값 수정 | `domain/character/entity.py` | 100 → 50 (API 문서 기준 일치) |
| 테스트 추가 | `tests/` | 인증·Todo CRUD·캐릭터 24개 테스트 (SQLite in-memory) |
| DDD 전환 — 비즈니스 로직 엔티티 이전 | `domain/character/entity.py` | `apply_todo_complete`, `apply_interact`, `apply_hunger_decay` 를 `Character` 엔티티 메서드로 이동. 서비스 레이어 제거. |
| persistence/ → domain/ 통합 | `domain/*/repository.py` | Repository 구현체를 domain 패키지로 병합, ABC 레이어 제거. `persistence/` 디렉터리 삭제. |
| 날짜 형식 가독성 개선 | `schemas/todo.py`, `schemas/character.py` | ISO 8601 → `YYYY-MM-DD HH:mm:ss` 포맷 변환. `field_serializer` 적용. |
