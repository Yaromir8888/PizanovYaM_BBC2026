import numpy as np
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = BASE / 'train.csv'
df = pd.read_csv(source)
required = {'Age','Sex','Pclass','Fare','Embarked','Cabin','Survived'}
assert required.issubset(df.columns), 'Missing required columns'

def age_stats(s):
    return pd.Series({'Среднее':s.mean(),'Медиана':s.median(),'Минимум':s.min(),'Максимум':s.max(),'Стандартное отклонение':s.std(),'Известных значений':s.count()})

def print_section(title, value):
    print('\n' + '='*20 + ' ' + title + ' ' + '='*20)
    print(value)

try:
    n = int(input('Сколько первых строк вывести (по умолчанию 5)? ') or 5)
except (ValueError, EOFError):
    n = 5
n = max(0, min(n, len(df)))
print_section('6–8. Загрузка, первые и последние строки', f'{df.head(n).to_string()}\nПоследние пять:\n{df.tail().to_string()}')
print_section('9–12. Структура', f'Размер: {df.shape}\nСтолбцы: {df.columns.tolist()}\nТипы:\n{df.dtypes}\nЧисловые по смыслу: Age, Fare, SibSp, Parch\nКатегориальные: Survived, Pclass, Sex, Embarked, Cabin, Ticket, Name, PassengerId (идентификатор)')
print_section('13. Описательная статистика', df.select_dtypes(include='number').agg(['mean','median','min','max','std']).to_string())
print_section('14. Классы', df.Pclass.value_counts().sort_index())
print_section('15. Уникальных Embarked', df.Embarked.nunique(dropna=True))
missing = pd.DataFrame({'Пропусков':df.isna().sum(), 'Процент':df.isna().mean()*100})
print_section('16–18. Пропуски', f'{missing.to_string()}\nМаксимум: {missing["Пропусков"].idxmax()}')
before = age_stats(df.Age)
processed = df.copy()
processed['Age'] = processed['Age'].fillna(df['Age'].median())
after = age_stats(processed.Age)
age_comparison = pd.DataFrame({'До обработки':before,'После заполнения Age':after})
age_comparison.to_csv(BASE/'age_comparison.csv', encoding='utf-8-sig')
print_section('19–22. Сравнение возрастов', age_comparison)
processed = processed.dropna(subset=['Embarked']).copy()
cabin_missing_fraction = df.Cabin.isna().mean()
if cabin_missing_fraction > 0.5:
    processed = processed.drop(columns='Cabin')
print_section('23–26. Обработка', f'Cabin пропущено: {cabin_missing_fraction:.2%}; исходный размер {df.shape}, итоговый {processed.shape}\nОстаточные пропуски:\n{processed.isna().sum()}')

def numpy_mean(series):
    return float(np.mean(series.to_numpy(dtype=float)))

survival = numpy_mean(df.Survived)*100
survival_by_sex = df.groupby('Sex').Survived.apply(lambda s:np.mean(s.to_numpy())*100)
ages_by_sex = df.groupby('Sex').Age.apply(lambda s:np.nanmean(s.to_numpy(dtype=float)))
ages_by_sex_survival = df.groupby(['Sex','Survived']).Age.apply(lambda s:np.nanmean(s.to_numpy(dtype=float)))
fare_stats = pd.Series({'min':np.min(df.Fare.to_numpy()),'max':np.max(df.Fare.to_numpy()),'mean':np.mean(df.Fare.to_numpy())})
std_age = float(np.nanstd(df.Age.to_numpy(dtype=float), ddof=1))
print_section('31–36. NumPy', f'Общая выживаемость: {survival:.2f}%\nПо полу:\n{survival_by_sex}\nВозраст по полу:\n{ages_by_sex}\nВозраст по полу и выживаемости:\n{ages_by_sex_survival}\nСтоимость билета:\n{fare_stats}\nСтандартное отклонение Age: {std_age:.4f}')
comparative = df.groupby(['Sex','Survived'],dropna=False).agg(Пассажиров=('PassengerId','size'),Средний_возраст=('Age','mean'),Средняя_стоимость=('Fare','mean')).reset_index()
comparative.to_csv(BASE/'numpy_comparison.csv',index=False,encoding='utf-8-sig')
f1 = df[(df.Sex=='male') & (df.Age>30) & (df.Pclass==1)]
f2 = df[((df.Age<18) | (df.Sex=='female')) & (df.Survived==1)]
third_mean = df.loc[df.Pclass==3,'Fare'].mean()
f3 = df[(df.Pclass==3) & (df.Fare>third_mean)]
f4 = df[df.Age.between(20,40,inclusive='both') & (df.Embarked=='S')]
for i, subset in enumerate([f1,f2,f3,f4],1):
    subset.to_csv(BASE/f'filter_{i}.csv',index=False,encoding='utf-8-sig')
    print_section(f'Фильтр {i}: {len(subset)} пассажиров',subset.head(10).to_string())
print_section('Фильтр 3: средняя цена третьего класса',third_mean)
stats = processed.groupby(['Pclass','Sex']).agg(Пассажиров=('PassengerId','size'),Средний_возраст=('Age','mean'),Доля_выживших_проц=('Survived',lambda s:s.mean()*100),Средняя_стоимость=('Fare','mean')).reset_index()
ports = processed.groupby('Embarked').agg(Пассажиров=('PassengerId','size'),Доля_выживших_проц=('Survived',lambda s:s.mean()*100)).reset_index()
class_survival = processed.groupby('Pclass').Survived.mean()*100
print_section('37. Класс и пол',stats.to_string(index=False))
print_section('38. Порт',ports.to_string(index=False))
print_section('39. Максимальная выживаемость по классу',f'{class_survival.idxmax()} класс, {class_survival.max():.2f}%')
processed.to_csv(BASE/'titanic_processed.csv',index=False,encoding='utf-8-sig')
stats.to_csv(BASE/'titanic_statistics.csv',index=False,encoding='utf-8-sig')
ports.to_csv(BASE/'embarked_statistics.csv',index=False,encoding='utf-8-sig')
reloaded = pd.read_csv(BASE/'titanic_processed.csv')
pd.testing.assert_frame_equal(processed.reset_index(drop=True),reloaded,check_dtype=False)
print_section('40–42. Проверка сохранения',f'Успешно: {reloaded.shape}, значения совпадают')
print_section('43–47. Выводы',f'Больше всего пропусков: Cabin ({df.Cabin.isna().sum()}), Age ({df.Age.isna().sum()}). После очистки {len(processed)} строк и {len(processed.columns)} столбцов. Женщины: {survival_by_sex["female"]:.2f}% выживших, мужчины: {survival_by_sex["male"]:.2f}%. Наибольшая доля выживших — класс {class_survival.idxmax()}. Pandas удобен для очистки и группировки, NumPy — для статистики массивов.')
