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




def generar_dim_fecha(fecha_inicio: str, fecha_fin: str) -> pd.DataFrame:

    # Genera un rango de todos los días entre las dos fechas

    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')

    dias_es = {

        1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves',

        5: 'Viernes', 6: 'Sábado', 7: 'Domingo'

    }

    meses_es = {

        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',

        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',

        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'

    }

    df = pd.DataFrame({'fecha': fechas})

    

    # Clave sustituta: formato YYYYMMDD como entero

    df['key_fecha'] = df['fecha'].dt.strftime('%Y%m%d').astype(int)

    

    # Atributos de negocio

    df['fecha_completa']     = df['fecha'].dt.date

    df['año']                = df['fecha'].dt.year

    df['mes']                = df['fecha'].dt.month

    df['nombre_mes']         = df['fecha'].dt.strftime('%B')  

    df['nombre_mes']         = df['mes'].map(meses_es)      

    df['trimestre']          = df['fecha'].dt.quarter

    df['semana_año']         = df['fecha'].dt.isocalendar().week.astype(int)

    df['dia_mes']            = df['fecha'].dt.day

    df['dia_semana']         = df['fecha'].dt.dayofweek + 1 

       

          

    df['nombre_dia']         = df['fecha'].dt.strftime('%A')  

    df['nombre_dia']         = df['dia_semana'].map(dias_es)       

    df['es_fin_semana']      = df['fecha'].dt.dayofweek >= 5        

    df['es_festivo']         = False 

    

    

    df['es_dia_habil']       = ~df['es_fin_semana'] & ~df['es_festivo']

    

    return df[['key_fecha', 'fecha_completa', 'año', 'trimestre',

               'mes', 'nombre_mes', 'semana_año', 'dia_mes',

               'dia_semana', 'nombre_dia', 'es_fin_semana',

               'es_festivo', 'es_dia_habil']]





dim_fecha = generar_dim_fecha('2020-01-01', '2027-12-31')

dim_fecha.head(10)
dim_fecha.to_sql('dim_fecha', etl_conn, if_exists='replace', index=False)