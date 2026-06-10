from contextlib import asynccontextmanager
from typing import Annotated

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Session, create_engine, select
from models.card_model import Card, CardPublic, CardCreate, CardUpdate


#connection stuff
#settting variables
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
#creating engine
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
#create tables using engine
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
#create session that will store objects
def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    yield



app = FastAPI(lifespan=lifespan)

origins = ["http://localhost", 
           "http://localhost:8080",
           "http://localhost:5173",
           "https://pokemon-gallery-backend.onrender.com",
           "https://pokemon-gallery-frontend.onrender.com"
           ]
app.add_middleware(CORSMiddleware,
                   allow_origins = origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.post("/card/", status_code=201, response_model=CardPublic)
async def create_card(card: CardCreate, session:SessionDep):
    db_card = Card.model_validate(card)
    session.add(db_card)
    session.commit()
    session.refresh(db_card)
    return db_card

@app.get("/cards/", response_model=list[CardPublic])
async def read_all_cards(session: SessionDep,
                         offset: int = 0,
                         limit: Annotated[int, Query(le=100)]= 100,
                         ) -> list[Card]:
    cards = session.exec(select(Card).offset(offset).limit(limit)).all()
    return cards

@app.get("/cards/{id}", response_model=CardPublic)
async def read_one_card(id: int, session: SessionDep):
    card = session.get(Card, id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card 

@app.patch("/cards/{id}", response_model=CardPublic)
def update_card(id:int, card: CardUpdate, session: SessionDep):
    card_db = session.get(Card, id)
    if not card_db:
        raise HTTPException(status_code=404, detail="Card not found")
    card_data = card.model_dump(exclude_unset=True)
    card_db.sqlmodel_update(card_data)
    session.add(card_db)
    session.commit()
    session.refresh(card_db)
    return card_db

@app.delete("/cards/{id}")
async def delete_card(id:int, session: SessionDep):
    card = session.get(Card, id)
    if not card:
        raise HTTPException(status_code=404, detail="card not found")
    session.delete(card)
    session.commit()
    return {"deleted": card}