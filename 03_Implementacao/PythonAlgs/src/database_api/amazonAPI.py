
#RdsUser:awsprojeto
#user: A44094@alunos.isel.pt
#pass: Projetopass2019

from database_api.databaseAPI import Database
import boto3
from botocore.client import Config
import MySQLdb


class Amazon_API():

    def __init__(self):
        self.__access_key = 'AKIAILM6X6WLXAAMBQQA'
        self.__secret_access_key = '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'
        self.__bucket_name= 'filestorate'
        self.__s3=0
        self.__connection=0

    def connect_to_s3(self):
        self.__s3 = boto3.resource(
            's3',
            aws_access_key_id=self.__access_key,
            aws_secret_access_key=self.__secret_access_key,
            config=Config(signature_version='s3v4')
        )
    def connect_to_rds(self):
        # self.__connection = MySQLdb.connect(host="mydbinstance.csc9g8achgy1.eu-west-3.rds.amazonaws.com",
        #              user="awsprojeto",
        #              password="Projetopass2019",
        #              db="mydbtracking")
        return Database("mydbinstance.csc9g8achgy1.eu-west-3.rds.amazonaws.com","mydbtracking","awsprojeto", "Projetopass2019")

    def upload(self,filename,name):
        data = open(filename,'rb')
        print(data)
        print(filename)
        self.__s3.Bucket(self.__bucket_name).put_object(Key=name,Body=data, ACL='public-read')




    def close(self):
        self.__connection.close()





#
#a = amazonAPI()
#conexao= a.connect_to_rds()
#conexao.create_tables()
#conexao.drop_tables()
#conexao.close()
#a.connect_to_s3()
#a.upload("../../Dataset/videos/VideoTest2.mp4","joaocosta.mp4")
