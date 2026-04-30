from app.models.character import Character

# 레벨업에 필요한 경험치 = 레벨 * 100
EXP_PER_LEVEL = 100

# 할 일 완료 시 보상
TODO_COMPLETE_EXP = 20
TODO_COMPLETE_HAPPINESS = 5

# 상호작용(쓰다듬기) 보상
INTERACT_HAPPINESS = 10
INTERACT_EXP = 5


def _exp_needed_for_levelup(level: int) -> int:
    return level * EXP_PER_LEVEL


def add_exp(character: Character, amount: int) -> bool:
    """경험치를 추가하고 레벨업 여부를 반환한다."""
    character.exp += amount
    needed = _exp_needed_for_levelup(character.level)
    if character.exp >= needed:
        character.exp -= needed
        character.level += 1
        return True
    return False


def apply_todo_complete(character: Character) -> bool:
    """할 일 완료 시 캐릭터에 보상을 적용하고 레벨업 여부를 반환한다."""
    leveled_up = add_exp(character, TODO_COMPLETE_EXP)
    character.happiness = min(100, character.happiness + TODO_COMPLETE_HAPPINESS)
    return leveled_up


def apply_interact(character: Character) -> bool:
    """쓰다듬기 상호작용을 적용하고 레벨업 여부를 반환한다."""
    leveled_up = add_exp(character, INTERACT_EXP)
    character.happiness = min(100, character.happiness + INTERACT_HAPPINESS)
    return leveled_up


def apply_hunger_decay(character: Character, amount: int = 5) -> None:
    """시간 경과에 따른 배고픔 감소를 적용한다.

    TODO: APScheduler 또는 Redis 기반 백그라운드 태스크로 주기적으로 호출해야 합니다.
    """
    character.hunger = max(0, character.hunger - amount)
