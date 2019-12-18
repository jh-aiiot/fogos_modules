# -*- coding: utf-8 -*-
import sqlite3
import subprocess
from datetime import datetime, date, time

def create_db():
    # Remove the previously used db file and create a new one.
    subprocess.call(['rm', 'device.db'])
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()

    # Create tables.
    sql = ('create table DeviceID ('
            'id integer primary key autoincrement,'
            'temp_device_id text not null,'
            'device_id text)'
    )
    curs.execute(str(sql))

    sql = ('create table DeviceJoined ('
            'id integer primary key autoincrement,'
            'status text not null,'
            'timestamp datetime default current_timestamp)'
    )
    curs.execute(str(sql))

    sql = ('create table RegisterID ('
            'id integer primary key autoincrement,'
            'register_list text,'
            'timestamp datetime default current_timestamp)'
    )
    curs.execute(str(sql))

    sql = ('create table RegisterList ('
            'id integer primary key autoincrement,'
            'flex_id text,'
            'hash text not null,'
            'register_type text not null,'
            'category text not null,'
            'attributes text,'
            'cache text,'
            'segment text,'
            'collisionAvoid text,'
            'timestamp datetime default current_timestamp)'
    )
    curs.execute(str(sql))

    sql = ('create table QueryList ('
            'id integer primary key autoincrement,'
            'query_type text not null,'
            'category text not null,'
            'relay text not null default "none",'
            'result_order text,'
            'result_desc text not null default "true",'
            'result_limit integer not null default 1,'
            'requirements text not null default "[]",'
            'additionalFields text,'
            'timestamp datetime default current_timestamp)'
    )
    curs.execute(str(sql))

    sql = ('create table ActionTime ('
            'id integer primary key autoincrement,'
            'action text not null,'
            'timestr text not null,'
            'timestamp datetime default current_timestamp)'
    )
    curs.execute(str(sql))

    #curs.execute('create table Resources (id integer primary key autoincrement, temp_device_id text not null, device_id text)')
    #curs.execute('create table DeviceID(id integer primary key autoincrement, device_id text not null)')

    # Insert default values if necessary.
    #curs.execute("insert into DeviceID (id, temp_device_id) values (1, 'fdjiaiofjiowfjeio')")
    #curs.execute("insert into DeviceID (id, temp_device_id) values (2, 'vhaodshdvoihjioawio')")
    #curs.execute("insert into DeviceID (id, temp_device_id) values (3, '8fcv9y23hq89vhaq9')")
    curs.execute("insert into DeviceJoined (status) values ('leave')")
    curs.execute("insert into RegisterList (hash, register_type, category, attributes, cache, segment, collisionAvoid) VALUES ('42389ghdfasdf9dha8f932hf293f','Service','Bandwidth','[\"bandwidth=24Mbps\"]','true','false','true')")
    conn.commit()
    conn.close()


def get_device_status():
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute('SELECT * FROM DeviceJoined WHERE id=(SELECT MAX(id) FROM DeviceJoined);')

    status = None
    rows = curs.fetchall()
    for row in rows:
        status = row[1]
        conn.close()
    return status

def set_device_status(status):
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute("insert into DeviceJoined (status) values ('"+status+"')")
    conn.commit()
    conn.close()

def set_temp_device_id(temp_device_id):
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute("insert into DeviceID (temp_device_id) values ('"+temp_device_id+"')")
    conn.commit()
    conn.close()

def get_temp_device_id():
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute('SELECT * FROM DeviceID WHERE id=(SELECT MAX(id) FROM DeviceID);')

    device_id = None
    rows = curs.fetchall()
    for row in rows:
        device_id = row[1]
        conn.close()
    return device_id

def set_device_id(temp_device_id, device_id):
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute("update DeviceID SET device_id='"+device_id+"' WHERE temp_device_id='"+temp_device_id+"'")
    conn.commit()
    conn.close()

def get_device_id():
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute('SELECT * FROM DeviceID WHERE id=(SELECT MAX(id) FROM DeviceID);')

    device_id = None
    rows = curs.fetchall()
    for row in rows:
        device_id = row[2]
        conn.close()
    return device_id

def get_register_id(register_list):
    #Debug
    print('[get_register_id] ', str(register_list))

    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute("INSERT INTO RegisterID (register_list) VALUES (?)", (str(register_list),))
    register_id = curs.lastrowid
    print('  - lastrowid = ', register_id)

    conn.commit()
    conn.close()
    return register_id

def add_register_list(register_list):
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()

    data = []
    for reg in register_list:
        reg_item = (reg['hash'], reg['registerType'], reg['category'], str(reg['attributes']), reg['cache'], reg['segment'], reg['collisionAvoid'])
        data.append(reg_item)

    print('$$$$$$$$$$$$$$ \n',data)

    curs.executemany("INSERT INTO RegisterList (hash, register_type, category, attributes, cache, segment, collisionAvoid) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def add_register(reg):
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()

    data = (reg['hash'], reg['registerType'], reg['category'], str(reg['attributes']), reg['cache'], reg['segment'], reg['collisionAvoid'])
    curs.execute("INSERT INTO RegisterList (hash, register_type, category, attributes, cache, segment, collisionAvoid) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
    reg_index = curs.lastrowid
    print('  - register index:', reg_index)
    conn.commit()
    conn.close()
    return reg_index

def set_register_flex_id(reg_index, flex_id):
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute("update RegisterList SET flex_id='"+flex_id+"' WHERE id="+reg_index)
    conn.commit()
    conn.close()

def get_register_list():
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute('SELECT * FROM RegisterList')
    rows = curs.fetchall()
    conn.close()
    return rows

def add_query(query):
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()

    data = (query['queryType'], query['category'], query['order'], query['desc'], query['limit'], query['requirements'], query['additionalFields'])
    curs.execute("INSERT INTO QueryList (query_type, category, result_order, result_desc, result_limit, requirements, additionalFields) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
    query_index = curs.lastrowid
    print('  - query index:', query_index)
    conn.commit()
    conn.close()
    return query_index

def save_time_of_action(action):
    conn = sqlite3.connect('device.db')
    curs = conn.cursor()
    curs.execute("INSERT INTO ActionTime (action, timestr) VALUES (?, ?)", (action, datetime.now(),))
    conn.commit()
    conn.close()

#
# Debug: test code
#
if __name__ == '__main__':
    create_db()
    device_id = get_device_id()
    print(device_id)
