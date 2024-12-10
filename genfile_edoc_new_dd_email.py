import random
import hashlib
from faker import Faker
from datetime import datetime
import json
import shutil
import zipfile
import boto3
import os
from io import BytesIO

from encryption import Encryption
from secrets_manager import SecretManager

fake = Faker()
Faker.seed(0)

s3_client = boto3.client('s3')

def get_round_v(total_record, n):
    curr = int(n)
    ntotal_record = int(total_record)
    round_validate = []
    for i in range(0, ntotal_record + 1, curr):
        if ntotal_record > i:
            round_validate.append(i)
    return round_validate


# ฟังก์ชันสำหรับสร้างชื่อไฟล์ zip
def generate_zip_file_name(base_name, round_no, sequence_no, total_files, date, output_folder=None):
    if not output_folder:
        return f"{base_name}_{sequence_no:03}_{date}.zip"
    return os.path.join(output_folder, f"{base_name}_{sequence_no:03}_{date}.zip")

# ฟังก์ชันสำหรับสร้างชื่อไฟล์ PDF
def generate_pdf_file_name(base_name, thai_id, date, output_folder=None):
    hash_id = hashlib.sha256(thai_id.encode()).hexdigest()
    # ใช้ 3 ตัวแรกของ thai_id
    prefix = int(thai_id[:3])
    if not output_folder:
        return f"{base_name}_{prefix}_{date}.pdf"
    return os.path.join(output_folder, f"{base_name}_{prefix}_{date}.pdf")

# คัดลอกและเปลี่ยนชื่อ PDF
def copy_pdf(source_file, dest_file):
    shutil.copy(source_file, dest_file)

# สร้างไฟล์ ZIP
def create_zip_file(zip_file_name, files_to_include):
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for file in files_to_include:
            zipf.write(file, os.path.basename(file))

# อัปโหลดไฟล์ไปยัง S3
def upload_to_s3(file_name, bucket_name, s3_key):
    s3_client.upload_file(file_name, bucket_name, s3_key)

# สร้างข้อมูล header
def create_header(date, branch_code="051000", system_code="TACN", round_no=1, file_code="EVDDDEML"):
    return f"H|{date}|{branch_code}|{system_code}|{round_no:03}|{file_code}"

# สร้างข้อมูล detail
def create_detail_record(data, date, round_no=1, sequence_no=1, total_files=1):
    # แปลง date จาก YYYYMMDD เป็น YYYY-MM-DD
    original_date = date
    date_obj = datetime.strptime(original_date, "%Y%m%d")
    formatted_date = date_obj.strftime("%Y-%m-%d")  # เปลี่ยนเป็นฟอร์แมตที่ต้องการ

    thai_id = data["cid"]
    datetime_sending = f"{formatted_date}T09:29:45.123+0700"  # ใช้ formatted_date แทน date ที่ไม่ได้ปรับ
    email_body_zip = generate_zip_file_name("EVD_1stDD_Email_body", round_no, sequence_no, total_files, original_date)
    email_body_pdf = generate_pdf_file_name("EVD_1stDD_Email_body", thai_id, original_date)
    
    loan_account_no = data["partner_customer_id"]
    term_loan_account_no = data.get("partner_account_no", "")
    product_name = "02"
    email = fake.email()
    datetime_sending = f"{formatted_date}T09:29:45.123+0700"  # ใช้ formatted_date แทน date ที่ไม่ได้ปรับ
    result = "000"  # สมมุติว่าผ่าน
    reject_reason = ""
    transfer_date = data["transfer_date"]
        
    return f"D|{thai_id}|{loan_account_no}|{term_loan_account_no}|{product_name}|{email}|{datetime_sending}|{email_body_pdf}|{email_body_zip}.enc|{result}|{reject_reason}|{transfer_date}|||||"
        
        
# สร้างข้อมูล trailer
def create_trailer(date, branch_code="051000", system_code="TACN", round_no=1, total_records=1):
    return f"T|{date}|{branch_code}|{system_code}|{round_no:03}|{total_records}"

# สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ
def generate_file_name(date, round_no=1, sequence_no=1, total_files=1, output_folder="output"):
    return os.path.join(output_folder, f"TCRB_EVD1stDDEmail_{date}{round_no:03}_{sequence_no:03}of{total_files:03}.txt")

# ฟังก์ชันสำหรับลบไฟล์
def cleanup_files(files):
    for file in files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")


# ปรับฟังก์ชัน generate_file
def generate_file(
    json_file_path,
    pdf_email_body,
    pdf_template,
    bucket_name,
    round_no=1,
    sequence_no=1,
    total_files=1,
    max_records=None,
    public_key_secret_name=None,
    records_per_file=1000
):
    output_folder = "output"
    
    # สร้างโฟลเดอร์ output หากยังไม่มี
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # สร้าง list_round
    list_round = get_round_v(total_record=max_records, n=records_per_file)
    print(f"list_round: {list_round}")
    total_round = len(list_round)
    print(f"total_round: {total_round}")


    # อ่านข้อมูล JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    if max_records:
        json_data = json_data[:max_records]

    date = datetime.now().strftime("%Y%m%d")
    details = []

    # สร้างไฟล์ ZIP สำหรับ EVD_1stDD_Email_body
    for idx, start_idx in enumerate(list_round[:-1]):
        end_idx = list_round[idx + 1]
        zip_file_name = generate_zip_file_name(
            "EVD_1stDD_Email_body", round_no, idx + 1, total_round, date, output_folder
        )

        try:
            with zipfile.ZipFile(zip_file_name, 'a') as evdtf_zipf:
                existing_files = evdtf_zipf.namelist()  # ดึงรายชื่อไฟล์ใน ZIP
                for record in json_data[start_idx:end_idx]:
                    detail = create_detail_record(record, date, round_no, idx + 1, total_round)
                    details.append(detail)

                    pdf_file_name = generate_pdf_file_name("EVD_1stDD_Email_body", record["cid"], date, output_folder)
                    copy_pdf(pdf_template, pdf_file_name)
                    # ตรวจสอบว่าไฟล์ PDF มีอยู่ใน ZIP หรือไม่
                    if os.path.basename(pdf_file_name) not in existing_files:
                        evdtf_zipf.write(pdf_file_name, os.path.basename(pdf_file_name))
                    # else:
                    #     print(f"Skipped adding duplicate file: {pdf_file_name}")
                    # evdtf_zipf.write(pdf_file_name, os.path.basename(pdf_file_name))
                    cleanup_files([pdf_file_name])
        except Exception as e:
            print(f"Error creating EVD_1stDD_Email_body ZIP: {e}")
            return
        
    # เพิ่มขั้นตอนสร้างไฟล์สำหรับช่วงสุดท้าย
    if list_round[-1] < len(json_data):
        zip_file_name = generate_zip_file_name(
            "EVD_1stDD_Email_body", round_no, total_round, total_round, date, output_folder
        )

        try:
            with zipfile.ZipFile(zip_file_name, 'a') as evdtf_zipf:
                existing_files = evdtf_zipf.namelist()  # ดึงรายชื่อไฟล์ใน ZIP
                for record in json_data[list_round[-1]:]:
                    detail = create_detail_record(record, date, round_no, total_round, total_round)
                    details.append(detail)

                    pdf_file_name = generate_pdf_file_name("EVD_1stDD_Email_body", record["cid"], date, output_folder)
                    copy_pdf(pdf_template, pdf_file_name)
                    if os.path.basename(pdf_file_name) not in existing_files:
                        evdtf_zipf.write(pdf_file_name, os.path.basename(pdf_file_name))
                    cleanup_files([pdf_file_name])
        except Exception as e:
            print("error naja")
            print(f"Error creating EVD_1stDD_Email_body ZIP for final round: {e}")
            return

    # สร้างไฟล์ TXT รวม Header, Detail และ Trailer
    filename = generate_file_name(date, round_no, sequence_no, total_files, output_folder)
    header = create_header(date, round_no=round_no)
    trailer = create_trailer(date, total_records=max_records, round_no=round_no)

    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.writelines("\n".join(details) + "\n")
        f.write(trailer + "\n")

    print(f"File '{filename}' generated successfully!")





# ตัวอย่างการเรียกใช้งาน
json_file_path = "customer_account_202412031404.json"  # กำหนด path ของไฟล์ JSON
pdf_email_body = "pdf_email_body.pdf"
pdf_template = "pdf_file_name.pdf"
bucket_name = "tcrb-debtacq-temp-pvt-nonprod"  # กำหนดชื่อ bucket
max_records = 2000
round_no = 2
public_key = "key/debt-acq/ascend-debt-public-gpg"
records_per_file = 1000

generate_file(json_file_path, pdf_email_body, pdf_template, bucket_name, round_no=round_no, sequence_no=1, total_files=1, max_records=max_records, public_key_secret_name=public_key, records_per_file=records_per_file)
