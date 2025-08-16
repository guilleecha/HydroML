import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth import get_user_model
from projects.models import Project, DataSource, DataSourceType


User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample projects and realistic datasets for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to assign as owner of projects (defaults to first superuser)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('\n=== SEEDING DATABASE WITH SAMPLE DATA ===')
        )
        
        # Get user to assign as project owner
        user_id = options.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ User with ID {user_id} not found')
                )
                return
        else:
            # Use first superuser
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('❌ No superuser found. Create a superuser first.')
                )
                return
        
        self.stdout.write(f'📝 Using user: {user.username} (ID: {user.id})')
        
        # Create projects and datasets
        try:
            self.create_sales_project(user)
            self.create_clinical_project(user)
            self.create_economic_project(user)
            self.create_energy_project(user)
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during seeding: {e}')
            )
            raise

    def create_sales_project(self, user):
        """Create supermarket sales analysis project with TWO related datasets for fusion testing"""
        self.stdout.write('\n🛒 Creating: Análisis de Ventas de Supermercado...')
        
        project = Project.objects.create(
            name="Análisis de Ventas de Supermercado",
            description="Análisis predictivo de ventas de productos en cadena de supermercados. "
                       "Incluye datos de transacciones y catálogo de productos para fusión de datos.",
            owner=user
        )
        
        # Generate sales data (ventas.parquet)
        np.random.seed(42)
        n_records = 5000
        
        # Date range: last 2 years
        start_date = datetime.now() - timedelta(days=730)
        dates = [start_date + timedelta(days=x) for x in range(730)]
        
        # Product IDs (will match with products dataset)
        product_ids = list(range(1, 201))  # 200 products
        
        sales_data = []
        for _ in range(n_records):
            fecha = np.random.choice(dates)
            producto_id = np.random.choice(product_ids)
            cantidad = np.random.randint(1, 50)
            precio_unitario = np.random.uniform(0.5, 150.0)
            descuento = np.random.choice([0, 5, 10, 15, 20], p=[0.6, 0.15, 0.15, 0.05, 0.05])
            sucursal_id = np.random.randint(1, 21)  # 20 branches
            vendedor_id = np.random.randint(1, 101)  # 100 sales people
            
            sales_data.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'producto_id': producto_id,
                'cantidad': cantidad,
                'precio_unitario': round(precio_unitario, 2),
                'descuento_porcentaje': descuento,
                'venta_total': round(cantidad * precio_unitario * (1 - descuento/100), 2),
                'sucursal_id': sucursal_id,
                'vendedor_id': vendedor_id,
                'dia_semana': fecha.strftime('%A'),
                'mes': fecha.month,
                'trimestre': (fecha.month - 1) // 3 + 1
            })
        
        sales_df = pd.DataFrame(sales_data)
        self.save_dataframe_as_parquet(sales_df, 'ventas.parquet', project, 
                                      "Datos de transacciones de ventas diarias")
        
        # Generate products catalog (productos.parquet)
        categories = ['Lácteos', 'Carnes', 'Frutas y Verduras', 'Panadería', 'Bebidas', 
                     'Limpieza', 'Cuidado Personal', 'Snacks', 'Congelados', 'Conservas']
        
        brands = ['Marca A', 'Marca B', 'Marca C', 'Marca D', 'Marca E', 'Marca Premium',
                 'Marca Económica', 'Marca Local', 'Marca Internacional', 'Marca Orgánica']
        
        products_data = []
        for producto_id in product_ids:
            categoria = np.random.choice(categories)
            marca = np.random.choice(brands)
            nombre_producto = f"{categoria.split()[0]} {marca} #{producto_id:03d}"
            precio_base = np.random.uniform(1.0, 200.0)
            peso_kg = np.random.uniform(0.1, 5.0) if categoria in ['Carnes', 'Frutas y Verduras'] else None
            
            products_data.append({
                'producto_id': producto_id,
                'nombre_producto': nombre_producto,
                'categoria': categoria,
                'marca': marca,
                'precio_sugerido': round(precio_base, 2),
                'peso_kg': round(peso_kg, 2) if peso_kg else None,
                'es_perecedero': categoria in ['Lácteos', 'Carnes', 'Frutas y Verduras', 'Panadería'],
                'proveedor': f"Proveedor {np.random.choice(['Norte', 'Sur', 'Centro', 'Este', 'Oeste'])}",
                'codigo_barras': f"78{producto_id:08d}",
                'activo': np.random.choice([True, False], p=[0.9, 0.1])
            })
        
        products_df = pd.DataFrame(products_data)
        self.save_dataframe_as_parquet(products_df, 'productos.parquet', project,
                                      "Catálogo de productos con detalles y características")
        
        self.stdout.write(f'  ✅ Created project with 2 related datasets (fusion-ready)')

    def create_clinical_project(self, user):
        """Create clinical pharmaceutical study project"""
        self.stdout.write('\n💊 Creating: Estudio Clínico Fármaco X...')
        
        project = Project.objects.create(
            name="Estudio Clínico Fármaco X",
            description="Estudio fase III para evaluar eficacia y seguridad del nuevo fármaco X "
                       "en pacientes con hipertensión arterial.",
            owner=user
        )
        
        # Generate clinical trial data
        np.random.seed(123)
        n_patients = 1200
        
        clinical_data = []
        for patient_id in range(1, n_patients + 1):
            # Demographics
            edad = np.random.randint(25, 80)
            sexo = np.random.choice(['M', 'F'])
            peso = np.random.normal(75, 15)
            altura = np.random.normal(170, 10)
            imc = peso / ((altura/100) ** 2)
            
            # Treatment assignment
            grupo = np.random.choice(['Control', 'Fármaco_X'], p=[0.5, 0.5])
            dosis_mg = np.random.choice([0, 5, 10, 20]) if grupo == 'Fármaco_X' else 0
            
            # Baseline measurements
            presion_sistolica_basal = np.random.normal(150, 20)
            presion_diastolica_basal = np.random.normal(95, 10)
            
            # Post-treatment measurements (with treatment effect)
            if grupo == 'Fármaco_X':
                reduction_factor = 0.8 + (dosis_mg * 0.02)  # Dose-response
                presion_sistolica_final = presion_sistolica_basal * reduction_factor + np.random.normal(0, 5)
                presion_diastolica_final = presion_diastolica_basal * reduction_factor + np.random.normal(0, 3)
            else:
                presion_sistolica_final = presion_sistolica_basal + np.random.normal(0, 8)
                presion_diastolica_final = presion_diastolica_basal + np.random.normal(0, 5)
            
            # Adverse events
            eventos_adversos = np.random.poisson(0.3)
            abandono_estudio = np.random.choice([True, False], p=[0.15, 0.85])
            
            clinical_data.append({
                'paciente_id': patient_id,
                'edad': edad,
                'sexo': sexo,
                'peso_kg': round(peso, 1),
                'altura_cm': round(altura, 1),
                'imc': round(imc, 1),
                'grupo_tratamiento': grupo,
                'dosis_mg': dosis_mg,
                'presion_sistolica_basal': round(presion_sistolica_basal, 1),
                'presion_diastolica_basal': round(presion_diastolica_basal, 1),
                'presion_sistolica_final': round(presion_sistolica_final, 1),
                'presion_diastolica_final': round(presion_diastolica_final, 1),
                'reduccion_sistolica': round(presion_sistolica_basal - presion_sistolica_final, 1),
                'reduccion_diastolica': round(presion_diastolica_basal - presion_diastolica_final, 1),
                'eventos_adversos': eventos_adversos,
                'abandono_estudio': abandono_estudio,
                'dias_seguimiento': np.random.randint(84, 365) if not abandono_estudio else np.random.randint(7, 84)
            })
        
        clinical_df = pd.DataFrame(clinical_data)
        self.save_dataframe_as_parquet(clinical_df, 'ensayo_clinico_farmaco_x.parquet', project,
                                      "Datos de ensayo clínico fase III con mediciones pre/post tratamiento")

    def create_economic_project(self, user):
        """Create macroeconomic analysis project for LATAM"""
        self.stdout.write('\n📊 Creating: Análisis Macroeconómico LATAM...')
        
        project = Project.objects.create(
            name="Análisis Macroeconómico LATAM",
            description="Análisis de indicadores macroeconómicos de países latinoamericanos "
                       "para predicción de crecimiento del PIB.",
            owner=user
        )
        
        # Generate macroeconomic data
        np.random.seed(456)
        countries = ['Argentina', 'Brasil', 'Chile', 'Colombia', 'México', 'Perú', 'Uruguay', 'Ecuador']
        years = list(range(2010, 2025))
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        
        macro_data = []
        for country in countries:
            # Base trends per country
            base_gdp_growth = np.random.uniform(-1, 4)
            base_inflation = np.random.uniform(2, 8)
            base_unemployment = np.random.uniform(5, 15)
            
            for year in years:
                for quarter in quarters:
                    # Add cyclical and noise components
                    cycle_component = np.sin(2 * np.pi * (year - 2010) / 7) * 2  # 7-year cycle
                    noise = np.random.normal(0, 1)
                    
                    gdp_growth = base_gdp_growth + cycle_component + noise
                    inflation = max(0, base_inflation + np.random.normal(0, 2))
                    unemployment = max(0, base_unemployment + np.random.normal(0, 1.5))
                    
                    # Commodity prices (simplified)
                    oil_price = 50 + 30 * np.sin(2 * np.pi * (year - 2010) / 5) + np.random.normal(0, 10)
                    copper_price = 3000 + 1000 * np.sin(2 * np.pi * (year - 2010) / 6) + np.random.normal(0, 500)
                    
                    # Exchange rate vs USD
                    base_exchange = {'Argentina': 100, 'Brasil': 5, 'Chile': 800, 'Colombia': 3500, 
                                   'México': 20, 'Perú': 4, 'Uruguay': 40, 'Ecuador': 1}[country]
                    exchange_rate = base_exchange * (1 + np.random.uniform(-0.2, 0.2))
                    
                    macro_data.append({
                        'pais': country,
                        'año': year,
                        'trimestre': quarter,
                        'periodo': f"{year}-{quarter}",
                        'crecimiento_pib': round(gdp_growth, 2),
                        'inflacion_anual': round(inflation, 2),
                        'desempleo': round(unemployment, 1),
                        'precio_petroleo_usd': round(max(20, oil_price), 2),
                        'precio_cobre_usd_ton': round(max(1500, copper_price), 0),
                        'tipo_cambio_usd': round(exchange_rate, 2),
                        'inversion_extranjera_mm_usd': round(np.random.uniform(100, 5000), 1),
                        'deficit_fiscal_pct_pib': round(np.random.uniform(-5, 2), 1),
                        'reservas_internacionales_mm_usd': round(np.random.uniform(5000, 50000), 1),
                        'indice_confianza_consumidor': round(np.random.uniform(30, 80), 1)
                    })
        
        macro_df = pd.DataFrame(macro_data)
        self.save_dataframe_as_parquet(macro_df, 'indicadores_macroeconomicos_latam.parquet', project,
                                      "Indicadores macroeconómicos trimestrales de países LATAM")

    def create_energy_project(self, user):
        """Create renewable energy generation prediction project"""
        self.stdout.write('\n🔋 Creating: Predicción Energía Renovable...')
        
        project = Project.objects.create(
            name="Predicción Energía Renovable",
            description="Análisis y predicción de generación de energía solar y eólica "
                       "basado en condiciones meteorológicas.",
            owner=user
        )
        
        # Generate energy data
        np.random.seed(789)
        n_days = 365 * 2  # 2 years of daily data
        start_date = datetime.now() - timedelta(days=n_days)
        
        energy_data = []
        for day in range(n_days):
            current_date = start_date + timedelta(days=day)
            month = current_date.month
            
            # Seasonal patterns
            seasonal_solar = 0.5 + 0.5 * np.cos(2 * np.pi * (month - 6) / 12)  # Peak in summer
            seasonal_wind = 0.6 + 0.4 * np.cos(2 * np.pi * (month - 12) / 12)  # Peak in winter
            
            # Weather conditions
            temperatura_max = 15 + 15 * seasonal_solar + np.random.normal(0, 5)
            temperatura_min = temperatura_max - np.random.uniform(5, 15)
            humedad = np.random.uniform(30, 90)
            velocidad_viento = np.random.gamma(2, 3)  # Gamma distribution for wind
            horas_sol = max(0, 6 + 6 * seasonal_solar + np.random.normal(0, 2))
            nubosidad = np.random.uniform(0, 100)
            
            # Energy generation (with realistic relationships)
            solar_capacity_mw = 100
            wind_capacity_mw = 150
            
            # Solar generation depends on sun hours and cloudiness
            generacion_solar_mwh = (solar_capacity_mw * horas_sol * 
                                   (1 - nubosidad/100) * 0.7 + np.random.normal(0, 10))
            generacion_solar_mwh = max(0, generacion_solar_mwh)
            
            # Wind generation depends on wind speed (with cut-in and cut-out)
            if velocidad_viento < 3:  # Cut-in speed
                generacion_eolica_mwh = 0
            elif velocidad_viento > 25:  # Cut-out speed
                generacion_eolica_mwh = 0
            else:
                # Cubic relationship with wind speed (simplified)
                generacion_eolica_mwh = min(wind_capacity_mw * 24, 
                                          wind_capacity_mw * (velocidad_viento ** 2) / 100)
            
            generacion_eolica_mwh += np.random.normal(0, 5)
            generacion_eolica_mwh = max(0, generacion_eolica_mwh)
            
            energy_data.append({
                'fecha': current_date.strftime('%Y-%m-%d'),
                'año': current_date.year,
                'mes': current_date.month,
                'dia_año': current_date.timetuple().tm_yday,
                'dia_semana': current_date.weekday(),
                'temperatura_max_c': round(temperatura_max, 1),
                'temperatura_min_c': round(temperatura_min, 1),
                'humedad_promedio': round(humedad, 1),
                'velocidad_viento_ms': round(velocidad_viento, 1),
                'horas_sol': round(horas_sol, 1),
                'nubosidad_promedio': round(nubosidad, 1),
                'presion_atmosferica_hpa': round(np.random.normal(1013, 20), 1),
                'precipitacion_mm': round(max(0, np.random.gamma(0.5, 2)), 1),
                'generacion_solar_mwh': round(generacion_solar_mwh, 2),
                'generacion_eolica_mwh': round(generacion_eolica_mwh, 2),
                'generacion_total_renovable_mwh': round(generacion_solar_mwh + generacion_eolica_mwh, 2),
                'demanda_energetica_mwh': round(np.random.uniform(200, 800), 2),
                'precio_energia_usd_mwh': round(np.random.uniform(30, 150), 2)
            })
        
        energy_df = pd.DataFrame(energy_data)
        self.save_dataframe_as_parquet(energy_df, 'generacion_energia_renovable.parquet', project,
                                      "Datos diarios de generación de energía renovable y condiciones meteorológicas")

    def save_dataframe_as_parquet(self, df, filename, project, description):
        """Save DataFrame as parquet file and create DataSource object"""
        # Convert DataFrame to parquet bytes
        parquet_buffer = df.to_parquet(index=False)
        
        # Create DataSource object
        datasource = DataSource.objects.create(
            name=filename.replace('.parquet', '').replace('_', ' ').title(),
            description=description,
            project=project,
            data_type=DataSourceType.ORIGINAL,
            status=DataSource.Status.READY
        )
        
        # Save parquet file
        content_file = ContentFile(parquet_buffer)
        datasource.file.save(filename, content_file, save=True)
        
        self.stdout.write(f'    📄 {filename}: {len(df)} records, {len(df.columns)} columns')
        
        return datasource
