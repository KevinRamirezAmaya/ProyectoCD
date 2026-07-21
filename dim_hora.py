import pandas as pd

import numpy as np

import psycopg2

import sqlalchemy as db

from sqlalchemy import create_engine

import yaml
with open('.\\config.yml', 'r') as f:

    config = yaml.safe_load(f)

    config_co = config['mensajeria']

    config_etl = config['ETL_PRO']



# Construct the database URL

url_co = (f"{config_co['drivername']}://{config_co['user']}:{config_co['password']}@{config_co['host']}:"

          f"{config_co['port']}/{config_co['dbname']}")

url_etl = (f"{config_etl['drivername']}://{config_etl['user']}:{config_etl['password']}@{config_etl['host']}:"

           f"{config_etl['port']}/{config_etl['dbname']}")

# Create the SQLAlchemy Engine

mensajeria = create_engine(url_co)

etl_conn = create_engine(url_etl)
def generar_dim_hora() -> pd.DataFrame:

    

    segundos = pd.date_range(start='00:00:00', end='23:59:59', freq='1s')

    

    df = pd.DataFrame({'tiempo': segundos})

    

    # Clave sustituta: HHMMSS como entero (0 a 235959)

    df['key_hora'] = df['tiempo'].dt.strftime('%H%M%S').astype(int)

    

    # Atributos

    df['hora']         = df['tiempo'].dt.hour

    df['minutos']      = df['tiempo'].dt.minute

    df['segundos']     = df['tiempo'].dt.second

    df['hora_formato'] = df['tiempo'].dt.strftime('%H:%M:%S')

    df['hora_completa'] = df['tiempo'].dt.time

    start_hour = (df['hora'] // 3) * 3

    end_hour = start_hour + 3

    df['hora_rango'] = start_hour.astype(str).str.zfill(2) + '-' + end_hour.astype(str).str.zfill(2)

    

    # Franjas horarias

    df['franja'] = pd.cut(

        df['hora'],

        bins=  [0,  6, 12, 14, 18, 21, 24],

        labels=['madrugada', 'mañana', 'mediodía', 'tarde', 'noche', 'noche alta'],

        right=False

    )

    

    df['es_hora_habil'] = (df['hora'] >= 8) & (df['hora'] < 18)

    

    return df[['key_hora', 'hora', 'minutos', 'segundos','hora_completa',

               'hora_formato', 'franja', 'es_hora_habil']]





dim_hora = generar_dim_hora()

print(dim_hora.shape)   # (86400, 7) → 86.400 segundos en un día

print(dim_hora.tail())

print(dim_hora['hora_completa'].iloc[0])  # 00:00:00
dim_hora.info()
dim_hora.to_sql('dim_hora', etl_conn, if_exists='replace', index=False)