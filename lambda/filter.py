import json
import boto3
import uuid
from urllib.parse import unquote_plus

def lambda_handler(event, context):

    print("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    print("From SNS: " + message)
    
    json_message = json.loads(message)
    print("Input JSON: " + json.dumps(json_message, indent=2))
    
    key = extract_key(json_message)
    if key:
        good_file = check_file(json_message)
        if good_file:
            destination_key, candidate_name, candidate_email = move_file_good(key)
            if destination_key:
                publish_message("Resume submission from " + candidate_name,
                		"Resume ready for processing: " + destination_key + "\n" +
                		"Candidate email " + candidate_email)
            else:
                publish_message("Failed submission",
				"Unable to process request: " + json.dumps(json_message, indent=2))
                return "Failure"
        else:
            destination_key, candidate_name, candidate_email = move_file_bad(key)
            if destination_key:
                publish_message("WARNING - Suspicious resume submission from " + candidate_name,
                		"Resume has been copied to: " + destination_key + "\n" +
                		"Candidate email " + candidate_email + "\n" +
                		"Details of analysis:\n" + 
                		json.dumps(json_message['report'], indent = 2))
            else:
                publish_message("Failed submission",
                		"Unable to process request: " + json.dumps(json_message, indent=2))
                return "Failure" 
    else:
        publish_message("Failed submission",
			"Unable to process request: " + json.dumps(json_message, indent=2))
        return "Failure"
    
    return "Success"
    
def extract_key(message):
    try:
       return unquote_plus(message['s3']['object']['key'])
    except Exception as e:
       print("Error extracting key: " + str(e))
       return None
    
def check_file(message):
    try:
       return message['report']['score'] >= 50   
    except Exception as e:
       print("Error reading report: " + str(e))
    
    return False

def move_file_good(key):
    try:
        s3 = boto3.resource('s3', region_name='eu-central-1')
        
        info = s3.meta.client.head_object(Bucket='ostriches-in', Key=key)
        metadata = info['Metadata']
        
        copy_source = {
            'Bucket': 'ostriches-in',
            'Key': key
        }
        destination_key = uuid.uuid4().hex + "/" + key
        s3.meta.client.copy(copy_source, 'ostriches-good', destination_key)
    
        obj = s3.Object('ostriches-in', key)
        obj.delete()
    
        return destination_key, metadata['x-amz-meta-candidate-name'], metadata['x-amz-meta-candidate-email']
        
    except Exception as e:
        print("Error moving file: " + str(e))

def move_file_bad(key):
    try:
        s3 = boto3.resource('s3', region_name='eu-central-1')
        
        info = s3.meta.client.head_object(Bucket='ostriches-in', Key=key)
        metadata = info['Metadata']
        
        copy_source = {
            'Bucket': 'ostriches-in',
            'Key': key
        }
        destination_key = uuid.uuid4().hex + "/" + key
        s3.meta.client.copy(copy_source, 'ostriches-bad', destination_key)

        obj = s3.Object('ostriches-in', key)
        obj.delete()
    
        return destination_key, metadata['x-amz-meta-candidate-name'], metadata['x-amz-meta-candidate-email']
    except Exception as e:
        print("Error moving file: " + str(e))
        

def publish_message(subject, message):

    sns_client = boto3.client('sns')
    
    sns_client.publish(
        TopicArn='arn:aws:sns:eu-central-1:457649757384:ostriches-email',
        Subject=subject,
        Message=message
    )
    
    
    
    
    

