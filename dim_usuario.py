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
tabla_usuario = pd.read_sql_table('clientes_usuarioaquitoy', mensajeria)

tabla_usuario.head(10)
tabla_usuario_django = pd.read_sql_table('auth_user', mensajeria)

tabla_usuario_django['is_active'].value_counts()
tabla_areas=pd.read_sql_table('area',mensajeria)

tabla_areas.head(10)
dim_usuario = pd.merge(tabla_usuario,tabla_areas,left_on='area_id',right_on='area_id', how='left')

dim_usuario = dim_usuario.drop(columns=['telefono','sede_id','ciudad_id','token_Firebase','descripcion','cliente_id','lider','area_id'])

dim_usuario = pd.merge(dim_usuario,tabla_usuario_django,left_on='user_id',right_on='id',how='left')

dim_usuario.drop(columns=['password','last_login','is_superuser','email','is_staff','is_active','date_joined','user_id','id_y'],inplace=True)

dim_usuario.rename(columns={'id_x':'id_persona','username':'nombre_usuario','first_name':'nombre','last_name':'apellido','nombre':'area_trabajo'}, inplace=True)

dim_usuario['key_usuario'] = range(1,len(dim_usuario)+1)

dim_usuario.head(10)
dim_usuario.nunique()

dim_usuario.to_sql('dim_usuario', etl_conn, if_exists='replace', index=False) 