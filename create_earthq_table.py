import argparse
import pymssql
import pandas as pd


def create_table(args):
    conn = pymssql.connect(host=args.server_name + ".database.windows.net", user=args.user_name, password=args.password, database=args.db_name)
    cur = conn.cursor()
    
    cur.execute(f"CREATE SCHEMA {args.schema_name};")

    SQL_QUERY = f"""
                CREATE TABLE {args.schema_name}.{args.table_name} (
                    time int,
                    latitude float,
                    longitude float,
                    depth float,
                    mag float,
                    net varchar(255),
                    id varchar(255));"""
    cur.execute(SQL_QUERY)
    data = pd.read_csv(args.file_path)
          
    for (_, row) in data.iterrows():
        sql_query = f"INSERT INTO {args.schema_name}.{args.table_name} VALUES ("
        for element in row:
            if pd.isna(element):
                element = 'NULL'
                sql_query += f"{element},"
            else:
                if "'" in str(element):
                    element = str(element).replace("'", "''")
                sql_query += f"'{element}',"
        sql_query = sql_query[:-1] + ");"
        print(sql_query)
        cur.execute(sql_query)
    conn.commit()
    print('Table created and data inserted')
    conn.close()
    
    
if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--server_name', type=str, required=True)
    args.add_argument('--db_name', type=str, required=True)
    args.add_argument('--user_name', type=str, required=True)
    args.add_argument('--password', type=str, required=True)
    
    args.add_argument('--schema_name', type=str, required=True)
    args.add_argument('--table_name', type=str, required=True)
    
    args.add_argument('--file_path', type=str, required=True)
    
    args = args.parse_args()
    
    create_table(args)