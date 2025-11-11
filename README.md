# Farm Stock — Django Project

Farm Stock es un sistema web desarrollado en Django para gestionar y visualizar el stock de farmacia.  
Permite administrar inventario, monitorear movimientos y brindar acceso desde múltiples equipos dentro de la red local.

---

## ✅ Requerimientos
- Python 3.10+
- Django (instalado desde `requirements.txt`)
- Acceso a base de datos configurado en `.env`

---

## 🚀 Instalación

### 1️⃣ Clonar el repositorio
git clone <URL_REPO>
cd farm-stock

---

### 2️⃣ Crear archivo `.env`
Copiar el archivo de ejemplo:
cp env.example .env

Completar las variables según corresponda:
SECRET_KEY=
DEBUG=
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASS=

---

### 3️⃣ Crear entorno virtual (fuera del proyecto)
cd ..
python -m venv venv

---

### 4️⃣ Activar entorno virtual

Windows:
venv\Scripts\activate

Linux / Mac:
source venv/bin/activate

---

### 5️⃣ Instalar dependencias
pip install -r farm-stock/requirements.txt

---

### 6️⃣ Aplicar migraciones
cd farm-stock
python manage.py migrate

---

### 7️⃣ Ejecutar el servidor accesible por la red
python manage.py runserver 0.0.0.0:8000

---

## 🌐 Acceso desde otras computadoras
1. Obtener IP del servidor  
   Windows:
   ipconfig

   Linux/macOS:
   ifconfig

2. Desde cualquier PC en la red abrir:
   http://<IP_DEL_SERVIDOR>:8000

Ejemplo:
   http://192.168.0.25:8000

⚠️ Asegurarse de permitir el puerto 8000 en el firewall.

---

### (Opcional) Crear usuario administrador
python manage.py createsuperuser

---

## ✅ Resumen rápido
1. cp env.example .env
2. Crear y activar entorno virtual
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py runserver 0.0.0.0:8000
6. Acceder vía navegador desde la red
