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
