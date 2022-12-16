'''
This code should be copied into a Lambda function of AWS.
Make sure to create an 'ENDPOINT_NAME' variable to points to your SageMaker Endpoint.
'''

import os
import boto3
import json
import pandas as pd

# grab environment variables
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']

runtime = boto3.client('runtime.sagemaker')
s3_client = boto3.client('s3')
bucket = 'glp-course-recommender'
courses_filename = 'CPD_Courses.csv'

def lambda_handler(event, context):

    payload = json.dumps(event)
    
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='application/json',
                                       Body=payload)
    
    file_contents = s3_client.get_object(Bucket=bucket, Key=courses_filename)
    courses = pd.read_csv(file_contents['Body'], usecols=[0,1], index_col=0, squeeze=True).to_dict()
    
    course_id = event['CourseID']
    predicted_value = courses[course_id] + ' : ' + response['Body'].read().decode()
    
    return predicted_value
