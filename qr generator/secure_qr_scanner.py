import cv2
from pyzbar.pyzbar import decode
from cryptography.fernet import Fernet
import json

# Load booth secret key
with open("booth_secret.key", "rb") as key_file:
    BOOTH_SECRET_KEY = key_file.read()

cipher = Fernet(BOOTH_SECRET_KEY)

def scan_and_decrypt_qr():
    cap = cv2.VideoCapture(0)
    print("Authorized Booth Scanner Active (Press Q to exit)")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        decoded_objects = decode(frame)

        for obj in decoded_objects:
            encrypted_data = obj.data

            try:
                decrypted = cipher.decrypt(encrypted_data)
                voter_data = json.loads(decrypted.decode())

                cap.release()
                cv2.destroyAllWindows()

                print("✅ VALID QR SCANNED")
                print("Voter ID:", voter_data["voter_id"])
                print("Name:", voter_data["name"])
                return voter_data

            except Exception:
                print("🚨 Unauthorized or invalid QR code")

        cv2.imshow("Secure QR Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


if __name__ == "__main__":
    scan_and_decrypt_qr()
