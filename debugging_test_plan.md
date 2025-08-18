# 🔧 PLAN DE TESTING - DEBUGGING FORMULARIO "NUEVO EXPERIMENTO"

## Objetivo
Verificar el flujo completo de datos desde la selección de DataSource hasta la población de dropdowns usando los logs implementados.

## Metodología de Testing

### 1. **Testing Frontend** 🖥️
- [ ] Abrir formulario "Nuevo Experimento"
- [ ] Verificar logs de inicialización en consola de navegador
- [ ] Seleccionar un DataSource
- [ ] Verificar logs del evento onChange
- [ ] Verificar construcción de URL de API
- [ ] Verificar llamada fetch()

### 2. **Testing Backend** 🐍
- [ ] Verificar logs de Django en terminal
- [ ] Confirmar recepción de requests a `/api/get-columns/<uuid>/`
- [ ] Verificar validación de DataSource
- [ ] Verificar lectura de archivo
- [ ] Verificar respuesta JSON

### 3. **Testing de Conectividad** 🌐
- [ ] Verificar que URL patterns están correctos
- [ ] Verificar que API endpoint es accesible
- [ ] Verificar headers de request/response

### 4. **Testing de Datos** 📊
- [ ] Verificar que DataSource tiene archivo válido
- [ ] Verificar que archivo se puede leer con pandas
- [ ] Verificar que columnas se extraen correctamente

## Comandos de Verificación

```bash
# Verificar contenedores
docker ps -a

# Ver logs de Django
docker-compose logs -f web

# Ver logs de worker
docker-compose logs -f worker

# Acceder a contenedor para debugging
docker-compose exec web bash
```

## Puntos de Verificación Críticos

1. **Elemento DOM `id_input_datasource` existe** ✅
2. **Event listener se registra correctamente** ✅
3. **URL template está disponible en dataset** ✅
4. **Fetch request se envía** ✅
5. **Backend recibe request** ✅
6. **DataSource se valida exitosamente** ✅
7. **Archivo se lee correctamente** ✅
8. **Respuesta JSON es válida** ✅
9. **Frontend procesa respuesta** ✅
10. **Dropdowns se actualizan** ✅

## Resultados Esperados

- Console logs detallados del flujo completo
- Identificación precisa del punto de falla
- Datos específicos sobre el error (si existe)
- Path hacia la solución definitiva
