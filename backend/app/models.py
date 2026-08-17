import datetime
import decimal
import enum
from sqlalchemy import Numeric, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    BET = "bet"
    PAYOUT = "payout"

class Operator(Base):
    __tablename__ = "operators"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False) 

class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey("operators.id"), nullable=False)

class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, unique=True)
    balance: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), default=decimal.Decimal("0.00"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wallet_id: Mapped[int] = mapped_column(Integer, ForeignKey("wallets.id"), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)