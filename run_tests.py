import subprocess
import sys


def instalar_dependencias():
    print("Instalando dependencias...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        check=True
    )


def limpiar_volumenes_anonimos():
    print("\nLimpiando volúmenes anónimos de Docker...")
    try:
        # Obtiene lista de volúmenes anónimos
        result = subprocess.run(
            ["docker", "volume", "ls", "--filter", "dangling=true", "-q"],
            capture_output=True, text=True
        )
        volumenes = result.stdout.strip().split("\n")
        volumenes = [v for v in volumenes if v]  # elimina líneas vacías

        if not volumenes:
            print("No hay volúmenes anónimos para eliminar.")
            return

        # Elimina cada volumen
        for volumen in volumenes:
            subprocess.run(["docker", "volume", "rm", volumen], capture_output=True)
            print(f"  ✅ Eliminado: {volumen}")

        print(f"\nTotal eliminados: {len(volumenes)} volúmenes")

    except Exception as e:
        print(f"Error al limpiar volúmenes: {e}")


def correr_pruebas():
    print("\nCorriendo suite de pruebas BDD...")
    resultado = subprocess.run(
        [sys.executable, "-m", "behave"],
        check=False
    )
    return resultado.returncode


def verificar_consistencia():
    print("\n" + "="*50)
    print("VERIFICANDO CONSISTENCIA - 3 EJECUCIONES")
    print("="*50 + "\n")

    resultados = []
    for i in range(1, 4):
        print(f"\n--- Ejecución {i} de 3 ---\n")
        codigo = correr_pruebas()
        resultados.append(codigo)
        print(f"\nEjecución {i}: {'✅ PASÓ' if codigo == 0 else '❌ FALLÓ'}")

    print("\n" + "="*50)
    print("RESUMEN DE CONSISTENCIA")
    print("="*50)
    for i, codigo in enumerate(resultados, 1):
        print(f"Ejecución {i}: {'✅ PASÓ' if codigo == 0 else '❌ FALLÓ'}")

    if all(c == 0 for c in resultados):
        print("\n✅ Suite consistente - todas las ejecuciones pasaron")
    else:
        print("\n❌ Suite inconsistente - hay pruebas intermitentes")

    return 0 if all(c == 0 for c in resultados) else 1


if __name__ == "__main__":
    instalar_dependencias()
    limpiar_volumenes_anonimos()
    codigo_salida = verificar_consistencia()
    sys.exit(codigo_salida)