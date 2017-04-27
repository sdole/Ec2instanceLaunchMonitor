from __future__ import print_function

import boto3
import json
import datetime
import sys
import traceback

cw_client = boto3.client('cloudwatch')
ec2_client = boto3.client('ec2')


def run(event, context):
    try:
        config = json.load(open("ec2_launch_monitor.config.json"))
        print(json.dumps(event))
        instance_state = event["detail"]["state"]
        instance = ec2_client.describe_instances(InstanceIds=[event["detail"]["instance-id"]])
        instance_size = instance["Reservations"][0]["Instances"][0]["InstanceType"]
        if instance_state in ["pending", "terminated", "stopped"]:
            if instance_state == "pending":
                state_dim = "started"
            else:
                state_dim = "stopped"
            dimensions = [{'Name': 'state', 'Value': state_dim}, {'Name': 'size', 'Value': instance_size}]
            put_metric(config, dimensions)
            dimensions = [{'Name': 'state', 'Value': state_dim}]
            put_metric(config, dimensions)
    except BaseException as be:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        raise be


def put_metric(config, dimensions):
    response = cw_client.put_metric_data(
        Namespace=config["MetricNameSpace"],
        MetricData=[
            {
                'MetricName': config["MetricName"],
                'Dimensions': dimensions,
                'Timestamp': datetime.datetime.now(),
                'Value': 1,

                'Unit': 'Count'
            },
        ]
    )
    return response


if __name__ == "__main__":
    run({
        "account": "623990728151",
        "region": "us-east-1",
        "detail": {
            "state": "pending",
            "instance-id": "i-0099133e34fee89b5"
        },
        "detail-type": "EC2 Instance State-change Notification",
        "source": "aws.ec2",
        "version": "0",
        "time": "2017-04-21T14:17:06Z",
        "id": "240df010-1942-4465-91b0-6a895483aed5",
        "resources": [
            "arn:aws:ec2:us-east-1:623990728151:instance/i-03b57910f29b4cb82"
        ]
    }, None)
