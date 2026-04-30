from fastapi import FastAPI
from models import Product
from config import session,engine
import database_models

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

#  to add the products in the db
def init_db():
    db=session();
    for product in products:
        db.add(database_models.Product(**product.model_dump()))
    db.commit()
init_db()

# to fetch all products, GET request
@app.get("/products")    #use localhost:8000/docs- for swagger (to execute within an inbuilt ui provided by fastapi)
def get_products():
    
    #db_connection
    # db = session()
    # #query
    # db.query()
    return products

# to fetch product by id
@app.get("/products/{id}")
def get_product_byID(id:int):
    for product in products:
        if product.id==id:
            return product
    
    return "product not found"

# to add a product, POST request
@app.post("/products")
def add_product(product:Product):
    products.append(product)
    return product

# to update a product , PUT request
@app.put("/products")
def update_product(id:int,product:Product):
    for i in range(len(products)):
        if products[i].id==id:
            products[i]=product
            
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