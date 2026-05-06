from app.db.base_class import Base  # noqa: F401

# 모든 엔티티를 여기서 import해야 Alembic이 마이그레이션을 감지한다
from app.domain.user.entity import User  # noqa: F401, E402
from app.domain.todo.entity import Todo  # noqa: F401, E402
from app.domain.character.entity import Character  # noqa: F401, E402
