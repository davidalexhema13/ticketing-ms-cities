from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3

# Si usas autenticación, descomenta esta línea y asegúrate de tener auth.py en esta carpeta
# from auth import router as auth_router

from permissions import admin_required

app = FastAPI(title="Cities Microservice")

# DB init
def create_tables():
    conn = sqlite3.connect("cities.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

create_tables()


class City(BaseModel):
    name: str
    country: str
    description: str | None = None


# Si tienes auth, activa esta línea
# app.include_router(auth_router)


# GET all (public)
@app.get("/cities")
def get_cities():
    conn = sqlite3.connect("cities.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, country, description FROM cities")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "country": r[2], "description": r[3]} for r in rows]


# GET one (public)
@app.get("/cities/{city_id}")
def get_city(city_id: int):
    conn = sqlite3.connect("cities.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, country, description FROM cities WHERE id=?", (city_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada.")
    return {"id": row[0], "name": row[1], "country": row[2], "description": row[3]}


# CREATE (admin)
@app.post("/cities", status_code=201)
def create_city(city: City, user=Depends(admin_required)):
    conn = sqlite3.connect("cities.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cities (name, country, description) VALUES (?, ?, ?)",
        (city.name, city.country, city.description)
    )
    conn.commit()
    conn.close()
    return {"message": "Ciudad creada correctamente."}


# UPDATE (admin)
@app.put("/cities/{city_id}")
def update_city(city_id: int, city: City, user=Depends(admin_required)):
    conn = sqlite3.connect("cities.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cities SET name=?, country=?, description=? WHERE id=?",
        (city.name, city.country, city.description, city_id)
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada.")
    conn.commit()
    conn.close()
    return {"message": "Ciudad actualizada correctamente."}


# DELETE (admin)
@app.delete("/cities/{city_id}", status_code=204)
def delete_city(city_id: int, user=Depends(admin_required)):
    conn = sqlite3.connect("cities.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cities WHERE id=?", (city_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada.")
    conn.commit()
    conn.close()
    return
