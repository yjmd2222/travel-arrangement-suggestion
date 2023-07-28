from flask import Flask, render_template, request

from flask_1p_option_selection import bp as bp_1
from flask_2p_option_selection import bp as bp_2
from flask_3p_result import bp as bp_3

app = Flask(__name__)
app.register_blueprint(bp_1)
app.register_blueprint(bp_2)
app.register_blueprint(bp_3)

@app.route('/')
def index():
    return '''
        <!DOCTYPE html>
        <html>
        <head>
        <title>제주도 날씨와 맛집</title>
        </head>
        <body>
        <h1>제주도 날씨와 맛집 정보🍊</h1>
        <h2></h2>
        <p>날짜를 입력해주세요🗓️</p>
        <form action="/process" method="post">  <!-- change the action attribute -->
            <h2>
            <label for="start_date">Start Date:</label>
            <input type="date" id="start_date" name="start_date" required>
            <label for="end_date">End Date:</label>
            <input type="date" id="end_date" name="end_date" required>
            </h2>
            <label for="keyword">Keyword:</label>
            <input type="text" id="keyword" name="keyword" required>
            <button type="submit">Enter</button>
        </form>
        </body>
        </html>
    '''

@app.route('/process', methods=['POST'])
def process():
    start_date = request.form['start_date'] 
    end_date = request.form['end_date']  
    keyword = request.form['keyword']  

    weather_output = filter_weather_data(start_date, end_date)
    mangoplate_output = get_mangoplate_info(keyword)
    
    return render_template('output.html', start_date=start_date, end_date=end_date,
                       keyword=keyword, weather_output=weather_output,
                       mangoplate_output=mangoplate_output)


if __name__ == '__main__':
    app.run()
