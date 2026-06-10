
from pydantic import BaseModel
from sqlmodel import SQLModel, Field



#data model (info for users)
class CardBase(SQLModel): # cardbase inherits fields of sqlmodel
    name: str = Field(index=True)
    image: str
    rarity: str = Field(index=True)
#table model (important info for devs)
class Card(CardBase, table=True): #card inherits from cardbase
    id: int | None = Field(default=None, primary_key=True)
    secret_id: str
#public data model (specifically for returning to clients)
class CardPublic(CardBase): #cardpubic inherits from cardbase
    id: int #by re-declaring id: int we enforce a contract saying when responding to a client id will be int not None
#data model to create a card
class CardCreate(CardBase):
    secret_id: str
    
class CardUpdate(CardBase):
    name: str | None = None
    image: str | None = None
    rarity: str | None = None
    secret_id: str | None = None

#why multiple models? think about what we want and what we want to hide when doing an operation for instance
#(cardCreate)we want a user to create a card but not create an id for the card
#(cardpublic) we want to return a card but not show the secret id the the response 
#think of these as shallow lenses for a specific task