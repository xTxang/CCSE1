from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum, update, Float, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped

Base = declarative_base()

class products(Base):
    """intialise the products table, containing all products on the site"""
    __tablename__ = "products"

    # columns in the table
    productID = Column(Integer, primary_key=True)
    productName = Column(String, nullable=False )
    productCost = Column(Float, nullable = False)
    productImg = Column(String(200), nullable=False)
    productQuant = Column(Integer, nullable=False)



class user(Base):
    """intialise the user table, containing both customers and admins"""
    __tablename__ = "user"

     # columns in the table
    userID = Column(Integer, primary_key=True)
    userName = Column(String, nullable=False )
    userLogin = Column(String(200), nullable=False)
    userPass = Column(String(200), nullable=False)
    userHouse = Column(Integer, nullable=False)
    userStreet = Column(String(200), nullable=False)
    userCity = Column(String(200), nullable=False)
    userPostcode = Column(String(200), nullable=False)
    userType = Column(Integer, nullable = False)


# type 1 or 2(admin or user)


class order(Base):
    """Table of purchased orders by users"""
    __tablename__ = "order"
    orderID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey("user.userID"), nullable=True)
    orderDate = Column(Integer, nullable=True)
    orderQuant = Column(Integer, nullable=True)
    orderPrice = Column(Integer, nullable=True)


    # links products to users

class productOrder(Base):
    __tablename__ = "productOrder"
    orderID = Column(Integer, ForeignKey("order.orderID"), nullable=True)
    productID = Column(Integer, ForeignKey("products.productID"), nullable=True)


    # Defines a composite primary key to keep database normalisation 
    __table_args__ = (
        PrimaryKeyConstraint('orderID', 'productID'),
    )

    # productID, order ID as a composite key


class Database():
    def __init__(self):
        engine = create_engine('sqlite:///database.db')#Creates database with  the name database.db
        # Create all tables
        Base.metadata.create_all(engine)
        self._sessionOpen = sessionmaker(bind=engine)
        # session = Session()#Creates a session instance

        self.new_username = ""
        self.new_password = ""
        # session.commit()#

        # # Query all products from the database
        # session.close()
    def store_username(self, username: str, password: str):
        self.new_password = password
        self.new_username = username
        return f"works: {self.new_password}, {self.new_username}"


    def createUser(self, name, house, street,city,postcode):
        #add admin and hashing etc

        new_user = user(
            userID = 15,
            userName=name,
            userLogin=self.new_username,
            userPass=self.new_password,
            userHouse=house,
            userStreet=street,
            userCity=city,
            userPostcode=postcode,
            userType = 1
        )
        with self._sessionOpen.begin() as session:
            session.add(new_user)


    def search_user(self, enteredUser,enteredPass):
        with self._sessionOpen() as session:
            requestedUser = session.query(user).filter_by(userLogin=enteredUser, userPass=enteredPass).first()


            if requestedUser:
                return requestedUser
            else:
                return None


    def returnProducts(self):   
        with self._sessionOpen() as session:
            self.product_list = session.query(products).all()
        return self.product_list









# class initDb():#Initialises database
#     engine = create_engine('sqlite:///database.db')#Creates database with  the name database.db
#     # Create all tables
#     Base.metadata.create_all(engine)
#     Session = sessionmaker(bind=engine)
#     session = Session()#Creates a session instance
#     if session.query(products).count() == 0:
#         new_product = products(
#             productName="Example Product",
#             productCost=999.99,
#             productImg="example.jpg",
#             productQuant=10
#         )
#         # Add to session and commit
#         session.add(new_product)

    # Add testing data for users
    # users_data = [
    #     user(userName="John Doe", userLogin="john_doe", userPass="password123", userHouse=123,
    #             userStreet="Main St", userCity="Springfield", userPostcode="12345", userType=1),
    #     user(userName="Jane Smith", userLogin="jane_smith", userPass="securepass", userHouse=456,
    #             userStreet="Elm St", userCity="Shelbyville", userPostcode="67890", userType=2)
    # ]
    # session.add_all(users_data)

# Add testing data for orders

    # orders_data = [
    #     order(userID=1, orderDate=20230101, orderQuant=2, orderPrice=1999.98),
    #     order(userID=2, orderDate=20230102, orderQuant=1, orderPrice=99.99)
    # ]
    # session.add_all(orders_data)

# Add testing data for productOrder

    # product_orders_data = [
    #     productOrder(orderID=1, productID=1),
    #     productOrder(orderID=1, productID=2),
    #     productOrder(orderID=2, productID=3)
    # ]
    # session.add_all(product_orders_data)

    
    # session.commit()#

    # # Query all products from the database
    # product_list = session.query(products).all()
    # session.close()
    # #return product_list

    # def createUser(session, name, username, password, house, street, city, postcode, userType):
    #     new_user = user(
    #         userID = 4
    #         userName=name,
    #         userLogin=username,
    #         userPass=password,
    #         userHouse=house,
    #         userStreet=street,
    #         userCity=city,
    #         userPostcode=postcode,
    #         userType = 1 
    #     )
    #     session.add(new_user)



# if __name__ == "__main__":
#     db = Database()

    # for product in product_list:   
    #     print(f"ID: {product.productID}, Name: {product.productName}, Cost: {product.productCost}, Image: {product.productImg}, Quantity: {product.productQuant}")
    # print(product_list)







