import os
import zipfile
import hashlib
import json
import boto3
import gnupg  # Import the GPG library
from pathlib import Path

class FileProcessor:
    def __init__(self):
        region_name = 'ap-southeast-1'
        self.secret_manager = boto3.client('secretsmanager', region_name=region_name)
        
        # Initialize GPG
        self.gpg = gnupg.GPG()
        
        # Create necessary directories
        self.input_dir = Path('input')
        self.zipped_dir = Path('zipped')
        self.encrypted_dir = Path('encrypted')
        self.result_dir = Path('result')
        
        # Create folders if they do not exist
        for directory in [self.input_dir, self.zipped_dir, self.encrypted_dir, self.result_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    # def zip_file(self, file_path: str, output_name: str) -> str:
    #     """Zip the file and store it in the zipped directory."""
    #     output_path = self.zipped_dir / f'{output_name}.zip'
    #     with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    #         zip_file.write(file_path, arcname=os.path.basename(file_path))
    #     return str(output_path)

    # def encrypt_gpg_file(self, file_name, public_key: str, input_file_path: str) -> str:
    #     """เข้ารหัสไฟล์โดยใช้ GPG และบันทึกเป็นไฟล์ไบนารี"""
    #     # นำเข้า public key
    #     import_result = self.gpg.import_keys(public_key)
    #     print(f'Imported fingerprints: {import_result.fingerprints}')
    #     if not import_result or not import_result.fingerprints:
    #         raise ValueError("นำเข้า public key สำหรับการเข้ารหัส GPG ไม่สำเร็จ")

    #     # เตรียมเส้นทางไฟล์ output
    #     output_file_path = self.encrypted_dir / f"{file_name}.zip.enc"
    #     print(f'output_file_path: {output_file_path}')
    #     # เปิดไฟล์เพื่อเข้ารหัส
    #     with open(input_file_path, 'rb') as file:
    #         # เข้ารหัสเนื้อหาไฟล์โดยใช้ fingerprint แรก
    #         status = self.gpg.encrypt(file.read(), recipients=[import_result.fingerprints[0]], always_trust=True)

    #         # ตรวจสอบความสำเร็จของการเข้ารหัส
    #         if not status.ok:
    #             print(f"ข้อผิดพลาดในการเข้ารหัส GPG: {status.stderr}")  # ข้อมูล debug
    #             raise ValueError(f"การเข้ารหัส GPG ล้มเหลว: {status.status}")

    #     # บันทึกข้อมูลที่เข้ารหัสลงไฟล์
    #     with open(output_file_path, 'wb') as file_encrypt:
    #         file_encrypt.write(status.data)
            
    #     print(f"การเข้ารหัสสำเร็จ: {output_file_path}")
    #     return str(output_file_path)


    def create_ctrl_file(self, org_file_name: str, file_name: str, record_count: int, date: str, checksum: str) -> str:
        """Create the control file content."""
        ctrl_content = f"{file_name}|{record_count}|{date}|{checksum}"
        ctrl_file_path = self.result_dir / f'CTRL_{org_file_name}.txt'
        with open(ctrl_file_path, 'w') as ctrl_file:
            ctrl_file.write(ctrl_content)
        return str(ctrl_file_path)

    def _calculate_checksum_from_file(self, file_path):
        """Calculate checksum (SHA256) from the provided file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def process_file(self, file_name: str, input_file: str, public_key: str, record_count: int, date: str) -> str:
        """Main processing function to zip, encrypt, and create control file."""
        # Step 1: Zip the file
        # zip_file_path = self.zip_file(input_file, file_name)

        # Step 2: Encrypt the zipped file with GPG
        # encrypted_file_path = self.encrypt_gpg_file(file_name, public_key, zip_file_path)
        encrypted_file_path = f"input/{file_name}.zip.enc"
        # Step 3: Get the checksum of the encrypted file for the control file
        checksum = self._calculate_checksum_from_file(encrypted_file_path)
        print(f"cal checksum : {checksum}")
        
        # Step 4: Create the control file
        ctrl_file_path = self.create_ctrl_file(file_name, f"{file_name}.zip.enc", record_count, date, checksum)

        # Step 5: Move the encrypted file to the result directory
        # encrypted_result_path = self.result_dir / f"{file_name}.zip.gpg"
        # os.rename(encrypted_file_path, encrypted_result_path)

        return ctrl_file_path

    def get_secret_plain_text(self, secret_name):
        try:
            get_secret_value_response = self.secret_manager.get_secret_value(SecretId=secret_name)
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                secret = get_secret_value_response['SecretBinary']
            return secret
        except Exception as e:
            print(f"An unknown error occurred: {str(e)}.")
            raise e
 
        

# Usage example
if __name__ == "__main__":
    print('##### START #####')
    processor = FileProcessor()

    file_path = 'input/EIM_EDGE_BLACKLIST_20241030_125300.txt'
    file_name = 'EIM_EDGE_BLACKLIST_20241030_125300'
    print(f"file_path: {file_path}")
    print(f"file_name: {file_name}")
    

    # Example data and parameters
    public_key = processor.get_secret_plain_text('key/debt-acq/edge-public-pgp')

    record_count = 0  # Replace with the actual count
    date = "20241030"  # The date in your format

    # Process the file
    ctrl_file_path = processor.process_file(file_name, file_path, public_key, record_count, date)
    print(f"Control file created at: {ctrl_file_path}")
