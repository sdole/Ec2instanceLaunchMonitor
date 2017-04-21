from __future__ import print_function

import boto3
import json
import datetime

cw_client = boto3.client('cloudwatch')
ec2_client = boto3.client('ec2')


def run(event, context):
    print(json.dumps(event))
    instance_state = event["detail"]["state"]
    instance = ec2_client.describe_instances(InstanceIds=[event["detail"]["instance-id"]])
    instance_size = instance["Reservations"][0]["Instances"]["InstanceType"]
    if instance_state in ["pending", "terminated", "stopped"]:
        if instance_state == "pending":
            state_dim = "started"
        else:
            state_dim = "stopped"
        response = cw_client.put_metric_data(
            Namespace='SSI/ArchDev/EC2',
            MetricData=[
                {
                    'MetricName': 'InstanceStateEvent',
                    'Dimensions': [
                        {
                            'Name': 'region',
                            'Value': event["region"]
                        },
                        {
                            'Name': 'state',
                            'Value': state_dim
                        }
                        ,
                        {
                            'Name': 'size',
                            'Value': instance_size
                        }
                    ],
                    'Timestamp': datetime.time(),
                    'Value': 1,

                    'Unit': 'Count'
                },
            ]
        )
        print(json.dumps(response))
