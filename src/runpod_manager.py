#!/usr/bin/env python3
"""
RunPod Auto Manager
Automatiza start/stop de pods para minimizar costos

Usage:
    export RUNPOD_API_KEY="your_key"
    export RUNPOD_POD_ID="your_pod_id"

    python runpod_manager.py start
    python runpod_manager.py stop
    python runpod_manager.py status
"""

import os
import sys
import time
import requests
import json

RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY')
RUNPOD_POD_ID = os.getenv('RUNPOD_POD_ID')
RUNPOD_API_URL = "https://api.runpod.io/graphql"


def check_credentials():
    """Verificar que las credenciales estén configuradas"""
    if not RUNPOD_API_KEY:
        print("❌ Error: RUNPOD_API_KEY no configurada")
        print("\n💡 Configura con:")
        print("   export RUNPOD_API_KEY='your_api_key'")
        sys.exit(1)

    if not RUNPOD_POD_ID:
        print("❌ Error: RUNPOD_POD_ID no configurada")
        print("\n💡 Configura con:")
        print("   export RUNPOD_POD_ID='your_pod_id'")
        sys.exit(1)


def make_graphql_request(query):
    """
    Hacer request a la API de RunPod
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RUNPOD_API_KEY}"
    }

    try:
        response = requests.post(
            RUNPOD_API_URL,
            json={"query": query},
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def get_pod_status():
    """Obtener status actual del pod"""
    query = """
    query {
        pod(input: {podId: "%s"}) {
            id
            name
            runtime {
                uptimeInSeconds
            }
            desiredStatus
            machine {
                gpuDisplayName
                podHostId
            }
        }
    }
    """ % RUNPOD_POD_ID

    result = make_graphql_request(query)

    if result and 'data' in result and result['data']['pod']:
        return result['data']['pod']
    else:
        print(f"❌ Error obteniendo status del pod")
        if result and 'errors' in result:
            print(f"   Errores: {result['errors']}")
        return None


def start_pod():
    """Start pod y esperar hasta que esté ready"""
    print("🚀 Starting RunPod...")

    query = """
    mutation {
        podResume(input: {podId: "%s"}) {
            id
            desiredStatus
        }
    }
    """ % RUNPOD_POD_ID

    result = make_graphql_request(query)

    if not result or 'errors' in result:
        print(f"❌ Error iniciando pod")
        if result and 'errors' in result:
            print(f"   Errores: {result['errors']}")
        return False

    print("✅ Pod starting...")
    print("⏳ Esperando hasta que esté ready...")

    # Esperar hasta ready (máximo 5 minutos)
    max_wait = 300  # 5 minutos
    start_time = time.time()

    while time.time() - start_time < max_wait:
        status = get_pod_status()

        if status and status['desiredStatus'] == "RUNNING":
            uptime = status.get('runtime', {}).get('uptimeInSeconds', 0)
            if uptime > 10:  # Dar 10 segundos de gracia
                print("✅ Pod ready!")
                print(f"   GPU: {status['machine']['gpuDisplayName']}")
                return True

        time.sleep(10)
        print("   ⏳ Esperando...")

    print("❌ Timeout esperando pod ready")
    return False


def stop_pod():
    """Stop pod para no incurrir costos"""
    print("🛑 Stopping RunPod...")

    query = """
    mutation {
        podStop(input: {podId: "%s"}) {
            id
            desiredStatus
        }
    }
    """ % RUNPOD_POD_ID

    result = make_graphql_request(query)

    if not result or 'errors' in result:
        print(f"❌ Error deteniendo pod")
        if result and 'errors' in result:
            print(f"   Errores: {result['errors']}")
        return False

    print("✅ Pod stopped - no más billing")
    return True


def show_status():
    """Mostrar status detallado del pod"""
    print("📊 Pod Status:\n")

    status = get_pod_status()

    if not status:
        return False

    print(f"ID: {status['id']}")
    print(f"Name: {status['name']}")
    print(f"Status: {status['desiredStatus']}")

    if status.get('machine'):
        print(f"GPU: {status['machine']['gpuDisplayName']}")

    if status.get('runtime'):
        uptime = status['runtime']['uptimeInSeconds']
        hours = uptime / 3600
        print(f"Uptime: {uptime}s ({hours:.2f} horas)")

        # Calcular costo aproximado (asumiendo $0.19/hora)
        cost = hours * 0.19
        print(f"Costo aproximado actual: ${cost:.2f}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python runpod_manager.py [start|stop|status]")
        sys.exit(1)

    check_credentials()

    command = sys.argv[1].lower()

    if command == 'start':
        success = start_pod()
    elif command == 'stop':
        success = stop_pod()
    elif command == 'status':
        success = show_status()
    else:
        print(f"❌ Comando desconocido: {command}")
        print("   Comandos disponibles: start, stop, status")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
