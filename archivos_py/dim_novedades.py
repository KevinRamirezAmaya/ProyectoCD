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

tabla_novedades = pd.read_sql_table('mensajeria_novedadesservicio',mensajeria)

tabla_novedades['tipo_novedad_id'].value_counts()
tabla_novedades.head(10)

tabla_tiponovedad = pd.read_sql_table('mensajeria_tiponovedad', mensajeria)
tabla_tiponovedad.head(10)

import re

def clasificar_novedad(desc):
    if not isinstance(desc, str):
        return "Sin especificar"
    desc_lower = desc.lower().strip()
    
    if any(k in desc_lower for k in ["pinche", "pinch", "vare", "guaya", "llanta", "daño", "dao", "mecanic", "trafico", "trfico", "tránsito"]):
        return "Problema de Vehículo / Tránsito"
    if any(k in desc_lower for k in ["compañero", "compaero", "toma otro", "hace otro", "realiza otro", "así el", "as el", "asé el", "lleva", "entrego a", "trasbordo", "lo toma", "lo hace", "lo realiza"]):
        return "Reasignación / Trasbordo de Mensajero"
    if any(k in desc_lower for k in ["alist", "despach", "factur", "referencia", "buscando", "prepar", "bodega", "almacen", "almacén"]):
        return "Espera de Alistamiento / Facturación"
    if any(k in desc_lower for k in ["cerrado", "cerr", "almuerzo", "horario de atencion", "abierto", "no abre"]):
        return "Establecimiento Cerrado / Almuerzo"
    if any(k in desc_lower for k in ["no se encuentra", "no esta", "no est", "reunion", "reunin", "no contesta", "no responde", "no respondio", "ausente", "no ha llegado", "no a llegado", "no ah llegado"]):
        return "Cliente / Contacto No Disponible"
    if any(k in desc_lower for k in ["cancel", "reprogram"]):
        return "Cancelado / Reprogramado"
        
    has_moto = re.search(r'\bmoto\b', desc_lower) or "es de moto" in desc_lower or "moto carguero" in desc_lower
    has_camioneta = "camioneta" in desc_lower or "carro" in desc_lower
    if any(k in desc_lower for k in ["no coincide", "direccion", "direccin", "mal colocado", "mal programado", "documento"]) or has_moto or has_camioneta:
        return "Error en Datos / Tipo de Vehículo"
        
    if any(k in desc_lower for k in ["espera", "sigo en", "sigo a la", "turno", "banco", "consign", "cola", "ingreso", "autoricen", "porteria"]):
        return "Espera de Turno / Fila / Trámite"
        
    return "Otros / Comentarios Varios"

dim_novedades= pd.merge(tabla_novedades,tabla_tiponovedad, left_on='tipo_novedad_id', right_on='id', how='left')
dim_novedades = dim_novedades.drop(columns=['id_y','mensajero_id','tipo_novedad_id'])
dim_novedades['key_novedad'] = range(1,len(dim_novedades)+1)
dim_novedades = dim_novedades.rename(columns={'id_x': 'novedad_id'})
dim_novedades['grupo_novedad'] = dim_novedades['descripcion'].apply(clasificar_novedad)
dim_novedades.head(10)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)
df = pd.read_sql_table('mensajeria_estadosservicio', mensajeria)
df[df['servicio_id'] == 21953].head(100).T

dim_novedades['descripcion'].value_counts()

dim_novedades.to_sql('dim_novedades', etl_conn, if_exists='replace', index=False)
