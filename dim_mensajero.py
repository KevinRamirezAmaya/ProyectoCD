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
tabla_mensajero = pd.read_sql_table('clientes_mensajeroaquitoy', mensajeria)

tabla_mensajero.head(10)

tabla_mensajero['activo'].value_counts()
tabla_persona = pd.read_sql_table('auth_user', mensajeria)

tabla_persona.head(10)

tabla_ciudad = pd.read_sql_table('ciudad', mensajeria)

tabla_ciudad.head(10)
dim_mensajero=pd.merge(tabla_mensajero,tabla_persona, left_on='user_id',right_on='id', how='left' )

dim_mensajero['key_mensajero'] = range(1,len(dim_mensajero)+1)

dim_mensajero.drop(columns=['user_id','fecha_entrada','fecha_salida','salario','telefono','activo','is_superuser','email',

                            'token_Firebase','url_foto','id_y','password','last_login','is_staff','is_active','date_joined'], inplace=True)

dim_mensajero=pd.merge(dim_mensajero,tabla_ciudad, left_on='ciudad_operacion_id',right_on='ciudad_id', how='left' )

dim_mensajero.drop(columns=['ciudad_operacion_id','ciudad_id','departamento_id','first_name','last_name'], inplace=True)

dim_mensajero.rename(columns={'nombre':'ciudad_operacion','id_x':'id_operaciones','username':'nombre',}, inplace=True)

#Aun falta hacer limpieza de datos, pero por ahora se deja asi para poder cargar la tabla en el data warehouse

#Hay que limpiar username, reemplazar estos como el nuevo first y last name

dim_mensajero.head(10)
def limpiar_nombre_mensajero(nombre):

    if not isinstance(nombre, str):

        return nombre

    

    # 1. Limpieza estándar inicial (reemplazar guiones y guiones bajos por espacios)

    nombre_limpio = nombre.replace('_', ' ').replace('-', ' ').strip()

    

    # 2. Diccionario de corrección exacta para los 50 casos del negocio

    correcciones = {

        # Nombres pegados y acentos

        'JHONTROCHEZ': 'Jhon Tróchez',

        'ANDRESGUTIERREZ': 'Andrés Gutiérrez',

        'LUISCARDONA': 'Luis Cardona',

        'ALEXANDERMOSQUERA': 'Alexander Mosquera',

        'JHONMUÑOZ': 'Jhon Muñoz',

        'CARLOSGONZALEZ': 'Carlos González',

        'VICTORARARAT': 'Víctor Ararat',

        'YESYDVINASCO': 'Yesyd Vinasco',

        'LUISGIL': 'Luis Gil',

        'JOELVILLADA': 'Joel Villada',

        'JULIANVILLANUEVA': 'Julián Villanueva',

        'ESTEBANMUÑOZ': 'Esteban Muñoz',

        'JONATANMANZANO': 'Jonatan Manzano',

        'DANIELMAZUERA': 'Daniel Mazuera',

        'ALEXISLASSO': 'Alexis Lasso',

        'JORGEMOSQUERA': 'Jorge Mosquera',

        'HENRYCARABALI': 'Henry Carabalí',

        'WILSONMORALES': 'Wilson Morales',

        

        # Iniciales y abreviaciones

        'JPEDROZA': 'J. Pedroza',

        'RVALLEJO': 'R. Vallejo',

        'BMAYORGA': 'B. Mayorga',

        'HVARGAS': 'H. Vargas',

        'JSANCHEZ': 'J. Sánchez',

        'YBOLANOS': 'Y. Bolaños',

        'ADELGADO': 'A. Delgado',

        

        # Corrección de acentos y nombres con espacios/errores

        'Sebastian Acuña': 'Sebastián Acuña',

        'Laura Acuña': 'Laura Acuña',

        'Nicolas Maduro': 'Nicolás Maduro',

        'Biil Gates': 'Bill Gates',

        'James Rodriguez': 'James Rodríguez',

        'Hector Aquiles': 'Héctor Aquiles',

        'Yeison Jimenez': 'Yeison Jiménez',

        

        # Casos especiales/Administrativos

        'admin': 'Admin',

        'mensajero1': 'Mensajero 1',

        'mensajero2': 'Mensajero 2',

        'mensajero o': 'Mensajero O',

    }

    

    # Si el nombre limpio está en nuestro diccionario, devolvemos su valor corregido

    if nombre_limpio in correcciones:

        return correcciones[nombre_limpio]

        

    # Si es un nombre normal con espacios (ej. "Juan Solano"), le aplicamos formato de nombre propio

    return nombre_limpio.title()



dim_mensajero['nombre'] = dim_mensajero['nombre'].apply(limpiar_nombre_mensajero)

# 2. Reconstruir 'first_name' y 'last_name' limpios a partir de 'nombre'

dim_mensajero['first_name'] = dim_mensajero['nombre'].apply(

    lambda x: x.split(' ', 1)[0] if isinstance(x, str) else ''

)

dim_mensajero['last_name'] = dim_mensajero['nombre'].apply(

    lambda x: x.split(' ', 1)[1] if isinstance(x, str) and len(x.split(' ', 1)) > 1 else ''

)

# Visualizar el DataFrame final

dim_mensajero.head(10)

dim_mensajero.to_sql('dim_mensajero', etl_conn, if_exists='replace', index=False) 