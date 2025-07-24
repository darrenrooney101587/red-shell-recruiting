resource "aws_s3_bucket" "email_bucket" {
  bucket = "red-shell-recruiting-emails"
  force_destroy = true
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda-ses-forward-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "ses_lambda_access" {
  name = "ses-s3-lambda-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:GetObject", "s3:PutObject"],
        Resource = "${aws_s3_bucket.email_bucket.arn}/*"
      },
      {
        Effect = "Allow",
        Action = "ses:ReceiveEmail",
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "forwarder" {
  function_name = "ses-email-forwarder"
  filename      = "${path.module}/lambda/forward_email.zip"
  handler       = "forward_email.lambda_handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_exec.arn
  timeout       = 30
  source_code_hash = filebase64sha256("${path.module}/lambda/forward_email.zip")
}

resource "aws_ses_receipt_rule_set" "default" {
  rule_set_name = "default-rule-set"
}

resource "aws_ses_receipt_rule" "forward_rule" {
  name          = "forward-rule"
  rule_set_name = aws_ses_receipt_rule_set.default.rule_set_name
  recipients    = ["redshellrecruiting.com"]
  enabled       = true
  scan_enabled  = true
  tls_policy    = "Optional"

  s3_action {
    position          = 1
    bucket_name       = aws_s3_bucket.email_bucket.bucket
    object_key_prefix = "emails/"
  }

  lambda_action {
    position          = 2
    function_arn      = aws_lambda_function.forwarder.arn
    invocation_type   = "Event"
  }

  stop_action {
    position          = 3
    scope             = "RuleSet"
  }
}
