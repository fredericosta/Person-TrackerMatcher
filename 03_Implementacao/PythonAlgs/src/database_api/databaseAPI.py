#import mysql.connector
import numpy as np
import itertools
import MySQLdb


class Database:

    def __init__(self, servername, database, username, password):
        #self.__conn = mysql.connector.connect(host=servername, database=database, user=username, passwd=password)
        self.__conn = MySQLdb.connect(host=servername, user=username, passwd=password, db=database)
        self.__cursor = 0
        self.__tipos = ["area", "histograma"]

    def __insertRota(self, idRota, path):
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute("INSERT INTO ROTA VALUES(%s,%s)", (idRota, path))
        self.__conn.commit()
        self.__cursor.close()

    def __insertUtilizador(self, idRota, idPessoaEntrada, idPessoaSaida, eventEntrada, eventSaida):
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute("INSERT INTO UTILIZADOR VALUES(%s,%s,%s,%s,%s)", (idRota, idPessoaEntrada,
                              idPessoaSaida, eventEntrada, eventSaida))
        self.__conn.commit()
        self.__cursor.close()

    def __insertCaracteristica(self, idRota, idPessoaEntrada, idPessoaSaida, tipo, caracteristicasEntrada,
                               CaracteristicasSaida):
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute("INSERT INTO CARACTERISTICA VALUES(%s,%s,%s,%s,%s,%s)", (idRota,
                              idPessoaEntrada, idPessoaSaida, self.__tipos[tipo],
                           caracteristicasEntrada, CaracteristicasSaida))
        self.__cursor.close()
    def recieve(self):
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute("SELECT idRota,videoPath FROM ROTA")
        tabela_rota = self.__cursor.fetchall()

        self.__cursor.execute("SELECT idRota,idEntrada,idSaida,horaEntrada,horaSaida FROM UTILIZADOR")
        tabela_utilizador = self.__cursor.fetchall()

        self.__cursor.execute("SELECT idRota,idEntrada,idSaida,tipo,CaracteristicaEntrada,CaracteristicaSaida "
                              "FROM CARACTERISTICA")
        tabela_caracteristica = self.__cursor.fetchall()
        self.__cursor.close()
        return tabela_rota, tabela_utilizador, tabela_caracteristica

    def insert(self, matching, path):
        '''
        Inserting values on the sql database for statistic purposes

        :param matching: list of matching id's
        :param path: string that contains the path of the video
        :return: Nothing
        '''

        # calcula o próximo id da rota disponível
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute("SELECT idRota from ROTA")
        ids = self.__cursor.fetchall()
        idRota = 1
        
        if ids:
            idRota = list(ids)
            idRota = idRota[-1][0] + 1

        self.__insertRota(idRota, path)

        # lista de objetos Pessoa entrada/saida
        listaEntrada = matching[1]
        listaSaida = matching[2]

        # verificar se as listas não são nulas
        if len(listaEntrada) != 0 or len(listaSaida) != 0:
            # para cada pessoa dentro de cada lista
            for pessoaEntrada, pessoaSaida in itertools.zip_longest(listaEntrada, listaSaida):
                # verificar se existe matching entre entrada/saida
                if pessoaEntrada is not None and pessoaSaida is not None:

                    self.__insertUtilizador(idRota, pessoaEntrada.id, pessoaSaida.id, pessoaEntrada.event_time,
                                            pessoaSaida.event_time)

                    self.__insertCaracteristica(idRota, pessoaEntrada.id, pessoaSaida.id, 0, pessoaEntrada.area,
                                                pessoaSaida.area)
                    self.__insertCaracteristica(idRota, pessoaEntrada.id, pessoaSaida.id, 1,
                                                np.array2string(pessoaEntrada.hue_hist),
                                                np.array2string(pessoaSaida.hue_hist))



                # no caso de não haver matching verificar se existe pessoaEntrada ou saida e colocar na tabela
                # Será inserido -1 ao id da pessoa que não estiver na lista
                else:
                    if pessoaEntrada is None:
                        self.__insertUtilizador(idRota, -1, pessoaSaida.id, None, pessoaSaida.event_time)

                        self.__insertCaracteristica(idRota, -1, pessoaSaida.id, 0, "Null", pessoaSaida.area)
                        self.__insertCaracteristica(idRota, -1, pessoaSaida.id, 1, "Null",
                                                    np.array2string(pessoaSaida.hue_hist))


                    else:
                        self.__insertUtilizador(idRota, pessoaEntrada.id, -1, pessoaEntrada.event_time, None)

                        self.__insertCaracteristica(idRota, pessoaEntrada.id, -1, 0, pessoaEntrada.area, "Null")
                        self.__insertCaracteristica(idRota, pessoaEntrada.id, -1, 1,
                                                    np.array2string(pessoaEntrada.hue_hist), "Null")
        self.__cursor.close()


    def create_tables(self):
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute(
            '''
            CREATE TABLE ROTA(
            idRota int not null,
            videoPath varchar(100),
            CONSTRAINT pk_idRota PRIMARY KEY (idRota)
            );
            ''')
        self.__cursor.execute(
            '''
            CREATE TABLE UTILIZADOR(
            idRota int not null,
            idEntrada int not null,
            idSaida int not null,
            horaEntrada DATETIME null,
            horaSaida DATETIME null,
            CONSTRAINT pk_id PRIMARY KEY (idEntrada,idSaida,idRota)
            )
            '''
        )
        self.__cursor.execute(
            '''
            CREATE TABLE CARACTERISTICA (
            idRota int not null,
            idEntrada int not null,
            idSaida int not null,
            tipo varchar(20) not null,
            CaracteristicaEntrada text,
            CaracteristicaSaida text,
            CONSTRAINT pk_tipo PRIMARY KEY (tipo,idRota,idEntrada,idSaida)
            )
            '''
        )
        self.__cursor.execute(
            '''
            ALTER TABLE UTILIZADOR
            ADD CONSTRAINT fk_rota FOREIGN KEY (idRota) REFERENCES ROTA (idRota);
            '''
        )
        self.__cursor.execute(
            '''
            ALTER TABLE CARACTERISTICA
            ADD CONSTRAINT fk_id FOREIGN KEY (idEntrada,idSaida,idRota) REFERENCES UTILIZADOR(idEntrada,idSaida,idRota);
            '''
        )
        self.__cursor.close()

    def drop_tables(self):

        self.__cursor = self.__conn.cursor()
        self.__cursor.execute(

            '''
            ALTER TABLE UTILIZADOR DROP
            FOREIGN KEY fk_rota
            '''
        )

        self.__cursor.execute(

            '''
            ALTER TABLE CARACTERISTICA
            DROP FOREIGN KEY fk_id
            '''
        )
        self.__cursor.execute(

            '''

            DROP TABLE ROTA, UTILIZADOR,CARACTERISTICA
            '''
        )
        self.__cursor.close()

    def close(self):

        self.__conn.close()



if __name__ == "__main__":
        servername = "localhost"
        database = "Tracking"
        username = "root"
        password = "projetopass"
        db_obj = Database(servername, database, username, password)
        db_obj.insertRota(2,'C://pasta//video2.mp4')
