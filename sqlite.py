import sqlite3


class Database:
    def __init__(self, patch_to_db='qr_bot.db'):
        self.patch_to_db = patch_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.patch_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def create_table_store_info(self):
        sql = '''
        CREATE TABLE AllQrCodes (
        ID varchar(255) NOT NULL,
        ТипПродукта varchar(255),
        Проволка varchar(255),
        Пластикат varchar(255),
        Количество varchar(255),
        Метраж varchar(255),
        Поставщик varchar(255),
        Волочение varchar(255),
        Изготовитель varchar(255),
        Дата varchar(255),
        PRIMARY KEY (ID)
        );
        '''

        try:
            self.execute(sql, commit=True)
        except:
            print('Таблица уже существует')

    def add_automate(self, id, type_product, wire, plasticat, volume, metr, supplier, drawing, manufacturer, date_now,
                     user_id, user_descript):
        sql = 'INSERT INTO AllQrCodes(ID, ТипПродукта, Проволка, Пластикат, Количество, Метраж, Поставщик, Волочение, Изготовитель, Дата, user_id, user_descript) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        parameters = (
        id, type_product, wire, plasticat, volume, metr, supplier, drawing, manufacturer, date_now, user_id,
        user_descript)
        try:
            self.execute(sql, parameters=parameters, commit=True)
            return True
        except:
            return False

    def add_operation_puv(self, id, type_product, wire, color, date_now, user_id, user_descript, metr,
                          defect_reason=None):
        sql = 'INSERT INTO AllOperationQR(id, type_operation, wire, color, date_time, user_id, user_descript, metr, defect_reason) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)'
        parameters = (id, type_product, wire, color, date_now, user_id, user_descript, metr, defect_reason)
        try:
            self.execute(sql, parameters=parameters, commit=True)
            return True
        except Exception as EX:
            print(EX)
            return False

    def select_all_products(self):
        sql = "SELECT * FROM AllQrCodes"
        return self.execute(sql, fetchall=True)

    def select_all_operation(self):
        sql = "SELECT * FROM AllOperationQR"
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f'{item} = ?' for item in parameters.keys()
        ])
        return sql, tuple(parameters.values())

    def select_product(self, **kwargs):
        sql = "SELECT * FROM AllProducts WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchone=True)

    def count_products(self):
        return self.execute('SELECT COUNT(*) FROM AllProducts;', fetchone=True)[0]

    def update_name(self, name, art):
        sql = 'UPDATE AllProducts SET name=? WHERE art=?'
        return self.execute(sql, parameters=(name, art), commit=True)

    def update_type_0(self, type_0, art):
        sql = 'UPDATE AllProducts SET type_0=? WHERE art=?'
        return self.execute(sql, parameters=(type_0, art), commit=True)

    def update_name_0(self, name_0, art):
        sql = 'UPDATE AllProducts SET name_0=? WHERE art=?'
        return self.execute(sql, parameters=(name_0, art), commit=True)

    def update_status(self, status, art):
        sql = 'UPDATE AllProducts SET status=? WHERE art=?'
        return self.execute(sql, parameters=(status, art), commit=True)

    def delete_all_products(self):
        self.execute('DELETE FROM AllProducts WHERE True', commit=True)

    def delete_product(self, **kwargs):
        sql = "DELETE FROM AllProducts WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        self.execute(sql, parameters, commit=True)

    def add_operation_twinse(self, ID, Name_twinse, Wire, Metr, Date, Operator_id, Operator_name, Section, Piece_1,
                             Piece_2, Piece_3, Piece_4, Piece_5):
        sql = 'INSERT INTO AllTwinse(ID, Name_twinse, Wire, Metr, Date, Operator_id, Operator_name, Section, ' \
              'Piece_1, Piece_2, Piece_3, Piece_4, Piece_5) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        parameters = (ID, Name_twinse, Wire, Metr, Date, Operator_id, Operator_name, Section, Piece_1, Piece_2, Piece_3,
                      Piece_4, Piece_5)
        try:
            self.execute(sql, parameters=parameters, commit=True)
            return True
        except Exception as EX:
            print(EX)
            return False

    def select_all_products_twinse(self):
        sql = "SELECT * FROM AllTwinse"
        return self.execute(sql, fetchall=True)


def logger(statement):
    print(f'СДЕЛАЛ: {statement}')
