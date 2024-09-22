import unittest

from unittest.mock import patch, MagicMock

from src.script import *

class TestMyModule(unittest.TestCase):

    @patch('boto3.client')
    def test_create_bucket(self):
        # Arrange
        s3_client = boto3.client('s3', region_name='us-east-1')
        bucket_name = "teste-trigger-lambda"

        create_bucket(bucket_name)

        buckets = s3_client.list_buckets()["Buckets"]
        self.assertEqual(len(buckets), 1)
        self.assertEqual(buckets[0]["Name"], bucket_name)

    @patch('boto3.client')
    def test_add_permission(self):
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        function_name = "lambda-trigger-s3"

        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.8',
            Role='role-arn',
            Handler='handler_name',
            Code={'ZipFile': b'function_code'}
        )

        add_permission(function_name, "teste-trigger-lambda")

        permissions = lambda_client.get_policy(FunctionName=function_name)
        self.assertIn('s3.amazonaws.com', permissions['Policy'])

    @patch('boto3.client')
    def test_put_bucket_notification_configuration_lambda(self):
        s3_client = boto3.client('s3', region_name='us-east-1')
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        function_name = "lambda-trigger-s3"
        bucket_name = "teste-trigger-lambda"
        
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.8',
            Role='role-arn',
            Handler='handler_name',
            Code={'ZipFile': b'function_code'}
        )
        s3_client.create_bucket(Bucket=bucket_name)

        put_bucket_notification_configuration_lambda(bucket_name, function_name, 'uploads/', '.json')

        notification_config = s3_client.get_bucket_notification_configuration(Bucket=bucket_name)
        self.assertIn('LambdaFunctionConfigurations', notification_config)
        self.assertEqual(len(notification_config['LambdaFunctionConfigurations']), 1)

if __name__ == '__main__':
    unittest.main()
