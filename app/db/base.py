from app.db.base_class import Base  # noqa: F401

# 모든 모델을 여기서 import해야 Alembic이 마이그레이션을 감지한다
from app.models.user import User  # noqa: F401, E402
from app.models.todo import Todo  # noqa: F401, E402
from app.models.character import Character  # noqa: F401, E402
