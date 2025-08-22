# 📄 Implementar Paginación Básica en Data Studio

## 🎯 Objetivo

Agregar paginación funcional a la tabla HTML del Data Studio para permitir navegación a través de todas las filas de datos disponibles (actualmente limitado a 10 de 50 filas totales).

## 📋 Descripción

Implementar un sistema de paginación simple y eficiente que permita a los usuarios navegar por los datos del DataSource sin sobrecargar la interfaz. La implementación debe mantener la estabilidad actual del template limpio.

## 🔧 Especificaciones Técnicas

### Frontend (JavaScript Puro)
- **Controles de paginación:** Botones Previous/Next + números de página
- **Opciones de filas por página:** 10, 20, 50, 100
- **Información de estado:** "Mostrando X-Y de Z registros"
- **Navegación rápida:** Ir a primera/última página

### Backend (Django)
- **API endpoint:** `/api/data-studio/{datasource_id}/paginated-data/`
- **Parámetros:** `page`, `page_size`, `offset`
- **Response:** JSON con `data`, `total_count`, `has_next`, `has_previous`

### UI/UX
- **Posición:** Debajo de la tabla, centrado
- **Responsive:** Funcional en mobile y desktop  
- **Accesibilidad:** ARIA labels y navegación por teclado
- **Performance:** Carga bajo demanda (AJAX)

## 📊 Casos de Uso

### Caso de Uso 1: Navegación Básica
**Como:** Investigador analizando datos  
**Quiero:** Ver más de 10 filas de datos  
**Para:** Analizar dataset completo sin limitaciones  

**Flujo:**
1. Usuario ve tabla con 10 filas iniciales
2. Ve controles de paginación: "← Anterior | 1 [2] 3 4 5 | Siguiente →"
3. Click en "2" carga filas 11-20
4. Click en "Siguiente" carga filas 21-30
5. Puede cambiar a "50 por página" para ver más datos

### Caso de Uso 2: Navegación Rápida
**Como:** Usuario con dataset grande  
**Quiero:** Saltar rápidamente al final de los datos  
**Para:** Ver las últimas entradas sin hacer muchos clicks  

**Flujo:**
1. Click en "Última página" va directamente a la página final
2. Selector de "100 por página" muestra más datos por pantalla
3. Campo "Ir a página X" permite salto directo

## 🛠️ Implementación

### 1. Modelo Django (sin cambios)
```python
# El modelo DataSource ya existe, no requiere modificaciones
# Solo necesitamos optimizar las queries
```

### 2. Vista Django Actualizada
```python
# data_tools/views/data_studio_views.py
def data_studio_paginated_api(request, datasource_id):
    """API para datos paginados"""
    datasource = get_object_or_404(DataSource, id=datasource_id)
    
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    # Calcular offset
    offset = (page - 1) * page_size
    
    # Obtener datos paginados
    df = load_datasource_data(datasource)
    total_count = len(df)
    
    # Slice de datos
    paginated_data = df.iloc[offset:offset + page_size]
    
    return JsonResponse({
        'data': [list(row.values()) for row in paginated_data.to_dict('records')],
        'columns': list(df.columns),
        'total_count': total_count,
        'current_page': page,
        'page_size': page_size,
        'has_next': offset + page_size < total_count,
        'has_previous': page > 1,
        'total_pages': math.ceil(total_count / page_size)
    })
```

### 3. JavaScript para Paginación
```javascript
// data_tools/static/data_tools/js/pagination-manager.js
class PaginationManager {
    constructor(datasourceId, containerId) {
        this.datasourceId = datasourceId;
        this.container = document.getElementById(containerId);
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalCount = 0;
        this.totalPages = 0;
        
        this.init();
    }
    
    async init() {
        await this.loadPage(1);
        this.renderPaginationControls();
        this.setupEventListeners();
    }
    
    async loadPage(page) {
        try {
            const response = await fetch(
                `/api/data-studio/${this.datasourceId}/paginated-data/?page=${page}&page_size=${this.pageSize}`
            );
            const data = await response.json();
            
            this.updateTableData(data);
            this.updatePaginationState(data);
            
        } catch (error) {
            console.error('Error loading page:', error);
        }
    }
    
    updateTableData(data) {
        // Actualizar tbody de la tabla con nuevos datos
        const tbody = document.querySelector('table tbody');
        tbody.innerHTML = data.data.map(row => 
            `<tr class="hover:bg-gray-50">
                ${row.map(cell => 
                    `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${cell || '-'}
                    </td>`
                ).join('')}
            </tr>`
        ).join('');
    }
    
    renderPaginationControls() {
        const paginationHTML = `
            <div class="flex items-center justify-between px-6 py-3 bg-white border-t border-gray-200">
                <div class="flex items-center text-sm text-gray-700">
                    <span>Mostrando 
                        <span class="font-medium" id="showing-from">${((this.currentPage - 1) * this.pageSize) + 1}</span>
                        a 
                        <span class="font-medium" id="showing-to">${Math.min(this.currentPage * this.pageSize, this.totalCount)}</span>
                        de 
                        <span class="font-medium" id="showing-total">${this.totalCount}</span>
                        registros
                    </span>
                </div>
                <div class="flex items-center space-x-2">
                    <select id="page-size-selector" class="border border-gray-300 rounded px-2 py-1 text-sm">
                        <option value="10" ${this.pageSize === 10 ? 'selected' : ''}>10 por página</option>
                        <option value="20" ${this.pageSize === 20 ? 'selected' : ''}>20 por página</option>
                        <option value="50" ${this.pageSize === 50 ? 'selected' : ''}>50 por página</option>
                    </select>
                    <div class="flex space-x-1">
                        <button id="first-page" class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50" 
                                ${this.currentPage === 1 ? 'disabled' : ''}>Primera</button>
                        <button id="prev-page" class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                                ${this.currentPage === 1 ? 'disabled' : ''}>Anterior</button>
                        <span class="px-3 py-1 text-sm">
                            Página ${this.currentPage} de ${this.totalPages}
                        </span>
                        <button id="next-page" class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                                ${this.currentPage === this.totalPages ? 'disabled' : ''}>Siguiente</button>
                        <button id="last-page" class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                                ${this.currentPage === this.totalPages ? 'disabled' : ''}>Última</button>
                    </div>
                </div>
            </div>
        `;
        
        // Insertar después de la tabla
        const table = document.querySelector('table').parentElement;
        table.insertAdjacentHTML('afterend', paginationHTML);
    }
}
```

### 4. Template HTML Actualizado
```html
<!-- En data_studio_clean.html, agregar después de la tabla -->
<div id="pagination-container">
    <!-- Los controles se insertan aquí via JavaScript -->
</div>

<!-- En el bloque extra_js -->
<script src="{% static 'data_tools/js/pagination-manager.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const paginationManager = new PaginationManager(
        "{{ datasource.id }}", 
        "pagination-container"
    );
});
</script>
```

## ✅ Criterios de Aceptación

### Funcionalidad
- [ ] Navegación Previous/Next funciona correctamente
- [ ] Selector de filas por página (10/20/50) actualiza la vista
- [ ] Información "Mostrando X-Y de Z" es precisa
- [ ] Botones Primera/Última página funcionan
- [ ] AJAX loading sin errores

### UX/UI
- [ ] Controles visualmente claros y accesibles
- [ ] Loading states durante cambio de página
- [ ] Responsive en mobile y desktop
- [ ] Estados disabled apropiados (primera/última página)
- [ ] No hay flash o parpadeo durante navegación

### Performance
- [ ] Carga de página < 1 segundo
- [ ] No memory leaks en navegación
- [ ] Handling de errores de red
- [ ] Funciona con datasets grandes (500+ filas)

### Técnico
- [ ] JavaScript puro (sin dependencias)
- [ ] API REST bien estructurada
- [ ] Error handling robusto
- [ ] Logging apropiado
- [ ] Tests unitarios para pagination manager

## 🔧 Testing

### Manual Testing
1. **Navegación básica:** Verificar Previous/Next
2. **Cambio page size:** Probar 10/20/50 filas por página
3. **Navegación rápida:** Primera/Última página
4. **Edge cases:** Página 1, última página, dataset vacío
5. **Responsive:** Verificar en mobile y desktop

### Automated Testing
```python
# tests/test_pagination.py
class TestDataStudioPagination(TestCase):
    def test_paginated_api_response(self):
        # Test API structure
        
    def test_page_size_options(self):
        # Test different page sizes
        
    def test_edge_cases(self):
        # Test empty dataset, single page, etc.
```

## 📈 Métricas de Éxito

### User Experience
- **Time to see data:** < 2 segundos para cambio de página
- **Error rate:** < 1% de fallos en navegación
- **User satisfaction:** Facilidad de navegación por datos

### Technical Performance  
- **API response time:** < 500ms para consultas paginadas
- **Memory usage:** Sin leaks en navegación prolongada
- **Browser compatibility:** Chrome, Firefox, Safari, Edge

## 🚀 Valor de Negocio

### Para Usuarios
- **Acceso completo a datos:** Ver todas las 50 filas disponibles
- **Navegación eficiente:** Saltar rápidamente a secciones específicas
- **Control de densidad:** Elegir cuántos datos ver simultáneamente
- **Performance mejorada:** Carga solo datos necesarios

### Para Desarrollo
- **Foundation sólida:** Base para filtros y ordenamiento
- **Patrón reutilizable:** Pagination manager para otras vistas
- **API escalable:** Preparada para datasets grandes
- **Mantenible:** Código limpio y bien estructurado

## 📝 Notas de Implementación

### Consideraciones
- **Mantener simplicidad:** No over-engineer para dataset actual de 50 filas
- **Preparar escalabilidad:** Diseño que funcione con miles de filas futuras  
- **Consistencia:** Mantener estilo visual del template actual
- **Sin dependencias:** JavaScript puro para evitar conflictos

### Fases de Desarrollo
1. **Phase 1:** API backend + JavaScript básico
2. **Phase 2:** UI controls + navegación
3. **Phase 3:** Page size selection + navegación rápida
4. **Phase 4:** Testing + optimización

---

**Estimación:** 4-6 horas de desarrollo  
**Complejidad:** Baja-Media  
**Riesgo:** Bajo (no afecta funcionalidad existente)  
**Valor:** Alto (acceso completo a datos)