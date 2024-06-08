from sqlalchemy.orm import Session
from app.models import Contact
from app.schemas import ContactCreate, ContactUpdate
from datetime import datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError


def get_contact(db: Session, contact_id: int):
	return db.query(Contact).filter(Contact.id == contact_id).first()


def get_contacts(db: Session, skip: int = 0, limit: int = 10):
	return db.query(Contact).offset(skip).limit(limit).all()


def create_contact(db: Session, contact: ContactCreate):
	try:
		db_contact = Contact(**contact.dict())
		db.add(db_contact)
		db.commit()
		db.refresh(db_contact)
		return db_contact
	except IntegrityError:
		db.rollback()


def update_contact(db: Session, contact_id: int, contact: ContactUpdate):
	try:
		db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
		if db_contact is None:
			return None
		for key, value in contact.dict().items():
			setattr(db_contact, key, value)
		db.commit()
		db.refresh(db_contact)
		return db_contact
	except IntegrityError:
		db.rollback()


def delete_contact(db: Session, contact_id: int):
	db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
	if db_contact is None:
		return None
	db.delete(db_contact)
	db.commit()
	return db_contact


def search_contacts(db: Session, query: str):
	return db.query(Contact).filter(
		or_(
			(Contact.first_name.ilike(f"%{query}%"))
			(Contact.last_name.ilike(f"%{query}%"))
			(Contact.email.ilike(f"%{query}%"))
		)
	).all()


def get_birthdays_within_next_week(db: Session):
	today = datetime.today().date()
	next_week = today + timedelta(days=7)
	return db.query(Contact).filter(
		or_(
			Contact.birthday >= today,
			Contact.birthday <= next_week
		)
	).all()
