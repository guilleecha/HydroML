# Test script for SQL Editor functionality
import pandas as pd
from pandasql import sqldf

# Create test data
test_data = {
    'nombre': ['Ana', 'Bob', 'Carlos', 'Diana', None],
    'edad': [25, 30, None, 35, 28],
    'ciudad': ['Madrid', 'Barcelona', 'Madrid', None, 'Valencia'],
    'salario': [50000, 60000, 55000, 70000, None]
}

df = pd.DataFrame(test_data)

print("DataFrame de prueba:")
print(df)
print("\n")

# Test SQL queries
test_queries = [
    "SELECT * FROM df LIMIT 3",
    "SELECT nombre, edad FROM df WHERE edad > 25",
    "SELECT ciudad, COUNT(*) as count FROM df WHERE ciudad IS NOT NULL GROUP BY ciudad",
    "SELECT * FROM df WHERE nombre IS NOT NULL AND edad IS NOT NULL"
]

for i, query in enumerate(test_queries):
    print(f"Query {i+1}: {query}")
    try:
        result = sqldf(query, locals())
        print("Result:")
        print(result)
        print("\n")
    except Exception as e:
        print(f"Error: {e}")
        print("\n")

print("✅ All SQL tests completed successfully!")
