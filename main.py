from flask import Flask, request, render_template, redirect, url_for
import flask
from database import Database #Imports session and products from database.py to populate the e-commerce
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy 

#TODO add user roles
#TODO add admin roles(use authorisation code to add admin?)


db = Database()# intialises the database object

def numberCheck(word):
    return any(i.isdigit() for i in word)

app = Flask(__name__)



@app.route('/')
# @app.route('/index')
# def index():
#     return render_template('dashboad.html')

def home():
    return render_template('dashboad.html')

from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    
    # session = initDb
    # print(session)
    # print(products)
    # products = session.query(products).all()
    # Render the 'index.html' template, passing the products data
    product_list = db.returnProducts()
    return render_template('shop.html', products=product_list)
   # return render_template('shop.html')  # Fixed "dashboad" typo

# @app.route('/basket')
# def basket():
#     return render_template('basket.html')  # Render the basket template when this route is accessed

# @app.route('/login', methods=['POST'])
# def login():
#     return render_template('login.html')

#     if requrestm


# # @app.route('/login', methods=['POST'])
# # # Function to check entered credentials and provide correct response
# # def login():
# #     # Get entered credentials
# #     action = request.form.get('action')  # Retrieve the value of the clicked button
# #     email = request.form.get('email')
# #     password = request.form.get('password')

# #     if action == 'login':
# #         # Logic for login button
# #         return "You clicked Sign In!"
# #     elif action == 'signup':
# #         # Logic for signup button
# #         return "You clicked Sign Up!"

# #     if 1 == 2:
# #         return render_template('shop.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Render the login form when accessed via GET
        # Handle form submission when accessed via POST
        action = request.form.get('action')  # Retrieve the value of the clicked button
        new_username = request.form.get('username')
        new_password = request.form.get('password')

        if action == 'login':  
            returnedUser = db.search_user(new_username,new_password)
            if returnedUser == None:
                return render_template('login.html', failed_login=True)
            else:
                print('worked')
                userId = returnedUser.userID
                print(userId)
                return redirect(f'/shop/{userId}')

            
            

            #TODO Check if login is in database, then if good, send back to shop page
            return render_template('shop.html')
        elif action == 'signup':

            if len(new_password) < 8 or len(new_username) < 8 or numberCheck(new_password) == False:
                return render_template("login.html", failed_signup=True)
            else:
                db.store_username(new_username, new_password)
                return redirect('/signup')
    return render_template('login.html')

@app.route('/admin', methods=['GET','POST'])#TODO remove get when fully implemented
def adminDash():
    """Basic route for admin functionality, facilitating adding products and editing products"""
    print('test')

    if request.method == "POST":
        action = request.form.get("action")  # Get the button value
        print(f"Action received: {action}")
        if action == "view":
            product_list = db.returnProducts()
            return render_template('adminDash.html', action="view", products=product_list)
        

        elif action == 'remove':#Remove an item
            productId = request.form.get('productID')
            print('This is the product ID:', productId)
            db.removeProduct(productId)
            #TODO add are you sure message
            #TODO add success message
        
        elif action == 'quantity':#Change quantity in stock of item
            productId = request.form.get('productId')
            newQuantity = request.form.get('quantity')
            print(productId)
            print(newQuantity)
            db.changeProductQuant(productId,newQuantity)
            #TODO add frontend success message
        
        elif action == "add":#When admin wants to add a product
            return render_template('adminDash.html', action="add")
        

        elif action == 'submitProduct':
            print('is this working??')
            productName = request.form.get('prodName')
            productCost = request.form.get('prodCost')
            productImg = request.form.get('productImg')
            productQuant = request.form.get('productQuant')

            
            newProductID = db.createProduct(productName,productCost,productImg,productQuant)

            return render_template('adminDash.html', newProductID=newProductID)



                #TODO check if there is an item with the same name?




        

    return render_template('adminDash.html', action = None)

#add produtcs, change prices+stock, remove products



@app.route('/signup', methods=['GET','POST'])
def signup():
    action = request.form.get('action')  # Get the value of the button
    if action == 'submit':
        print('hello')
        name = request.form.get('name')
        houseNum = request.form.get('house')
        street = request.form.get('street')
        city = request.form.get('city')
        postcode = request.form.get('postcode')
        print(name)
        print(houseNum)
        print(street)
        print(city)
        print(postcode)

        db.createUser(name, houseNum, street, city, postcode)
        return redirect('/shop/<userId>')
    return render_template("signup.html")


# @app.route('/shop')
# def shop():
#     #TODO how do i do auth i cant do it

#     return render_template('shop.html')



@app.route('/shop/<userId>', methods = ['GET','POST'])
def userShop(userId):
    print(userId)
    product_list = db.returnProducts()

    if request.method == 'POST':
        print('hello')
        productID = request.form.get('productId')
        quantity = int(request.form.get('quant'))
        if quantity > 2:
            quantity = quantity+1#because the counter starts at 1, it otherwise shows 1 below

        db.addtoBasket(userId, productID, quantity)

        print(productID)
        print(quantity)
        # requestedproductID = request.form.get('')
        # db.addtoBasket()






    return render_template('userShop.html', products=product_list, userId=userId)


@app.route('/logout')
def logout():
    print('hello')
    return redirect('/index')

@app.route('/basket/<userId>')
def basket(userId):#TODO add to the html item is unavailable
    """Redirects to the basket of a specific user when the button is pressed on their webpage"""
    basketItems = db.getBasket(userId)

    for basketItem in basketItems:
        print(basketItem.itemName)
    
    return render_template('basket.html', basketItems=basketItems, userId=userId)

    

if __name__ == '__main__':
    app.run(debug=True)

