from econolab.data_engine.importador import importar_archivo
from econolab.data_engine.diagnostico import diagnosticar_datos
from econolab.data_engine.recomendaciones import generar_recomendaciones
from econolab.data_engine.limpieza import SesionLimpieza


# 1. Importar archivo
ruta = "../econolab_pruebas/econolab_pruebas/datos_prueba/pib.csv"

resultado = importar_archivo(ruta)

datos = resultado["datos"]


# 2. Diagnosticar datos
informe = diagnosticar_datos(datos)


# 3. Mostrar resultados
print("\n========== ECONOLAB ==========")
print("DIAGNÓSTICO INICIAL")
print("==============================")

print(f"\nArchivo: {resultado['nombre']}")
print(f"Filas: {informe['filas']}")
print(f"Columnas: {informe['numero_columnas']}")

print(f"\nFilas completamente vacías: {informe['filas_vacias']}")
print(f"Columnas completamente vacías: {informe['columnas_vacias']}")
print(f"Filas duplicadas: {informe['filas_duplicadas']}")


print("\n--- ANÁLISIS POR VARIABLE ---")

for columna, informacion in informe["detalle_columnas"].items():

    print(f"\nVariable: {columna}")
    print(f"  Tipo: {informacion['tipo']}")
    print(f"  Valores vacíos: {informacion['valores_vacios']}")
    print(f"  Valores únicos: {informacion['valores_unicos']}")

# 4. Generar recomendaciones
recomendaciones = generar_recomendaciones(datos, informe)


# 5. Mostrar recomendaciones
print("\n========== RECOMENDACIONES ==========")

if recomendaciones:

    for numero, recomendacion in enumerate(recomendaciones, start=1):

        print(f"\n{numero}. {recomendacion['problema']}")
        print(f"   Cantidad: {recomendacion['cantidad']}")
        print(f"   Gravedad: {recomendacion['gravedad']}")
        print(f"   Acción propuesta: {recomendacion['accion']}")

        if recomendacion["automatico"]:
            print("   Tipo: Acción automática segura")
        else:
            print("   Tipo: Requiere aprobación del usuario")

else:
    print("No se han detectado problemas.")

# 6. Iniciar sesión de limpieza
sesion = SesionLimpieza(datos)

print("\n========== MOTOR DE LIMPIEZA ==========")

print("\nEstado inicial:")
print("Filas:", len(sesion.actual))
print("Columnas:", len(sesion.actual.columns))


# 7. Ejecutar operaciones
print("\n--- OPERACIONES ---")

print(sesion.eliminar_filas_vacias())
print(sesion.eliminar_columnas_vacias())
print(sesion.normalizar_nombres_columnas())


# 8. Mostrar estado después de la limpieza
print("\nEstado después de la limpieza:")
print("Filas:", len(sesion.actual))
print("Columnas:", len(sesion.actual.columns))


# 9. Mostrar historial
print("\n--- HISTORIAL ---")

for operacion in sesion.mostrar_registro():
    print(operacion["operacion"])


# 10. Deshacer las operaciones
print("\n--- DESHACER ---")

print(sesion.deshacer())
print(sesion.deshacer())
print(sesion.deshacer())


# 11. Comprobar recuperación
print("\n--- COMPROBACIÓN FINAL ---")

print("¿Se recuperaron los datos originales?")
print(sesion.actual.equals(sesion.original))