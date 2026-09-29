def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["application"] == "deal-intelligence-agent"
    assert "database" in data
    assert "hindsight" in data


def test_user_registration(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Sales",
            "email": "jane@example.com",
            "password": "securepassword123",
            "role": "sales_rep"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane@example.com"
    assert data["name"] == "Jane Sales"
    assert "id" in data
    assert "password_hash" not in data


def test_user_login_and_authenticated_me(client):
    # 1. Register user
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Alex Manager",
            "email": "alex@example.com",
            "password": "mypassword123",
            "role": "manager"
        }
    )
    assert reg_response.status_code == 201

    # 2. Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "alex@example.com",
            "password": "mypassword123"
        }
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Get /me with token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "alex@example.com"
    assert me_data["role"] == "manager"


def test_company_deal_and_interaction_creation(client):
    # 1. Register & Login
    client.post(
        "/api/auth/register",
        json={
            "name": "Rep User",
            "email": "rep@example.com",
            "password": "password123",
            "role": "sales_rep"
        }
    )
    login_res = client.post(
        "/api/auth/login",
        json={"email": "rep@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Company
    comp_res = client.post(
        "/api/companies",
        headers=headers,
        json={
            "name": "Acme Corp",
            "industry": "Software",
            "size": "100-500",
            "website": "https://acme.com",
            "description": "Enterprise SaaS company"
        }
    )
    assert comp_res.status_code == 201
    comp_data = comp_res.json()
    company_id = comp_data["id"]
    assert comp_data["name"] == "Acme Corp"

    # 3. Create Contact
    contact_res = client.post(
        f"/api/companies/{company_id}/contacts",
        headers=headers,
        json={
            "name": "John Doe",
            "job_title": "CTO",
            "email": "john@acme.com",
            "role_in_deal": "Technical Decision Maker"
        }
    )
    assert contact_res.status_code == 201
    contact_id = contact_res.json()["id"]

    # 4. Create Deal
    deal_res = client.post(
        "/api/deals",
        headers=headers,
        json={
            "company_id": company_id,
            "name": "Acme Enterprise License",
            "description": "Annual enterprise license deal",
            "stage": "DISCOVERY",
            "value": "150000.00",
            "currency": "USD",
            "probability": 0.25,
            "status": "OPEN"
        }
    )
    assert deal_res.status_code == 201
    deal_data = deal_res.json()
    deal_id = deal_data["id"]
    assert deal_data["name"] == "Acme Enterprise License"

    # 5. Create Interaction for Deal
    inter_res = client.post(
        f"/api/deals/{deal_id}/interactions",
        headers=headers,
        json={
            "contact_id": contact_id,
            "type": "DISCOVERY" if False else "MEETING",
            "title": "Initial Discovery Call with CTO",
            "content": "Discussed scalability concerns and security compliance requirements."
        }
    )
    assert inter_res.status_code == 201
    inter_data = inter_res.json()
    assert inter_data["deal_id"] == deal_id
    assert inter_data["title"] == "Initial Discovery Call with CTO"
    assert "hindsight_memory_status" in inter_data
    assert inter_data["hindsight_memory_status"] in ["stored", "not_configured", "unavailable", "pending", "error"]

    # 6. Check Dashboard metrics
    dash_res = client.get("/api/deals/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_active_deals"] == 1
    assert float(dash_data["open_pipeline_value"]) == 150000.0
