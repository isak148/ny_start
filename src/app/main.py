from fastapi import FastAPI
import uvicorn

from app.frost_api import hent_vaerdata
from frcm.fireriskmodel.compute import compute

from contextlib import asynccontextmanager
from app.database import create_db_and_tables

#Dette sørger for at databasen opprettes i det sekundet serveren starter.
@asynccontextmanager
async def lifespan(app: FastAPI):
    #Kjør kode ved oppstart av serveren
    create_db_and_tables()
    yield
    
#oppretter selve web-applikasjonen
app = FastAPI(title="Brannrisiko API", version="0.1.0", lifespan=lifespan)

#Et veldig enkelt endepunkt for  å teste at serveren lever
@app.get("/")
def read_root():
    return {"message": "Velkommen til Brannrisiko API!"}

@app.get ("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/risk/{station_id}")
def get_risk(station_id: str):
    try:
        #1. Hent værdata for stasjonen fra forst API
        vaerdata = hent_vaerdata(station_id)

        #Sjekk at vi faktisk fikk data
        if not vaerdata.data:
           return{"error": {"status_code": 404, "detail": "Ingen værdata funnet for denne stasjonen"}}

        #2. beregn brannrisiko basert på frcm modellen
        risk_prediction = compute(vaerdata)

        #3. Retuner resyltatene (FastAPI gjør dette automatisk om til json
        return risk_prediction
    
    except Exception as e:
        return{"error": f"Det oppsto en feil: {str(e)}"}


    #Kjør kode ved nedstenging av serveren (om nødvendig)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

