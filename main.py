from flask import Flask, request, render_template, redirect, url_for
import flask
from database import Database #Imports session and products from database.py to populate the e-commerce
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy 
import os



#TODO add user roles
#TODO add admin roles(use authorisation code to add admin?)


db = Database()# intialises the database object

def numberCheck(word):
    """Checks if password contains a digit """
    return any(i.isdigit() for i in word)

app = Flask(__name__)
key_bytes = os.urandom(16)#creates bytes for key
app.secret_key = key_bytes.hex()#key for session
print(app.secret_key)

@app.route('/')
@app.route('/index', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        print('post')

        action = request.form.get('action')
        if action == 'submit':
            print('button is pressed')
            product_list = db.returnProducts()

            return render_template('shop.html',products=product_list,alert=True)

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

        if action == 'login':#To see if user is correct, password is hashed and compared
            
            #First, username is encrypted and compared against the database
            print(new_username)
            returnedUser = db.finduserfromEmail(new_username)
            print(returnedUser.userName)
            print(returnedUser)
            # hashedPassword = db.passwordHash(new_password,returnedUser.salt)#Hashes password with salt

            if returnedUser == None:
                return render_template('login.html', failed_login=True)
            elif returnedUser.userPass == db.passwordHash(new_password,returnedUser.salt):#if password is correct
                userId = returnedUser.userID
                print(flask.session)

                flask.session['role'] = userId # Creates a flask session with the role, stops users accessing unauthorised pages
                #Checks if user is an admin or customer
                if returnedUser.userType == 1:#Customer
                    return redirect(f'/shop/{userId}')

                
                elif returnedUser.userType == 2:#Admin
                    return redirect('/admin')
    
            elif db.passwordHash(new_password,returnedUser.salt) != returnedUser.userPass:#If password is incorrect
                return render_template('login.html', failed_login=True)
                #TODO add amount of times to stop brute force attacks



            # else:
            #     print('worked')
            #     userId = returnedUser.userID
            #     print(userId)
            #     #TODO
            #     #fetch from db
            #     # flask.session['role'] == userType
            #     #if 1, go to user
            #     #if 2 go to admin
            #     return redirect(f'/shop/{userId}')

            
            

        #     return render_template('shop.html')
        # elif action == 'signup':

        #     if len(new_password) < 8 or len(new_username) < 8 or numberCheck(new_password) == False:
        #         return render_template("login.html", failed_signup=True)
        #     else:
        #         db.store_username(new_username, new_password)
        #         return redirect('/signup')
    return render_template('login.html')

@app.route('/admin', methods=['GET','POST'])#TODO remove get when fully implemented
def adminDash():
    """Basic route for admin functionality, facilitating adding products and editing products"""
    try:
        adminCheck = db.getuserfromID(flask.session['role'])
    except KeyError:
        return redirect('/index')

    if adminCheck.userType !=  2:#checks if user is an admin
        return redirect('/index')
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
            productName = request.form.get('prodName')
            productCost = request.form.get('prodCost')
            productImg = request.form.get('productImg')
            productQuant = request.form.get('productQuant')

            # try:#This increments product ID by 1 for the new product :) TODO, must be a better way to do this(leads to gaps when items are removed?)
            #     x = x + 1
            # except NameError:
            #     x = 1

            
            newProductID = db.createProduct(productName,productCost,productImg,productQuant)

            return render_template('adminDash.html', newProductID=newProductID)



                #TODO check if there is an item with the same name?

    return render_template('adminDash.html', action = None)

#add produtcs, change prices+stock, remove products



@app.route('/signup', methods=['GET','POST'])
def signup():
    action = request.form.get('action')  # Get the value of the button
    if action == 'submit':
        inputtedUsername = request.form.get('username')
        inputtedPassword = request.form.get('password')
        name = request.form.get('name')
        houseNum = request.form.get('house')
        street = request.form.get('street')
        city = request.form.get('city')
        postcode = request.form.get('postcode')


        if len(inputtedPassword) < 8 or len(inputtedUsername) < 8 or numberCheck(inputtedPassword) == False:
            return render_template('signup.html', failed_signup=True)      
        else:

            userId = db.createUser(inputtedUsername,inputtedPassword,name, houseNum, street, city, postcode)

            flask.session['role'] = userId
            return redirect(f'/shop/<userId>')

    return render_template("signup.html")


# @app.route('/shop')
# def shop():
#     #TODO how do i do auth i cant do it

#     return render_template('shop.html')



@app.route('/shop/<userId>', methods = ['GET','POST'])
def userShop(userId):
    if flask.session['role'] != int(userId):#if user attempts to access an unauthorised path
        return redirect('/index')#TODO  keyerror

    product_list = db.returnProducts()
    unencryptedName  = db.decryptUser(userId)


    if request.method == 'POST':
        print('hello')
        productID = request.form.get('productId')
        quantity = int(request.form.get('quant'))
        if quantity > 2:#TODO this makes no fucking sense
            quantity = quantity+1#because the counter starts at 1, it otherwise shows 1 below
        db.addtoBasket(userId, productID, quantity)



        print(productID)
        print(quantity)
        # requestedproductID = request.form.get('')
        # db.addtoBasket()

    return render_template('userShop.html', products=product_list, userId=userId,unencryptedName=unencryptedName[0])

@app.route('/checkout/<userId>', methods=['POST'])#TODO the checkout logic
def checkout(userId):
    action = request.form.get('action')
    basketItems = db.getBasket(userId)
    if action == 'submit':
        cardNumber = request.form.get('cardNum')#TODO card info?
        expiryDate = request.form.get('expiryDate')
        CVV = request.form.get('CVV')

        
        db.addOrder(basketItems)
        #TODO decrease item amount

        return render_template('checkout.html', paid=True)


        

    return render_template('checkout.html', basketItems=basketItems,userId=userId,paid = False)


@app.route('/userDash/<userId>',methods = ['GET','POST'])
def userDash(userId):#TODO session auth
    """Allows for alteration of user details and viewing of invoices"""
    action = request.form.get('action')
    if action == 'invoice':

        returnedOrder = db.getOrder(userId)
        print(returnedOrder)
        for order in returnedOrder:
            print('==========================')
            print(f"Order ID: {order[0]}, Date: {order[1]}, Price: {order[2]}, Quantity: {order[3]}, Product: {order[4]}")
        return render_template('userdash.html', userId = userId, returnedOrder=returnedOrder, invoice = True)

    
    elif action == 'infoChange':
        return render_template('userDash.html', userId = userId, info = True)

    elif action == 'address':#Change address

        return render_template('userDash.html', userId = userId, addressChange = True)

    elif action == 'password':#Change password
        return render_template('userDash.html', userId = userId, passwordChange = True)
    
    elif action == 'email':#Change email
        return render_template('userDash.html', userId = userId, emailChange = True)
    

    elif action == 'submitAddress':
        houseNum = request.form.get('house')
        street = request.form.get('street')
        city = request.form.get('city')
        postcode = request.form.get('postcode')
        print('Checkpoint 1')
        db.changeAddress(userId,houseNum,street,city,postcode)

    elif action == 'submitEmail':
        email = request.form.get('email')
        db.changeEmail(userId,email)

    elif action == 'submitPassword':
        returnedUser = db.getuserfromID(userId)#Gets user
        oldPassword = request.form.get('oldPassword')
        newPassword = request.form.get('newPassword')
        if db.passwordHash(oldPassword,returnedUser.salt) != returnedUser.userPass:
            return render_template('userDash.html',failedLogin = True)
        elif numberCheck(newPassword) == False or len(newPassword) < 8:
            return render_template('userDash.html',failedLogin = True)
        else:
            db.changePassword(userId, newPassword)
            return render_template('userDash.html',successLogin = True)
        



    return render_template('userDash.html', userId = userId)

@app.route('/logout')
def logout():
    print('hello')
    return redirect('/index')

@app.route('/basket/<userId>')
def basket(userId):#TODO add to the html item is unavailable
    """Redirects to the basket of a specific user when the button is pressed on their webpage"""
    basketItems = db.getBasket(userId)


    totalPrice = sum(item.basketPrice for item in basketItems)

    for item in basketItems:#Checks if there is enough quantity in stock
        product = db.getproductfromID(item.productID)
        if product.productQuant < item.orderQuant:
            return render_template('basket.html')#TODO fix, make the product page have a limit on quantity 

    
    return render_template('basket.html', basketItems=basketItems, userId=userId, totalPrice=totalPrice)

    

if __name__ == '__main__':
    app.run(debug=True)

