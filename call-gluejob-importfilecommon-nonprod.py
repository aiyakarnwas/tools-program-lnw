import boto3
import logging
from botocore.exceptions import ClientError

# ตั้งค่า logger สำหรับแสดง log
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# สร้างคลาส GlueWrapper
class GlueWrapper:
    """Encapsulates AWS Glue actions."""

    def __init__(self, glue_client):
        """
        :param glue_client: A Boto3 Glue client.
        """
        self.glue_client = glue_client

    def start_job_run(self, name, s3_bucket,s3_path,s3_file_names,prefix_name,total_file):
        """
        Starts a job run. A job run extracts data from the source, transforms it,
        and loads it to the output bucket.

        :param name: The name of the job definition.
        :param s3_bucket: s3 bucket.
        :param s3_path: .
        :param s3_file_names: .
        :param prefix_name: .
        :param total_file: .
        :return: The ID of the job run.
        """
        try:
            # The custom Arguments that are passed to this function are used by the
            # Python ETL script to determine the location of input and output data.
            response = self.glue_client.start_job_run(
                JobName=name,
                Arguments={
                    "--s3_bucket": s3_bucket,
                    "--s3_path": s3_path,
                    "--s3_file_names": s3_file_names,
                    "--prefix_name": prefix_name,
                    "--total_file": total_file,
                },
            )
        except ClientError as err:
            logger.error(
                "Couldn't start job run %s. Here's why: %s: %s",
                name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["JobRunId"]

# สร้าง Boto3 Glue client
glue_client = boto3.client('glue', region_name='ap-southeast-1')

# สร้าง object ของ GlueWrapper
glue_wrapper = GlueWrapper(glue_client)

job_name = 'tcrb-debtacq-importfile-common-import-job'
s3_bucket = 'tcrb-debtacq-debtacquisition-nonprod'
s3_path = 'inbound/internal_data/edge/specialist/process'
s3_file_names = '[{"ctrl_file": "CTRL_EIM_EDGE_BLACKLIST_20241022_123204.txt", "data_file": "EIM_EDGE_BLACKLIST_20241022_123204.zip.enc"}]'
prefix_name = 'EIM_EDGE_BLACKLIST'
total_file = '0'

try:
    job_run_id = glue_wrapper.start_job_run(
        name=job_name, 
        s3_bucket=s3_bucket,
        s3_path=s3_path,
        s3_file_names=s3_file_names,
        prefix_name=prefix_name,
        total_file=total_file
    )
    logger.info(f"Started Glue job run with ID: {job_run_id}")
except ClientError as e:
    logger.error(f"Failed to start Glue job: {e}")
