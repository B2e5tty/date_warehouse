import pandas as pd
import numpy as np
import logging
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
phone = os.getenv('phone')
user = os.getenv('user')
password = os.getenv('password')     
database = os.getenv('database')
host=os.getenv('host')   
port=os.getenv('port')


class Exploratory:
    def __init__(self, dataframe):
        self.info_log = logging.getLogger('info')
        self.info_log.setLevel(logging.INFO)

        info_handler = logging.FileHandler('..\logs\info.log')
        info_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        info_handler.setFormatter(info_formatter)
        self.info_log.addHandler(info_handler)

        self.error_log = logging.getLogger('error')
        self.error_log.setLevel(logging.ERROR)

        error_handler = logging.FileHandler('..\logs\error.log')
        error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        error_handler.setFormatter(error_formatter)
        self.error_log.addHandler(error_handler)

        try :
            self.df = dataframe
            self.info_log('Loading dataframe')
        except:
            self.error_log.error("Error occurred when loading the dataframe")

    # close the log
    def close_log(self):
        self.info_log.info('Closing logging')
        handlers = self.info_log.handlers[:]

        # close info logging 
        for handler in handlers:
            handler.close()
            self.info_log.removeHandler(handler)

        # close error logging
        handlers = self.error_log.handlers[:]
        for handler in handlers:
            handler.close()
            self.error_log.removeHandler(handler)


    # return the dataframe
    def get_dataframe(self):
        self.info_log.info('Return the dataframe')
        return self.df
    
    # overview info on the dataframe
    def over_view(self):
        self.info_log.info('Overview of the dataframe')
        # information on the dataframe
        self.df.info()

        # unique value in channel title and channel username
        print('\n')
        print(f"Unique channel titles in the dataframe: {self.df['Channel Title'].unique()}")
        print(f"Unique channel username in the dataframe: {self.df['Channel Username'].unique()}")

        # check if ID column contains duplicate values
        print('\n')
        print(f"Does ID contain duplicated values: {self.df.duplicated(subset=['ID']).any()}")

    # change data types
    def data_cleaning(self):
        self.info_log.info('Data cleaning process')
        # change date from object to datetime
        self.df['Date'] = pd.to_datetime(self.df['Date'])

        # fill NaN value of Media Path
        self.df['Media Path'] = self.df['Media Path'].fillna('No media')

        # removing null values
        self.df = self.df.dropna()

        # change datatype
        self.df['Date'] = pd.to_datetime(self.df['Date'])

    # export the table to postrgres database
    def export_sql(self):
        try:
            engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
            self.df.to_sql('scraped_medical_data', engine, if_exists='replace', index = False)

            self.info_log.info("Data successfully exported to table scraped_medical_data in the database.")    

        except Exception as e:
            self.error_log.error(f"Error while exporting data to PostgreSQL: {e}")

        finally:
            engine.dispose()





