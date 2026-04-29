# API 목록

> Base URL: `http://localhost:8000/api/v1`

인증이 필요한 엔드포인트는 `Authorization: Bearer <token>` 헤더를 포함해야 합니다.

---

## 인증 (Users)

### POST /users/register
회원가입

**Request Body**
```json
{
  "email": "user@example.com",
  "password": "abcd1234"
}
```
- `password`: 최소 8자 이상

**Response** `201`
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true
}
```

**오류**
| 코드 | 원인 |
|------|------|
| 400  | 이미 사용 중인 이메일 |
| 422  | 비밀번호 8자 미만 |

---

### POST /users/login
로그인 (form-data)

**Request Body** (`application/x-www-form-urlencoded`)
```
username=user@example.com
password=abcd1234
```

**Response** `200`
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

**오류**
| 코드 | 원인 |
|------|------|
| 401  | 이메일 또는 비밀번호 불일치 |

---

## 할 일 (Todos)

> 모든 엔드포인트 인증 필요

### GET /todos/
내 할 일 목록 조회

**Query Parameters**
| 이름  | 기본값 | 설명 |
|-------|--------|------|
| skip  | 0      | 건너뛸 항목 수 |
| limit | 100    | 최대 반환 수 |

**Response** `200`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "운동하기",
    "description": "30분 달리기",
    "is_completed": false,
    "created_at": "2026-04-29T10:00:00Z",
    "updated_at": "2026-04-29T10:00:00Z"
  }
]
```

---

### POST /todos/
할 일 생성

**Request Body**
```json
{
  "title": "운동하기",
  "description": "30분 달리기"
}
```
- `description`: 선택 항목

**Response** `201` — TodoResponse

---

### PATCH /todos/{todo_id}
할 일 수정 / 완료 토글

**Path Parameter**: `todo_id` (int)

**Request Body** (모든 필드 선택)
```json
{
  "title": "수정된 제목",
  "description": "수정된 내용",
  "is_completed": true
}
```

> `is_completed`를 `false → true`로 변경하면 캐릭터 EXP · 행복도가 상승합니다.

**Response** `200` — TodoResponse

**오류**
| 코드 | 원인 |
|------|------|
| 404  | 존재하지 않거나 본인 소유가 아닌 Todo |

---

### DELETE /todos/{todo_id}
할 일 삭제

**Path Parameter**: `todo_id` (int)

**Response** `204 No Content`

**오류**
| 코드 | 원인 |
|------|------|
| 404  | 존재하지 않거나 본인 소유가 아닌 Todo |

---

## 캐릭터 (Character)

> 모든 엔드포인트 인증 필요. 계정당 캐릭터 1개.

### POST /character/
캐릭터 생성

**Request Body**
```json
{
  "name": "모찌"
}
```

**Response** `201`
```json
{
  "id": 1,
  "user_id": 1,
  "name": "모찌",
  "level": 1,
  "exp": 0,
  "happiness": 50,
  "hunger": 50,
  "created_at": "2026-04-29T10:00:00Z",
  "updated_at": "2026-04-29T10:00:00Z"
}
```

**오류**
| 코드 | 원인 |
|------|------|
| 400  | 캐릭터가 이미 존재함 |

---

### GET /character/
캐릭터 상태 조회

**Response** `200` — CharacterResponse

**오류**
| 코드 | 원인 |
|------|------|
| 404  | 캐릭터 없음 |

---

### POST /character/interact
캐릭터 쓰다듬기

요청 바디 없음.

**Response** `200`
```json
{
  "character": { /* CharacterResponse */ },
  "leveled_up": false,
  "message": "캐릭터를 쓰다듬었습니다!"
}
```

**오류**
| 코드 | 원인 |
|------|------|
| 404  | 캐릭터 없음 |
