from pybo import db
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship

question_voter = db.Table(
    'question_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), primary_key=True)
)

answer_voter = db.Table(
    'answer_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('answer_id', db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), primary_key=True)
)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('question_set'))
    modify_date = db.Column(db.DateTime(), nullable=True)
    voter = db.relationship('User', secondary=question_voter, backref=db.backref('question_voter_set'))


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'))
    question = db.relationship('Question', backref=db.backref('answer_set'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('answer_set'))
    modify_date = db.Column(db.DateTime(), nullable=True)
    voter = db.relationship('User', secondary=answer_voter, backref=db.backref('answer_voter_set'))

    
    
class User(db.Model):
    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(15))

    # CheckConstraint를 사용하여 비밀번호 조건 정의
    __table_args__ = (
        CheckConstraint(
            "CHAR_LENGTH(password) >= 8 AND "
            "password ~ '[a-z]' AND "
            "password ~ '[A-Z]' AND "
            "password ~ '[0-9]' AND "
            "password ~ '[^a-zA-Z0-9]'"
        ),
    )

class Ticket(db.Model):
    __tablename__ = 'tickets'

    tid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_name = db.Column(db.String(100), nullable=False)
    entry_datetime = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    total_quantity = db.Column(db.Integer, nullable=False)

    # CheckConstraint를 사용하여 total_quantity 조건 정의
    __table_args__ = (
        CheckConstraint('total_quantity <= 250', name='check_total_quantity'),
    )
    
class PurchaseHistory(db.Model):
    __tablename__ = 'purchase_history'

    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, ForeignKey('users.uid'))
    tid = db.Column(db.Integer, ForeignKey('tickets.tid'))
    purchase_datetime = db.Column(db.DateTime, default=func.current_timestamp())
    total_price = db.Column(db.Integer)
    purchase_quantity = db.Column(db.Integer)

    user = relationship('User', backref='purchase_history')
    ticket = relationship('Ticket', backref='purchase_history')