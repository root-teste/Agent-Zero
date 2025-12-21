from core.database import SessionLocal
from core.models import Script

db = SessionLocal()
script = db.query(Script).filter(Script.id == 1).first()

if script:
    script.is_scheduled = True
    script.schedule_interval = 1 # Rodar a cada 1 minuto
    db.commit()
    print(f"Script '{script.name}' agendado para rodar a cada minuto!")
else:
    print("Script 1 não encontrado.")

db.close()
