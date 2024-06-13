from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# 读取CSV数据
data_file = 'static/data/data-1.csv'
df = pd.read_csv(data_file)

@app.route('/')
def index():
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
    app.run(debug=True)
