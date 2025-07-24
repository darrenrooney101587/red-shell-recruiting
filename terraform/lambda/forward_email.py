import boto3
import email
import os
import json

FORWARD_TO = os.environ.get("FORWARD_TO", "yourname@gmail.com")


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    ses = boto3.client("ses")

    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        obj = s3.get_object(Bucket=bucket, Key=key)
        raw_email = obj["Body"].read().decode("utf-8")

        msg = email.message_from_string(raw_email)

        subject = "FWD: " + msg.get("Subject", "")
        body = msg.get_payload()

        response = ses.send_email(
            Source="no-reply@redshellrecruiting.com",
            Destination={"ToAddresses": [FORWARD_TO]},
            Message={
                "Subject": {"Data": subject},
                "Body": {
                    "Text": {"Data": body if isinstance(body, str) else str(body)}
                },
            },
        )

    return {"status": "forwarded"}
