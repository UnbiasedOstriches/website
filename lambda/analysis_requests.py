import json
import logging
import boto3
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import os
import requests
from urllib.parse import unquote_plus




def lambda_handler(event, context):
    # TODO implement
    logger.info('Got event: ' + str(event))
    s3_client = boto3.client('s3')
    sns_client = boto3.client('sns')
    process_records(event['Records'], s3_client, sns_client)


def process_records(records, s3_client, sns_client):
    for record in records:
        print(record['s3'])
        logger.info('Got record: ' + str(record))
        #print("Json record" + str(json_record))
        bucket_name=None
        file_name=None
        if "s3" in record and "bucket" in record['s3'] and "name" in record['s3']['bucket']:
            bucket_name = record['s3']['bucket']['name']
            print("Bucket Name : " + bucket_name)
        if "s3" in record and "object" in record['s3'] and "key" in record['s3']['object']:
            file_name = record['s3']['object']['key']
            print("File Name : " + file_name)
        if bucket_name != None and file_name != None:
            get_file(s3_client, bucket_name, file_name)

        auth_key = os.environ['AUTH_KEY']
        #print("Auth key", str(auth_key))
        access_token = get_auth_token(auth_key)
        #print("Access token : ", str(access_token))

        response_text = submit_static_request("/tmp/"+file_name, access_token)
        print("Response :", response_text )

        result = {}
        result['report'] = response_text['report']
        result['s3'] = record['s3']

        sns_client.publish(
            TopicArn=os.environ['SNS_TOPIC_NAME'],
            Message=json.dumps(result)
            )



def get_file(s3_client, bucket_name, file_name):
    with open("/tmp/"+file_name, 'wb') as filedata:
        s3_client.download_fileobj(bucket_name, unquote_plus(file_name), filedata)


def get_auth_token(auth_key):
    try:
        POST_HEADERS = { 'Authorization' : auth_key, 'Content-Type': 'application/x-www-form-urlencoded'}
        BODY_PARAMS = {'grant_type' : 'client_credentials'}
        response = requests.post( url = os.environ['AUTH_URL'], data = BODY_PARAMS, headers = POST_HEADERS)
        if response.status_code == 200 :
            json_output = json.loads(response.text)
            if "access_token" in json_output:
                return json_output['access_token']
            else:
                return None
    except requests.ConnectionError:
        logging.error('Connection Error for the request')
    except :
        logging.error("Exception in getting static report")


def submit_static_request(filepath, ACCESS_TOKEN):
    try:
        POST_HEADERS = { 'Authorization': ACCESS_TOKEN , 'Accept': 'application/json' }
        files = {'file': ('resume', open(filepath, 'rb'), 'multipart/form-data') }
        response = requests.post( url = os.environ['STATIC_URL'], files = files, headers = POST_HEADERS)
        #print (response.text)
        if response.status_code == 200 :
            return json.loads(response.text)
        elif response.status_code == 202:
            response_text = json.loads(response.text)
            if 'jobStatus' in response_text:
                job_status=response_text['jobStatus']
            else:
                return None
            if job_status == "IN_PROGRESS":
                if   "jobId" in response_text:
                    jobid = response_text['jobId']
                    count=0
                    while True:
                        if count > 10:
                            return None
                            break;
                        response = get_static_report_jobid(jobid)
                        if response.status_code == 202:
                            time.sleep(5)
                            count = count + 1
                            continue
                        elif response.status_code == 200:
                            return json.loads(response.text)
                else:
                    return None
        else:
            return None

    except requests.ConnectionError:
        logging.error('Connection Error for the request')
    except :
        logging.error("Exception in getting static report")


def get_static_report_jobid(jobid, ACCESS_TOKEN):
    try:

        AUTH_HEADERS = { 'Authorization': ACCESS_TOKEN }
        static_url = os.environ['STATIC_URL'] + "/reports/" + jobid
        print (static_url)
        response = requests.get( url = static_url, headers = AUTH_HEADERS, params = PARAMS )
        if response.status_code == 200 :
            return response
    except requests.ConnectionError:
        logging.error('Connection Error for the request')
    except :
        logging.error("Exception in getting static report")


