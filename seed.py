from app.database import SessionLocal, engine
from app.models import Base, User, FinancialRecord
from app.routers.auth import hash_password
from app.enums import Role, TransactionType
from datetime import date


Base.metadata.create_all(bind=engine)

db = SessionLocal()


users = [
    User(
        name="Admin User",
        email="admin@finance.com",
        password_hash=hash_password("admin123"),
        role=Role.admin,
        is_active=True
    ),
    User(
        name="Alice Analyst",
        email="alice@finance.com",
        password_hash=hash_password("alice123"),
        role=Role.analyst,
        is_active=True
    ),
    User(
        name="Bob Viewer",
        email="bob@finance.com",
        password_hash=hash_password("bob123"),
        role=Role.viewer,
        is_active=True
    ),
    User(
        name="Charlie Analyst",
        email="charlie@finance.com",
        password_hash=hash_password("charlie123"),
        role=Role.analyst,
        is_active=True
    ),
    User(
        name="Diana Viewer",
        email="diana@finance.com",
        password_hash=hash_password("diana123"),
        role=Role.viewer,
        is_active=False  
    ),
]

db.add_all(users)
db.commit()

# refresh to get ids
for u in users:
    db.refresh(u)

admin = users[0]


records = [
    FinancialRecord(amount=50000, type=TransactionType.income, category="salary",    date=date(2024, 1, 1),  notes="January salary",       created_by=admin.id),
    FinancialRecord(amount=50000, type=TransactionType.income, category="salary",    date=date(2024, 2, 1),  notes="February salary",      created_by=admin.id),
    FinancialRecord(amount=50000, type=TransactionType.income, category="salary",    date=date(2024, 3, 1),  notes="March salary",         created_by=admin.id),
    FinancialRecord(amount=50000, type=TransactionType.income, category="salary",    date=date(2024, 4, 1),  notes="April salary",         created_by=admin.id),
    FinancialRecord(amount=50000, type=TransactionType.income, category="salary",    date=date(2024, 5, 1),  notes="May salary",           created_by=admin.id),
    FinancialRecord(amount=50000, type=TransactionType.income, category="salary",    date=date(2024, 6, 1),  notes="June salary",          created_by=admin.id),
    FinancialRecord(amount=15000, type=TransactionType.income, category="freelance", date=date(2024, 1, 15), notes="Freelance project A",  created_by=admin.id),
    FinancialRecord(amount=20000, type=TransactionType.income, category="freelance", date=date(2024, 3, 20), notes="Freelance project B",  created_by=admin.id),
    FinancialRecord(amount=10000, type=TransactionType.income, category="freelance", date=date(2024, 5, 10), notes="Freelance project C",  created_by=admin.id),
    FinancialRecord(amount=5000,  type=TransactionType.income, category="bonus",     date=date(2024, 3, 31), notes="Q1 performance bonus", created_by=admin.id),
    FinancialRecord(amount=8000,  type=TransactionType.income, category="bonus",     date=date(2024, 6, 30), notes="Q2 performance bonus", created_by=admin.id),

   
    FinancialRecord(amount=15000, type=TransactionType.expense, category="rent",      date=date(2024, 1, 5),  notes="January rent",         created_by=admin.id),
    FinancialRecord(amount=15000, type=TransactionType.expense, category="rent",      date=date(2024, 2, 5),  notes="February rent",        created_by=admin.id),
    FinancialRecord(amount=15000, type=TransactionType.expense, category="rent",      date=date(2024, 3, 5),  notes="March rent",           created_by=admin.id),
    FinancialRecord(amount=15000, type=TransactionType.expense, category="rent",      date=date(2024, 4, 5),  notes="April rent",           created_by=admin.id),
    FinancialRecord(amount=15000, type=TransactionType.expense, category="rent",      date=date(2024, 5, 5),  notes="May rent",             created_by=admin.id),
    FinancialRecord(amount=15000, type=TransactionType.expense, category="rent",      date=date(2024, 6, 5),  notes="June rent",            created_by=admin.id),
    FinancialRecord(amount=8000,  type=TransactionType.expense, category="food",      date=date(2024, 1, 31), notes="Groceries + dining",   created_by=admin.id),
    FinancialRecord(amount=7500,  type=TransactionType.expense, category="food",      date=date(2024, 2, 28), notes="Groceries + dining",   created_by=admin.id),
    FinancialRecord(amount=9000,  type=TransactionType.expense, category="food",      date=date(2024, 3, 31), notes="Groceries + dining",   created_by=admin.id),
    FinancialRecord(amount=6000,  type=TransactionType.expense, category="food",      date=date(2024, 4, 30), notes="Groceries + dining",   created_by=admin.id),
    FinancialRecord(amount=8500,  type=TransactionType.expense, category="food",      date=date(2024, 5, 31), notes="Groceries + dining",   created_by=admin.id),
    FinancialRecord(amount=7000,  type=TransactionType.expense, category="food",      date=date(2024, 6, 30), notes="Groceries + dining",   created_by=admin.id),
    FinancialRecord(amount=2000,  type=TransactionType.expense, category="transport", date=date(2024, 1, 31), notes="Fuel + cab",           created_by=admin.id),
    FinancialRecord(amount=1800,  type=TransactionType.expense, category="transport", date=date(2024, 2, 29), notes="Fuel + cab",           created_by=admin.id),
    FinancialRecord(amount=2200,  type=TransactionType.expense, category="transport", date=date(2024, 3, 31), notes="Fuel + cab",           created_by=admin.id),
    FinancialRecord(amount=1500,  type=TransactionType.expense, category="utilities", date=date(2024, 1, 20), notes="Electricity + water",  created_by=admin.id),
    FinancialRecord(amount=1600,  type=TransactionType.expense, category="utilities", date=date(2024, 2, 20), notes="Electricity + water",  created_by=admin.id),
    FinancialRecord(amount=1400,  type=TransactionType.expense, category="utilities", date=date(2024, 3, 20), notes="Electricity + water",  created_by=admin.id),
    FinancialRecord(amount=3000,  type=TransactionType.expense, category="shopping",  date=date(2024, 2, 14), notes="Valentine's shopping", created_by=admin.id),
    FinancialRecord(amount=5000,  type=TransactionType.expense, category="shopping",  date=date(2024, 4, 20), notes="Electronics",          created_by=admin.id),
    FinancialRecord(amount=12000, type=TransactionType.expense, category="travel",    date=date(2024, 5, 20), notes="Goa trip",             created_by=admin.id),
    FinancialRecord(amount=800,   type=TransactionType.expense, category="health",    date=date(2024, 3, 10), notes="Doctor visit",         created_by=admin.id),
    FinancialRecord(amount=2500,  type=TransactionType.expense, category="health",    date=date(2024, 4, 15), notes="Gym membership",       created_by=admin.id),
]

db.add_all(records)
db.commit()
db.close()

print(" Database seeded successfully")
print("Admin:   admin@finance.com   / admin123")
print("Analyst: alice@finance.com   / alice123")
print("Analyst: charlie@finance.com / charlie123")
print("Viewer:  bob@finance.com     / bob123")
print("Viewer:  diana@finance.com   / diana123 (inactive)")