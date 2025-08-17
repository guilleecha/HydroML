import pandas as pd
from pandasql import sqldf

df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
result = sqldf('SELECT * FROM df WHERE a > 1', locals())
print('✅ pandasql working correctly')
print(result)
