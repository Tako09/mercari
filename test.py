import pandas as pd

df = pd.read_csv('data\selling_item.csv')
true = 1
if true:
    print('ugoku')
df['selling_date_is_empty'] = df['selling_date'].isnull().astype(int)
print(dict(df['no_discount'].value_counts())[0])
print(dict(df['no_discount'].value_counts()))