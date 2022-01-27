import os
import sqlite3

class DABDatabase():
    HOME = os.environ['HOME']
    db_name = HOME+'/.config/dab.db'
    conn = None
    cursor = None

    

    def __init__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS ensembles( eid int, ecc int, charset int, abbrev1 int, abbrev0 int, label text, tuned_index int) ''')
        self.cursor.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS idx_tuned_index ON ensembles(tuned_index) ''')
        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS services( service_id int, component_id int, service_info int, local_flag int, num_components int, prog_type int, srv_link_flag int, service_label text, tuned_index int) ''')
        self.cursor.execute(''' CREATE INDEX IF NOT EXISTS idx_tuned_index ON services(tuned_index) ''')
        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS favourites( service_id int, component_id int, service_info int, local_flag int, num_components int, prog_type int, srv_link_flag int, service_label text, tuned_index int) ''')
        self.cursor.execute(''' CREATE INDEX IF NOT EXISTS idx_tuned_index ON favourites(tuned_index) ''')
        self.conn.commit()
        
    def __del__(self):
        #self.conn.commit()
        self.conn.close()
    
    def add_ensemble(self, ensemble):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('INSERT INTO ensembles (eid, ecc, charset, abbrev0, abbrev1, label, tuned_index) values (?, ?, ?, ?, ?, ?, ?)',
            (ensemble.eid, ensemble.ecc, ensemble.charset, ensemble.abbrev0, ensemble.abbrev1, ensemble.label, ensemble.status.tuned_index ))
        self.conn.commit()

    def get_ensembles(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        rows = self.cursor.execute('SELECT label, tuned_index FROM ensembles ORDER BY label')
        return rows.fetchall()

    def clear_database(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM ensembles")
        self.cursor.execute("DELETE FROM services")
        self.conn.commit()
        
    def add_services(self, services, tuned_index):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        #i = 1
        for service in services:
            self.cursor.execute('INSERT INTO services ( service_id, component_id, service_info, local_flag, num_components, prog_type, srv_link_flag, service_label, tuned_index) values (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (service.service_id, service.components[0] , service.service_info, service.local_flag, service.num_components, service.prog_type, service.srv_link_flag, service.service_label, tuned_index ))
            #i = i+1
        self.conn.commit()

    def get_services_for_ensemble(self, tuned_index):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        rows = self.cursor.execute('SELECT * FROM services WHERE tuned_index=? AND prog_type = 0 ORDER BY service_label', (tuned_index,))
        return rows.fetchall()
    
    def get_services(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        rows = self.cursor.execute('SELECT * FROM services WHERE prog_type = 0 ORDER BY service_label')
        return rows.fetchall()
    
    def get_favourites(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        rows = self.cursor.execute('SELECT * FROM favourites WHERE prog_type = 0 ORDER BY service_label')
        return rows.fetchall()

    def get_favourite(self, fav):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        rows = self.cursor.execute('SELECT * FROM favourites WHERE service_id=? and component_id=?', (fav[0], fav[1]))
        return rows.fetchall()

    def add_favourite(self, fav):
        #(49700, 4, 0, 0, 1, 0, 1, 'BBC Radio 4', 9)
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('INSERT INTO favourites ( service_id, component_id, service_info, local_flag, num_components, prog_type, srv_link_flag, service_label, tuned_index) values (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (fav[0], fav[1] , fav[2], fav[3], fav[4], fav[5], fav[6], fav[7], fav[8] ))
        self.conn.commit()
    
    def remove_favourite(self, fav):
        #(49700, 4, 0, 0, 1, 0, 1, 'BBC Radio 4', 9)
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('DELETE FROM favourites WHERE service_id=? AND component_id=?', (fav[0], fav[1]))
        self.conn.commit()