from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import jwt

app = FastAPI()

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

ASSIGNED_ISS = "https://idp.exam.local"
ASSIGNED_AUD = "tds-r5gij7z6.apps.exam.local"

class TokenPayload(BaseModel):
    token: str

@app.post("/verify")
async def verify_token(payload: TokenPayload):
    try:
        claims = jwt.decode(
            payload.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=ASSIGNED_AUD,
            issuer=ASSIGNED_ISS
        )
        return {
            "valid": True,
            "email": claims.get("email"),
            "sub": claims.get("sub"),
            "aud": claims.get("aud")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"valid": False, "error": "Expired"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"valid": False, "error": "Invalid"})
