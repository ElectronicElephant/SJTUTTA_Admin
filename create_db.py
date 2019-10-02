import sqlite3
import os
import logging

logging.basicConfig(level=logging.DEBUG)

def create_db(db_name):
    conn = sqlite3.connect(db_name)

    c = conn.cursor()

    c.execute('''SELECT datetime('now')''')
    print(c.fetchall())

    # members
    c.execute('''CREATE TABLE members
                (add_date INTEGER, 
                name TEXT, 
                college TEXT, 
                phone INTEGER, 
                QQ INTEGER, 
                card_id INTEGER, 
                identity INTEGER,
                valid_date INTEGER,
                id INTEGER PRIMARY KEY
                );''')
                # UNIX Timestamp <- UTC
                # Identity: 1 students
                #           2 alumni
                #           3 staff
                #           4 society

    c.execute("INSERT INTO members VALUES (strftime('%s','now'),'测试学生 1','电子信息与电气工程',13800138000,54749110, NULL, 1,NULL, NULL)")
    c.execute("INSERT INTO members VALUES (strftime('%s','now'),'校外用户 1',NULL, 13800138001,54749111, '', 4,365*24*60*60,NULL)")

    c.execute('''CREATE TABLE card_uid
                 (card_uid TEXT PRIMARY KEY,
                 user_id INTEGER
                 )''')
    c.execute("INSERT INTO card_uid VALUES ('01234567', 0)")
    c.execute("INSERT INTO card_uid VALUES ('396c8e99', 1)")

    conn.commit()

    conn.close()

def clear(db_name):
    if os.path.exists(db_name):
        os.remove(db_name)
        logging.info(f'{db_name} removed')
    else:
        logging.info(f'{db_name} does not exist')

def main(db_name):
    clear(db_name)
    create_db(db_name)

if __name__ == '__main__':
    main('sjtutta.db')
    main('example.db')