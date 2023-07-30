from flask import Blueprint, render_template, request, json
from flask_page_template_settings import (
    travel_item_kv,
    all_columns_kv,
    all_columns_kv_2_disp,
    all_columns_kv_2_select,
    travel_item_order_by_kv,
    sql_select_keys as keys)

bp = Blueprint('2페이지', __name__, url_prefix='/2페이지')

def page_2_wrap_other_funcs(json_data_raw:dict, additional_options:dict):
    '하나의 함수로 병합'
    def unfoil_inner_json(travel_item, json_data_inner:list):
        'json 안에 호텔,렌트카,항공권 개별 데이터 처리'
        # 솔직히 리스트였으면 아래 스텝 하나 필요 없음
        list_ = [list(item.values()) for item in json_data_inner] # [[칼럼명,값],...]
        list_ = [[all_columns_kv[travel_item][item[0]],item[1]] for item in list_] # [[sql_칼럼명,값],...]
        return [' == \''.join(item)+'\'' for item in list_] # ['칼럼명 == \'값\'',...]

    def unfoil_outer_json(json_data_whole:dict):
        '전체 json 데이터 정리해서 where문 안에 들어갈 str들로 반환'
        from datetime import datetime

        dict_ = {travel_item: [[],''] for travel_item in list(travel_item_kv.values())}
        # print(json_data_whole.items())
        for k, v in json_data_whole.items():
            # 항공권, 렌트카, 호텔이라면
            if k != 'dateRange':
                # list로 감싸서 str 저장. 항공권의 경우 datetime append해야 함
                dict_[travel_item_kv[k]][0] = unfoil_inner_json(k, v)
            # 날짜라면
            else:
                # 날짜 추가해야함
                start_date, end_date = v.split(' - ')
                # 항공권만 편도/왕복 있음
                start_date = datetime.strptime(start_date, r'%m/%d/%Y')
                end_date = datetime.strptime(end_date, r'%m/%d/%Y')
                start_date_flight = start_date.strftime(r'%Y-%m-%d')
                end_date_flight = end_date.strftime(r'%Y-%m-%d')
                start_date_else = start_date.strftime(r'%Y-%m-%d %H:%M:%S')
                end_date_else = end_date.strftime(r'%Y-%m-%d %H:%M:%S')
                # else: dateRange. 이 루프에서만 아래 코드 진행이라 n^2가 아니라 n+m임
                for k_ in dict_:
                    # sql 시간 조회
                    if k_ != list(travel_item_kv)[0]:
                        dict_[k_][1] = f'start_date == \'{start_date_else}\' AND end_date == \'{end_date_else}\''
                    else:
                        dict_[k_][1] = [f'DATE(SUBSTR(departure_datetime, 1, 10)) == \'{date_flight}\'' for date_flight in (start_date_flight, end_date_flight)]
                print(dict_)
        return dict_, [start_date_flight, end_date_flight] # 두 번째 리스트는 표기용 날짜 전달로 사용

    def add_conditions_sql(travel_item, conditions, date_condition):
        '여러 조건문 적용 시 빈 테이블이면 조건 무시'
        sql = f'WITH Step0 AS (SELECT {", ".join(all_columns_kv_2_select[travel_item])} FROM {travel_item} WHERE {date_condition})'
        if travel_item == '호텔':
            sql = sql[:-1] + ' GROUP BY hotel_name)'
        idx = 0
        while idx < len(conditions):
            if idx+1 == 1:
                sql += f''', Step1 AS (SELECT * FROM Step0 WHERE {conditions[idx]})
                    , Step1check AS (
                        SELECT * FROM Step1
                        UNION
                        SELECT * FROM Step0 WHERE NOT EXISTS (SELECT 1 FROM Step1)
                        )
                    '''
            elif idx+1 == 2:
                sql += f''', Step{idx+1} AS (
                    SELECT * FROM (
                        SELECT * FROM Step{idx}
                        UNION
                        SELECT * FROM Step{idx-1} WHERE NOT EXISTS (SELECT 1 FROM Step{idx})
                        )
                    WHERE {conditions[idx]}
                    ),
                    Step{idx+1}check AS (
                    SELECT * FROM Step{idx+1}
                    UNION
                    SELECT * FROM Step{idx} WHERE NOT EXISTS (SELECT 1 FROM Step{idx+1})
                    )
                    '''
            else:
                sql += f''', Step{idx+1} AS (
                    SELECT * FROM (
                        SELECT * FROM Step{idx}
                        UNION
                        SELECT * FROM Step{idx-1} WHERE NOT EXISTS (SELECT 1 FROM Step{idx})
                        )
                    WHERE {conditions[idx]}
                    ),
                    Step{idx+1}check AS (
                    SELECT * FROM Step{idx+1}
                    UNION
                    SELECT * FROM Step{idx}check WHERE NOT EXISTS (SELECT 1 FROM Step{idx+1})
                    )
                    '''
            idx += 1
        order_by = f'{travel_item_order_by_kv[travel_item]}'
        if travel_item == '항공권':
            order_by = f'{order_by} ASC'
        else:
            order_by = f'{order_by} DESC'
        if idx == 0:
                sql += f' SELECT * FROM Step0 ORDER BY {order_by} LIMIT 3'
        else:
            sql += f''' SELECT * FROM Step{idx}check ORDER BY {order_by} LIMIT 3'''
        return sql

    # print(add_conditions_sql('렌터카', ['brand_name == \'현대\'', 'seats == 5', 'transmission_type == \'수동\'', 'fuel_type == \'휘발유\''], 'start_date == \'2023-07-27 00:00:00\' AND end_date == \'2023-07-28 00:00:00\''))

    def return_select_sqls(conditions_dict):
        'sql문 반환'

        # # sql 내에서 계산할 것이 아니라 python에서 계산한다면
        # # 가는 표 오는 표 각각 필요할 듯
        # # 1. 항공권
        # flight_other_columns = where_dict[list(travel_item_kv.values())[0]][0]
        # flight_where_to_jeju = f'arrival == \'CJU\' AND DATE(SUBSTR(departure_datetime, 1, 10)) == \'{where_dict[list(travel_item_kv.values())[0]][1][0]}\''
        # flight_where_from_jeju = f'departure == \'CJU\' AND DATE(SUBSTR(departure_datetime, 1, 10)) == \'{where_dict[list(travel_item_kv.values())[0]][1][1]}\''
        # if flight_other_columns:
        #     flight_where_to_jeju = ' AND ' + flight_where_to_jeju
        #     flight_where_from_jeju = ' AND ' + flight_where_from_jeju
        # flight_where_to_jeju = flight_other_columns + flight_where_to_jeju
        # flight_where_from_jeju = flight_other_columns + flight_where_from_jeju
        # sql_select_flights_to_jeju = f"""
        # SELECT *
        # FROM {list(travel_item_kv.values())[0]}
        # WHERE
        # {flight_where_to_jeju}
        # ORDER BY adult_charge
        # LIMIT 3
        # """
        # sql_select_flights_from_jeju = f"""
        # SELECT *
        # FROM {list(travel_item_kv.values())[0]}
        # WHERE
        # {flight_where_from_jeju}
        # ORDER BY adult_charge
        # LIMIT 3
        # """

        # # 2. 렌터카
        # sql_select_cars = f"""
        # SELECT *
        # FROM {list(travel_item_kv.values())[1]}
        # WHERE
        # {where_dict[list(travel_item_kv.values())[1]][0]}
        # ORDER BY ratings DESC
        # LIMIT 3
        # """

        # # 3. 호텔
        # sql_select_hotels = f"""
        # SELECT *
        # FROM {list(travel_item_kv.values())[2]}
        # WHERE
        # {where_dict[list(travel_item_kv.values())[2]][0]}
        # ORDER BY ratings DESC
        # LIMIT 3
        # """

        flight_db_name, hotel_db_name, car_db_name = travel_item_kv.values()
        # 항공권: 오가는 표 구분 필요해서 다른 것과는 형식 약간 다름.
        sql_select_flights_to_jeju = add_conditions_sql(flight_db_name, ['direction == \'come\''] + conditions_dict[flight_db_name][0], conditions_dict[flight_db_name][1][0])
        sql_select_flights_from_jeju = add_conditions_sql(flight_db_name, ['direction == \'back\''] + conditions_dict[flight_db_name][0], conditions_dict[flight_db_name][1][1])

        # 숙박시설
        sql_select_hotels = add_conditions_sql(hotel_db_name, *conditions_dict[hotel_db_name])

        # 렌터카
        sql_select_cars = add_conditions_sql(car_db_name, *conditions_dict[car_db_name])

        # 나중에 삭제. 현재는 디버깅용
        print(sql_select_cars)
        print(sql_select_hotels)
        print(sql_select_flights_to_jeju)
        print(sql_select_flights_from_jeju)

        return sql_select_flights_to_jeju, sql_select_flights_from_jeju, sql_select_hotels, sql_select_cars

    def get_connection():
        'connection obj return하는 함수'
        import sqlite3
        conn = sqlite3.connect('../data/SQL/proj.db')

        return conn

    def fetch_data(sql_select, key)->list:
        'DB에서 데이터 fetch하기'
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(sql_select)

        rows = cur.fetchall()
        # 딕셔너리 형태로 결과 반환
        rows = [{tuple_[0]: tuple_[1] for tuple_ in zip(all_columns_kv_2_disp[key], row)} for row in rows]

        cur.close()
        conn.close()

        return rows

    where_dict, date_range = unfoil_outer_json(json_data_raw)
    sqls = return_select_sqls(where_dict)

    # 추가 옵션: 편도/왕복 적용
    one_way_or_round = additional_options.get('편도/왕복')
    dict_ = {key: [] for key in keys}
    for idx, key in enumerate(dict_):
        if idx == 1:
            if one_way_or_round == '편도':
                dict_[key] = []
            else:
                dict_[key] = fetch_data(sqls[idx], key)
        else:
            dict_[key] = fetch_data(sqls[idx], key)

    # 디버깅용
    print(dict_)

    # 항공권
    for list_ in (dict_['항공권_to'], dict_['항공권_from']):
        for item in list_:
            item['항공권 종류'] = item['항공권 종류_']
            item['출발 공항'] = item['출발공항(이름)'] + '공항(' + item['출발공항(코드)'] + ')'
            item['도착 공항'] = item['도착공항(이름)'] + '공항(' + item['도착공항(코드)'] + ')'
            item['출발 시간'] = item['출발시간(datetime)'][-8:-3]
            item['도착 시간'] = item['도착시간(datetime)'][-8:-3]
            for age_group in ('성인', '아동'):
                num = additional_options.get(age_group)
                if num:
                    item[age_group] = int(num)
                else:
                    item[age_group] = 0
            if item['성인'] == item['아동'] == 0:
                item['성인'] = 1
            item['총 금액'] = item['성인'] * item['성인요금'] + item['아동'] * item['아동요금'] # 이름 주의. 요금은 최종적으로 표기 안 함. 금액 항목만 표기
            # 콤마 표기
            for price in ['성인요금', '아동요금', '총 금액']:
                item[price] = f'{item[price]:,}'
            for to_delete in all_columns_kv_2_disp['항공권_to'][2:]: # 금전상황, 항공사는 포함. from과 to 동일
                del item[to_delete]

    # 숙박시설
    for item in dict_['호텔']:
        item['인원수'] = str(item['인원수']) + '명'
        item['별점'] = round(item['별점'], 1)
        item['금액'] = f'{item["금액"]:,}'

    # 렌터카
    for item in dict_['렌트카']:
        item['나이제한'] = str(item['나이제한']) + '세이상'
        item['운전경력'] = str(item['운전경력']) + '년이상'
        item['인승'] = str(item['인승']) + '인승'
        item['별점'] = '-' if item['별점'] == 0 and item['리뷰수'] == 0 else item['별점']
        item['금액'] = f'{item["금액"]:,}'
        del item['리뷰수']

    # 디버깅용
    print(dict_)


    return dict_, date_range, one_way_or_round

@bp.route('/', methods=['GET'])
def page_2():
    # Get the data sent from the form
    data = request.args.get('input_data', '{}')
    additional_options = request.args.get('additional_input_data')

    # Convert the data from URL encoded string to a Python dictionary
    data_dict, date_range, one_way_or_round = page_2_wrap_other_funcs(json.loads(data), json.loads(additional_options))
    # print(data_dict)
    
    # Pass the data to the template for the second page
    return render_template('page2.html', data=data_dict, date_range=date_range, one_way_or_round=one_way_or_round)
