from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
 
# Configuración de la base de datos
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
Base = declarative_base()
 
# Definición del modelo
class Book(Base):
    __tablename__ = "reservavuelo"
 
    id = Column(Integer, primary_key=True, index=True)
    nombre_pasajero = Column(String(100))
    origen = Column(String(100))
    destino = Column(String(100))
    fecha = Column(DateTime)
    estado = Column(String(20))
    
 
# Crea la tabla si no existe
Base.metadata.create_all(bind=engine)
 
# Definición de modelos Pydantic para entrada y salida
class BookCreate(BaseModel):
    nombre_pasajero: str
    origen: str
    destino: str
    fecha: datetime
    estado: str
 
class BookUpdate(BaseModel):
    nombre_pasajero: str
    origen: str
    destino: str
    fecha: datetime
    estado: str
 
class BookOut(BaseModel):
    nombre_pasajero: str
    origen: str
    destino: str
    fecha: datetime
    estado: str

# Función para obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    return db
 
# Inicializa la aplicación FastAPI
app = FastAPI()
 
# Ruta para obtener todas las reseñas
@app.get("/reservas/", response_model=list[BookOut])
async def read_booking(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    books = db.query(Book).offset(skip).limit(limit).all()
    return books
 
# Ruta para crear una reseña
@app.post("/reservas/", response_model=BookOut)
async def create_booking(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
 
# Ruta para obtener una reseña por ID
@app.get("/reservas/{book_id}", response_model=BookOut)
async def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="book not found")
    return db_book
 
# Ruta para actualizar una reseña por ID
@app.put("/reservas/{book_id}", response_model=BookOut)
async def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="book not found")
    
    db_book.nombre_pasajero = book.nombre_pasajero
    db_book.origen = book.origen
    db_book.destino = book.destino
    db_book.fecha = book.fecha
    db_book.estado = book.estado   
    db.commit()
    return db_book
 
# Ruta para eliminar una reseña por ID
@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "book deleted"}