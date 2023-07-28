from flask import Blueprint, render_template, request, json
from flask_weather_pd import filter_weather_data
from flask_mangoplate_add import get_mangoplate_info

bp = Blueprint('3페이지', __name__, url_prefix='/3페이지')

def get_total_price(selected_output:dict):
    '요금 합산. dict value:dict의 맨 마지막 value'
    values_list = []
    for item in selected_output.values():
        if item:
            values_list.append(list(item.values())[-1])
    return sum(values_list)

@bp.route('/', methods=['GET'])
def page_3():
    start_date, end_date = request.args.get('date_range').strip('[]').replace('&#39;','').split(', ')
    region = request.args.get('region')
    mango_region = request.args.get('new_region')

    weather_output = filter_weather_data(start_date, end_date)
    mangoplate_output = get_mangoplate_info(mango_region)

    # 이해하기 어렵지만 dict value의 dict가 str으로 되어있음.
    selected_output = json.loads(request.args.get('input_data'))
    selected_output = {k: json.loads(v.replace("'", '"')) for k,v in selected_output.items()}
    total_price = get_total_price(selected_output)

    return render_template('page3.html',
                           start_date=start_date,
                           end_date=end_date,
                           region=region,
                           weather_output=weather_output,
                           mangoplate_output=mangoplate_output,
                           selected_output=selected_output,
                           total_price=total_price
                           )
