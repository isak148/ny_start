from sqlmodel import Field, SQLModel,create_engine,Session

#HEr definerervi tabellen for brukere

# Sjekk at dette stemmer i src/app/database.py
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str # <-- Sannsynligvis lagt til
    password: str # <-- Sannsynligvis lagt til
    default_station: str = Field(default="SN18700")
    favorites: str = Field(default="")

    # lagrer favoritt-statuser for brukeren, som komma-separert string
    # Eksempel: "SN18700,SN50540,SN90450"
    favorites: str = Field(default="")

#Konfigurerer SQLite database. den vil opprette eb fil son heter branrisiko.db
sqlite_file_name = "brannrisiko.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

#Oppretter selve database-motoren
engine = create_engine(sqlite_url, connect_args={"check_same_thread":False})


#funksjon som oppretter tabellene i databasen om de ikke allerede finnes
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

#Funksjon for å hente en database seksjon når fastAPI trenger det
def get_session():
    with Session(engine) as session:
        yield session

