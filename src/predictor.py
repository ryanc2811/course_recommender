import os
from flask import Flask, Response, request
from collections import defaultdict
import pickle
import pandas as pd

# Path where SageMaker mounts data in our container
prefix = '/opt/ml/'
model_path = os.path.join(prefix, 'model', 'recommender_system')
input_path = prefix + 'input/data'
channel_name_train = 'train'
training_path = os.path.join(input_path, channel_name_train)

class ScoringService(object):
    model = None

    @classmethod
    def get_model(cls):
        """Get the model for this instance if not already loaded."""
        if cls.model == None:
            print('Loading model ...')
            _, cls.model = pickle.load(open(model_path, 'rb'))
        return cls.model


    @classmethod
    def load_data():
        progress_path=os.path.join(training_path,'Progress.csv')
        courses_path=os.path.join(training_path,'CPD_Courses.csv')
        
        df_progress = pd.read_csv(progress_path)
        df_courses = pd.read_csv(courses_path)
        
        return df_progress,df_courses

    @classmethod
    def get_list_of_categories(courses):
        category_list = []
        
        for category in courses.Categories.str.split('|'):
            for name in category:
                if name not in category_list: 
                    category_list.append(name.strip())
                
        return category_list

    @classmethod
    def predict(cls, user_id):
        """For the inputs, do the prediction and return it."""
        model = cls.get_model()
        """ print('Predicting rating ...')
        #convert numpy array to dataframe and give column name of cluster
        cluster_df = pd.DataFrame(data=model.predictions)
        cluster_df.columns = ['assigned_cluster']
        
        category_watch_time_df=pd.DataFrame(data=model.trainset)
        # merge data to see the assigned cluster for user ID and drop unnecessary columns
        user_cluster_df = pd.DataFrame(columns = ['UserID', 'assigned_cluster'])
        user_cluster_df = pd.concat([cluster_df, category_watch_time_df], axis=1)
        user_cluster_df = user_cluster_df[user_cluster_df.columns[user_cluster_df.columns.isin(['UserID', 'assigned_cluster'])]]

        progress_df,courses_df=cls.load_data()
        cluster = df.loc[df['UserID'] == user_id].assigned_cluster.values[0]
        df= df.loc[df['assigned_cluster'] == cluster]

        cluster_users_df = progress_df[progress_df['UserID'].isin(df['UserID'])]
        #convert progress percentage string to numeric data
        cluster_users_df['Progress'] = cluster_users_df['Progress'].astype('float') / 100.0
        #limit to only courses that are above a 90% watch rate
        cluster_users_df = cluster_users_df.loc[cluster_users_df['Progress'] > .90]
        #Get the course categories for courses watched (course Id) by students in cluster 
        cluster_courses_watched_df = courses_df[courses_df['CourseID'].isin(cluster_users_df['CourseID'])]
        #Get rid of NaN
        cluster_courses_watched_df.dropna(subset=['Categories'], inplace=True)

        category_list = cls.get_list_of_categories(cluster_courses_watched_df)
        print("The amount of categories for Cluster "+str(cluster)+": ", len(category_list))
        print("The categories in Cluster "+str(cluster), category_list) """
      
        return model


# The flask app for serving predictions
app = Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    health = ScoringService.get_model() is not None
    status = 200 if health else 404
    return Response(response='\n', status=status, mimetype='application/json')

@app.route('/invocations', methods=['POST'])
def recommend():
    """Determine the prediction for the given user and movie."""
    content = request.json
    user_id = content['UserID']
    response = ScoringService.predict(user_id)
    return Response(response=response, status=200, mimetype="application/json")
