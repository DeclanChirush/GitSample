from flask import Flask, request, render_template, send_file
from flask_cors import CORS
import db
from model import User
from datetime import datetime, timedelta
import impact_of_company_financial.fbp as impact_of_company_financial_forecast
import impact_of_inflation.predictor as impact_of_inflation_forecast
from statsmodels.tsa.arima.model import ARIMAResults

from pycaret.classification import *

impact_of_news_model = load_model('impact_of_news/lr')
impact_of_stock_market_behavior_model = ARIMAResults.load('impact_of_stock_market_behavior/model.pkl')

db = db.DB()

app = Flask(__name__)
CORS(app)

current_user = User(0, 'null', 'null', 'null', 'user')


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        company_name = request.form['company_name']
        no_of_months = int(request.form['no_of_months'])
        net_profit_margin, earnings_per_share, future_dates = impact_of_company_financial_forecast.forecast_fbp(
            company_name,
            no_of_months)
        net_profit_margin_data = ''
        earnings_per_share_data = ''
        x_data = ''

        for i in range(len(net_profit_margin)):
            if i == len(net_profit_margin) - 1:
                net_profit_margin_data += str(net_profit_margin[i])
                earnings_per_share_data += str(earnings_per_share[i])
                x_data += str(i)
            else:
                net_profit_margin_data += str(net_profit_margin[i]) + ', '
                earnings_per_share_data += str(earnings_per_share[i]) + ', '
                x_data += str(i) + ', '

        return render_template('index.html', y_earnings_per_share=earnings_per_share_data,
                               y_data_net_profit_margin=net_profit_margin_data, x_data=x_data,
                               company_name=company_name)
    else:

        company_name = 'ASIA_ASSET_FINANCE_PLC'
        no_of_months = 6
        net_profit_margin, earnings_per_share, future_dates = impact_of_company_financial_forecast.forecast_fbp(
            company_name,
            no_of_months)
        net_profit_margin_data = ''
        earnings_per_share_data = ''
        x_data = ''

        for i in range(len(net_profit_margin)):
            if i == len(net_profit_margin) - 1:
                net_profit_margin_data += str(net_profit_margin[i])
                earnings_per_share_data += str(earnings_per_share[i])
                x_data += str(i)
            else:
                net_profit_margin_data += str(net_profit_margin[i]) + ', '
                earnings_per_share_data += str(earnings_per_share[i]) + ', '
                x_data += str(i) + ', '

        return render_template('index.html', y_earnings_per_share=earnings_per_share_data,
                               y_data_net_profit_margin=net_profit_margin_data, x_data=x_data,
                               company_name=company_name)


@app.route('/inflation', methods=['GET', 'POST'])
def inflation():
    if request.method == 'POST':
        no_of_months = int(request.form['no_of_months'])

        future_dates, predicted_data = impact_of_inflation_forecast.getData(no_of_months)
        y_data = ''
        x_data = ''
        data = []

        for i in range(len(predicted_data)):
            data.append([future_dates[i], predicted_data[i]])
            if i == len(predicted_data) - 1:
                y_data += str(round(predicted_data[i], 2))
                x_data += str(i)
            else:
                y_data += str(round(predicted_data[i], 2)) + ', '
                x_data += str(i) + ', '

        return render_template('inflation.html', y_data=y_data, x_data=x_data, data=data)
    else:

        no_of_months = 6

        future_dates, predicted_data = impact_of_inflation_forecast.getData(no_of_months)
        y_data = ''
        x_data = ''
        data = []

        for i in range(len(predicted_data)):
            data.append([future_dates[i], predicted_data[i]])
            if i == len(predicted_data) - 1:
                y_data += str(round(predicted_data[i], 2))
                x_data += str(i)
            else:
                y_data += str(round(predicted_data[i], 2)) + ', '
                x_data += str(i) + ', '

        return render_template('inflation.html', y_data=y_data, x_data=x_data, data=data)


@app.route('/news', methods=['GET', 'POST'])
def news():
    if request.method == 'POST':
        headline = request.form['headline']
        article = request.form['article']

        data = np.array(
            [['Headline', 'Article'], [headline, article]])

        result = \
            predict_model(impact_of_news_model,
                          data=pd.DataFrame(data=data[0:, 0:], index=data[0:, 0], columns=data[0, 0:])).iat[
                1, 2]
        return_data = 'This news will create grade ' + str(result) + ' impact on stock market'
        return render_template('news.html', return_data=return_data)
    else:
        return render_template('news.html')


@app.route('/stock_behavior', methods=['GET', 'POST'])
def stock_behavior():
    if request.method == 'POST':
        no_of_days = int(request.form['no_of_days'])

        df = pd.read_csv('impact_of_stock_market_behavior/data/data.csv', index_col='Date', parse_dates=True)
        df = df.dropna()

        today = datetime.now()
        n_days = today + timedelta(days=no_of_days)
        print(today.strftime("%Y.%m.%d"), n_days.strftime("%Y.%m.%d"))
        index_future_dates = pd.date_range(start=today.strftime("%Y.%m.%d"), end=n_days.strftime("%Y.%m.%d"))
        # print(index_future_dates)
        pred = impact_of_stock_market_behavior_model.predict(start=len(df), end=len(df) + no_of_days,
                                                             typ='levels').rename('ARIMA Predictions')
        # print(comp_pred)
        pred.index = index_future_dates
        output_value = []

        for x in range(len(pred)):
            output_value.append(round(pred[x], 2))

        y_data = ''
        x_data = ''

        for i in range(len(output_value)):
            if i == len(output_value) - 1:
                y_data += str(output_value[i])
                x_data += str(i)
            else:
                y_data += str(output_value[i]) + ', '
                x_data += str(i) + ', '

        return render_template('stock_behavior.html', y_data=y_data, x_data=x_data)
    else:
        no_of_days = 6

        df = pd.read_csv('impact_of_stock_market_behavior/data/data.csv', index_col='Date', parse_dates=True)
        df = df.dropna()

        today = datetime.now()
        n_days = today + timedelta(days=no_of_days)
        print(today.strftime("%Y.%m.%d"), n_days.strftime("%Y.%m.%d"))
        index_future_dates = pd.date_range(start=today.strftime("%Y.%m.%d"), end=n_days.strftime("%Y.%m.%d"))
        # print(index_future_dates)
        pred = impact_of_stock_market_behavior_model.predict(start=len(df), end=len(df) + no_of_days,
                                                             typ='levels').rename('ARIMA Predictions')
        # print(comp_pred)
        pred.index = index_future_dates
        output_value = []

        for x in range(len(pred)):
            output_value.append(round(pred[x], 2))
        y_data = ''
        x_data = ''

        for i in range(len(output_value)):
            if i == len(output_value) - 1:
                y_data += str(output_value[i])
                x_data += str(i)
            else:
                y_data += str(output_value[i]) + ', '
                x_data += str(i) + ', '

        return render_template('stock_behavior.html', y_data=y_data, x_data=x_data)


@app.route('/all', methods=['GET', 'POST'])
def all():
    if request.method == 'POST':
        no_of_days = int(request.form['no_of_days'])
        if no_of_days < 2:
            no_of_days = 2
        headline = request.form['headline']
        article = request.form['article']

        data = np.array(
            [['Headline', 'Article'], [headline, article]])

        news_result = \
            predict_model(impact_of_news_model,
                          data=pd.DataFrame(data=data[0:, 0:], index=data[0:, 0], columns=data[0, 0:])).iat[
                1, 2]

        df = pd.read_csv('impact_of_stock_market_behavior/data/data.csv', index_col='Date', parse_dates=True)
        df = df.dropna()

        today = datetime.now()
        n_days = today + timedelta(days=no_of_days)
        print(today.strftime("%Y.%m.%d"), n_days.strftime("%Y.%m.%d"))
        index_future_dates = pd.date_range(start=today.strftime("%Y.%m.%d"), end=n_days.strftime("%Y.%m.%d"))
        # print(index_future_dates)
        pred = impact_of_stock_market_behavior_model.predict(start=len(df), end=len(df) + no_of_days,
                                                             typ='levels').rename('ARIMA Predictions')
        # print(comp_pred)
        pred.index = index_future_dates
        output_value = []

        for x in range(len(pred)):
            output_value.append(round(pred[x], 2))

        stock_behavior_result = output_value

        future_dates, predicted_data = impact_of_inflation_forecast.getData(no_of_days)
        y_data = ''
        x_data = ''
        data = []

        for i in range(len(predicted_data)):
            data.append([future_dates[i], predicted_data[i]])
            if i == len(predicted_data) - 1:
                y_data += str(round(predicted_data[i], 2))
                x_data += str(i)
            else:
                y_data += str(round(predicted_data[i], 2)) + ', '
                x_data += str(i) + ', '

        inflation_result = data

        company_name = 'ASIA_ASSET_FINANCE_PLC'
        net_profit_margin, earnings_per_share, future_dates = impact_of_company_financial_forecast.forecast_fbp(
            company_name,
            no_of_days)

        company_result = net_profit_margin

        print('news_result * 0.2', news_result * 0.2)
        print('stock', ((stock_behavior_result[-2] - stock_behavior_result[-1]) * 0.4))
        print('dd', stock_behavior_result[-2], stock_behavior_result[-1])
        print('inflation', (inflation_result[-2][1] - inflation_result[-1][1]) / inflation_result[-2][1] * 0.1)
        print('company', (company_result[-2] - company_result[-1]) / company_result[-2] * 0.4)
        all_result = (news_result * 0.2) + (
                    (stock_behavior_result[-2] - stock_behavior_result[-1]) / stock_behavior_result[
                -2] * 0.4) + ((inflation_result[-2][1] - inflation_result[-1][1]) / inflation_result[-2][1] * 0.1) + (
                             (company_result[-2] - company_result[-1]) / company_result[-2] * 0.4)

        return render_template('all.html', all_result=all_result)
    else:
        no_of_days = 2
        headline = 'some'
        article = 'some'

        data = np.array(
            [['Headline', 'Article'], [headline, article]])

        news_result = \
            predict_model(impact_of_news_model,
                          data=pd.DataFrame(data=data[0:, 0:], index=data[0:, 0], columns=data[0, 0:])).iat[
                1, 2]

        df = pd.read_csv('impact_of_stock_market_behavior/data/data.csv', index_col='Date', parse_dates=True)
        df = df.dropna()

        today = datetime.now()
        n_days = today + timedelta(days=no_of_days)
        print(today.strftime("%Y.%m.%d"), n_days.strftime("%Y.%m.%d"))
        index_future_dates = pd.date_range(start=today.strftime("%Y.%m.%d"), end=n_days.strftime("%Y.%m.%d"))
        # print(index_future_dates)
        pred = impact_of_stock_market_behavior_model.predict(start=len(df), end=len(df) + no_of_days,
                                                             typ='levels').rename('ARIMA Predictions')
        # print(comp_pred)
        pred.index = index_future_dates
        output_value = []

        for x in range(len(pred)):
            output_value.append(round(pred[x], 2))

        stock_behavior_result = output_value

        future_dates, predicted_data = impact_of_inflation_forecast.getData(no_of_days)
        y_data = ''
        x_data = ''
        data = []

        for i in range(len(predicted_data)):
            data.append([future_dates[i], predicted_data[i]])
            if i == len(predicted_data) - 1:
                y_data += str(round(predicted_data[i], 2))
                x_data += str(i)
            else:
                y_data += str(round(predicted_data[i], 2)) + ', '
                x_data += str(i) + ', '

        inflation_result = data

        company_name = 'ASIA_ASSET_FINANCE_PLC'
        net_profit_margin, earnings_per_share, future_dates = impact_of_company_financial_forecast.forecast_fbp(
            company_name,
            no_of_days)

        company_result = net_profit_margin
        print('news_result * 0.2', news_result * 0.2)
        print('stock', ((stock_behavior_result[-2] - stock_behavior_result[-1]) * 0.4))
        print('dd', stock_behavior_result[-2], stock_behavior_result[-1])
        print('inflation', (inflation_result[-2][1] - inflation_result[-1][1]) / inflation_result[-2][1] * 0.1)
        print('company', (company_result[-2] - company_result[-1]) / company_result[-2] * 0.4)
        all_result = (news_result * 0.2) + ((stock_behavior_result[-2] - stock_behavior_result[-1]) / stock_behavior_result[
            -2] * 0.4) + ((inflation_result[-2][1] - inflation_result[-1][1]) / inflation_result[-2][1] * 0.1) + (
            (company_result[-2] - company_result[-1]) / company_result[-2] * 0.4)

        return render_template('all.html', all_result=all_result)


# Actions
@app.route('/login_action', methods=['POST'])
def login_action():
    email = request.form['email']
    password = request.form['password']

    login_status, user = db.login(email=email, password=password)

    if login_status:
        global current_user
        current_user = user

        company_name = 'ASIA_ASSET_FINANCE_PLC'
        no_of_months = 6
        net_profit_margin, earnings_per_share, future_dates = impact_of_company_financial_forecast.forecast_fbp(
            company_name,
            no_of_months)
        net_profit_margin_data = ''
        earnings_per_share_data = ''
        x_data = ''

        for i in range(len(net_profit_margin)):
            if i == len(net_profit_margin) - 1:
                net_profit_margin_data += str(net_profit_margin[i])
                earnings_per_share_data += str(earnings_per_share[i])
                x_data += str(i)
            else:
                net_profit_margin_data += str(net_profit_margin[i]) + ', '
                earnings_per_share_data += str(earnings_per_share[i]) + ', '
                x_data += str(i) + ', '

        return render_template('index.html', y_earnings_per_share=earnings_per_share_data,
                               y_data_net_profit_margin=net_profit_margin_data, x_data=x_data,
                               company_name=company_name, username=user.get_name(), user_type=user.get_user_type())

    else:
        return render_template('login.html', status='Username Or Password Invalid')


@app.route('/register_action', methods=['POST'])
def register_action():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    cpassword = request.form['cpassword']

    user_type = 'user'

    if password == cpassword:
        db.save_user(name=name, email=email, password=password, user_type=user_type)
        return render_template('login.html', status='Register Success')
    else:
        return render_template('register.html', status='Password did not match')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500, debug=True)
