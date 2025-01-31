from flask import Flask, request, render_template, redirect
import flask
from database import Database #Imports session and products from database.py to populate the e-commerce

import os
#for files https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
from werkzeug.utils import secure_filename
from flask_limiter import Limiter#Used to limit logins for brute force attacks
from flask_limiter.util import get_remote_address

UPLOAD_FOLDER = 'static\CSS\images'


db = Database()# intialises the database object
def numberCheck(word):
    """Checks if password contains a digit """
    return any(i.isdigit() for i in word)

app = Flask(__name__)
key_bytes = os.urandom(16)#creates bytes for key
app.secret_key = key_bytes.hex()#key for session
limiter = Limiter(get_remote_address, app=app)#Limiter for brute force attacks.

app.config['uploadFolder'] = UPLOAD_FOLDER#Defines where images will be saved

#Mitigates against session hijacking
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

@app.route('/')
@app.route('/index', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'submit':

            product_list = db.returnProducts()

            return render_template('shop.html',products=product_list)

    product_list = db.returnProducts()
    return render_template('shop.html', products=product_list)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit('5/minute') #Limits login to 5 requests per minute to aid against brute force attacks
def login():
    if request.method == 'POST':
        action = request.form.get('action')  # Retrieves the value of the clicked button
        new_username = request.form.get('username')
        new_password = request.form.get('password')

        if action == 'login':#To see if user is correct, password is hashed and compared      
            #First, username is encrypted and compared against the database
            returnedUser = db.finduserfromEmail(new_username)
            if returnedUser == None:
                return render_template('login.html', failed_login=True)
            
            elif returnedUser.userPass == db.passwordHash(new_password,returnedUser.salt):#if password is correct
                userId = returnedUser.userID
                flask.session['role'] = userId # Creates a flask session with the role, stops users accessing unauthorised pages
                if returnedUser.userType == 1:#Customer
                    return redirect(f'/shop/{userId}')   
                     
                elif returnedUser.userType == 2:#Admin
                    return redirect('/admin')
                
            elif db.passwordHash(new_password,returnedUser.salt) != returnedUser.userPass:#If password is incorrect  
                return render_template('login.html', failed_login=True)
    return render_template('login.html')

@app.route('/admin', methods=['GET','POST'])
def adminDash():
    """Basic route for admin functionality, facilitating adding products and editing products"""
    try:#Session authentication 
        adminCheck = db.getuserfromID(flask.session['role'])
    except KeyError:
        return redirect('/index')

    if adminCheck.userType !=  2:#checks if user is an admin
        return redirect('/index')
    if request.method == "POST":
        action = request.form.get("action")  # Get the button value

        product_list = db.returnProducts()
        if action == "view":#View products action
            return render_template('adminDash.html', action="view", products=product_list)
        

        elif action == 'remove':#Remove an item
            productId = request.form.get('productID')
            db.removeProduct(productId)
        
        elif action == 'quantity':#Open change quantity box
            return render_template('admindash.html', action = 'view', quantity = True,products=product_list)

        elif action == 'submitQuantity':#Allows admin to change quantity
            productId = request.form.get('productID')
            newQuantity = request.form.get('quantity')
            db.changeProductQuant(productId,newQuantity)


        elif action == 'price':#Opens price change box
            return render_template('admindash.html', action = 'view',price = True,products=product_list)

        
        elif action == 'submitPrice':#Changes price of a product
            productId = request.form.get('productID')
            newPrice = request.form.get('priceVal')
            db.changeproductPrice(productId, newPrice)
           
        
        elif action == "add":#When admin wants to add a product
            return render_template('adminDash.html', action="add")
        

        elif action == 'submitProduct':#Retrieves product information when submitted
            productName = request.form.get('prodName')
            productCost = request.form.get('prodCost')
            file = request.files['productImg']
            productQuant = request.form.get('productQuant')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['uploadFolder'], filename))
            productImg = filename
            newProductID = db.createProduct(productName,productCost,productImg,productQuant)

            return render_template('adminDash.html', newProductID=newProductID)
    return render_template('adminDash.html', action = None)



@app.route('/signup', methods=['GET','POST'])
def signup():
    action = request.form.get('action')  # Gets the value of the button
    if action == 'submit':
        inputtedUsername = request.form.get('username')
        inputtedPassword = request.form.get('password')
        name = request.form.get('name')
        houseNum = request.form.get('house')
        street = request.form.get('street')
        city = request.form.get('city')
        postcode = request.form.get('postcode')#Retrieve info from signup

        if len(inputtedPassword) < 8 or len(inputtedUsername) < 8 or numberCheck(inputtedPassword) == False:#Check email and password requriements
            return render_template('signup.html', failed_signup=True)      
        else:#Creates either an admin or user
            result,userType = db.createUser(inputtedUsername,inputtedPassword,name, houseNum, street, city, postcode)
            print(userType)

            if result == True:#if email is already in use
                return render_template('signup.html', inUse = True)
            else:
                userId =  result
                flask.session['role'] = userId
                if userType == 2:#Redirects user to either admin or customer dashboard
                    return redirect('/admin') 
                elif userType == 1:
                    return redirect(f'/shop/{userId}')
    return render_template("signup.html")


@app.route('/shop/<userId>', methods = ['GET','POST'])
def userShop(userId):
    try:#Session authentication
        if flask.session['role'] != int(userId):
            return redirect('/index')
    except KeyError:
        return redirect('/index')

    #Gets the user's name and products to display on the HTML
    product_list = db.returnProducts()
    unencryptedName  = db.decryptUser(userId)

    if request.method == 'POST':
        productID = request.form.get('productId')
        quantity = int(request.form.get('quant'))
        if quantity > 2:#Quantity counter starts at 0, so 1 is added for the requested quantity
            quantity = quantity+1
        db.addtoBasket(userId, productID, quantity)



    return render_template('userShop.html', products=product_list, userId=userId,unencryptedName=unencryptedName[0])

@app.route('/checkout/<userId>', methods=['POST'])
def checkout(userId):
    try:
        if flask.session['role'] != int(userId):
            return redirect('/index')
    except KeyError:
        return redirect('/index')
    
    action = request.form.get('action')
    basketItems = db.getBasket(userId)
    if action == 'submit':
        cardNumber = request.form.get('cardNum')
        expiryDate = request.form.get('expiryDate')
        CVV = request.form.get('CVV')  
        db.addOrder(basketItems) 
        return render_template('checkout.html', paid=True,userId=userId)
    return render_template('checkout.html', basketItems=basketItems,userId=userId,paid = False)


@app.route('/userDash/<userId>',methods = ['GET','POST'])
def userDash(userId):
    """Allows for alteration of user details and viewing of invoices"""
    try:#Session authentication

        if flask.session['role'] != int(userId):
            return redirect('/index')
    except KeyError:
        return redirect('/index')

    action = request.form.get('action')
    if action == 'invoice':#Returns invoices
        returnedOrder = db.getOrder(userId)
        return render_template('userdash.html', userId = userId, returnedOrder=returnedOrder, invoice = True)
    
    elif action == 'infoChange':#Returns the options to change information(address, email, password)
        return render_template('userDash.html', userId = userId, info = True)

    elif action == 'address':#Allows user to enter new address information
        return render_template('userDash.html', userId = userId, addressChange = True)

    elif action == 'password':#Allows user to enter new password
        return render_template('userDash.html', userId = userId, passwordChange = True)
    
    elif action == 'email':#Allows user to enter new email
        return render_template('userDash.html', userId = userId, emailChange = True)
    
    elif action == 'submitAddress':#Changes the user's address information
        houseNum = request.form.get('house')
        street = request.form.get('street')
        city = request.form.get('city')
        postcode = request.form.get('postcode')
        db.changeAddress(userId,houseNum,street,city,postcode)

    elif action == 'submitEmail':#Changes the user's email
        email = request.form.get('email')
        db.changeEmail(userId,email)

    elif action == 'submitPassword':#Changes user's password
        returnedUser = db.getuserfromID(userId)#Gets user
        oldPassword = request.form.get('oldPassword')
        newPassword = request.form.get('newPassword')
        if db.passwordHash(oldPassword,returnedUser.salt) != returnedUser.userPass:#Hashes the password and compares it
            return render_template('userDash.html',failedLogin = True)
        elif numberCheck(newPassword) == False or len(newPassword) < 8:#Ensures password has a number and is longer than 8 digits
            return render_template('userDash.html',failedLogin = True)
        else:
            db.changePassword(userId, newPassword)#
            return render_template('userDash.html',successLogin = True)
    return render_template('userDash.html', userId = userId)

@app.route('/logout')
def logout():
    flask.session.pop('role',None)#Removes role when a user logs out
    return redirect('/index')

@app.route('/basket/<userId>', methods = ['GET','POST'])
def basket(userId):
    """Redirects to the basket of a specific user when the button is pressed on their webpage"""
    try:
        if flask.session['role'] != int(userId):
            return redirect('/index')
    except KeyError:
        return redirect('/index')
    
    if request.method == "POST":

        basketID = request.form.get('basketID')
        db.removefromBasket(basketID)

    basketItems = db.getBasket(userId)
    totalPrice = sum((item.basketPrice * item.basketQuant) for item, _ in basketItems)#Calculates price dynamically

    return render_template('basket.html', basketItems=basketItems, userId=userId, totalPrice=totalPrice)

    
if __name__ == '__main__':
    app.run(ssl_context='adhoc')
