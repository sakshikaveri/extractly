
from pydantic import BaseModel  #pydantic is used for data validation

class Product(BaseModel):
    id: int
    name:str
    description:str
    price:float
    quantity:int
