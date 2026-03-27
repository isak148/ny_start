from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from app.database import engine, User
from app.frost_api import hent_vaerdata
from frcm.fireriskmodel.compute import compute

def sjekk_brannfare_for_alle_stasjoner():
    """Dette er funksjon som skal kjøre automatisk i bakgrunnen."""
    print("\n---- Starter automatisk sjekk av brannfare")

    #Åpner en fersk tilkobling til databasen
    with Session(engine) as session:
        #finn alle unike standard-stasjoner som finnes i brukertabellen
        statement = select(User.default_station).distinct()
        stasjoner = session.exec(statement).all()

        if not stasjoner: 
            print("Ingen brukere/stasjoner i databasen enda.")
            return
        
        for stasjon in stasjoner:
            try: 
                print(f"Henter ferske data for stasjon{stasjon}...")
                vaerdata = hent_vaerdata(stasjon)

                if len(vaerdata.data) > 0:
                    risk__prediction = compute(vaerdata)
                    #Hent den aller nyeste TTF-verdien (den siste i listen)
                    siste_risiko = risk__prediction.firerisks[-1]
                    print(f"Siste TTF for {stasjon} kl {siste_risiko.timestamp}: {siste_risiko.ttf:.2f}")

                    #Her kommer kode for å sende epost varslinger

                else:
                    print(f"Mangler data for å beregne risiko på {stasjon}")

            except Exception as e:
                print(f"Feil ved sjekk av {stasjon}: {e}")

    print("automatisk sjekk ferdig")

#setter opp plamlegger
scheduler = BackgroundScheduler()

#Setter opp at den skal hente data hver time.
scheduler.add_job(sjekk_brannfare_for_alle_stasjoner, 'interval', hours=1)





