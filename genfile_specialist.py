import pandas as pd
import random
from faker import Faker
import time
from datetime import datetime

start_time = time.time()
fake_th = Faker('th_TH')
fake_en = Faker('en_US')
print('######## START ########')

def format_large_number(n):
    if n >= 1_000_000:
        return f"{n // 1_000_000}M"
    elif n >= 1_000:
        return f"{n // 1_000}K"
    else:
        return str(n)

def generate_national_id(country_code):
    if random.random() < 0.3:
        return None
    if country_code == 'TH':
        return f"{random.randint(1, 9)}{random.randint(1000000000, 9999999999)}"
    elif country_code == 'US':
        return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    elif country_code == 'GB':
        return f"{fake_en.random_uppercase_letter()}{fake_en.random_uppercase_letter()}{random.randint(100000, 999999)}{fake_en.random_uppercase_letter()}"
    elif country_code == 'FR':
        return f"{random.randint(1, 2)}{random.randint(10, 99)}{random.randint(1, 12)}{random.randint(0, 999)}{random.randint(0, 999)}{random.randint(0, 99)}"
    elif country_code == 'DE':
        return f"{random.randint(10, 99)}{random.randint(100000000, 999999999)}"
    else:
        return f"{random.randint(100000, 999999)}"

def generate_zipcode():
    return f"{random.randint(10000, 99999)}"

def create_random_record():
    country_code = random.choice(['TH', 'US', 'GB', 'FR', 'DE'])
    customer_name_th = fake_th.name() if random.random() > 0.3 else None
    customer_name_en = fake_en.name() if random.random() > 0.3 else None

    return {
        "row_no": None,
        "CustomerNo": generate_national_id(country_code),
        "Customer_Name_Th": customer_name_th,
        "ChkThaiName": customer_name_th,
        "ChkEngName": customer_name_en,
        "Customer_Name_En": customer_name_en,
        "DOB": fake_th.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
        "CountryCode": country_code,
        "CustomerType": random.choice(['W', 'N']),
        "Zipcode": generate_zipcode(),
        "ACTION": random.choice(['A', 'B']),
        "Old_Act": None,
        "OVRACT": None,
        "POB": fake_th.city(),
        "ReasonCode": None,
        "RTN_Customer": None,
        "SrcSEQ": "(1)(2)(3)"
    }

num_records = 10  # จำนวนเรคคอร์ดตัวอย่าง
records = [create_random_record() for _ in range(num_records)]
df = pd.DataFrame(records)

df['row_no'] = df.index + 1

# สร้างชื่อไฟล์ตามวันที่และเวลาปัจจุบัน
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'EIM_EDGE_BLACKLIST_{timestamp}.txt'
df.to_csv(filename, index=False, sep='|', encoding='utf-8-sig')

# ใช้ฟังก์ชัน format_large_number เพื่อแสดงจำนวนเรคคอร์ดในรูปแบบย่อ
record_count_text = format_large_number(num_records)

print(f"File generated successfully with {record_count_text} records.")
print(f"gen file {filename} ใช้เวลา: {time.time() - start_time:.2f} วินาที")
