import pandas as pd
import torch
import cv2
import logging
import os
import sys
import imghdr
import shutil
from dotenv import load_dotenv
from sqlalchemy import create_engine
from IPython.display import display, Image


load_dotenv()
user = os.getenv('user')
password = os.getenv('password')     
database = os.getenv('database')
host=os.getenv('host')   
port=os.getenv('port')

class Detection:
    def __init__(self):
        self.info_log = logging.getLogger('info')
        self.info_log.setLevel(logging.INFO)

        info_handler = logging.FileHandler('../logs/info.log')
        info_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        info_handler.setFormatter(info_formatter)
        self.info_log.addHandler(info_handler)

        self.error_log = logging.getLogger('error')
        self.error_log.setLevel(logging.ERROR)

        error_handler = logging.FileHandler('../logs/error.log')
        error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        error_handler.setFormatter(error_formatter)
        self.error_log.addHandler(error_handler)

        try:
            # connect to a database
            engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

            # read the data
            query = "SELECT * FROM medical_data_transformation"
            self.df = pd.read_sql(query, engine)

            self.info_log('Successfully imported data from database')

        except:
            self.error_log.error("Error occurred when loading the dataframe")

        finally:
            engine.dispose()

    # closes logging
    def close_log(self):
        self.info_log.info('Closing logging')
        handlers = self.info_log.handlers[1:]

        # close info logging 
        for handler in handlers:
            handler.close()
            self.info_log.removeHandler(handler)

        handlers = self.error_log.handlers[1:]

        # close error logging
        for handler in handlers:
            handler.close()
            self.error_log.removeHandler(handler)

    # return the dataframe
    def get_dataframe(self):
        self.info_log.info('Return the dataframe')
        return self.df
    
    # delete the directory if exists
    def delete_directory(path):
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)

    # object detection using YOLO
    def object_detection(self):
        self.info_log.info('Detecting objects within images')
        model = torch.hub.load('ultralytics/yolov5', 'yolov5m')

        images = self.df['Media Path']
        detection_df = pd.DataFrame(columns=['Image','Name','Confidence','xmin','ymin','xmax','ymax'])
    
        for img_path in images:
            # check if the file is image
            image_type = imghdr.what(img_path)
            image_name = os.path.basename(img_path)

            # Directory where results will be saved
            save_dir = 'detection_results/'

            # delete if the directory exists
            if os.path.exists(save_dir) and os.path.isdir(save_dir):
                shutil.rmtree(save_dir)

            if image_type != None:
                # load the image
                img = cv2.imread(img_path)

                # run the object detection
                result = model(img)

                # show the result
                result.show()

                # extract data from results
                detections = result.pandas().xyxy[0]
                
                # append to a dataframe
                detections['Image'] = image_name

                if detections.empty:   # check if their is no detection
                    empty_row = pd.DataFrame({'Image': [image_name]})
                    detection_df = pd.concat([detection_df, empty_row],ignore_index = True)

                else:
                    detection_df = pd.concat([detection_df, detections[['Image','name','confidence','xmin','ymin','xmax','ymax']].rename(columns={
                        'name':'Name','confidence':'Confidence'
                    })], ignore_index = True)

            else: pass

        # export as csv file
        detection_df.info()
        detection_df.to_csv(f'detection_results.csv', index = False)
        
    # export the dataframe to database
    def detection_to_postgres(self,dataframe):
        try:
            engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
            # export the detection result to a postgres database
            dataframe.to_sql('detection_results', engine, if_exists='replace', index = False)

            self.info_log.info("Data successfully exported to table detection_results in the database.") 

        except Exception as e:
            self.error_log.error(f"Error while exporting data to PostgreSQL: {e}")

        finally:
            engine.dispose()


            
    



