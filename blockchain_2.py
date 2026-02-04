import cv2
from pyzbar.pyzbar import decode
import hashlib
import json
from datetime import datetime
from cryptography.fernet import Fernet


# ===================== DEVICE AUTHORIZATION =====================

# Load booth-specific secret key (device identity)
with open("booth_secret.key", "rb") as key_file:
    DEVICE_SECRET_KEY = key_file.read()

cipher = Fernet(DEVICE_SECRET_KEY)


# ===================== BLOCK & BLOCKCHAIN =====================

class Block:
    def __init__(self, index, timestamp, voter_hash, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.voter_hash = voter_hash
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.voter_hash}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "voter_hash": self.voter_hash,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            voter_hash="GENESIS",
            previous_hash="0"
        )
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    # 🔴 CHANGED: timestamp is now passed explicitly
    def add_block(self, voter_hash, timestamp):
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=timestamp,
            voter_hash=voter_hash,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True

    def save_to_file(self, filename):
        with open(filename, "w") as file:
            json.dump([block.to_dict() for block in self.chain], file, indent=4)


# ===================== HELPER FUNCTIONS =====================

def hash_voter_id(voter_id):
    salt = "OBVV_SECURE_SALT"
    return hashlib.sha256((voter_id + salt).encode()).hexdigest()


def scan_qr_code():
    cap = cv2.VideoCapture(0)
    print("QR Scanner started. Show QR to camera (press 'q' to cancel).")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        decoded_objects = decode(frame)

        for obj in decoded_objects:
            try:
                encrypted_data = obj.data
                decrypted = cipher.decrypt(encrypted_data)
                voter_data = json.loads(decrypted.decode())

                cap.release()
                cv2.destroyAllWindows()
                return voter_data

            except Exception:
                print("🚨 Unauthorized or invalid QR")

        cv2.imshow("Scan Voter QR Code", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


# ===================== MAIN =====================

if __name__ == "__main__":
    booth_blockchain = Blockchain()
    print("OBVV Polling Booth Started (Offline)")

    while True:
        print("\nPress ENTER to scan QR or type 'exit' to stop:")
        cmd = input()

        if cmd.lower() == "exit":
            break

        voter = scan_qr_code()

        if voter is None:
            print("QR scan cancelled or failed.")
            continue

        # ✅ Timestamp captured AT SCAN TIME
        scan_timestamp = datetime.now().isoformat()

        voter_hash = hash_voter_id(voter["voter_id"])
        booth_blockchain.add_block(voter_hash, scan_timestamp)

        print("Vote validated and recorded")
        print("Timestamp:", scan_timestamp)

    print("\nBlockchain valid:", booth_blockchain.is_chain_valid())
    booth_blockchain.save_to_file("booth_ledger_2.json")
    print("Ledger saved as booth_ledger_2.json")
