# Guía de Solución de Problemas: Django Tabler Icons

## Error Típico
```
ValueError at /tools/studio/{uuid}/
Icon x not found
```

## Síntomas del Problema
1. **Template Error**: `TemplateSyntaxError: Invalid block tag 'tabler_icons'. Did you forget to register or load this tag?`
2. **Icon Not Found**: `ValueError: Icon x not found`
3. **Página no carga**: Error 500 en plantillas que usan íconos

## Causa Raíz
El problema surge por **sintaxis incorrecta** en el uso de django-tabler-icons y **íconos no descargados**.

## Solución Completa (Paso a Paso)

### 1. Verificar Instalación
```bash
# En requirements.txt debe estar:
django-tabler-icons

# En settings.py debe estar:
INSTALLED_APPS = [
    # ...
    'tabler_icons',
    # ...
]
```

### 2. Corregir Sintaxis en Templates

#### ❌ **INCORRECTO** (Causa el error)
```django
{% load static tabler_icons %}              <!-- MAL: load con static -->
{% tabler_icons 'x' 'h-6 w-6' %}           <!-- MAL: tabler_icons con 's' -->
{% tabler_icon_outline 'x' 'h-6 w-6' %}    <!-- MAL: sin descargar íconos -->
```

#### ✅ **CORRECTO** (Funciona)
```django
{% load static %}
{% load tabler_icons %}                     <!-- BIEN: load separado -->
{% tabler_icon 'x' 'h-6 w-6' %}            <!-- BIEN: tabler_icon sin 's' -->
```

### 3. Descargar Íconos (CRÍTICO)
```bash
# Dentro del contenedor Docker:
docker-compose exec web python manage.py download_icons

# O fuera del contenedor (requiere confirmación):
django_tabler_icons download --yes
```

### 4. Coleccionar Archivos Estáticos
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 5. Reiniciar Servicios
```bash
docker-compose restart web
```

## Sintaxis Correcta - Referencia Rápida

### Template Tags Disponibles
```django
{% load tabler_icons %}

{% tabler_icon 'icon-name' 'css-classes' %}              <!-- Alias para outline -->
{% tabler_icon_outline 'icon-name' 'css-classes' %}      <!-- Estilo outline -->
{% tabler_icon_filled 'icon-name' 'css-classes' %}       <!-- Estilo filled -->
```

### Parámetros
1. **icon-name**: Nombre del ícono sin prefijo (ej: 'x', 'plus', 'search')
2. **css-classes**: Clases CSS opcionales (ej: 'w-5 h-5', 'text-gray-500')
3. **keep_default_classes**: 'no' para remover clases por defecto (opcional)

### Ejemplos Válidos
```django
{% tabler_icon 'x' 'h-6 w-6' %}
{% tabler_icon 'plus' 'w-5 h-5 text-blue-500' %}
{% tabler_icon 'search' 'absolute left-2.5 top-2 w-4 h-4 text-gray-500' %}
{% tabler_icon_filled 'heart' 'w-6 h-6 text-red-500' %}
```

## Diferencias Importantes

### django-tabler-icons vs otros paquetes
- **django-bootstrap-icons**: Usa `{% bs_icon 'name' %}`
- **django-icons**: Usa `{% icon 'name' %}`
- **django-tabler-icons**: Usa `{% tabler_icon 'name' %}` (sin 's')

### Template Tag vs Variable
```django
{% tabler_icon 'x' %}          <!-- Template tag (correcto) -->
{{ tabler_icon }}              <!-- Variable (incorrecto) -->
```

## Ubicación de Íconos Descargados
Los íconos se descargan automáticamente a:
- **Contenedor Docker**: `/root/.local/share/django-tabler-icons/icons/`
- **Sistema local**: `~/.local/share/django-tabler-icons/icons/` (Linux/Mac)
- **Windows**: `%LOCALAPPDATA%\django-tabler-icons\icons\`

## Troubleshooting Adicional

### Si sigue fallando después de la solución:

1. **Limpiar Cache de Django**
   ```bash
   docker-compose exec web python manage.py clearcache
   ```

2. **Verificar permisos de archivos**
   ```bash
   docker-compose exec web ls -la /root/.local/share/django-tabler-icons/
   ```

3. **Re-descargar íconos forzadamente**
   ```bash
   docker-compose exec web rm -rf /root/.local/share/django-tabler-icons/
   docker-compose exec web python manage.py download_icons
   ```

4. **Revisar logs detallados**
   ```bash
   docker-compose logs web | grep -i "tabler\|icon\|template"
   ```

## Prevención Futura

### Checklist de Implementación
- [ ] ✅ `django-tabler-icons` en requirements.txt
- [ ] ✅ `'tabler_icons'` en INSTALLED_APPS
- [ ] ✅ `{% load tabler_icons %}` (sin static)
- [ ] ✅ `{% tabler_icon 'name' %}` (sin 's' al final)
- [ ] ✅ Ejecutar `python manage.py download_icons`
- [ ] ✅ Ejecutar `collectstatic`
- [ ] ✅ Reiniciar servidor

### Template de Referencia
```django
{% load static %}
{% load tabler_icons %}

<!-- Navigation icons -->
{% tabler_icon 'layout-dashboard' 'w-5 h-5' %}
{% tabler_icon 'database' 'w-5 h-5' %}
{% tabler_icon 'flask' 'w-5 h-5' %}

<!-- Action icons -->
{% tabler_icon 'plus' 'w-4 h-4' %}
{% tabler_icon 'x' 'w-6 w-6' %}
{% tabler_icon 'search' 'w-4 h-4' %}
```

## Resolución Exitosa - 23 de agosto de 2025

### Problema Original
- Error: `ValueError: Icon x not found`
- Sintaxis mixta: `{% tabler_icon_outline %}` + `{% tabler_icon %}`
- Íconos no descargados

### Solución Aplicada
1. ✅ Corregido template loading: `{% load static %}` + `{% load tabler_icons %}`
2. ✅ Unificada sintaxis: Solo `{% tabler_icon 'name' %}` 
3. ✅ Descargados íconos: `python manage.py download_icons`
4. ✅ Colectados static files
5. ✅ Reiniciado servicios

### Resultado
- ✅ Página carga sin errores
- ✅ Todos los íconos se muestran correctamente
- ✅ Navigation y sidebar funcionando
- ✅ Data Studio completamente funcional

---

**Tiempo de resolución**: ~45 minutos
**Error frecuencia**: Medio (puede repetirse en nuevos deployments)
**Severidad**: Alta (bloquea completamente la UI)
**Solución permanente**: Documentada y validada