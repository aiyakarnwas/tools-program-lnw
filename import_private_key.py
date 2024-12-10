import gnupg

# สร้างออบเจกต์ GPG
gpg = gnupg.GPG()

def import_private_key(private_key_str):
    # นำเข้าคีย์จากสตริง
    import_result = gpg.import_keys(private_key_str)
    
    # แสดงผลการนำเข้า
    print(f"Import counts: {import_result.counts}")
    print(f"Fingerprints: {import_result.fingerprints}")
    # print(f"Messages: {import_result.messages}")

    # ตรวจสอบว่าการนำเข้าสำเร็จหรือไม่
    if import_result.counts['imported'] == 0:
        print("Import private key failed")
        return None
    else:
        print(f"Imported key fingerprints: {import_result.fingerprints}")

    return import_result

# คีย์ส่วนตัวในรูปแบบสตริง
private_key = """
-----BEGIN PGP PRIVATE KEY BLOCK-----

lQPGBGKyhZQBCADOc+1SMdlSKqXJrjSFLkIUjwNq01H9cXd6F6iUfu7XpZtyCdB0
zzBXMtRWo8Lg2zuXD56zlvIzdiJvsL2/CdOe9Kf7Mu6tHeskIMTOdUiGNKtLdOtR
pjIOkFXFHknDPy+aX1rA+9vIbfEv7HVg7Qgx4Bo8Z5hrS/XtSgGPTytzBBT+BGxO
yEu/5UJx3rBQpFATKZZh/CEm1+GAPk7JTM2rVLvOH7Ccfpw8K2jRhnpOPhtuD/QK
JQGlpU0/9tJxOqKXIMi5JrUixqvd7JjLl5t6CjrwGhw9nOI0Ucasm18Sju5bpaLC
ttenZZWn/cZjwIz4Neic1sf8ECsV7ER/lDsdABEBAAH+BwMCoGnFhemptgL17Sav
33sGmNciE82RV0pzJYoQCUz5K2q21YVpMiEeSaXL8h+Sd73yNCNDnolsmob3qV76
Yy3LPCiQP/GOU6dIjB3AhForZKtAKQF5MriCxP0Fexh2U+bzUe4zuFa7gZ6gFvpv
LixnkOkJg7iR2lw5z7kWy5R7mwuWqt3lSyoufUfz5vm/gCC7YQ6TVIVObw+KWS5G
La/ggg2yF67KAZnpivjc7E4YVCAQy2UjCchwDq2GFH+rPBgTA9R9j3w9dHTNbYgF
fCGlnw60rsmLek67cFt4b+xyo8muQop4Vu/R5QIekYkrJAMMhGj149wpYif26slm
/0nk2n1gxf8R0ELR9mrLRdjjU39My5DafwU/dhNKsumiX2vW69dF202BMTma/XlW
1+WcjLjnvF1bX2qGI8DSrno6BWhLykUltdmZh94rXMn61tX4M8eQ80mK6Zujfonv
cdM+uTyDspOJh2MoQ7UIDnnoUoNDaNNHiEZINj32xvKhVb/mfAxxGKHUhm1a4bK0
g1hjBQL4k6ZEIEyZ/G2Tk/J0CHjMZwCDv7n4i49RWQGAgai6AtcNM3cbKNBSCDvR
QGym7ElVzzk9zXKfxGFe3SNMLI6EYsQTNZNkYe2x8QkU5PBH7fsjkdLYE+h25PSm
nNbWRk2XUlvqEv4rxCWf+m0gI7G1Tc+YGX/veI0rT8fb81pdFX1VmVnpiCxKxJRm
Bk7HkL1JSIBNlzXoGTw2j+WBXnlu6mbQfUWPQCXhShxuGEickoMi/eymRMH+vZB5
tZIhmmUnSYrWCgMKKZ6JjGjGSZXRRTiKwX7TEcmtxiG67KC+0auTfgdUtTTipsoH
9GMcxi+942j8cfVxFSPjrAILc8XVHLKyffhkki8eXkZwOllQCkjXE/AyBRlRdOwY
tQxIbqj8WW6stDFlZGdlX2RlYnRfbm9ucHJvZCA8ZWRnZV9kZWJ0X25vbnByb2RA
dGNyYmFuay5jb20+iQFSBBMBCAA8FiEEIJouGcrgIg+KLOhmWd5wciJV/94FAmKy
hZQCGw0FCwkIBwIDIgIBBhUKCQgLAgQWAgMBAh4HAheAAAoJEFnecHIiVf/e6hAH
/192DSzWKBnbXo/69wrZjcqUgq+h07O2yk5udW1nnfh5aDEi0TByXrhqMe3NgB7e
vB4bNTRuTIgexToyOagKZWc0C+K19z0m90+iC3lg77WENQtYlkH7zPrijBaF0z9F
dxxBEjqY9HUCLRolLQET5GQQVyX7zLp7us9BYRGi9m2EFsaqTQJL6eYw4S+aF/Dy
pUtn+JyPlJrAwCW0Hsd1jnKdAn3ZYuHTw7BL0B4hf4H7zBSIWGQjxJkJE6bK29BK
Y6NS51XltTLVQufMR7cTyDTVu46CMLPojRhCyBu+kSLLcp8NDmLk8ZMRysVKC9rY
yypcBOd3vxVf6HTDsGmtipg=
=CjhA
-----END PGP PRIVATE KEY BLOCK-----
"""

if __name__ == "__main__":
    # นำเข้าคีย์
    import_private_key(private_key)
