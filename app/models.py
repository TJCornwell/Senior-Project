from datetime import datetime, timezone
from tokenize import Double
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    user_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    registration_date: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    #do we need these?
    accounts: so.WriteOnlyMapped['Account'] = so.relationship(back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    @login.user_loader
    def load_user(id):
        return db.session.get(User, int(id))
    def get_id(self):
        return self.user_id

class Account(db.Model):
    account_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.user_id))
    amount: so.Mapped[float] = so.mapped_column(sa.Float(asdecimal=True), default=lambda: 0)
    merchant: so.Mapped[str] = so.mapped_column(sa.String(128))#what is this field for? optional? 

    user: so.Mapped[User] = so.relationship(back_populates='accounts')
    transactions: so.WriteOnlyMapped['Transaction'] = so.relationship(back_populates='account')
    
    def __repr__(self):
        return f'<Account {self.merchant}>'

class Transaction(db.Model):
    transaction_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    bank: so.Mapped[str] = so.mapped_column(sa.String(128))#what is this field for?
    amount: so.Mapped[float] = so.mapped_column(sa.Float(asdecimal=True))
    account_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey(Account.account_id))#optional? how would it connect to the user if optional?
    tag: so.Mapped[str] = so.mapped_column(sa.String(64), default=lambda:"")

    account: so.Mapped[Account] = so.relationship(back_populates='transactions')
    
    def __repr__(self):
        return f'<Transaction ID# {self.transaction_id}>'

