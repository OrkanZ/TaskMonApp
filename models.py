from datetime import date
from typing import Optional
from sqlalchemy import String, Date, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    pass

class ItemType(str, enum.Enum):
    POKEBALL = "Pokéball"
    MASTERBALL = "Masterball"
    ULTRABALL = "Ultraball"
    ACELERADOR = "Acelerador Eclosión"
    CARAMELO_RARO = "Caramelo Raro"
    CEBO = "Baya Meloc"
    BOOST_XP = "Huevo Suerte"
    HUEVO = "Huevo Misterioso"
    FOSIL_PLUMA = "Fósil Pluma"
    FOSIL_TAPA = "Fósil Tapa"
    FOSIL_MISTERIOSO = "Fósil Misterioso"
    
    PIEDRA_HOJA = "Piedra Hoja"
    PIEDRA_FUEGO = "Piedra Fuego"
    PIEDRA_AGUA = "Piedra Agua"
    PIEDRA_LUNAR = "Piedra Lunar"
    PIEDRA_INTERCAMBIO = "Piedra Intercambio"
    PIEDRA_DIA = "Piedra Día"
    PIEDRA_TRUENO = "Piedra Trueno"
    PIEDRA_NOCHE = "Piedra Noche"
    PIEDRA_SOLAR = "Piedra Solar"


class ListaTareas(Base):
    __tablename__ = "listas_tareas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    icono: Mapped[str] = mapped_column(String(50)) # ft.Icons name
    color: Mapped[str] = mapped_column(String(20)) # hex color
    
class Seccion(Base):
    __tablename__ = "secciones"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    lista_id: Mapped[int] = mapped_column(ForeignKey("listas_tareas.id"))
    orden: Mapped[int] = mapped_column(default=0)
    
    # Relación
    lista: Mapped["ListaTareas"] = relationship()

class MissionType(str, enum.Enum):
    DIARIA = "Diaria"
    SEMANAL = "Semanal"

class Dificultad(str, enum.Enum):
    MUY_FACIL = "Muy Fácil"
    FACIL = "Fácil"
    NORMAL = "Normal"
    DIFICIL = "Difícil"

class Prioridad(str, enum.Enum):
    SIN_PRIORIDAD = "Sin prioridad"
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"

class BossTier(str, enum.Enum):
    B = "B"
    A = "A"
    S = "S"

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nivel: Mapped[int] = mapped_column(default=1)
    xp_actual: Mapped[int] = mapped_column(default=0)
    monedas: Mapped[int] = mapped_column(default=0)
    boost_xp_restantes: Mapped[int] = mapped_column(default=0)

class Inventario(Base):
    __tablename__ = "inventario"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_objeto: Mapped[ItemType] = mapped_column(unique=True)
    cantidad: Mapped[int] = mapped_column(default=0)

class RegistroPokedex(Base):
    __tablename__ = "registro_pokedex"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    pokeapi_id: Mapped[int] = mapped_column(unique=True, index=True)

class PokemonCapturado(Base):
    __tablename__ = "pokemon_capturados"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    pokeapi_id: Mapped[int] = mapped_column(unique=True, index=True) # ID de PokeAPI, único para evitar duplicados
    nivel: Mapped[int] = mapped_column(default=1)
    xp: Mapped[int] = mapped_column(default=0)
    en_equipo: Mapped[bool] = mapped_column(default=False) # Lógica de máx 3 se controlará en el backend

class Huevo(Base):
    __tablename__ = "huevos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tareas_requeridas: Mapped[int] = mapped_column(default=50)
    tareas_completadas: Mapped[int] = mapped_column(default=0)
    equipado: Mapped[bool] = mapped_column(default=False)
    tipo_huevo: Mapped[Optional[ItemType]] = mapped_column(nullable=True)

class BancoMisiones(Base):
    __tablename__ = "banco_misiones"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    lista_id: Mapped[int] = mapped_column(ForeignKey("listas_tareas.id"))
    cooldown_dias: Mapped[int] = mapped_column(default=1)
    ultima_aparicion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dificultad: Mapped[Dificultad] = mapped_column(default=Dificultad.NORMAL)
    prioridad: Mapped[Prioridad] = mapped_column(default=Prioridad.SIN_PRIORIDAD)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seccion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("secciones.id"), nullable=True)
    recurrencia_dias: Mapped[Optional[int]] = mapped_column(default=None)
    
    # Relaciones
    lista: Mapped["ListaTareas"] = relationship()
    seccion: Mapped[Optional["Seccion"]] = relationship()

class MisionRegular(Base):
    __tablename__ = "misiones_regulares"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    banco_mision_id: Mapped[int] = mapped_column(ForeignKey("banco_misiones.id"))
    tipo: Mapped[MissionType] = mapped_column()
    completada: Mapped[bool] = mapped_column(default=False)
    fecha_asignacion: Mapped[date] = mapped_column(Date, default=date.today)
    fecha_limite: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    orden: Mapped[int] = mapped_column(default=0)
    
    # Relación para acceder fácilmente a los datos de la misión original
    banco_mision: Mapped["BancoMisiones"] = relationship()

class JefeMisionPrincipal(Base):
    __tablename__ = "jefes_mision_principal"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200)) # Objetivo en la vida real
    pokemon_id: Mapped[int] = mapped_column() # ID de PokeAPI para el Boss
    nivel: Mapped[int] = mapped_column(default=1) # Nivel del Boss
    hp_maximo: Mapped[int] = mapped_column()
    hp_actual: Mapped[int] = mapped_column()
    tier: Mapped[BossTier] = mapped_column()
    completada: Mapped[bool] = mapped_column(default=False)
    capturado: Mapped[bool] = mapped_column(default=False)

class Estadisticas(Base):
    __tablename__ = "estadisticas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    monedas_gastadas: Mapped[int] = mapped_column(default=0)
    objetos_usados: Mapped[int] = mapped_column(default=0)
    huevos_eclosionados: Mapped[int] = mapped_column(default=0)
    pokemon_evolucionados: Mapped[int] = mapped_column(default=0)
    encuentro_comun_progreso: Mapped[int] = mapped_column(default=0)
    encuentro_raro_progreso: Mapped[int] = mapped_column(default=0)

class RecompensaPersonal(Base):
    __tablename__ = "recompensas_personales"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    precio: Mapped[int] = mapped_column(default=100)
    icono: Mapped[str] = mapped_column(String(50), default="STAR")

class LogroDesbloqueado(Base):
    __tablename__ = "logros_desbloqueados"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    logro_id: Mapped[str] = mapped_column(String(100), unique=True)
    fecha: Mapped[date] = mapped_column(Date, default=date.today)
