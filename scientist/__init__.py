"""
    Example Text
    https://www.blindtextgenerator.de/
"""
import itertools, sqlite3, threading, re

from .collection import Collection


class DatabaseConnector:

    def __init__(self, location: str, autoCommit: bool = True):
        self.database: sqlite3.Connection = sqlite3.connect(location)
        self.autoCommit: bool = autoCommit

    def get(self, table: str, columns: [str, list], where: list[str, (str, int)] = False) -> list:
        # build the sql str
        sql_str: str = f"SELECT "
        if isinstance(columns, list):
            sql_str += ", ".join(columns)
        else:
            sql_str += columns
        sql_str += f" FROM {table}"
        if where:
            if isinstance(where[1], str):
                sql_str += f" WHERE '{where[1]}'"
            else:
                sql_str += f" WHERE {str(where[1])}"
        return self.database.execute(sql_str).fetchall()

    def set(self, table: str, columns: [str, list], values: [str, list], where: list[str, (str, int)] = False):
        # build the sql str
        sql_str: str = f"UPDATE {table} SET "
        if isinstance(columns, list):
            saving_values: list = []
            for z in zip(columns, values):
                if isinstance(z[0], str):
                    saving_values.append(f"{z[0]} = '{z[1]}'")
                else:
                    saving_values.append(f"{z[0]} = {z[1]}")
            sql_str += ", ".join(saving_values)
        else:
            sql_str += columns + ", " + values
        sql_str += f" FROM {table}"
        if where:
            if isinstance(where[1], str):
                sql_str += f" WHERE '{where[1]}'"
            else:
                sql_str += f" WHERE {str(where[1])}"
        self.database.execute(sql_str).fetchall()

        # commit automatically new data
        if self.autoCommit: self.commit()

    def commit(self):
        self.database.commit()


class DataScientist:

    def __init__(self, connector: DatabaseConnector, saveDataLocal: bool = True):
        """
        :param connector: connector of the database
        :param saveDataLocal: Daten werden beim starten einmal geladen und
        anschließend immer in einem Dict abgespeichert, daten werden nicht erneut aus der datenbank gezogen
        """
        self.connector: DatabaseConnector = connector
        self.data: dict = {}
        self.Collection = Collection
        self.Collection.dataScientist = self

    def pointLocationConverter(self, step: str):
        return step.replace(".", "\&!")

    def get(self, location: str) -> [int, str, bool]:
        """
        Get Data
        :param location: data path
        :return: returns data
        """
        location: list = re.split(r"[.]+\b(?<!\\.)", location)
        data: any = self.data
        loc: any
        for step in location:
            if not isinstance(data, dict): break
            if not data.__contains__(step): return None
            data = data[step]
        return data

    def set(self, location: str, data: [int, str, bool]):
        """
        Set specific data
        :param location:
        :param data:
        :return:
        """
        location: list = re.split(r"[.]+\b(?<!\\.)", location)
        save = self.data
        for count, step in enumerate(location):
            if count != len(location) - 1:
                if not save.__contains__(step): save[step] = {}
                save = save[step]
            else:
                save[step] = data

    def exists(self, location: str) -> bool:
        """
        Get Data
        :param location: data path
        :return: returns data
        """
        location: list = re.split(r"[.]+\b(?<!\\.)", location)
        data: any = self.data.copy()
        if not data.__contains__(location[0]): return False
        loc: any
        for step in location:
            if not data.__contains__(step): return False
            data = data[step]
            if not isinstance(data, dict):
                if step != data[-1]: return False
                break
        return True

    def save(self) -> bool:
        """
        Save your data
        :return: is successful
        """
        return True

    def insert(self, text: str, save_under: str = "collection", replacer: list = [], startAsThread: bool = False) -> [None, threading.Thread]:
        """

        :param startAsThread:
        :param replacer:
        :param save_under:
        :param text:
        :return:
        """

        def run(text):
            for re in replacer:
                text = text.replace(re[0], re[1])
            words: list = text.split(" ")
            for word in words:
                word = word.replace(".", "\.")
                if not self.exists(f"{save_under}.{word}"):
                    col = self.Collection(word, save_under)
                else:
                    col = self.get(f"{save_under}.{word}.self")
                col.addCount()
        if not startAsThread:
            run(text)
            return None
        else:
            thread = threading.Thread(target=run, args=(text,), daemon=True)
            thread.start()
            return thread
        ## wichtig ! Threading
        #client = Client(client_socket, address)
        #clients.append(client)
        #thread = threading.Thread(target=client.listen, daemon=True)
        #client.thread = thread
        #client.send("connection accept")
        #client.thread.run()

    def waitFinish(self, threadList: list):
        """

        :param threadList:
        :return:
        """
        t: threading.Thread
        for t in threadList:
            t.join()