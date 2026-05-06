from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

EXP_PER_LEVEL = 100
TODO_COMPLETE_EXP = 20
TODO_COMPLETE_HAPPINESS = 5
INTERACT_HAPPINESS = 10
INTERACT_EXP = 5


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1)
    exp: Mapped[int] = mapped_column(Integer, default=0)
    happiness: Mapped[int] = mapped_column(Integer, default=50)  # 0~100
    hunger: Mapped[int] = mapped_column(Integer, default=50)     # 0~100
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def _add_exp(self, amount: int) -> bool:
        self.exp += amount
        needed = self.level * EXP_PER_LEVEL
        if self.exp >= needed:
            self.exp -= needed
            self.level += 1
            return True
        return False

    def apply_todo_complete(self) -> bool:
        leveled_up = self._add_exp(TODO_COMPLETE_EXP)
        self.happiness = min(100, self.happiness + TODO_COMPLETE_HAPPINESS)
        return leveled_up

    def apply_interact(self) -> bool:
        leveled_up = self._add_exp(INTERACT_EXP)
        self.happiness = min(100, self.happiness + INTERACT_HAPPINESS)
        return leveled_up

    def apply_hunger_decay(self, amount: int = 5) -> None:
        self.hunger = max(0, self.hunger - amount)
