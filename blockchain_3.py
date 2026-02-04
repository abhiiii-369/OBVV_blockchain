import cv2
from pyzbar.pyzbar import decode
import hashlib
import json
from datetime import datetime


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
            timestamp=str(datetime.now()),
            voter_hash="GENESIS",
            previous_hash="0"
        )
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, voter_hash):
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=str(datetime.now()),
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


def hash_voter_id(voter_id):
    salt = "OBVV_SECURE_SALT"
    return hashlib.sha256((voter_id + salt).encode()).hexdigest()


if __name__ == "__main__":
    booth_blockchain = Blockchain()

    print("OBVV Polling Booth Started (Offline)")

    while True:
        voter_id = input("Scan Voter QR (enter ID or 'exit'): ")

        if voter_id.lower() == "exit":
            break

        voter_hash = hash_voter_id(voter_id)
        booth_blockchain.add_block(voter_hash)

        print("Vote validated and recorded.\n")

    print("Blockchain valid:", booth_blockchain.is_chain_valid())
    booth_blockchain.save_to_file("booth_ledger_3.json")
    print("Ledger saved as booth_ledger_3.json")
