import boto3
from botocore.exceptions import ClientError


class SecretManager:
    def __init__(self, region_name='ap-southeast-1'):
        self.secret_manager = boto3.client('secretsmanager', region_name=region_name)
    
    def get_secret_value(self, secret_name: str) -> str:
        try:
            response = self.secret_manager.get_secret_value(SecretId=secret_name)
            return response["SecretString"]
        except self.secret_manager.exceptions.ResourceNotFoundException as e:
            msg = f"The requested secret '{secret_name}' was not found."
            print(msg)
            raise ValueError(msg) from e
        except self.secret_manager.exceptions.AccessDeniedException as e:
            msg = f"Access denied to secret '{secret_name}'. Check IAM permissions."
            print(msg)
            raise PermissionError(msg) from e
        except ClientError as e:
            print(f"A client error occurred: {e.response['Error']['Message']}.")
            raise e
        except Exception as e:
            print(f"An unknown error occurred: {str(e)}.")
            raise e

    def get_secret_plain_text(self, secret_name):
        try:
            get_secret_value_response = self.secret_manager.get_secret_value(SecretId=secret_name)
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                secret = get_secret_value_response['SecretBinary']
            return secret
        except ClientError as e:
            print(f"A client error occurred: {e.response['Error']['Message']}.")
            raise e
        except Exception as e:
            print(f"An unknown error occurred: {str(e)}.")
            raise e

