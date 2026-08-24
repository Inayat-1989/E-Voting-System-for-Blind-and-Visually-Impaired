import csv
import random

# Mapping configuration based on polling station rules
regions = [
    {
        "province": "Balochistan",
        "city": "Quetta",
        "blocks": [
            (1, 1, 100),
            (2, 101, 200),
            (3, 201, 300),
            (4, 301, 400),
            (5, 401, 500),
        ],
    },
    {
        "province": "Punjab",
        "city": "Lahore",
        "blocks": [
            (6, 1, 100),
            (7, 101, 200),
            (8, 201, 300),
            (9, 301, 400),
            (10, 401, 500),
        ],
    },
    {
        "province": "Sindh",
        "city": "Karachi",
        "blocks": [
            (11, 1, 100),
            (12, 101, 200),
            (13, 201, 300),
            (14, 301, 400),
            (15, 401, 500),
        ],
    },
    {
        "province": "Khyber Pakhtunkhwa",
        "city": "Peshawar",
        "blocks": [
            (16, 1, 100),
            (17, 101, 200),
            (18, 201, 300),
            (19, 301, 400),
            (20, 401, 500),
        ],
    },
    {
        "province": "Islamabad Capital Territory",
        "city": "Islamabad",
        "blocks": [
            (21, 1, 100),
            (22, 101, 200),
            (23, 201, 300),
            (24, 301, 400),
            (25, 401, 500),
        ],
    },
]

first_names = [
    "Muhammad",
    "Ahmed",
    "Ali",
    "Usman",
    "Hamza",
    "Bilal",
    "Zubair",
    "Tariq",
    "Imran",
    "Kamran",
    "Farhan",
    "Saad",
    "Adnan",
    "Faisal",
    "Shahid",
    "Waqas",
    "Asim",
    "Naveed",
    "Kashif",
    "Babar",
    "Rashid",
    "Yasir",
    "Arsalan",
    "Zeeshan",
    "Junaid",
    "Ayesha",
    "Fatima",
    "Zainab",
    "Maryam",
    "Sana",
    "Hira",
    "Sidra",
    "Iqra",
    "Rabia",
    "Samina",
]

last_names = [
    "Khan",
    "Ahmed",
    "Malik",
    "Chaudhry",
    "Bhatti",
    "Butt",
    "Raza",
    "Shah",
    "Siddiqui",
    "Qureshi",
    "Memon",
    "Abbasi",
    "Ansari",
    "Mirza",
    "Baig",
    "Sheikh",
    "Gul",
    "Khattak",
    "Tareen",
    "Mengal",
    "Rind",
    "Bugti",
    "Jan",
    "Laghari",
    "Mahar",
]

records = []

for region in regions:
    prov = region["province"]
    city = region["city"]
    for block_code, start_sno, end_sno in region["blocks"]:
        for sno in range(start_sno, end_sno + 1):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            records.append(
                {
                    "Cnic": "",  # Placeholder for your CNIC generator
                    "Full Name": name,
                    "Status": "Active",
                    "Disabled": "Yes",
                    "Province": prov,
                    "City": city,
                    "Block Code": block_code,
                    "Serial Number": sno,
                }
            )

# Export to CSV
output_filename = "voters_file.csv"
fieldnames = [
    "Cnic",
    "Full Name",
    "Status",
    "Disabled",
    "Province",
    "City",
    "Block Code",
    "Serial Number",
]

with open(output_filename, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)

print(f"Successfully generated {len(records)} rows in {output_filename}.")