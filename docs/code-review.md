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

---

## 조치 완료 항목

| 항목 | 파일 | 내용 |
|------|------|------|
| `apply_interact` EXP 미부여 버그 수정 | `services/character_logic.py` | 쓰다듬기 시 EXP +5 추가, 레벨업 반환값 정상화 |
| 응답 스키마에서 `user_id` 제거 | `schemas/todo.py`, `schemas/character.py` | 불필요한 내부 필드 노출 차단 |
| pydantic-settings v2 Config 스타일 적용 | `core/config.py` | `class Config` → `model_config = SettingsConfigDict(...)` |
| 캐릭터 초기 happiness/hunger 기본값 수정 | `models/character.py` | 100 → 50 (API 문서 기준 일치) |
| 테스트 추가 | `tests/` | 인증·Todo CRUD·캐릭터 24개 테스트 (SQLite in-memory) |
