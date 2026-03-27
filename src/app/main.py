from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import uvicorn

from app.frost_api import hent_vaerdata
from frcm.fireriskmodel.compute import compute
from app.database import create_db_and_tables, get_session, User
from app.scheduler import scheduler

#Dette sørger for at databasen opprettes i det sekundet serveren starter.
@asynccontextmanager
async def lifespan(app: FastAPI):
    #Kjør kode ved oppstart av serveren
    create_db_and_tables()
    scheduler.start()
    yield
    scheduler.shutdown
    
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

@app.post("/users/")
def create_user(user: User, session: Session = Depends(get_session)):
    """opretter en ny bruker i databasen"""
    #1. Sjekk om brukernavn allerede finnes
    statement = select(User).where(User.username == user.username)
    ekisterende_bruker = session.exec(statement).first()

    if ekisterende_bruker:
        raise HTTPException(status_code=400, detail="Brukernavnet er allerede i bruk")
    #2. Lagre den nye brukeren i databsen
    session.add(user)
    session.commit()
    session.refresh(user) #oppdaterer variabelenslik at vi får ID-en databasen ga den

    return user

@app.get("/users/{username}")
def get_user(username: str, session: Session = Depends(get_session)):
    """Henter informasjonom en spesifikk bruker"""
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=404, detail="fant ingen bruker med dette brukernavnet")
    
    return user 


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

