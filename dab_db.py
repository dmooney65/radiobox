import sqlite3

class DABDatabase():
    db_name = '~/.config/dab/dab.db'
    conn = None
    cursor = None
    def __init__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
			
        #get the count of tables with the name
        self.cursor.execute(" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ensembles' ")

        #if the count is 1, then table exists
        if self.cursor.fetchone()[0] is not 1 :
            #print('Table does not exist.')
            #self.cursor.execute(" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ensembles' ")
            self.cursor.execute(''' CREATE TABLE ensembles( eid int, ecc int, charset int, abbrev1 int, abbrev0 int, label text, tuned_index int) ''')
            self.cursor.execute(''' CREATE UNIQUE INDEX idx_tuned_index ON ensembles(tuned_index) ''')
            self.conn.commit()

    def __del__(self):
        #self.conn.commit()
        self.conn.close()

    def add_ensemble(self, ensemble):
        self.cursor.execute("insert into ensembles (eid, ecc, charset, abbrev0, abbrev1, label, tuned_index) values (?, ?, ?, ?, ?, ?, ?)",
            (ensemble.eid, ensemble.ecc, ensemble.charset, ensemble.abbrev0, ensemble.abbrev1, ensemble.label, ensemble.status.tuned_index ))
        self.conn.commit()

    def get_ensembles(self):
        rows = self.cursor.execute('SELECT label, tuned_index FROM ensembles ORDER BY label')
        #for row in rows:
        #    print(row)
        return rows.fetchall()

    def clear_ensembles(self):
        self.cursor.execute("DROP TABLE ensembles")
        self.conn.commit()
        self.cursor.execute(''' CREATE TABLE ensembles( eid int, ecc int, charset int, abbrev1 int, abbrev0 int, label text, tuned_index int) ''')
        self.cursor.execute(''' CREATE UNIQUE INDEX idx_tuned_index ON ensembles(tuned_index) ''')
        self.conn.commit()

#db = DABDatabase()
#db = None