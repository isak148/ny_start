from sqlmodel import Field, SQLModel,create_engine,Session

#HEr definerervi tabellen for brukere

class user(SQLmodel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True,index=True)
    email: str = Field(unique=True,index=True)
    password: str
    default_station: str = "Denne skal væe mulig å endre på sikt." \
"