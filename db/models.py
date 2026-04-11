"""
SQLAlchemy ORM models for all database tables.
"""

import datetime
from sqlalchemy import (
    BigInteger, String, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    referral_code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    referred_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )

    # Relationships
    deposits: Mapped[list["Deposit"]] = relationship(back_populates="user", lazy="selectin")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User telegram_id={self.telegram_id} balance={self.balance}>"


class Deposit(Base):
    """Deposit addresses mapped to users."""
    __tablename__ = "deposits"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    address: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="deposits", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Deposit user={self.user_telegram_id} addr={self.address[:12]}…>"


class Transaction(Base):
    """Records every on-chain deposit detected."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    tx_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="confirmed", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="transactions", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Transaction tx={self.tx_hash[:12]}… amount={self.amount}>"


class Referral(Base):
    """Tracks referrer→referee relationships."""
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    referrer_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    referee_telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_referral_pair", "referrer_telegram_id", "referee_telegram_id"),
    )

    def __repr__(self) -> str:
        return f"<Referral {self.referrer_telegram_id}→{self.referee_telegram_id}>"


class Commission(Base):
    """Referral commissions (pending or paid)."""
    __tablename__ = "commissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    referrer_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    referee_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    deposit_tx_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending | paid
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    paid_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Commission {self.referrer_telegram_id} ${self.amount} [{self.status}]>"
