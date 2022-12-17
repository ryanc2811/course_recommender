from flask import Flask, jsonify,request
from collections import defaultdict
import pandas as pd
from sklearn.cluster import KMeans


progress_path = '../../data/Progress.csv'
courses_path='../../data/CPD_Courses.csv'
# The flask app for serving predictions
app = Flask(__name__)


def load_data():
    df_progress = pd.read_csv(progress_path)
    df_courses = pd.read_csv(courses_path)
    
    return df_progress,df_courses

def generate_user_model():
    progress,courses=load_data()
        
    
    #convert progress percentage string to numeric data
    progress['Progress'] = progress['Progress'].astype('float') / 100.0

    # Calculate the average rating all categories per user
    category_watch_time_df = get_all_category_watch_time(progress, courses)
        
    #replace NaN with 0
    category_watch_time_df = category_watch_time_df.fillna(0)
        
    #remove student id from dataframe
    category_watch_time_list = category_watch_time_df.drop(['UserID'], axis=1)
        
    category_watch_time_list.shape
        
    # Turn our dataset into a list
    category_watch_time_list = category_watch_time_list.values
        
    # Create an instance of KMeans to find 20 clusters
    km = KMeans(n_clusters=20, random_state=0)

    predictions=km.fit_predict(category_watch_time_list)


    return predictions,category_watch_time_df
 
def get_list_of_categories(courses):
    category_list = []
    
    for category in courses.Categories.str.split('|'):
        for name in category:
            if name not in category_list: 
                category_list.append(name.strip())
            
    return category_list

def get_column_name_list(category_list):
    column_name = []
    
    for category in category_list:
        column_name.append('avg_' + category.strip() + '_watch')
      
    return column_name

#category watch time across ALL students across ALL categories
def get_all_category_watch_time(users, courses):
    category_progress = pd.DataFrame(columns = ['UserID'])
    category_list = get_list_of_categories(courses)
    column_names = get_column_name_list(category_list)
    
    #add studentId to list of columns
    column_names.insert(0,'UserID')
    
    for category in category_list:        
        course_categories = courses[courses['Categories'].str.contains(category)]
        
        #determine the average watch time for the given category; retain the studentId
        avg_watch_time_per_user = users[users['CourseID'].isin(course_categories['CourseID'])].loc[:, ['UserID', 'Progress']].groupby(['UserID'])['Progress'].mean().round(2).reset_index()      
    
        #merge the progress for the given catetgory with the prior categories
        category_progress = category_progress.merge(avg_watch_time_per_user, on='UserID', how='outer')
            
    category_progress.columns = column_names
    return category_progress

    
def predict(user_id, predictions):
    """For the inputs, do the prediction and return it."""

    print('Predicting rating ...')
    #convert numpy array to dataframe and give column name of cluster
    cluster_df = pd.DataFrame(data=predictions)
    cluster_df.columns = ['assigned_cluster']
    
    # merge data to see the assigned cluster for user ID and drop unnecessary columns
    user_cluster_df = pd.DataFrame(columns = ['UserID', 'assigned_cluster'])
    user_cluster_df = pd.concat([cluster_df, category_watch_time_df], axis=1)
    user_cluster_df = user_cluster_df[user_cluster_df.columns[user_cluster_df.columns.isin(['UserID', 'assigned_cluster'])]]

    progress_df,courses_df=load_data()
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

    category_list = get_list_of_categories(cluster_courses_watched_df)
    print("The amount of categories for Cluster "+str(cluster)+": ", len(category_list))
    print("The categories in Cluster "+str(cluster), category_list)
      
    return category_list


predictions,category_watch_time_df = generate_user_model()


@app.route('/',methods=["GET","POST"])
def prefict():
    if request.method=="POST":
        user_id=request.user_id
        # Check that user exists:
        try:
            users,courses=load_data()
            users.loc[user_id]
        except:
            return jsonify({"error": "The user does not exist"})
        user_predicted_categories = predict(user_id, predictions)
        return jsonify({"predicted_categories": user_predicted_categories})
    return jsonify({"error": "The user does not exist"})

if __name__=="__main__":
    app.run(host='0.0.0.0',port=80)
