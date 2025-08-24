# Data Tools Templates Structure Documentation

## 📁 Current Structure (Post-Refactoring)

### Active Templates (In Use)
```
data_tools/
├── data_studio.html              # Main Data Studio interface (Grove refactored)
├── error.html                    # Error handling template
└── _data_studio_sidebar.html     # Legacy sidebar (will be removed)
```

### Grove Components (New Architecture)
```
partials/
├── _data_studio_sidebar_header.html    # Grove sidebar header component
├── _data_studio_session_status.html    # Grove session status footer
├── _data_studio_nav_section.html       # Grove navigation section template
└── _data_tools_sidebar.html           # Grove-refactored main sidebar
```

### Useful Components (_to_include/)
Ready for integration into new Data Studio:

#### Export System
- `_export_wizard.html` - Multi-step export configuration
- `_export_history.html` - Export job tracking with real-time status
- `_export_button.html` - Quick export functionality

#### Data Analysis & Visualization
- `missing_data_results.html` - Advanced missing data analysis with Plotly
- `operations_panel.html` - Data transformation operations interface
- `recipe_builder.html` - Data transformation recipe management

#### Navigation & Layout
- `header.html` - Grove-compliant header with breadcrumbs
- `data_studio_clean.html` - Clean TanStack Table reference implementation

#### Data Integration
- `data_fusion.html` + `data_fusion_form.html` - Data merging capabilities
- `feature_engineering.html` + `feature_engineering_page.html` - Column formula builder

### Legacy Archive (legacy/)
Templates no longer in active use:
- `api_documentation.html` - API docs (needs refactoring for Grove)
- `data_preparer.html` - Simple legacy template
- `data_viewer.html` - Replaced by new implementation
- `data_grid.html` - Superseded by TanStack Table

## 🏗️ Grove Design System Integration

### CSS Architecture
```
# Grove Base Components (core/static/core/css/components/)
grove-sidebar.css           # Base sidebar layout and positioning
grove-nav-section.css       # Collapsible navigation sections

# Data Studio Extensions (data_tools/static/data_tools/css/)  
data-studio-extensions.css  # Data Studio-specific styling only
```

### Component Hierarchy
1. **Grove Base** - Core sidebar and navigation components
2. **Data Studio Extensions** - Specific styling for Data Studio features
3. **Legacy CSS** - Removed `data-studio-sidebar.css` (410 lines → 60 lines)

## 🔄 Migration Path

### Completed ✅
1. Refactored monolithic sidebar (248 lines) into modular Grove components
2. Created reusable Grove base components for other apps
3. Moved legacy templates to appropriate folders
4. Identified reusable components for future integration

### Next Steps 📋
1. **Integrate Export System** - Add export wizard and history to new Data Studio
2. **Add Data Fusion** - Integrate data merging capabilities
3. **Implement Analytics** - Add missing data analysis and operations panel
4. **API Integration** - Connect Grove components to existing backend services
5. **Test & Refine** - Ensure all functionality works with new architecture

## 🎯 Backend Integration Points

### APIs to Connect
- `/tools/api/v1/exports/` - Export job management
- `/data-tools/api/studio/{id}/session/` - Session management  
- `/data-tools/api/studio/{id}/bulk/` - Bulk operations
- WebSocket connections for real-time updates

### Services Available
- `ExportService` - Full export workflow management
- `DataStudioSessionManager` - Session state with undo/redo
- `TransformationAPIViews` - Feature engineering, scaling, encoding
- `DataCleaningService` - Advanced data quality operations

## 💡 Design Principles Applied

### Grove Design System Compliance
- ✅ Use Grove components as base (`grove-sidebar`, `grove-nav-section`)
- ✅ Apply Grove design tokens (`--grove-*`, `--space-*`, `--radius-*`)
- ✅ Follow semantic class naming patterns
- ✅ Maintain light/dark theme compatibility

### Code Quality Improvements
- ✅ Reduced CSS from 410 lines to 60 lines of specific extensions
- ✅ Modular HTML components for better maintainability  
- ✅ Consistent Alpine.js patterns across components
- ✅ Separation of concerns (Grove base vs Data Studio specific)

### Architecture Benefits
- **Reusability**: Grove components can be used across other apps
- **Maintainability**: Small, focused files instead of monolithic templates
- **Consistency**: Standardized patterns following Grove Design System
- **Performance**: Reduced CSS bundle size and better caching