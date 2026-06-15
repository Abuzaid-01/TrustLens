"""
Seed data — Realistic demo data that works like real production data.
5 businesses + 10 orders (2 per business) with real-looking data.
"""

import json
from app.database.db import get_db


def seed_database():
    """Populate the database with realistic demo data."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if already seeded
    count = cursor.execute("SELECT COUNT(*) FROM businesses").fetchone()[0]
    if count > 0:
        print("📦 Database already seeded, skipping.")
        conn.close()
        return

    # ── 5 Businesses ──
    businesses = [
        ("starbucks_downtown_01", "Starbucks Downtown", "cafe", "123 Main Street, Downtown, NY 10001"),
        ("pizzahut_central_02", "Pizza Hut Central", "restaurant", "456 Central Ave, Midtown, NY 10018"),
        ("samsung_store_03", "Samsung Experience Store", "electronics", "789 Tech Blvd, Silicon District, CA 94105"),
        ("hilton_garden_04", "Hilton Garden Inn", "hotel", "321 Hospitality Lane, Business Park, TX 75001"),
        ("uber_rides_05", "Uber Rides", "transportation", "Online Service — All Cities"),
    ]

    cursor.executemany(
        "INSERT INTO businesses (id, name, category, address) VALUES (?, ?, ?, ?)",
        businesses,
    )

    # ── 10 Orders (2 per business) ──
    orders = [
        # Starbucks orders
        (
            "BILL_SBX20260115_789",
            "starbucks_downtown_01",
            "Aarav Sharma",
            "aarav.sharma@email.com",
            12.50,
            "2026-05-28 09:15:00",
            json.dumps(["Caramel Latte", "Blueberry Muffin"]),
        ),
        (
            "BILL_SBX20260520_142",
            "starbucks_downtown_01",
            "Priya Patel",
            "priya.p@email.com",
            8.75,
            "2026-05-20 14:30:00",
            json.dumps(["Americano", "Chocolate Croissant"]),
        ),
        # Pizza Hut orders
        (
            "ORD_PHC20260525_331",
            "pizzahut_central_02",
            "Rahul Verma",
            "rahul.v@email.com",
            34.99,
            "2026-05-25 19:45:00",
            json.dumps(["Large Pepperoni Pizza", "Garlic Breadsticks", "Pepsi 2L"]),
        ),
        (
            "ORD_PHC20260530_887",
            "pizzahut_central_02",
            "Sneha Gupta",
            "sneha.g@email.com",
            28.50,
            "2026-05-30 20:00:00",
            json.dumps(["Medium Margherita", "Caesar Salad", "Chicken Wings"]),
        ),
        # Samsung orders
        (
            "INV_SAM20260501_005",
            "samsung_store_03",
            "Vikram Singh",
            "vikram.s@email.com",
            1299.99,
            "2026-05-01 11:00:00",
            json.dumps(["Samsung Galaxy S26 Ultra", "Galaxy Buds Pro"]),
        ),
        (
            "INV_SAM20260515_019",
            "samsung_store_03",
            "Ananya Desai",
            "ananya.d@email.com",
            649.99,
            "2026-05-15 15:20:00",
            json.dumps(["Samsung Galaxy Tab S10", "S-Pen", "Book Cover"]),
        ),
        # Hilton orders
        (
            "RES_HGI20260510_402",
            "hilton_garden_04",
            "Mohammed Khan",
            "m.khan@email.com",
            459.00,
            "2026-05-10 14:00:00",
            json.dumps(["Deluxe Room - 3 Nights", "Breakfast Buffet"]),
        ),
        (
            "RES_HGI20260522_718",
            "hilton_garden_04",
            "Deepika Joshi",
            "deepika.j@email.com",
            312.00,
            "2026-05-22 16:00:00",
            json.dumps(["Standard Room - 2 Nights", "Airport Shuttle"]),
        ),
        # Uber orders
        (
            "TRIP_UBR20260528_9A3",
            "uber_rides_05",
            "Arjun Nair",
            "arjun.n@email.com",
            24.50,
            "2026-05-28 08:30:00",
            json.dumps(["UberX - Downtown to Airport", "15.3 km"]),
        ),
        (
            "TRIP_UBR20260531_7B1",
            "uber_rides_05",
            "Kavita Reddy",
            "kavita.r@email.com",
            18.75,
            "2026-05-31 18:45:00",
            json.dumps(["UberGo - Mall to Home", "9.8 km"]),
        ),
    ]

    cursor.executemany(
        """INSERT INTO orders
           (order_id, business_id, customer_name, customer_email,
            amount, order_date, items)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        orders,
    )

    conn.commit()
    conn.close()

    print("✅ Database seeded with 5 businesses and 10 orders:")
    print("   🏪 Starbucks Downtown — 2 orders")
    print("   🍕 Pizza Hut Central — 2 orders")
    print("   📱 Samsung Experience Store — 2 orders")
    print("   🏨 Hilton Garden Inn — 2 orders")
    print("   🚗 Uber Rides — 2 orders")
