# 2.3GD

# Validación de Dataset con Python

Este proyecto implementa un script modular en Python para la limpieza y validación de un dataset de ventas que contiene errores intencionados (duplicados, valores nulos, fechas inexistentes y edades fuera de rango).

## Estructura del Proyecto
- `validacion.py`: Script principal con la lógica de validación.
- `ventas_sucias.csv`: Dataset original con errores.
- `registros_validos.csv`: Datos que pasaron todas las pruebas.
- `registros_erroneos.csv`: Datos rechazados.
- `validacion.log`: Registro detallado de cada error encontrado.

## Validaciones Implementadas

### Estructurales
1. **Detección de Duplicados**: Se identifican registros con IDs repetidos.
2. **Campos Obligatorios**: Validación de celdas vacías o con espacios en blanco en columnas clave.
3. **Consistencia de Tipos**: Verificación de que los montos económicos sean convertibles a formato numérico.

### Semánticas
1. **Rango de Edad**: Se filtran edades biológicamente imposibles (ej. 150 años).
2. **Integridad de Fecha**: Se validan las fechas contra un calendario real, detectando meses inexistentes (ej. mes 13).

## Decisiones Técnicas
- **Modularización**: Se utilizó una clase `DataValidator` para separar la lógica de carga, validación y exportación.
- **Logging**: Se implementó la librería `logging` de Python para generar trazabilidad del proceso sin interrumpir la ejecución.
- **Estandarización**: Los registros válidos pasan por un proceso de "normalización" (Title Case para ciudades y Lower Case para métodos de pago).
