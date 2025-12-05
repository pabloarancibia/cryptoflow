from fastapi import FastAPI, HTTPException, status
from src.services.identity.schemas import UserLogin, Token
from src.services.identity.utils import verify_password, create_access_token, get_password_hash

app = FastAPI(title="CryptoFlow Identity Service")

# Fake Database for Simulation
# In a real microservice, this would connect to its OWN database (e.g., 'users_db')
FAKE_USERS_DB = {
    "trader1": {
        "username": "trader1",
        # Hash for "password123"
        "hashed_password": get_password_hash("password123"),
        "role": "admin"
    }
}


@app.get("/health")
def health_check():
    return {"status": "identity_service_active"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserLogin):
    user = FAKE_USERS_DB.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate Token
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )

    return {"access_token": access_token, "token_type": "bearer"}