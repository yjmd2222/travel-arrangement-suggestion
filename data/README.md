# 데이터 설명(SQL/proj.db 기준)

## 항공권 데이터 컬럼 설명
```
name :               항공사 브랜드명
seat :               항공권 특징(일반, 할인, 특가)
adult_charge :       성인 1인 기준 항공권 가격
child_charge :       소아 1인 기준 항공권 가격
leavehour :          항공편 출발 시각(only hour)
check :              제주 기준 출발 or 도착 확인 컬럼
departure :          출발 공항(영어) 
arrival :            도착 공항(영어)
departure_kor :      출발 공항(한국어)
arrival_kor :        도착 공항(한국어)
departure_datetime : 출발 날짜 및 시간
arrival_datetime :   도착 날짜 및 시간
```

## 렌트카 데이터 컬럼 설명
```
car_name:            자동차 모델명
brand_name:          자동차 제조사명
seats:               좌석개수
size:                소형/중형 등
fuel_type:           연료타입
transmission_type:   자동/수동
rental_company_name: 렌트카 회사명
age_req:             필수 최소 나이
driving_experice:    운전 경력
year:                자동차 연식
ratings:             별점
num_ratings:         리뷰 개수
price:               렌트비용
start_date:          렌트 시작일
end_date:            렌트 종료일
```

## 호텔 데이터 컬럼 설명
```
hotel_name: 숙박시설 이름
region:     raw 지역명(시읍면동)
ratings:    별점
price:      숙박비용
start_date: 숙박 시작일
end_date:   숙박 종료일
capacity:   인원수
new_region: 전처리 후 지역명(시읍면동)
```
