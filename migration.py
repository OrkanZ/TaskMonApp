from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Inventario, Usuario

engine = create_engine("sqlite:///taskmon.db")
with Session(engine) as session:
    items = session.query(Inventario).all()
    for item in items:
        if item.tipo_objeto == "Acelerador":
            item.tipo_objeto = "Acelerador Eclosión"
        elif item.tipo_objeto == "Cebo":
            item.tipo_objeto = "Baya Meloc"
        elif item.tipo_objeto == "Boost de XP":
            item.tipo_objeto = "Huevo Suerte"
    session.commit()
    print("Migración de inventario completada.")
