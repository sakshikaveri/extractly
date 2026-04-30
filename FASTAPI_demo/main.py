from fastapi import FastAPI, Depends
from models import Product
from config import session,engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

database_models.Base.metadata.create_all(bind=engine)
# to return a output for server start
@app.get("/")
def greet_user():
    return "Hi, I am new to FASTAPI"

products = [
    Product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
    Product(id=2, name="Laptop", description="A powerful laptop", price=999.99, quantity=30),
    Product(id=5, name="Pen", description="A blue ink pen", price=1.99, quantity=100),
    Product(id=8, name="Table", description="A wooden table", price=199.99, quantity=20),
]

# // to provide session via dependancy injection to different tasks
def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close()

#  to add the products in the db
def init_db():
    db=session();
    count = db.query(database_models.Product).count
    
    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()
init_db()

# to fetch all products, GET request
@app.get("/products")    #use localhost:8000/docs- for swagger (to execute within an inbuilt ui provided by fastapi)
def get_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return db_products

# to fetch product by id
@app.get("/products/{id}")
def get_product_byID(id:int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return db_product
    return "product not found"

# to add a product, POST request
@app.post("/products")
def add_product(product:Product, db: Session = Depends(get_db)):
    db_product = db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return db_product

# to update a product , PUT request
@app.put("/products")
def update_product(id:int,product:Product,db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name=product.name
        db_product.description=product.description
        db_product.price=product.price
        db_product.quantity=product.quantity
        db.commit()  
        return "Record updated succesfully"
    
    return "Product not found"

# to delete a product , DELETE request
@app.delete("/products")
def delete_product(id:int):
    for i in range(len(products)):
        if products[i].id==id:
            del products[i]
            
            return "Product deleted succesfully"
    
    return "Product not found"