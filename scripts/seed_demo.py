"""
Seed realistic demo data for SWA ERP demos.

USAGE:
    APP_ENV=dev python3 scripts/seed_demo.py

Creates realistic clients, contacts, and projects for SWA Consultancy
(insulation engineering, Ahmedabad-based).
"""
import sys
import os
import uuid
import random
from datetime import datetime, timedelta, date
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    env = os.environ.get("APP_ENV", "dev")
    if env not in ("dev", "test"):
        print(f"REFUSING to seed in {env} environment.")
        sys.exit(1)

    db_url = os.environ.get("DATABASE_URL", "postgresql://swa:swa@localhost:5432/swa_erp")
    print(f"Seeding demo data into: {db_url}")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.backend.core.security import hash_password
    from src.backend.models.user import User
    from src.backend.models.client import Client
    from src.backend.models.contact import Contact
    from src.backend.models.project import Project

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    # ------------------------------------------------------------------
    # 1. USERS (if not exists)
    # ------------------------------------------------------------------
    user_seeds = [
        {"email": "admin@swa.co.in", "name": "Srujan Patel", "password": "admin123!", "role": "admin"},
        {"email": "pm@swa.co.in", "name": "Priya Mehta", "password": "pm123!", "role": "pm"},
        {"email": "designer@swa.co.in", "name": "Rahul Sharma", "password": "designer123!", "role": "designer"},
        {"email": "auditor@swa.co.in", "name": "Ankit Desai", "password": "auditor123!", "role": "auditor"},
        {"email": "viewer@swa.co.in", "name": "Neha Gupta", "password": "viewer123!", "role": "viewer"},
    ]

    users_by_role = {}
    for s in user_seeds:
        u = db.query(User).filter_by(email=s["email"]).first()
        if not u:
            u = User(
                id=uuid.uuid4(),
                email=s["email"],
                name=s["name"],
                password_hash=hash_password(s["password"]),
                role=s["role"],
                is_active=True,
            )
            db.add(u)
            db.flush()
            print(f"  + User: {s['name']} ({s['role']})")
        else:
            print(f"  ✓ User exists: {s['name']}")
        users_by_role[s["role"]] = u

    # ------------------------------------------------------------------
    # 2. CLIENTS
    # ------------------------------------------------------------------
    client_data = [
        {
            "name": "Tata Chemicals Ltd",
            "code": "TCL-001",
            "city": "Mithapur",
            "state": "Gujarat",
            "gst": "24AAACT1234A1Z5",
            "email": "procurement@tatachemicals.com",
            "phone": "+91 22 6665 8282",
        },
        {
            "name": "Adani Power Mundra",
            "code": "APM-002",
            "city": "Mundra",
            "state": "Gujarat",
            "gst": "24AABCA1234B1Z6",
            "email": "projects@adani.com",
            "phone": "+91 79 2656 5555",
        },
        {
            "name": "Reliance Industries Ltd",
            "code": "RIL-003",
            "city": "Jamnagar",
            "state": "Gujarat",
            "gst": "27AAACR1234C1Z7",
            "email": "engineering@ril.com",
            "phone": "+91 22 2278 5000",
        },
        {
            "name": "Gujarat State Fertilizers",
            "code": "GSF-004",
            "city": "Vadodara",
            "state": "Gujarat",
            "gst": "24AABCG1234D1Z8",
            "email": "maintenance@gsfc.in",
            "phone": "+91 265 242 2700",
        },
        {
            "name": "Ambuja Cements Ltd",
            "code": "ACL-005",
            "city": "Ambuja Nagar",
            "state": "Gujarat",
            "gst": "24AAACA1234E1Z9",
            "email": "technical@ambujacement.com",
            "phone": "+91 79 2646 2400",
        },
        {
            "name": "Suzlon Energy Ltd",
            "code": "SEL-006",
            "city": "Pune",
            "state": "Maharashtra",
            "gst": "27AABCS1234F1Z0",
            "email": "ops@suzlon.com",
            "phone": "+91 20 4012 2000",
        },
        {
            "name": "Torrent Power Ltd",
            "code": "TPL-007",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "gst": "24AABCT1234G1Z1",
            "email": "civil@torrentpower.com",
            "phone": "+91 79 2687 2100",
        },
        {
            "name": "Deepak Nitrite Ltd",
            "code": "DNL-008",
            "city": "Nandesari",
            "state": "Gujarat",
            "gst": "24AAACD1234H1Z2",
            "email": "projects@deepaknitrite.com",
            "phone": "+91 265 398 0100",
        },
        {
            "name": "Larsen & Toubro Ltd",
            "code": "LNT-009",
            "city": "Surat",
            "state": "Gujarat",
            "gst": "24AAACL1234I1Z3",
            "email": "insulation@ltconstruction.com",
            "phone": "+91 22 6752 5656",
        },
        {
            "name": "Welspun India Ltd",
            "code": "WIL-010",
            "city": "Anjar",
            "state": "Gujarat",
            "gst": "24AAACW1234J1Z4",
            "email": "facilities@welspun.com",
            "phone": "+91 2836 270 001",
        },
    ]

    clients = []
    for c in client_data:
        existing = db.query(Client).filter_by(code=c["code"]).first()
        if existing:
            clients.append(existing)
            print(f"  ✓ Client exists: {c['name']}")
            continue
        client = Client(
            id=uuid.uuid4(),
            name=c["name"],
            code=c["code"],
            address=f"Industrial Estate, {c['city']}",
            city=c["city"],
            state=c["state"],
            pincode=str(random.randint(360001, 395999)),
            country="India",
            gst_number=c["gst"],
            primary_email=c["email"],
            primary_phone=c["phone"],
            notes="",
            is_active=True,
        )
        db.add(client)
        db.flush()
        clients.append(client)
        print(f"  + Client: {c['name']}")

    # ------------------------------------------------------------------
    # 3. CONTACTS per client
    # ------------------------------------------------------------------
    designations = ["Project Manager", "Plant Engineer", "Maintenance Head", "Procurement Officer", "HOD - Technical"]
    contact_names = [
        "Amit Kumar", "Suresh Patel", "Vikram Singh", "Pooja Shah", "Manish Joshi",
        "Kiran Rao", "Divya Iyer", "Sanjay Bhatt", "Meera Jain", "Arjun Nair",
        "Bhavesh Modi", "Hetal Desai", "Jayesh Thakkar", "Kamal Trivedi", "Leela Menon",
    ]

    contact_idx = 0
    for client in clients:
        for _ in range(random.randint(2, 3)):
            contact = Contact(
                id=uuid.uuid4(),
                client_id=client.id,
                name=contact_names[contact_idx % len(contact_names)],
                email=f"{contact_names[contact_idx % len(contact_names)].lower().replace(' ', '.')}@{client.name.lower().replace(' ', '').replace('.','')[:10]}.com",
                phone=f"+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}",
                designation=random.choice(designations),
                is_primary=(contact_idx == 0),
            )
            db.add(contact)
            contact_idx += 1
    db.flush()
    print(f"  + {contact_idx} contacts created")

    # ------------------------------------------------------------------
    # 4. PROJECTS
    # ------------------------------------------------------------------
    project_names = [
        ("Boiler Insulation Retrofit", "Lead"), ("STG Unit 3 Cold Insulation", "Quote"),
        ("Furnace Wall Lining Replacement", "Awarded"), ("HRSG Duct Insulation", "Design"),
        ("Chilled Water Pipe Insulation", "Vendor"), ("Storage Tank Thermal Insulation", "Execution"),
        ("Turbine Exhaust Duct Lining", "Validation"), ("Ductwork Acoustic Treatment", "Closed"),
        ("Reformer Unit Hot Insulation", "Lead"), ("Flare Stack Refractory Repair", "Quote"),
        ("Cooling Tower Basin Lining", "Awarded"), ("Process Vessel Insulation", "Design"),
        ("Steam Distribution Line Insulation", "Vendor"), ("Reactor Head Insulation", "Execution"),
        ("Preheat Train Cold Insulation", "Validation"), ("Stack Emission Duct Lining", "Closed"),
        ("Condensate Line Insulation", "Lead"), ("Feedwater Heater Insulation", "Quote"),
        ("Rotary Kiln Refractory Lining", "Awarded"), ("ESP Hopper Insulation", "Design"),
    ]

    locations = [
        "Mithapur, Gujarat", "Mundra, Gujarat", "Jamnagar, Gujarat", "Vadodara, Gujarat",
        "Ambuja Nagar, Gujarat", "Pune, Maharashtra", "Ahmedabad, Gujarat", "Nandesari, Gujarat",
        "Surat, Gujarat", "Anjar, Gujarat",
    ]

    statuses = ["Lead", "Quote", "Awarded", "Design", "Vendor", "Execution", "Validation", "Closed"]

    for i, (name, status) in enumerate(project_names):
        code = f"SWA-2025-{i+1:03d}"
        existing = db.query(Project).filter_by(code=code).first()
        if existing:
            print(f"  ✓ Project exists: {code}")
            continue

        client = clients[i % len(clients)]
        status_idx = statuses.index(status)
        pm = users_by_role.get("pm")
        designer = users_by_role.get("designer")
        auditor = users_by_role.get("auditor")

        est_value = Decimal(str(random.randint(5, 150))) * Decimal("100000")
        start_offset = -status_idx * 15 if status_idx > 0 else 0
        start_date = date.today() + timedelta(days=start_offset) if status_idx > 0 else None
        target_end = start_date + timedelta(days=random.randint(60, 180)) if start_date else None
        actual_end = target_end + timedelta(days=random.randint(-10, 30)) if status == "Closed" and target_end else None
        actual_value = est_value * Decimal(str(random.uniform(0.9, 1.15))) if status == "Closed" else None

        project = Project(
            id=uuid.uuid4(),
            client_id=client.id,
            name=name,
            code=code,
            description=f"{name} for {client.name}. Includes material supply, installation, and QA compliance as per IS/ASTM standards.",
            status=status,
            pm_id=pm.id if pm and status_idx >= 2 else None,
            designer_id=designer.id if designer and status_idx >= 3 else None,
            auditor_id=auditor.id if auditor and status_idx >= 6 else None,
            location=locations[i % len(locations)],
            estimated_value=est_value,
            actual_value=actual_value.quantize(Decimal("0.01")) if actual_value else None,
            start_date=start_date,
            target_end_date=target_end,
            actual_end_date=actual_end,
            is_active=True,
        )
        db.add(project)
        print(f"  + Project: {code} ({status}) — ₹{est_value/Decimal('100000'):.0f}L")

    db.commit()
    db.close()

    print("\n✅ Demo data seeded successfully!")
    print(f"   {len(user_seeds)} users | {len(client_data)} clients | {contact_idx} contacts | {len(project_names)} projects")
    print("\nDemo credentials:")
    for s in user_seeds:
        print(f"   {s['email']} / {s['password']}  ({s['role']})")
    print()


if __name__ == "__main__":
    main()
