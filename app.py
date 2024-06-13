import os, uuid
import pandas as pd
from geopy.distance import geodesic
import pymssql
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, session, jsonify)

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = pymssql.connect(host='jiaying.database.windows.net' ,user='jiaying' ,password = 'Zjy20010521',database='jiaying')
cur = conn.cursor()

data_file = 'static/data/data-1.csv'
df = pd.read_csv(data_file)
#================================================================================================
# # Create a blob client using the local simulator
# try:
#     account_url = "https://sinong.blob.core.windows.net"
#     default_credential = DefaultAzureCredential()

#     # Create the BlobServiceClient object
#     blob_service_client = BlobServiceClient(account_url, credential=default_credential)
#     container_client = blob_service_client.get_container_client(container="quiz0")
#     blob_list = container_client.list_blobs()
#     for blob in blob_list:
#         print("\t" + blob.name)
# except:
#     print("Error creating the BlobServiceClient object")
#================================================================================================

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')


@app.route('/test')
def test():
    SQL_QUERY = """
                SELECT 
                TOP 5 c.CustomerID, 
                c.CompanyName, 
                COUNT(soh.SalesOrderID) AS OrderCount 
                FROM 
                SalesLT.Customer AS c 
                LEFT OUTER JOIN SalesLT.SalesOrderHeader AS soh ON c.CustomerID = soh.CustomerID 
                GROUP BY 
                c.CustomerID, 
                c.CompanyName 
                ORDER BY 
                OrderCount DESC;
                """
    cur.execute(SQL_QUERY)
    data = cur.fetchall()
    print('Request for test page received')
    return render_template('test.html', data=data)


@app.route('/assignment1')
def assignment1():
    data_file_path = os.path.join(app.root_path, 'static', 'data', 'people.csv')
    data = pd.read_csv(data_file_path)
    print('Request for assignment1 page received')

    return render_template('assignment1.html', contain_content=False, table_content=list(data.values.tolist()), titles=data.columns.values)


@app.route('/a1-upload', methods = ['POST'])   
def upload():   
    if request.method == 'POST':   
        f = request.files['file']
        file_path = os.path.join(app.root_path, 'uploads', f.filename)
        session['file_path'] = file_path
        f.save(file_path)

        data = pd.read_csv(file_path)

        for idx, (_, row) in enumerate(data.iterrows()):
            sql_query = f"INSERT INTO quiz1.people VALUES ("
            for element in row:
                if pd.isna(element):
                    element = 'NULL'
                    sql_query += f"{element},"
                else:
                    sql_query += f"'{element}',"
            sql_query = sql_query[:-1] + ");"
            print(sql_query)
            cur.execute(sql_query)

        conn.commit()
        return render_template('assignment1.html', contain_content=False, table_content=list(data.values.tolist()), titles=data.columns.values)


@app.route('/a1-searchbyname', methods = ['POST', 'GET'])
def a1_searchbyname():
    name = request.form.get('queryName')
    data_file_path = session.get('file_path')
    data = pd.read_csv(data_file_path)
    query_data = data.loc[data['name'] == name]
    print(name, query_data)
    for col in query_data.columns:
            query_data[col].fillna(f"no {col} available", inplace=True)
    return render_template('assignment1.html', contain_content=True, table_content=list(query_data.values.tolist()), titles=query_data.columns.values)

@app.route('/a1-searchbycostrange', methods = ['POST', 'GET'])
def a1_searchbycostrange():
    min_cost = request.form.get('minCost')
    max_cost = request.form.get('maxCost')
    data_file_path = session.get('file_path')
    data = pd.read_csv(data_file_path)
    query_data = data.loc[(data['cost'].astype(float) >= int(min_cost)) & (data['cost'].astype(float) <= int(max_cost))]
    print(min_cost, max_cost, query_data)
    for col in query_data.columns:
            query_data[col].fillna(f"no {col} available", inplace=True)
    return render_template('assignment1.html', contain_content=True, table_content=list(query_data.values.tolist()), titles=query_data.columns.values)


@app.route('/assignmnet2')
def assignment2():
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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

@app.route('/quiz2')
def quiz2():
    return render_template('quiz2.html')

@app.route('/search_earthquakes', methods=['POST'])
def search_earthquakes():
    latitude = float(request.form['latitude'])
    degrees = float(request.form['degrees'])
    filtered_df = df[(df['latitude'] >= latitude - degrees) & (df['latitude'] <= latitude + degrees)]
    results = filtered_df[['time', 'latitude', 'longitude', 'id']].to_dict(orient='records')
    return jsonify(results)

@app.route('/delete_by_net', methods=['POST'])
def delete_by_net():
    global df
    net_value = request.form['net']
    count = df[df['net'] == net_value].shape[0]
    df = df[df['net'] != net_value]
    remaining_count = df.shape[0]
    return jsonify({"deleted_count": count, "remaining_count": remaining_count})

@app.route('/add_entry', methods=['POST'])
def add_entry():
    global df
    new_entry = {
        "time": request.form['time'],
        "latitude": float(request.form['latitude']),
        "longitude": float(request.form['longitude']),
        "depth": float(request.form['depth']),
        "mag": float(request.form['mag']),
        "net": request.form['net'],
        "id": request.form['id']
    }
    if df[df['id'] == new_entry['id']].empty:
        df = df.append(new_entry, ignore_index=True)
        return jsonify({"message": "Entry added successfully"})
    else:
        return jsonify({"error": "ID already exists"}), 400

@app.route('/modify_entry', methods=['POST'])
def modify_entry():
    global df
    net_id = request.form['net']
    updated_fields = request.form.to_dict()
    if not df[df['net'] == net_id].empty:
        for key, value in updated_fields.items():
            if key in df.columns:
                df.loc[df['net'] == net_id, key] = value
        return jsonify({"message": "Entry updated successfully"})
    else:
        return jsonify({"error": "Net ID not found"}), 404
if __name__ == '__main__':
   app.run()
