from database import get_session
from models import ListaTareas, BancoMisiones, MisionRegular, Dificultad
from sqlalchemy import delete

diarias = [
    "Hacer la cama",
    "Hacer estiramientos",
    "10 minutos de meditacion",
    "Salir a dar un paseo corto sin mirar el movil",
    "Recoger y limpiar entorno de trabajo exprés",
    "Realizar limpieza de fotos en el movil de 3 meses",
    "Leer 10 paginas de un libro que no sea texto academico",
    "Hacer un kick nuevo",
    "Buscar nuevas ideas para contenido durante 15-20 minutos",
    "Pensar en un detalle para nuria",
    "Ponte al dia con tus últimos gastos financieros",
    "Resolver cuentas de cifras y letras",
    "Limpieza de suscripciones y correos durante 10-15 minutos",
    "Dejar una reseña positiva o negativa de algún establecimiento",
    "Subir contenido nuevo al servidor."
]

semanales = [
    "Hacer una nueva receta o ensayar otras.",
    "Componer o trabajar en un tema por al menos 3h",
    "Ver videos de produccion o una masterclass de harderclass por al menos 1h",
    "Haz una sesion de pinchar, descargar musica durante este tiempo cuenta tambien.",
    "Cumplir de forma perfecta la dieta esta semana.",
    "Limpieza a fondo del cuarto",
    "Limpieza a fondo de la cocina",
    "Tomar una foto de algo interesante o artistico cada dia de la semana",
    "Cumplir los 3 dias de gimnasio de la mañana sin falta",
    "Salir a correr o hacer algún ejercicio de cardio un día esta semana",
    "Salir de casa todos los dias de la semana"
]

def update_tasks():
    with get_session() as session:
        # Encontrar listas
        lista_diaria = session.query(ListaTareas).filter(ListaTareas.nombre == "Misiones Diarias").first()
        lista_semanal = session.query(ListaTareas).filter(ListaTareas.nombre == "Misiones Semanales").first()
        
        if not lista_diaria or not lista_semanal:
            print("No se encontraron las listas del sistema.")
            return

        # Borrar Misiones Regulares asociadas a bancos de estas listas
        for lista_id in [lista_diaria.id, lista_semanal.id]:
            bancos = session.query(BancoMisiones).filter(BancoMisiones.lista_id == lista_id).all()
            for b in bancos:
                session.query(MisionRegular).filter(MisionRegular.banco_mision_id == b.id).delete()
            
            # Borrar Bancos
            session.query(BancoMisiones).filter(BancoMisiones.lista_id == lista_id).delete()
            
        session.commit()
        
        # Insertar Diarias
        for d in diarias:
            m = BancoMisiones(
                titulo=d,
                lista_id=lista_diaria.id,
                cooldown_dias=1,
                dificultad=Dificultad.NORMAL,
                recurrencia_dias=None
            )
            session.add(m)
            
        # Insertar Semanales
        for s in semanales:
            m = BancoMisiones(
                titulo=s,
                lista_id=lista_semanal.id,
                cooldown_dias=7,
                dificultad=Dificultad.NORMAL,
                recurrencia_dias=None
            )
            session.add(m)
            
        session.commit()
        print("Misiones dummy eliminadas y nuevas misiones añadidas al BancoMisiones.")

if __name__ == "__main__":
    update_tasks()
