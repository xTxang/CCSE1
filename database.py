from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum, update, Float, PrimaryKeyConstraint, Boolean, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Mapped
import os
from hashlib import pbkdf2_hmac#Used for hashing
from aesAlgorithm import AEScipher
from datetime import datetime#for dates of orders

encryption = AEScipher()#Instatiates an AES encryption object


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

class basket(Base):
    """intialise the basket table, containing both customers and admins"""
    __tablename__ = "basket"
    basketID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey("user.userID"), nullable=True)
    productID = Column(Integer, ForeignKey("products.productID"), nullable=True)
    basketQuant = Column(Integer, nullable=False)
    basketPrice = Column(Float, nullable=False)
    itemName = Column(String, nullable=False)
    itemAvailability = Column(Boolean, default = True, nullable=False)



# class user(Base):
#     """intialise the user table, containing both customers and admins"""
#     __tablename__ = "user"

#      # columns in the table
#     userID = Column(String, primary_key=True)#TODO string?
#     userName = Column(String, nullable=False )
#     userLogin = Column(String(200), nullable=False)
#     userPass = Column(String(200), nullable=False)
#     userHouse = Column(Integer, nullable=False)
#     userStreet = Column(String(200), nullable=False)
#     userCity = Column(String(200), nullable=False)
#     userPostcode = Column(String(200), nullable=False)
#     salt = Column(String, nullable = False)
#     userType = Column(Integer, nullable = False)

class user(Base):
    """intialise the user table, containing both customers and admins"""
    __tablename__ = "user"

        # columns in the table
    userID = Column(Integer, primary_key=True)#TODO string?
    userName = Column(String, nullable=False )
    userLogin = Column(String, nullable=False)
    userPass = Column(String, nullable=False)
    userHouse = Column(String, nullable=False)
    userStreet = Column(String, nullable=False)
    userCity = Column(String, nullable=False)
    userPostcode = Column(String, nullable=False)
    salt = Column(String, nullable = False)
    userType = Column(Integer, nullable = False)


# type 1 or 2(admin or user)


class order(Base):
    """Table of purchased orders by users"""
    __tablename__ = "order"
    orderID = Column(Integer, primary_key=True)
    userID = Column(String, ForeignKey("user.userID"), nullable=True)
    orderDate = Column(Integer, nullable=True)
    orderQuant = Column(Integer, nullable=True)
    orderPrice = Column(Integer, nullable=True)


    # links products to users

class productOrder(Base):
    """Table to link products and order to ensure databasse normalisation"""
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
        self.engine = create_engine('sqlite:///database.db')#Creates database with  the name database.db
        # Create all tables
        Base.metadata.create_all(self.engine)
        self._sessionOpen = sessionmaker(bind=self.engine)
        # session = Session()#Creates a session instance
        # session.commit()#

        # # Query all products from the database
        # session.close()
        # salt = os.urandom(16)

        # new_user = user(
        #     userID = 1,
        #     userName= self.encryptData('AdminUser'),
        #     userLogin=self.encryptData('Admin'), 
        #     userPass=self.passwordHash('Admin1', salt),#already hashed, doesn't need to be encrypted
        #     userHouse=self.encryptData('test'),
        #     userStreet=self.encryptData('test'),
        #     userCity=self.encryptData('test'),
        #     userPostcode=self.encryptData('test'),
        #     salt = salt,
        #     userType = 2
        # )
        # with self._sessionOpen.begin() as session:
        #     session.add(new_user)



        # adminImplement = user(
        #     userID = 1,
        #     userName = 'AdminUser',
        #     userLogin = 'Admin',
        #     userPass = 'Admin1',
        #     userHouse = 'test',
        #     userStreet = 'test',
        #     userCity = 'test',
        #     userPostcode = 'test',
        #     salt = 'test',
        #     userType = 2
        # )
        # with self._sessionOpen.begin() as session:

        #     session.add(new_user)


    def createUser(self, username,password,name, house, street,city,postcode):
        """Creates a user and adds them to the database and hashes password"""
        #add admin and hashing etc

        salt = os.urandom(16)
        hashedPassword = self.passwordHash(password, salt)

        # try:
        #     self.setuserId = self.setuserId + 1
        # except AttributeError:
        #     self.setuserId = 1
        with self._sessionOpen() as session:
            highestUID = session.query(func.max(user.userID)).scalar()#Used to find the highest user id in the table, increments by 1 for next ID
        print(highestUID)
        self.setuserId = highestUID + 1




        new_user = user(
            userID = self.setuserId,
            userName= self.encryptData(name),
            userLogin=self.encryptData(username), 
            userPass=hashedPassword,#already hashed, doesn't need to be encrypted
            userHouse=self.encryptData(house),
            userStreet=self.encryptData(street),
            userCity=self.encryptData(city),
            userPostcode=self.encryptData(postcode),
            salt = salt,
            userType = 1
        )
        with self._sessionOpen.begin() as session:
            session.add(new_user)

        return self.setuserId#returns the ID of user created


     
    def passwordHash(self, password: str, salt: bytes) -> bytes:
        """Hashes entered user password with a salt, returns to be stored in database"""
        return pbkdf2_hmac("sha512", bytes(password, "utf-8"), salt, 500000)#Hashes password with sha512 algorithm

    def createProduct(self,productName,productCost,productImg,productQuant):

        try:    
            self.x = self.x + 1 
        except AttributeError:
            self.x = 1

        print(self.x)
        newProduct = products(
            productID = self.x,
            productName = productName,
            productCost = productCost,
            productImg = productImg,
            productQuant = productQuant
        )

        with self._sessionOpen.begin() as session:
            session.add(newProduct)
        return self.x


    def search_user(self, enteredUser,enteredPass):
        with self._sessionOpen() as session:
            requestedUser = session.query(user).filter_by(userLogin=enteredUser, userPass=enteredPass).first()
            if requestedUser:
                return requestedUser
            else:
                return None
            
    def finduserfromEmail(self,email):
        """Login functionality, retrieves email and encrypts it to compare against user table"""
        encryptedEmail = self.encryptData(email)
        print(encryptedEmail)
        with self._sessionOpen() as session:
            matchingUser = session.query(user).filter_by(userLogin = encryptedEmail).first()
        return matchingUser
        
            
    def getproductfromID(self, ID):
        """Used to retrieve user data from user id, in order for user specific pages"""
        with self._sessionOpen() as session:
            self.product_list = session.query(products).filter_by(userID=ID).first()     
        return self.product_list
    
    def getuserfromID(self, ID):
        """Used to retrieve user data from user id, in order for user specific pages"""
        with self._sessionOpen() as session:
            self.user = session.query(user).filter_by(userID=ID).first()     
        return self.user

    def returnProducts(self): 
        """Returns all products in the database"""  
        with self._sessionOpen() as session:
            self.product_list = session.query(products).all()

        return self.product_list
    

    def addtoBasket(self, userId, productId, quantity):
        """adds an item from the shop page to a specific user's basket"""
        with self._sessionOpen.begin() as session:#creataes an entry into the basket table
            basketItem = session.query(basket).filter_by(userID=userId, productID=productId).first()#Used to check if item is already in basket

            product = session.query(products).filter_by(productID=productId).first()#Retrieve product by comparing id, used to check total in stock and price

            totalPrice = quantity * product.productCost

            if quantity > product.productQuant:#there is not enough stock
                return False

            if basketItem:#if item is already in basket adds the extra amount
                basketItem.basketQuant = basket.basketQuant + quantity
                basketItem.basketPrice = basket.basketPrice + totalPrice

            else:#item is not in basket already, adds it
              basketItem = basket(
                  userID = userId,
                  productID = productId,
                  basketQuant = quantity,
                  basketPrice = totalPrice,
                  itemName = product.productName
              )
            session.add(basketItem)

    def getBasket(self,userId):
        """Runs when the basket page of a user is opened, finding all items added items linked to their ID"""
        print(userId)
        with self._sessionOpen() as session:
            self.basketItems = session.query(basket).filter_by(userID = userId).all()

        return self.basketItems


    def removeProduct(self, productId):
        """Finds item to remove via product id, removes from database"""

        with self._sessionOpen() as session:#Finds product via id, deletes and commits changes
            product = session.query(products).filter_by(productID=productId).first()

            iteminBasket = session.query(basket).filter_by(productID = productId).all()#If the item has been removed by an admin, adds unavailable

            if iteminBasket:#Checks if item is in basket, iterates through and sets availability as False
                for item in iteminBasket:
                    item.itemAvailability = False
            else:#The product is not in the basket of a user, no action needs to be taken
                pass

            print(product)
            session.delete(product)
            session.commit() 





    def changeProductQuant(self,productId,newQuant):
        """Changes quantity in stock of an item"""

        with self._sessionOpen() as session:#Finds product via id, changes quantity field
            product = session.query(products).filter_by(productID=productId).first()
            product.productQuant = newQuant
            print(product.productQuant)
            session.commit()



    def encryptData(self, data):
        """used to encrypt data before it is added to the database"""
        encryptedData = encryption.encrypt(data)
        return encryptedData

    def decryptData(self, datatoDecrypt):
        #TODO for fields in object decrpyt maybe?
        """This function iterates through entries and decrypts them for use"""
        decryptedData = encryption.decryt(datatoDecrypt)
        
        return decryptedData   
    

    def decryptUser(self, userId):
        """Finds a user via their ID, decrypts the relevant information and sends it back"""
        with self._sessionOpen() as session:#Finds product via id, deletes and commits changes
            foundUser = session.query(user).filter_by(userID=userId).first()
        print(foundUser.userName)
        name = encryption.decrypt(foundUser.userName)
        login = encryption.decrypt(foundUser.userLogin)
        houseNum = encryption.decrypt(foundUser.userHouse) 
        street =  encryption.decrypt(foundUser.userStreet)
        city =  encryption.decrypt(foundUser.userCity)
        postcode =  encryption.decrypt(foundUser.userPostcode)
        return name, login, houseNum, street, city, postcode
    

    def addOrder(self,basketItems):
        """Adds the items in the basket to the order table after checkout"""


        with self._sessionOpen() as session:
            # Iterate through basket items
            for item in basketItems:
                try:#Finds highest order ID
                    highestOID = session.query(func.max(order.orderID)).scalar()#Used to find the highest user id in the table, increments by 1 for next ID
                    self.setorderId = highestOID + 1
                except TypeError:#No orderID yet
                    self.setorderId = 1




                # Add item to the orders table
                new_order = order(
                    orderID = self.setorderId,
                    userID = item.userID,
                    orderDate = datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f"),
                    orderQuant = item.basketQuant,
                    orderPrice = item.basketPrice 
                )
                session.add(new_order)

                new_product_order = productOrder(
                    orderID = self.setorderId,
                    productID = item.productID
                )#adds to product order table
                
                session.add(new_product_order)
                # Remove item from the basket table

                # Update the product quantity in the product table
                product = session.query(product).filter_by(productID=item.productID).one_or_none()
                if product:
                    if product.productQuant >= item.basketQuant:
                        product.productQuant -= item.basketQuant
                else:#Should already check in basket
                    raise ValueError(f"Not enough stock for productID {item.productID}. Current stock: {product.productQuant}")#TODO
                session.delete(item)

            # Commit changes to the database
            session.commit()
    

    def changeAddress(self,userId,houseNum,street,city,postcode):
        """Used to change a users address"""

        # changeUser = self.getuserfromID(userId)
        with self._sessionOpen() as session:
            changeUser = session.query(user).filter_by(userID=userId).first()#This needs to be done without the getuserfromID methods, otherwise it detatches the object
            changeUser.userHouse = self.encryptData(houseNum)
            changeUser.userStreet = self.encryptData(street)
            changeUser.userCity = self.encryptData(city)
            changeUser.userPostcode = self.encryptData(postcode)
            print(changeUser.userPostcode)
 
            session.commit()
    
    def changeEmail(self,userId,email):
        """Used to change a users email"""
        with self._sessionOpen() as session:
            changeUser = session.query(user).filter_by(userID=userId).first()
            changeUser.userLogin = self.encryptData(email)
            session.commit()


    def changePassword(self,userId,newPassword):
        """Used to change a users password"""
        print('inFunc')
        with self._sessionOpen() as session:
            changeUser = session.query(user).filter_by(userID=userId).first()

            hashedPassword = self.passwordHash(newPassword, changeUser.salt)

            changeUser.userPass = hashedPassword


            session.commit()













        # If needed, you can return more detailed product information by joining with the products table










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







