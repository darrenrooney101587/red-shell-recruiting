#!/bin/bash
# Resume dev EC2 and RDS resources
# Usage: ./resume_dev_env.sh <aws_profile> <aws_region>

set -e

EC2_INSTANCE_ID="i-0ac8f914ed77e97b3"  # Replace with your EC2 instance ID
RDS_INSTANCE_ID="client-database-1"     # Replace with your RDS instance identifier
AWS_PROFILE=${1:-red-shell-recruiting-dev}
AWS_REGION=${2:-us-east-2}

# Start EC2 instance
echo "Starting EC2 instance: $EC2_INSTANCE_ID using profile $AWS_PROFILE in region $AWS_REGION"
aws ec2 start-instances --instance-ids "$EC2_INSTANCE_ID" --profile "$AWS_PROFILE" --region "$AWS_REGION"

# Start RDS instance
echo "Starting RDS instance: $RDS_INSTANCE_ID using profile $AWS_PROFILE in region $AWS_REGION"
aws rds start-db-instance --db-instance-identifier "$RDS_INSTANCE_ID" --profile "$AWS_PROFILE" --region "$AWS_REGION"
