import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, FinancialRecord
from app.routers.auth import hash_password
from app.enums import Role, TransactionType
from app.core.config import settings
from datetime import date


TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "/financedb", "/financedb_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)



@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()

    admin = User(
        name="Admin User", email="admin@test.com",
        password_hash=hash_password("admin123"), role=Role.admin, is_active=True
    )
    analyst = User(
        name="Alice Analyst", email="alice@test.com",
        password_hash=hash_password("alice123"), role=Role.analyst, is_active=True
    )
    viewer = User(
        name="Bob Viewer", email="bob@test.com",
        password_hash=hash_password("bob123"), role=Role.viewer, is_active=True
    )
    inactive = User(
        name="Diana Inactive", email="diana@test.com",
        password_hash=hash_password("diana123"), role=Role.viewer, is_active=False
    )

    db.add_all([admin, analyst, viewer, inactive])
    db.commit()
    for u in [admin, analyst, viewer, inactive]:
        db.refresh(u)

    records = [
        FinancialRecord(amount=50000, type=TransactionType.income,  category="salary", date=date(2024, 1, 1),  notes="January salary",  created_by=admin.id),
        FinancialRecord(amount=15000, type=TransactionType.expense, category="rent",   date=date(2024, 1, 5),  notes="January rent",    created_by=admin.id),
        FinancialRecord(amount=8000,  type=TransactionType.expense, category="food",   date=date(2024, 1, 31), notes="Groceries",       created_by=admin.id),
    ]
    db.add_all(records)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)



def login(email, password):
    res = client.post("/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}



def test_login_success():
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "admin123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_wrong_password():
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert res.status_code == 401

def test_login_inactive_user():
    res = client.post("/auth/login", json={"email": "diana@test.com", "password": "diana123"})
    assert res.status_code == 403



def test_admin_can_create_user():
    token = login("admin@test.com", "admin123")
    res = client.post("/users/", json={
        "name": "New User", "email": "new@test.com",
        "password": "new123", "role": "viewer"
    }, headers=auth_header(token))
    assert res.status_code == 200
    assert res.json()["email"] == "new@test.com"

def test_analyst_cannot_create_user():
    token = login("alice@test.com", "alice123")
    res = client.post("/users/", json={
        "name": "New User", "email": "new2@test.com",
        "password": "new123", "role": "viewer"
    }, headers=auth_header(token))
    assert res.status_code == 403

def test_admin_can_list_users():
    token = login("admin@test.com", "admin123")
    res = client.get("/users/", headers=auth_header(token))
    assert res.status_code == 200
    assert len(res.json()) >= 3

def test_admin_search_users_by_name():
    token = login("admin@test.com", "admin123")
    res = client.get("/users/?search=alice", headers=auth_header(token))
    assert res.status_code == 200
    assert any("alice" in u["email"].lower() for u in res.json())

def test_admin_can_update_user_role():
    token = login("admin@test.com", "admin123")
    users = client.get("/users/", headers=auth_header(token)).json()
    bob = next(u for u in users if u["email"] == "bob@test.com")
    res = client.patch(f"/users/{bob['id']}?role=analyst", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json()["role"] == "analyst"



def test_viewer_can_get_records():
    token = login("bob@test.com", "bob123")
    res = client.get("/records/", headers=auth_header(token))
    assert res.status_code == 200
    assert "data" in res.json()

def test_viewer_cannot_filter_records():
    token = login("bob@test.com", "bob123")
    res = client.get("/records/?category=food", headers=auth_header(token))
    assert res.status_code == 403

def test_analyst_can_filter_records():
    token = login("alice@test.com", "alice123")
    res = client.get("/records/?category=food", headers=auth_header(token))
    assert res.status_code == 200

def test_analyst_can_search_records():
    token = login("alice@test.com", "alice123")
    res = client.get("/records/?search=admin", headers=auth_header(token))
    assert res.status_code == 200

def test_analyst_cannot_create_record():
    token = login("alice@test.com", "alice123")
    res = client.post("/records/", json={
        "amount": 1000, "type": "income",
        "category": "test", "date": "2024-01-01"
    }, headers=auth_header(token))
    assert res.status_code == 403

def test_admin_can_create_record():
    token = login("admin@test.com", "admin123")
    res = client.post("/records/", json={
        "amount": 1000, "type": "income",
        "category": "bonus", "date": "2024-01-01"
    }, headers=auth_header(token))
    assert res.status_code == 200
    assert res.json()["category"] == "bonus"

def test_admin_can_soft_delete_record():
    token = login("admin@test.com", "admin123")
    records = client.get("/records/", headers=auth_header(token)).json()
    record_id = records["data"][0]["id"]
    res = client.delete(f"/records/{record_id}", headers=auth_header(token))
    assert res.status_code == 200
    res2 = client.get(f"/records/{record_id}", headers=auth_header(token))
    assert res2.status_code == 404

def test_invalid_amount_rejected():
    token = login("admin@test.com", "admin123")
    res = client.post("/records/", json={
        "amount": -500, "type": "income",
        "category": "test", "date": "2024-01-01"
    }, headers=auth_header(token))
    assert res.status_code == 422

def test_pagination():
    token = login("admin@test.com", "admin123")
    res = client.get("/records/?page=1&limit=2", headers=auth_header(token))
    assert res.status_code == 200
    assert len(res.json()["data"]) <= 2
    assert res.json()["page"] == 1


def test_viewer_can_get_summary():
    token = login("bob@test.com", "bob123")
    res = client.get("/dashboard/summary", headers=auth_header(token))
    assert res.status_code == 200
    assert "total_income" in res.json()
    assert "net_balance" in res.json()

def test_viewer_cannot_get_trends():
    token = login("bob@test.com", "bob123")
    res = client.get("/dashboard/trends", headers=auth_header(token))
    assert res.status_code == 403

def test_analyst_can_get_trends():
    token = login("alice@test.com", "alice123")
    res = client.get("/dashboard/trends", headers=auth_header(token))
    assert res.status_code == 200
    assert "data" in res.json()

def test_summary_values_correct():
    token = login("admin@test.com", "admin123")
    res = client.get("/dashboard/summary", headers=auth_header(token))
    data = res.json()
    assert float(data["total_income"]) == 50000
    assert float(data["total_expenses"]) == 23000
    assert float(data["net_balance"]) == 27000