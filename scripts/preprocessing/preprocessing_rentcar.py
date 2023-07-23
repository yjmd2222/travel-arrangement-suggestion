'''
테스트 전처리 코드 병합한 파이썬 스크립트
'''
import pandas as pd

# 불러오기
file_dir = 'data/raw/raw_cars.csv'
df_cars = pd.read_csv(file_dir)
df_cars.head()

# 숫자만 표기
# seats 인승 삭제
df_cars['seats'] = df_cars['seats'].str[:-2].astype(int)
# age_req 중간에 나이만 표기
df_cars['age_req'] = df_cars['age_req'].str[1:-2].astype(int)
# driving_experience 숫자만 표기
df_cars['driving_experice'] = df_cars['driving_experice'].str[:-3]

# 시간 type datetime으로 변경
df_cars['start_date'] = pd.to_datetime(df_cars['start_date'])
df_cars['end_date'] = pd.to_datetime(df_cars['end_date'])

# 저장
new_file_path = 'data/preprocessed/preprocessed_cars.csv'
df_cars.to_csv(new_file_path, index=False)
