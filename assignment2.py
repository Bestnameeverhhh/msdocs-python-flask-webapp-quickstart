from flask import Flask, request, jsonify, render_template
import pandas as pd
from datetime import datetime, timedelta
from geopy.distance import geodesic

app = Flask(__name__)

    #引入数据
file_path = 'static/data/data.csv'

@app.route('/')
def index():
    return render_template('assignment2.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    magnitude = data.get('magnitude', 0)
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    lat = data.get('latitude')
    lon = data.get('longitude')
    distance_km = data.get('distance_km', 0)

    # 读取CSV文件到DataFrame
    df = pd.read_csv(file_path)

    # 转换时间格式
    df['time'] = pd.to_datetime(df['time'])
    
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
    
    if magnitude:
        df = df[df['mag'] > magnitude]
    
    if lat and lon and distance_km:
        specified_location = (lat, lon)
        df['distance'] = df.apply(lambda row: geodesic((row['latitude'], row['longitude']), specified_location).km, axis=1)
        df = df[df['distance'] <= distance_km]

    count = df.shape[0]
    return jsonify({'count': count, 'data': df.to_dict(orient='records')})

@app.route('/clusters', methods=['POST'])
def clusters():
    # 读取CSV文件到DataFrame
    df = pd.read_csv(file_path)
    # 聚类分析逻辑...
    # 这里只提供一个简单示例，实际实现可能需要更复杂的聚类算法
    clusters = [{'latitude': row['latitude'], 'longitude': row['longitude'], 'count': 1} for index, row in df.iterrows()]
    return jsonify({'clusters': clusters})

@app.route('/night_quakes', methods=['POST'])
def night_quakes():
    # 读取CSV文件到DataFrame
    df = pd.read_csv(file_path)
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour
    night_df = df[(df['hour'] >= 18) | (df['hour'] < 6) & (df['mag'] > 4.0)]
    day_df = df[(df['hour'] >= 6) & (df['hour'] < 18) & (df['mag'] > 4.0)]
    
    night_count = night_df.shape[0]
    day_count = day_df.shape[0]
    
    return jsonify({'night_count': night_count, 'day_count': day_count})

if __name__ == '__main__':
    app.run(debug=True)
