import os
import time
import subprocess
from datetime import datetime
from netmiko import ConnectHandler

# --- CONFIGURACIÓN DE ROUTERS ---
equipos_cisco = [
    {
        "device_type": "cisco_ios",
        "ip": "192.168.126.101",
        "username": "admin",
        "password": "cisco123",
        "nombre": "Router1"
    },
    {
        "device_type": "cisco_ios",
        "ip": "192.168.126.102",
        "username": "admin",
        "password": "cisco123",
        "nombre": "Router2"
    },
    {
        "device_type": "cisco_ios",
        "ip": "192.168.126.103",
        "username": "admin",
        "password": "cisco123",
        "nombre": "Router3"
    }
]

DIRECTORIO_BASE = "respaldos"

def enviar_a_github(mensaje_commit):
    try:
        print(" [Git] Cambios detectados. Subiendo al repositorio...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", mensaje_commit], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(" [Git] ¡Respaldo subido a GitHub exitosamente!")
    except Exception as e:
        print(f" [Git Error] No se pudo realizar el push: {e}")

def obtener_ultimo_backup(carpeta_router):
    if not os.path.exists(carpeta_router):
        return None
    archivos = [os.path.join(carpeta_router, f) for f in os.listdir(carpeta_router) if f.endswith('.txt')]
    if not archivos:
        return None
    archivo_reciente = max(archivos, key=os.path.getmtime)
    with open(archivo_reciente, 'r', encoding='utf-8') as f:
        return f.read()

def realizar_backup(dispositivo):
    nombre_dev = dispositivo["nombre"]
    carpeta_router = os.path.join(DIRECTORIO_BASE, nombre_dev)
    os.makedirs(carpeta_router, exist_ok=True)
    
    try:
        params_conexion = dispositivo.copy()
        params_conexion.pop("nombre")
        
        conexion = ConnectHandler(**params_conexion)
        config_nueva = conexion.send_command("show running-config")
        conexion.disconnect()
        
        config_anterior = obtener_ultimo_backup(carpeta_router)
        
        if config_anterior and config_anterior.strip() == config_nueva.strip():
            print(f" [{nombre_dev}] Sin cambios detectados. Se conserva versión previa.")
        else:
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{nombre_dev}_backup_{fecha_str}.txt"
            ruta_completa = os.path.join(carpeta_router, nombre_archivo)
            
            with open(ruta_completa, "w", encoding="utf-8") as f:
                f.write(config_nueva)
                
            print(f" [✓ {nombre_dev}] ¡Configuración modificada! Guardado en: {ruta_completa}")
            
            msg_commit = f"Backup {nombre_dev} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            enviar_a_github(msg_commit)

    except Exception as error:
        print(f" [X Error {nombre_dev}]: {error}")

if __name__ == "__main__":
    print("==================================================")
    print("   INICIANDO SERVICIO AUTOMÁTICO DE NCM BACKUP   ")
    print("==================================================")
    
    while True:
        print(f"\n--- Comprobando estado de routers [{datetime.now().strftime('%H:%M:%S')}] ---")
        for router in equipos_cisco:
            realizar_backup(router)
        
        print("Esperando 5 segundos...")
        time.sleep(5)