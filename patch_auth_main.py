import re

with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# Add hashlib and LoginRequest class if not there
if "class LoginRequest" not in main_code:
    auth_imports_and_models = """import hashlib

class LoginRequest(BaseModel):
    email: str
    password: str

class ScrapeRequest(BaseModel):"""
    
    main_code = main_code.replace("class ScrapeRequest(BaseModel):", auth_imports_and_models)

# Add the /api/login endpoint
if "@app.post(\"/api/login\")" not in main_code:
    login_endpoint = """
@app.post("/api/login")
def login_api(request: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, password_hash FROM users WHERE email = ?", (request.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    # Verify hash
    hashed_input = hashlib.sha256(request.password.encode()).hexdigest()
    if hashed_input != user['password_hash']:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    # Generate mock token
    token = f"jwt-mock-{user['role']}-{'admin' if user['role']=='admin' else 'jury'}-8932"
    
    return {
        "status": "success",
        "role": user['role'],
        "token": token
    }

# THE LIVE INTEGRATION ENDPOINT"""
    
    main_code = main_code.replace("# THE LIVE INTEGRATION ENDPOINT", login_endpoint)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
