import boto3
import sys
import uuid

# Inicializando os clients
s3_client = boto3.client('s3')
lambda_client = boto3.client("lambda")

def main():
    bucket_name = sys.argv[1]
    lambda_function = sys.argv[2]
    folder = sys.argv[3]
    format_file = sys.argv[4]
    region = sys.argv[5]

    create_bucket(bucket_name, s3_client, region)
    add_permission(lambda_function, bucket_name, lambda_client)
    put_bucket_notification_configuration_lambda(bucket_name, lambda_function, folder, format_file, s3_client)

def create_bucket(bucket_name, s3_client, region):
    try:
        if region == 'us-east-1':
            response = s3_client.create_bucket(
                Bucket=bucket_name
            )
        else:
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                }
            )
        print(f"Bucket {bucket_name} criado com sucesso na região {region}")
    except Exception as e:
        print(f"Erro ao criar o bucket s3: {e}")

def add_permission(lambda_function, bucket_name, lambda_client):
    try:
        # gera StatementId dinâmico
        statement_id = f'id-{uuid.uuid4()}'

        response = lambda_client.add_permission(
            FunctionName=lambda_function,
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal='s3.amazonaws.com',
            SourceArn=f'arn:aws:s3:::{bucket_name}'
        )
        print('Permissões adicionadas à função Lambda com sucesso')
    except Exception as e:
        print(f'Erro ao adicionar permissões: {e}')

def put_bucket_notification_configuration_lambda(bucket_name, lambda_function, folder, format_file, s3_client):
    try:
        notification_configuration = {
            'LambdaFunctionConfigurations': [
                {
                    'LambdaFunctionArn': f'arn:aws:lambda:us-east-1:890438550356:function:{lambda_function}',
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {'Name': 'prefix', 'Value': folder},
                                {'Name': 'suffix', 'Value': format_file}
                            ]
                        }
                    }
                }
            ]
        }
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_configuration
        )
        print(f'Gatilho do bucket s3 adicionado com sucesso na lambda {lambda_function}')
    except Exception as e:
        print(f"Erro ao criar gatilho do bucket s3 na lambda: {e}")

if __name__ == "__main__":
    main()