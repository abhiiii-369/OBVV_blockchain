import json
from datetime import datetime
from collections import defaultdict


def load_ledger(filename):
    with open(filename, "r") as file:
        return json.load(file)


def parse_timestamp(ts):
    return datetime.fromisoformat(ts)


def detect_duplicates(ledger_files):
    vote_map = defaultdict(list)

    # Step 1: Collect all votes from all booths
    for booth_file in ledger_files:
        ledger = load_ledger(booth_file)

        for block in ledger:
            if block["index"] == 0:
                continue  # skip genesis block

            vote_map[block["voter_hash"]].append({
                "timestamp": parse_timestamp(block["timestamp"]),
                "booth": booth_file
            })

    valid_votes = []
    duplicate_votes = []

    # Step 2: Detect duplicates
    for voter_hash, entries in vote_map.items():
        entries.sort(key=lambda x: x["timestamp"])

        valid_votes.append({
            "voter_hash": voter_hash,
            "timestamp": entries[0]["timestamp"],
            "booth": entries[0]["booth"]
        })

        for dup in entries[1:]:
            duplicate_votes.append({
                "voter_hash": voter_hash,
                "timestamp": dup["timestamp"],
                "booth": dup["booth"]
            })

    return valid_votes, duplicate_votes


if __name__ == "__main__":
    booth_ledgers = [
        "booth_ledger_1.json",
        "booth_ledger_2.json",
        "booth_ledger_3.json"
    ]

    valid, duplicates = detect_duplicates(booth_ledgers)

    print("\n✅ VALID VOTES")
    for v in valid:
        print(v)

    print("\n🚨 DUPLICATE / FRAUD VOTES")
    for d in duplicates:
        print(d)

    # Save reports
    with open("valid_votes.json", "w") as f:
        json.dump(valid, f, default=str, indent=4)

    with open("duplicate_votes.json", "w") as f:
        json.dump(duplicates, f, default=str, indent=4)

    print("\nReports generated successfully.")
