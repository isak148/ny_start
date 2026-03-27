from fastapi import FastAPI
import uvicorn

#oppretter selve web-applikasjonen
app = FastAPI(title="Brannrisiko API", version="0.1.0")

#Et veldig enkelt endepunkt for  å teste at serveren lever
@app.get("/")
def read_root():
    return {"message": "Velkommen til Brannrisiko API!"}

@app.get ("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    
