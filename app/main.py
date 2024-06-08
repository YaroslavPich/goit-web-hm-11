from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import engine, Base, get_db
from app.schemas import ContactCreate, ContactUpdate, ContactInDB
import app.crud as crud
from app.models import Contact

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.post("/contacts/", response_model=ContactInDB)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
	try:
		if db.query(Contact).filter(Contact.email == contact.email).first():
			raise HTTPException(status_code=400, detail="Email already exists")
		if db.query(Contact).filter(Contact.phone_number == contact.phone_number).first():
			raise HTTPException(status_code=400, detail="Phone already exists")
		return crud.create_contact(db, contact)
	except HTTPException as e:
		raise e
	except Exception:
		raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/contacts/", response_model=List[ContactInDB])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
	contacts = crud.get_contacts(db, skip=skip, limit=limit)
	return contacts


@app.get("/contacts/{contact_id}", response_model=ContactInDB)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
	db_contact = crud.get_contact(db, contact_id)
	if db_contact is None:
		raise HTTPException(status_code=404, detail="Contact not found")
	return db_contact


@app.put("/contacts/{contact_id}", response_model=ContactInDB)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
	try:
		db_contact = crud.get_contact(db, contact_id)
		if db_contact is None:
			raise HTTPException(status_code=404, detail="Contact not found")
		if contact.email and db.query(Contact).filter(Contact.email == contact.email, Contact.id != contact_id).first():
			raise HTTPException(status_code=400, detail="Email already exists")
		if contact.phone_number and db.query(Contact).filter(Contact.phone_number == contact.phone_number,
		                                                     Contact.id != contact_id).first():
			raise HTTPException(status_code=400, detail="Phone already exists")
		updated_contact = crud.update_contact(db, contact_id, contact)
		return updated_contact
	except HTTPException as e:
		raise e
	except Exception:
		raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/contacts/{contact_id}", response_model=ContactInDB)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
	db_contact = crud.delete_contact(db, contact_id)
	if db_contact is None:
		raise HTTPException(status_code=404, detail="Contact not found")
	return db_contact


@app.get("/contacts/search/", response_model=List[ContactInDB])
def search_contacts(query: str, db: Session = Depends(get_db)):
	return crud.search_contacts(db, query)


@app.get("/contacts/birthdays/", response_model=List[ContactInDB])
def read_contacts_with_birthdays(db: Session = Depends(get_db)):
	return crud.get_birthdays_within_next_week(db)
