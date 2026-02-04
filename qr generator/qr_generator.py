import qrcode
import json
from cryptography.fernet import Fernet

# Booth-specific secret key (shared ONLY with that booth device)
# Generate once and store securely
BOOTH_SECRET_KEY = Fernet.generate_key()
cipher = Fernet(BOOTH_SECRET_KEY)

# Save key securely (only booth device should have this)
with open("booth_secret.key", "wb") as key_file:
    key_file.write(BOOTH_SECRET_KEY)

def generate_qr(voter_id, voter_name, qr_filename):
    voter_data = {
        "voter_id": voter_id,
        "name": voter_name
    }

    json_data = json.dumps(voter_data)
    encrypted_data = cipher.encrypt(json_data.encode())

    qr = qrcode.make(encrypted_data.decode())
    qr.save(qr_filename)

    print(f"QR generated for {voter_name} → {qr_filename}")


# Example usage
if __name__ == "__main__":
    generate_qr("VOTER12345", "Rahul Kumar", "voter_qr_1.png")
    generate_qr("VOTER67890", "Anjali Devi", "voter_qr_2.png")
