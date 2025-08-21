# HydroML Design Specifications

## Color System Philosophy

### Monochromatic Foundation
HydroML adopts a sophisticated monochromatic design approach emphasizing professionalism and clarity:

- **Primary Palette**: White (#FFFFFF), Black (#000000), Gray scales (50-900)
- **Accent Philosophy**: Soft, muted tones only - NO bright/vivid colors
- **Button Design**: Subtle gradients, monochromatic variations, professional appearance
- **Tags/Labels**: Pastel tones for visual hierarchy without distraction

### Color Usage Guidelines

**✅ APPROVED:**
- Monochromatic grays for primary interface elements
- Soft pastels for tags, badges, and classification indicators
- Subtle blue/green tints for success states (muted, not bright)
- Warm gray tones for neutral states
- Cool gray tones for inactive/disabled states

**❌ AVOID:**
- Bright/vivid primary colors (red, blue, yellow, green)
- High saturation accent colors
- Neon or fluorescent tones
- Multiple competing bright colors in single view

### Implementation Strategy

1. **Design Tokens Update**: Modify CSS custom properties to reflect monochromatic palette
2. **Component Library**: Ensure all Wave-inspired components follow color restrictions
3. **Theme System**: Light/dark themes maintain monochromatic approach
4. **Legacy Components**: Gradual migration of existing colorful elements

## Classification System Requirements

### Database Classification
- **Type**: Relational, NoSQL, Time-series, Vector, Document
- **Environment**: Development, Staging, Production, Archive
- **Sensitivity**: Public, Internal, Confidential, Restricted
- **Purpose**: Analytics, Operational, Backup, Testing

### Experiment Classification  
- **Status**: Planning, Running, Completed, Failed, Archived
- **Methodology**: Supervised, Unsupervised, Reinforcement, Deep Learning
- **Business Impact**: Research, Production, Optimization, POC
- **Resource Intensity**: Low, Medium, High, GPU-Required

### Workspace Classification
- **Team**: Data Science, Engineering, Research, Business
- **Project Phase**: Discovery, Development, Testing, Production
- **Access Level**: Public, Team, Private, Admin
- **Lifecycle**: Active, Maintenance, Deprecated, Archive

### Data Source Classification
- **Format**: CSV, JSON, Parquet, Database, API, Stream
- **Quality**: Raw, Cleaned, Validated, Processed, Analysis-Ready
- **Update Frequency**: Real-time, Hourly, Daily, Weekly, Static
- **Size Category**: Small (<1GB), Medium (1-10GB), Large (10-100GB), Big Data (>100GB)

## Visual Hierarchy Principles

### Typography Scale
- Use font weight and size for hierarchy, not color
- Monospace fonts for code/data display
- Sans-serif for UI elements
- Clear contrast ratios for accessibility

### Spacing System
- Consistent spacing scale (4px, 8px, 16px, 24px, 32px)
- Generous whitespace for professional appearance
- Logical grouping through spacing, not color

### Component Hierarchy
- Primary actions: Subtle gradients or monochromatic emphasis
- Secondary actions: Ghost/outline styles
- Destructive actions: Muted red/orange tones (not bright)
- Success states: Muted green/blue tones (not bright)

## Implementation Checklist

- [ ] Update Tailwind CSS configuration for monochromatic palette
- [ ] Modify existing design tokens in theme system
- [ ] Create classification models in Django
- [ ] Build classification UI components
- [ ] Update Wave Theme Integration components
- [ ] Migrate existing colorful elements
- [ ] Test accessibility compliance
- [ ] Document color usage guidelines