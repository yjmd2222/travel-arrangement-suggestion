from flask_page_template_settings import *

def get_connection():
    'connection obj return하는 함수'
    import sqlite3
    conn = sqlite3.connect('proj.db')

    return conn

if __name__ == '__main__':
    conn = get_connection()
    cur = conn.cursor()
    for idx, columns in enumerate((flight_columns_db, hotel_columns_db, car_columns_db)):
        travel_item = travel_item_list_db[idx]
        for col_name in columns:
            sql = f'select distinct {col_name} from {travel_item}'
            cur.execute(sql)
            rows = cur.fetchall()
            print(travel_item, col_name, [i[0] for i in rows])
    cur.close()
    conn.close()
