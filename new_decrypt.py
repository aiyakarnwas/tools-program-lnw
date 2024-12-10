import gnupg

# สร้าง instance ของ GPG
gpg = gnupg.GPG()

# ระบุ passphrase สำหรับ key
passphrase = 'passphrase'

# สร้าง key pair หากยังไม่มี (ควรทำเพียงครั้งแรก)
input_data = gpg.gen_key_input(name_email='your_email@example.com', passphrase=passphrase)
key = gpg.gen_key(input_data)

# ตรวจสอบ Key ID ที่มีอยู่
keys = gpg.list_keys()
if keys:
    key_id = keys[0]['keyid']  # ใช้ Key ID ของ key แรกในรายการ
    print(f'Key ID: {key_id}')
else:
    print("No keys found.")
    exit()

# ข้อความที่จะเข้ารหัส
plaintext_message = "Hello, this is a test message!"
plaintext_file = 'example.txt'  # ไฟล์ที่ต้องการเข้ารหัส

# เข้ารหัสแบบ PGP Block Message โดยใช้ Key ID
encrypted_block = gpg.encrypt(plaintext_message, recipients=key_id, passphrase=passphrase)
if encrypted_block.ok:
    print("PGP Block Message:\n", str(encrypted_block))
else:
    print("Error encrypting block message:", encrypted_block.stderr)

# เข้ารหัสแบบ Binary
# สร้างไฟล์ข้อความเพื่อเข้ารหัส
with open(plaintext_file, 'w') as f:
    f.write(plaintext_message)

# เข้ารหัสไฟล์แบบ Binary โดยใช้ Key ID
with open(plaintext_file, 'rb') as f:
    encrypted_binary = gpg.encrypt_file(f, recipients=key_id, passphrase=passphrase)

# แสดงผลลัพธ์การเข้ารหัสไฟล์แบบ Binary
if encrypted_binary.ok:
    with open('encrypted_file.gpg', 'wb') as ef:
        ef.write(encrypted_binary.data)
    print("Binary file encrypted and saved as 'encrypted_file.gpg'")
else:
    print("Error encrypting binary file:", encrypted_binary.stderr)
