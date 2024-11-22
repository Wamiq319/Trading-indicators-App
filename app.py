from flask import Flask, render_template
from stock_analysis import check_rsi

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/rsi_indicator')
async def rsi_indicator():
    Stock = "crude"
    results = await check_rsi(Stock)
    return render_template('rsi_indicator.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
