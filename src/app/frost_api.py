import requests
from datetime import datetime, timedelta
from frcm.datamodel.model import WeatherData, WeatherDataPoint

#Her må eg bytt ut med riktig ID når den er på plass
Forst_Client_ID = "d214a45c-f911-4a7a-a47b-b91e788ee51b"

def hent_vaerdata(station_id: str) -> WeatherData:
    """
    Henter dei siste 24 timene med vær data fra frost API for en gitt stasjon
    """
    #Vi henter datafra Frost sitt ovservasjons-endepunkt

    endpoint = 'https://frost.met.no/observations/v0.jsonld'

    #Definerer tidsrommet (For eksempel de siste 24 timene fram til nå
    
    naa = datetime.utcnow()
    i_gaar = naa - timedelta(days=1)
    time_str = f"{i_gaar.strftime('%Y-%m-%dT%H:%M:%SZ')}/{naa.strftime('%Y-%m-%dT%H:%M:%SZ')}"

    #Parametere vi sender til forst API
    parameters = {
        'sources': station_id, 
        'elements': 'air_temperature,relative_humidity,wind_speed',
        'referencetime': time_str,
        'timeresolutions': 'PT1H' # Vi ønsker data med 1 times mellomrom
    }
    
    #Utfør selve API-kallet, og send med client ID som brukernavn (passord er tomt)
    response = requests.get(endpoint, parameters, auth=(Forst_Client_ID, ''))

    #sjekk omvi fekk et gylig svar (HTTP 200 ok)
    if response.status_code != 200:
        raise Exception(f"Feil ved henting av data: {response.status_code} - {response.text}")

    data = response.json()['data']

    #vi må bygge en liste med weatherdatapunk som trengs til brannmodellen
    datapunkter = []

    for item in data:
        timestamp = datetime.fromisoformat(item['referenceTime'].replace('Z', '+00:00'))

        #Variavler for å golde påverienefor dette tidspunktet
        temp = None
        hum = None
        wind = None

        ##Forst gir oss en liste med observarjoner per tidspunkt
        for obs in item['observations']:
            element_id = obs['elementId']
            if element_id == 'air_temperature':
                temp = obs['value']
            elif element_id == 'relative_humidity':
                hum = obs['value']
            elif element_id == 'wind_speed':
                wind = obs['value']

        #Vi legger baretil punkter hvis vi har alle tre veridene
        if temp is not None and hum is not None and wind is not None:
            point = WeatherDataPoint(
                timestamp=timestamp,
                temperature=temp,
                humidity=hum,
                wind_speed=wind
            )
            datapunkter.append(point)

    return WeatherData(data = datapunkter)