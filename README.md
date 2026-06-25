# Proyecto Mensajería — Modelo Dimensional

Este proyecto construye un modelo dimensional (estrella) a partir de datos operativos de un servicio de mensajería, usando notebooks de Jupyter (`.ipynb`) y `pandas` para la transformación de datos.

## Requisitos previos

- **Python 3.11** instalado y agregado al PATH.
  Verifica la versión con:

  **Windows (PowerShell/CMD):**
  ```powershell
  python --version
  ```

  **Linux/macOS:**
  ```bash
  python3 --version
  ```
- **PostgreSQL** accesible (local o remoto), con las credenciales de conexión configuradas en `config.yml`.
- Git (opcional, solo si vas a clonar el repositorio).
- En Linux, es posible que necesites instalar el paquete de `venv` y las cabeceras de desarrollo de PostgreSQL antes de crear el entorno (necesarias para compilar dependencias como `psycopg2` si no se usa la variante `-binary`):
  ```bash
  sudo apt update
  sudo apt install python3-venv python3-dev libpq-dev
  ```

> ⚠️ El archivo `requirements.txt` original no incluía `psycopg2-binary`, necesario para la conexión a PostgreSQL (`import psycopg2`). Ya fue agregado en este archivo corregido.

## 1. Crear el entorno virtual

**Windows (PowerShell/CMD):**
```powershell
python -m venv venv
```

**Linux/macOS:**
```bash
python3 -m venv venv
```

Esto crea una carpeta `venv/` con un entorno de Python aislado.

## 2. Activar el entorno virtual

**Windows — PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows — CMD:**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS — bash/zsh:**
```bash
source venv/bin/activate
```

> Si PowerShell bloquea la ejecución del script con un error de política de ejecución, corre una sola vez (como usuario, no como administrador):
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

Sabrás que el entorno está activo porque verás `(venv)` al inicio de la línea de comandos, tanto en Windows como en Linux/macOS.

## 3. Instalar las dependencias

Con el entorno activado (en cualquiera de los dos sistemas, el comando es el mismo):

```bash
pip install -r requirements.txt
```

## 4. Configurar la conexión a la base de datos

Verifica que el archivo `config.yml` exista en la raíz del proyecto con los datos de conexión a PostgreSQL (host, puerto, usuario, contraseña, nombre de base de datos) que usan tus notebooks a través de `sqlalchemy`/`psycopg2`.

## 5. Registrar el entorno como kernel de Jupyter

Para que VS Code / Jupyter Notebook reconozcan el entorno virtual como kernel disponible (el comando es el mismo en Windows y Linux/macOS, con el entorno activado):

```bash
python -m ipykernel install --user --name=venv-mensajeria --display-name "Python (venv-mensajeria)"
```

Luego, al abrir cualquier `.ipynb` en VS Code o Jupyter, selecciona el kernel **"Python (venv-mensajeria)"**.

## 6. Orden de ejecución de los notebooks

Es **obligatorio** ejecutar los notebooks en este orden, ya que los notebooks de hechos dependen de las tablas de transformación intermedia y de todas las dimensiones ya construidas.

### Paso 1 — Dimensiones (orden indistinto entre ellas)

Ejecuta cada uno de estos notebooks de forma independiente (no dependen entre sí):

- `dim_usuario.ipynb`
- `dim_fecha.ipynb`
- `dim_geografia.ipynb`
- `dim_hora.ipynb`
- `dim_mensajero.ipynb`
- `dim_novedades.ipynb`
- `dim_proveedor.ipynb`
- `dim_sede.ipynb`

> `dim_pruebas.ipynb` es un notebook de pruebas/exploración y **no es necesario** para el flujo principal.

### Paso 2 — Transformación intermedia

Ejecuta:

- `trans_servicios.ipynb`

Este notebook limpia y pivotea los datos crudos de servicios (fechas y horas por estado) y prepara la tabla intermedia que usarán los notebooks de hechos.

### Paso 3 — Tablas de hechos (al final, en este orden)

Ejecuta, en este orden:

1. `hecho_servicios.ipynb`
2. `hecho_novedades.ipynb`

Estos notebooks dependen de que **todas las dimensiones del Paso 1** y la tabla intermedia del Paso 2 ya existan/estén cargadas, ya que hacen `merge` contra ellas para obtener las llaves sustitutas (`key_dim_*`).

## Resumen visual del flujo

```
dim_usuario ─┐
dim_fecha ───┤
dim_geografia┤
dim_hora ────┼──► trans_servicios ──► hecho_servicios
dim_mensajero┤                   └──► hecho_novedades
dim_novedades┤
dim_proveedor┤
dim_sede ────┘
```

## 7. Desactivar el entorno virtual

Cuando termines de trabajar (mismo comando en ambos sistemas):

```bash
deactivate
```
