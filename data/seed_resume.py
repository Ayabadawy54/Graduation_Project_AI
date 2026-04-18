"""
Talentree AI - Seed Generator FINAL RESUME
Only runs the 3 remaining steps that haven't completed yet:
  1. PayoutRequests (50 rows) - FIXED unique constraint
  2. BoProductionRequests (+200 rows)
  3. Products UPDATE
  4. AspNetUsers UPDATE
"""

import pyodbc
import random
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONNECTION

BO_USER_IDS = [
    "a091d9c9-e581-4f6e-8cf6-d38fc68dffbf",
    "abdd2fd2-08e0-48f1-b7b1-1f9b41c90c4d",
    "29c0dd99-7dfd-464f-9a74-30bb3ef47f13",
    "5800103d-c137-40b5-9056-5b7ae56ae778",
    "574ecf2d-a14d-4a90-b414-99150c738835",
    "a7565c7f-7309-4d0e-87a0-7ae06e12e0c0",
    "d9d3b8c3-425f-477e-973b-06c0682cc155",
    "224b3d75-6eee-4453-b257-abea45445526",
    "97716b6b-0711-4e26-b9d0-99dcf0acf0aa",
    "c98a3dff-ab6b-44f7-aa20-bce4a305cbff",
    "4ab34ce6-3f7c-42e3-940b-77f1893b1c45",
    "4caa8682-4f7f-472b-9f2c-d5ec0d47d43f",
    "081cb5f2-8418-44ca-9e62-a883e49327a3",
    "1bfd9db4-2858-4b4d-936d-efc8d16dbcd8",
    "b09209a1-bbe3-42ff-84f5-c550b8af33de",
    "11032d13-aaaa-4acb-88a1-a6a845e94c57",
    "11111111-1111-1111-1111-111111111101",
    "22222222-2222-2222-2222-222222222202",
    "33333333-3333-3333-3333-333333333303",
    "561ebbf3-f07a-472f-8f41-1e742dad3349",
    "b46c0d90-3ade-4ec4-b303-f1d2e1edaae1",
    "77d8ee37-d9ba-4a95-9639-6466428e59f6",
    "37e68335-4ff3-4a12-b6c4-9a544109c0f5",
    "2577da69-baf4-462d-a4cd-d1ef059ac935",
    "be56b997-e537-41e9-aed0-7c2e3ca868d4",
]

ALL_USER_IDS = [
    "a3dd216a-6b31-488a-b4b1-6c422d66e750", "a091d9c9-e581-4f6e-8cf6-d38fc68dffbf",
    "d937e88e-88c4-4815-8f1b-1ab287b02301", "e82bac50-dce5-4f59-80a3-017499043e34",
    "a7565c7f-7309-4d0e-87a0-7ae06e12e0c0", "d9d3b8c3-425f-477e-973b-06c0682cc155",
    "508fc0e8-9438-4ae7-b3a1-2502df301713", "68b69189-ba41-4d39-9c87-642e13abeabe",
    "c98a3dff-ab6b-44f7-aa20-bce4a305cbff", "224b3d75-6eee-4453-b257-abea45445526",
    "4ab34ce6-3f7c-42e3-940b-77f1893b1c45", "985593df-c763-4c8b-9a79-2c72e15b7f9d",
    "97716b6b-0711-4e26-b9d0-99dcf0acf0aa", "1bfd9db4-2858-4b4d-936d-efc8d16dbcd8",
    "4caa8682-4f7f-472b-9f2c-d5ec0d47d43f", "11032d13-aaaa-4acb-88a1-a6a845e94c57",
    "4271d311-b711-4b2e-ba36-5273feb387bc", "081cb5f2-8418-44ca-9e62-a883e49327a3",
    "b09209a1-bbe3-42ff-84f5-c550b8af33de", "c78baa8f-9529-4879-8b68-da01be3d7b01",
    "d5e772c6-a6ac-4b01-902f-e3905883041b", "8174e7e0-4b81-4a1e-9f4a-bc2dc187b507",
    "be56b997-e537-41e9-aed0-7c2e3ca868d4", "36ee4858-f811-4b83-aea6-bb8d058f16c2",
    "97f5b334-b66c-4667-a142-6581bc5375dc", "9c7025ae-20e9-4c49-9e9c-51a046cfba04",
    "389127aa-2bfc-4851-a7c1-30ee15cb304e", "be991173-9391-4f75-8431-64feb5fc5cc2",
    "2577da69-baf4-462d-a4cd-d1ef059ac935", "37e68335-4ff3-4a12-b6c4-9a544109c0f5",
    "77d8ee37-d9ba-4a95-9639-6466428e59f6", "0030e8dc-d747-4adf-a6d6-ecd315e8a191",
    "23633ddc-4599-49cb-9538-4cbda20c50ea", "abdd2fd2-08e0-48f1-b7b1-1f9b41c90c4d",
    "81b9fb83-adb2-4b85-94ff-a78fc7294566", "16121248-8cf8-4c6b-a636-4d9b0dfbd70b",
    "d40a23ed-8b15-46f5-b9c6-ae0501102401", "22222222-2222-2222-2222-222222222202",
    "1d292c28-acb1-413d-b7c9-5bcbd206b644", "99386a3c-0674-463a-b365-e7828bbedcc3",
    "29c0dd99-7dfd-464f-9a74-30bb3ef47f13", "3a503aad-d2f3-4ae0-a9a0-6368729fc322",
    "371ba4a1-367c-4921-a46d-2e00f4268721", "483fef4a-2417-4114-835a-3597aedeeb6f",
    "3eab1be0-d7d1-42a0-8bf5-ead6c51f7ea6", "561ebbf3-f07a-472f-8f41-1e742dad3349",
    "b46c0d90-3ade-4ec4-b303-f1d2e1edaae1", "11111111-1111-1111-1111-111111111101",
    "2c010332-773f-451f-8dda-72b3f47ff345", "574ecf2d-a14d-4a90-b414-99150c738835",
    "33333333-3333-3333-3333-333333333303", "5800103d-c137-40b5-9056-5b7ae56ae778",
    "525606c3-a9c7-49b2-90a6-a79557712066", "47503fff-6a46-43e7-b0ee-fcff94074534",
    "ed4b0446-b799-4818-8a25-6fd6b87685f9", "2f8a7a71-9b54-40f5-bc2c-e3ba74b84160",
    "6734df62-d369-4d87-a43b-58f8cd6681b6", "718ef72c-57f3-449c-9c7b-e4f12469771c",
    "a7864e08-4503-4302-aa00-668f2876a9d0", "5b705ad6-f15f-4f4c-844c-df5b7ca6e94b",
    "c38e76d2-1f4c-4ed7-b158-ab17630cbce3", "2ab89e5e-28ea-460c-82f9-d3ef8537e865",
    "0b316b48-668c-4b16-b8e0-f60cb2203c99",
]

PRODUCT_IDS = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
PRODUCT_PRICES = {15: 189.99, 16: 149.99, 17: 229.99, 18: 275.00,
                  19: 199.99, 20: 159.99, 21: 349.99, 22: 120.00,
                  23: 149.99, 24: 199.99, 25: 129.99, 26: 259.99}


def rand_date(days_back_max=180, days_back_min=1):
    delta = random.randint(days_back_min, days_back_max)
    return datetime.now() - timedelta(days=delta)

def rand_datetime_str(days_back_max=180, days_back_min=1):
    return rand_date(days_back_max, days_back_min).strftime("%Y-%m-%d %H:%M:%S")

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=db39807.public.databaseasp.net;"
        "DATABASE=db39807;"
        "UID=db39807;"
        "PWD=Ya8@_Dt4o9N=;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )


def seed_payout_requests(cursor):
    """PayoutRequests has unique index on (BusinessOwnerId, Status).
    So each BO can only have ONE payout per status. We give each BO
    exactly one payout per status = max 5 per BO, ~125 total."""
    print("Seeding PayoutRequests (unique per BO+Status)...")
    statuses = ["Pending", "Approved", "Processing", "Completed", "Rejected"]
    banks = ["CIB Bank", "NBE - National Bank of Egypt", "Banque Misr",
             "QNB Egypt", "HSBC Egypt", "Faisal Islamic Bank"]
    names = ["Ahmed Hassan", "Sara Mohamed", "Omar Khalil", "Nadia Ali", "Karim Taha"]

    # Get existing combos to avoid duplicates
    cursor.execute("SELECT BusinessOwnerId, Status FROM PayoutRequests")
    existing = {(row[0], row[1]) for row in cursor.fetchall()}

    sql = """INSERT INTO PayoutRequests
             (BusinessOwnerId, Amount, Currency, Status,
              BankName, AccountHolderName, AccountIdentifierEnc,
              RoutingSwiftCode, CreatedAt, UpdatedAt, CreatedBy)
             VALUES (?,?,?,?,?,?,?,?,?,?,?)"""
    inserted = 0
    for bo_id in BO_USER_IDS:
        # Give each BO 1-3 random statuses
        num_payouts = random.randint(1, 3)
        chosen_statuses = random.sample(statuses, num_payouts)
        for status in chosen_statuses:
            if (bo_id, status) in existing:
                continue
            amount = round(random.uniform(500, 20000), 2)
            bank = random.choice(banks)
            created = rand_datetime_str(120, 1)
            cursor.execute(sql, (
                bo_id, amount, "EGP", status,
                bank, random.choice(names),
                f"ENC_{random.randint(100000000, 999999999)}",
                "XXXXXXXX",
                created, created, bo_id
            ))
            inserted += 1
    print(f"  [OK] Inserted {inserted} PayoutRequests")


def seed_production_requests(cursor, count=200):
    print(f"Seeding {count} more BoProductionRequests...")
    statuses = ["Submitted", "UnderReview", "Quoted", "Confirmed",
                "InProduction", "Completed", "Rejected", "Cancelled"]
    weights = [15, 15, 10, 10, 15, 25, 5, 5]
    titles = [
        "Summer Abaya Collection - 200 Units", "Linen Dress Set - Spring Line",
        "Embroidered Hijabs - Eid Collection", "Leather Handbags - Limited Run",
        "Cotton Casual Shirts - 150 Units", "Modest Swimwear - 100 Units",
        "Scented Candle Gift Sets - 500 Units", "Macrame Wall Art - Large Format",
        "Resin Jewellery Collection - 200 Pieces", "Handmade Clay Pots - 150 Units",
        "Argan Oil Hair Serum - 300 Bottles", "Rose Water Toner - 500 Units",
        "Shea Body Butter - 400 Jars", "Natural Soap Bars - 600 Units",
        "Vitamin C Face Serum - 250 Bottles", "Herbal Face Mask - 200 Units",
        "Coconut Hair Mask - 300 Jars", "Lavender Bath Salts - 450 Bags",
        "Printed Scarves - 300 Units", "Gift Boxes - 300 Units",
        "Wooden Photo Frames - 100 Units", "Dried Flowers - 200 Units",
        "Vintage Denim Jackets - 80 Units", "Hand-painted Ceramics - 80 Units",
    ]
    sql = """INSERT INTO BoProductionRequests
             (BusinessOwnerId, Title, Notes, Status, QuotedPrice,
              EstimatedCompletionDate, CompletedAt,
              IsFraudFlag, FraudScore, PaymentStatus,
              CreatedAt, UpdatedAt, CreatedBy)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    inserted = 0
    for _ in range(count):
        bo_id = random.choice(BO_USER_IDS)
        title = random.choice(titles) + f" #{random.randint(100,999)}"
        status = random.choices(statuses, weights=weights)[0]
        is_fraud = random.random() < 0.08
        fraud_score = round(random.uniform(0.55, 0.95), 2) if is_fraud else round(random.uniform(0.0, 0.25), 2)
        quoted = round(random.uniform(2000, 50000), 2) if status not in ("Submitted", "UnderReview") else None
        created_dt = rand_date(180, 7)
        created = created_dt.strftime("%Y-%m-%d %H:%M:%S")
        est_complete = None
        completed_at = None
        if status in ("Confirmed", "InProduction", "Completed"):
            est_complete = (created_dt + timedelta(days=random.randint(14, 60))).strftime("%Y-%m-%d %H:%M:%S")
        if status == "Completed":
            completed_at = (created_dt + timedelta(days=random.randint(10, 50))).strftime("%Y-%m-%d %H:%M:%S")
        payment_status = "Paid" if status == "Completed" and random.random() > 0.3 else "Unpaid"
        cursor.execute(sql, (
            bo_id, title, "Production request for seasonal collection.",
            status, quoted, est_complete, completed_at,
            1 if is_fraud else 0, fraud_score,
            payment_status, created, created, bo_id
        ))
        inserted += 1
    print(f"  [OK] Inserted {inserted} BoProductionRequests")


def update_products(cursor):
    print("Updating Products with realistic view/purchase counts...")
    for product_id, price in PRODUCT_PRICES.items():
        view_count = random.randint(150, 3000)
        cart_count = random.randint(20, 400)
        purchase_count = random.randint(10, 150)
        revenue_total = round(price * purchase_count, 2)
        avg_rating = round(random.uniform(3.5, 5.0), 1)
        cursor.execute("""
            UPDATE Products
            SET ViewCount = ?, CartAddCount = ?, PurchaseCount = ?,
                RevenueTotal = ?, AvgRating = ?
            WHERE Id = ?
        """, (view_count, cart_count, purchase_count, revenue_total, avg_rating, product_id))
    print(f"  [OK] Updated {len(PRODUCT_PRICES)} Products")


def update_users_login_count(cursor):
    print("Updating AspNetUsers.LoginCount...")
    for user_id in ALL_USER_IDS:
        login_count = random.randint(1, 200)
        cursor.execute("UPDATE AspNetUsers SET LoginCount = ? WHERE Id = ?",
                       (login_count, user_id))
    print(f"  [OK] Updated {len(ALL_USER_IDS)} users LoginCount")


def main():
    print("=" * 60)
    print("  Talentree AI - Final Resume Seed")
    print("  Already done: Transactions, LoginHistories, Reviews,")
    print("  Tickets, Messages, Onboarding")
    print("  Now: PayoutRequests, ProdRequests, Products, Users")
    print("=" * 60)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        seed_payout_requests(cursor)
        conn.commit()
        print("  >> Committed PayoutRequests")

        seed_production_requests(cursor, 200)
        conn.commit()
        print("  >> Committed BoProductionRequests")

        update_products(cursor)
        conn.commit()
        print("  >> Committed Products UPDATE")

        update_users_login_count(cursor)
        conn.commit()
        print("  >> Committed AspNetUsers UPDATE")

        print("=" * 60)
        print("  [OK] ALL SEEDING COMPLETE!")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
