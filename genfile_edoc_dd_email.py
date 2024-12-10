import random
import hashlib
from faker import Faker
from datetime import datetime
import json
import shutil
import zipfile
import boto3
import os

fake = Faker()
Faker.seed(0)

s3_client = boto3.client('s3')

# ฟังก์ชันสำหรับสร้างชื่อไฟล์ zip
def generate_zip_file_name(base_name, round_no, sequence_no, total_files, date):
    return f"{base_name}_{date}{round_no:03}_{sequence_no:03}of{total_files:03}.zip"

# ฟังก์ชันสำหรับสร้างชื่อไฟล์ PDF
def generate_pdf_file_name(base_name, thai_id, date):
    hash_id = hashlib.sha256(thai_id.encode()).hexdigest()
    return f"{base_name}_{hash_id}_{date}.pdf"

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
def create_header(date, branch_code="051000", system_code="TACN", round_no=1, file_code="EVDTFEML"):
    return f"H|{date}|{branch_code}|{system_code}|{round_no:03}|{file_code}"

# สร้างข้อมูล detail
def create_detail_record(data, date, round_no=1, sequence_no=1, total_files=1):
    # แปลง date จาก YYYYMMDD เป็น YYYY-MM-DD
    original_date = date
    date_obj = datetime.strptime(original_date, "%Y%m%d")
    formatted_date = date_obj.strftime("%Y-%m-%d")  # เปลี่ยนเป็นฟอร์แมตที่ต้องการ

    thai_id = data["cid"]
    app_id = data["partner_customer_id"]
    acc_no = data["partner_account_no"]
    transfer_date = data["transfer_date"]
    email = fake.email()
    datetime_sending = f"{formatted_date}T09:29:45.123+0700"  # ใช้ formatted_date แทน date ที่ไม่ได้ปรับ
    zip_file_name = generate_zip_file_name("EVDTFInstallmentTable", round_no, sequence_no, total_files, original_date)
    pdf_file_name = generate_pdf_file_name("EVDTFInstallmentTable", thai_id, original_date)
    email_body_zip = generate_zip_file_name("EVD_TF_Email_body", round_no, sequence_no, total_files, original_date)
    email_body_pdf = generate_pdf_file_name("EVD_TF_Email_body", thai_id, original_date)
    
    return f"D|{thai_id}|{app_id}|{acc_no}|02|{email}|{datetime_sending}|{zip_file_name}.enc|{pdf_file_name}|{email_body_zip}.enc|{email_body_pdf}|||{transfer_date}|||"

# สร้างข้อมูล trailer
def create_trailer(date, branch_code="051000", system_code="TACN", round_no=1, total_records=1):
    return f"T|{date}|{branch_code}|{system_code}|{round_no:03}|{total_records}"

# สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ
def generate_file_name(date, round_no=1, sequence_no=1, total_files=1):
    return f"TCRB_EVDTFEmail_{date}{round_no:03}_{sequence_no:03}of{total_files:03}.txt"

# ฟังก์ชันสำหรับลบไฟล์
def cleanup_files(files):
    for file in files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

# ปรับปรุงฟังก์ชัน generate_evdd_file เพื่อรวมการสร้าง ZIP
def generate_evdd_file(json_file_path, pdf_email_body_template, bucket_name, round_no=1, sequence_no=1, total_files=1, max_records=None):
    # อ่านข้อมูล JSON จากไฟล์
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    # หากกำหนด max_records ให้เลือกจำนวนระเบียน
    if max_records:
        json_data = json_data[:max_records]
    
    date = datetime.now().strftime("%Y%m%d")  # ใช้วันที่ปัจจุบัน
    filename = f"TCRB_EVD1stDDEmail_{date}{round_no:03}_{sequence_no:03}of{total_files:03}.txt"
    zip_file_name = f"{filename}.zip"  # ชื่อไฟล์ ZIP
    email_body_pdf = f"EVD_1stDD_Email_body_{date}.pdf"  # PDF Template
    email_body_zip = f"EVD_1stDD_Email_body_{date}.zip.enc"  # ZIP Enc

    # คัดลอก PDF Template ไปยังชื่อไฟล์ที่ต้องการ
    copy_pdf(pdf_email_body_template, email_body_pdf)

    # สร้าง Header
    header = f"H|{date}|051000|TACN|{round_no:03}|EVD1stDD"

    # สร้างรายละเอียด (Detail)
    details = []
    record_count = 0  # ตัวนับ record
    
    for data in json_data:
        record_count += 1
        thai_id = data["cid"]
        loan_account_no = data["partner_account_no"]
        term_loan_account_no = data.get("term_loan_account_no", "")
        product_name = "02"
        email = fake.email()
        datetime_sending = f"{date}T09:29:45.123+0700"
        result = "000"  # สมมุติว่าผ่าน
        reject_reason = ""
        transfer_date = data["transfer_date"]
        
        # บันทึกข้อมูลในรูปแบบที่กำหนด
        detail = f"D|{thai_id}|{loan_account_no}|{term_loan_account_no}|{product_name}|{email}|{datetime_sending}|{email_body_pdf}|{email_body_zip}|{result}|{reject_reason}|{transfer_date}|||||"
        details.append(detail)
        
        # Log สถานะทุก 50 records
        if record_count % 50 == 0:
            print(f"Processed {record_count} records.")
    
    # สร้าง Trailer
    trailer = f"T|{date}|051000|TACN|{round_no:03}|{record_count}"

    # รวมข้อมูลทั้งหมดลงในไฟล์ TXT
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.writelines("\n".join(details) + "\n")
        f.write(trailer + "\n")
    
    print(f"File '{filename}' generated successfully!")

    # สร้างไฟล์ ZIP
    files_to_include = [filename, email_body_pdf]
    create_zip_file(zip_file_name, files_to_include)
    print(f"ZIP file '{zip_file_name}' created successfully!")

    # สร้าง ZIP Enc (จำลองโดยการเปลี่ยนชื่อไฟล์)
    zip_enc_name = email_body_zip
    os.rename(zip_file_name, zip_enc_name)
    print(f"Encrypted ZIP file '{zip_enc_name}' created successfully!")

    # อัปโหลด ZIP Enc ไปยัง S3
    # s3_key = f"generated_files/{zip_enc_name}"  # path ใน S3
    # upload_to_s3(zip_enc_name, bucket_name, s3_key)
    # print(f"Encrypted ZIP file '{zip_enc_name}' uploaded to S3 bucket '{bucket_name}' successfully!")

    # ทำความสะอาดไฟล์ชั่วคราว
    # cleanup_files([filename, email_body_pdf, zip_enc_name])
    
    return zip_enc_name



# ตัวอย่างการเรียกใช้งาน
json_file_path = "customer_account_202412031404.json"  # กำหนด path ของไฟล์ JSON
pdf_email_body = "pdf_email_body.pdf"
bucket_name = "tcrb-debtacq-temp-pvt-nonprod"  # กำหนดชื่อ bucket
max_records = 5000
round_no = 1

generate_evdd_file(json_file_path, pdf_email_body, bucket_name, round_no=round_no, sequence_no=1, total_files=1, max_records=max_records)