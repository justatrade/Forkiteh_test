from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tronpy import Tron
from tronpy.exceptions import BadAddress
from tronpy.providers import HTTPProvider


DATABASE_URL = "sqlite:///./test.db"
API_KEY = '87488e0b-d0b5-4d28-a9ab-b5adf050d0c9'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class WalletQuery(Base):
    __tablename__ = "wallet_queries"
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, index=True)
    query_result = Column(Text)


Base.metadata.create_all(bind=engine)

app = FastAPI()
tron_client = Tron(provider=HTTPProvider(api_key=API_KEY))


class WalletRequest(BaseModel):
    address: str


@app.post("/wallet_info")
def get_wallet_info(wallet: WalletRequest):
    session = SessionLocal()
    try:
        account = tron_client.get_account(wallet.address)
        bandwidth = tron_client.get_bandwidth(wallet.address)
        energy = tron_client.get_account_resource(wallet.address).get("EnergyLimit", 0)
        trx_balance = account.get("balance", 0) / 1_000_000

        result = {
            "bandwidth": bandwidth,
            "energy": energy,
            "trx_balance": trx_balance,
        }
        db_entry = WalletQuery(wallet_address=wallet.address, query_result=str(result))
        session.add(db_entry)
        session.commit()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid wallet address or network error.")

@app.get("/wallet_queries")
def get_wallet_queries(skip: int = 0, limit: int = 10):
    session = SessionLocal()
    try:
        queries = session.query(WalletQuery).offset(skip).limit(limit).all()
        return [
            {
                "id": query.id,
                "wallet_address": query.wallet_address,
                "query_result": query.query_result,
            }
            for query in queries
        ]
    finally:
        session.close()


if __name__ == "__main__":
    import os

    import uvicorn

    if not os.path.exists("test.db"):
        Base.metadata.create_all(bind=engine)

    uvicorn.run(app, host="127.0.0.1", port=8000)