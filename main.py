from flask import Flask, request, render_template, redirect
import flask
from database import Database
from flask_wtf.csrf import CSRFProtect, validate_csrf # generate_csrf is imported later
from flask_wtf import FlaskForm
# from wtforms import CSRFTokenField


import os
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

UPLOAD_FOLDER = 'static\CSS\images'

db = Database()

def numberCheck(word):
    """Checks if password contains a digit """
    return any(i.isdigit() for i in word)

app = Flask(__name__)



SECRET_KEY_FROM_ENV = os.environ.get('SECRET_KEY')

if SECRET_KEY_FROM_ENV:
    app.secret_key = SECRET_KEY_FROM_ENV
else:
    print("WARNING: SECRET_KEY environment variable not set. Using a dynamic key for local development.")
    app.secret_key = os.urandom(24).hex()

# Initialize CSRF protection
csrf = CSRFProtect(app)

limiter = Limiter(get_remote_address, app=app)
app.config['uploadFolder'] = UPLOAD_FOLDER

# Mitigates against session hijacking
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True


@app.after_request
def add_security_headers(response):
    # Content Security Policy
    csp_policy = (
        "default-src 'self'; "  # By default, only allow resources from the same origin
        "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; " # Allow stylesheets from self, Google Fonts, and inline styles
        "font-src 'self' https://fonts.gstatic.com; " # Allow fonts from self and Google Fonts
        "img-src 'self' data:; " 
        "script-src 'self'; "
        "object-src 'none'; " # Disallow plugins
        "base-uri 'self'; "  
        "form-action 'self';" 
        "frame-ancestors 'self';" 

    )
    response.headers['Content-Security-Policy'] = csp_policy

    #X-Frame-Options for legacy support
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    response.headers['X-Content-Type-Options'] = 'nosniff'


    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'


    return response



from flask_wtf.csrf import generate_csrf 


# Make CSRF token available in all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

@app.route('/')
@app.route('/index', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        # Validate CSRF token for POST requests
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            return render_template('shop.html', csrf_error=True), 400
            
        action = request.form.get('action')
        if action == 'submit':
            product_list = db.returnProducts()
            return render_template('shop.html',products=product_list)

    product_list = db.returnProducts()
    return render_template('shop.html', products=product_list)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit('5/minute')
def login():
    if request.method == 'POST':
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            return render_template('login.html', csrf_error=True), 400
            
        action = request.form.get('action')
        new_username = request.form.get('username')
        new_password = request.form.get('password')

        if action == 'login':
            returnedUser = db.finduserfromEmail(new_username)
            if returnedUser == None:
                return render_template('login.html', failed_login=True)
            
            elif returnedUser.userPass == db.passwordHash(new_password,returnedUser.salt):
                userId = returnedUser.userID
                flask.session['role'] = userId
                if returnedUser.userType == 1:
                    return redirect(f'/shop/{userId}')   
                elif returnedUser.userType == 2:
                    return redirect('/admin')
                
            elif db.passwordHash(new_password,returnedUser.salt) != returnedUser.userPass:
                return render_template('login.html', failed_login=True)
    return render_template('login.html')

@app.route('/admin', methods=['GET','POST'])
def adminDash():
    try:
        adminCheck = db.getuserfromID(flask.session['role'])
    except KeyError:
        return redirect('/index')

    if adminCheck.userType != 2:
        return redirect('/index')
        
    if request.method == "POST":
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            return render_template('adminDash.html', csrf_error=True), 400
            
        action = request.form.get("action")
        product_list = db.returnProducts()
        
        if action == "view":
            return render_template('adminDash.html', action="view", products=product_list)
        elif action == 'remove':
            productId = request.form.get('productID')
            db.removeProduct(productId)
        elif action == 'quantity':
            return render_template('admindash.html', action = 'view', quantity = True,products=product_list)
        elif action == 'submitQuantity':
            productId = request.form.get('productID')
            newQuantity = request.form.get('quantity')
            db.changeProductQuant(productId,newQuantity)
        elif action == 'price':
            return render_template('admindash.html', action = 'view',price = True,products=product_list)
        elif action == 'submitPrice':
            productId = request.form.get('productID')
            newPrice = request.form.get('priceVal')
            db.changeproductPrice(productId, newPrice)
        elif action == "add":
            return render_template('adminDash.html', action="add")
        elif action == 'submitProduct':
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
    if request.method == 'POST':
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            return render_template('signup.html', csrf_error=True), 400
            
        action = request.form.get('action')
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
                result,userType = db.createUser(inputtedUsername,inputtedPassword,name, houseNum, street, city, postcode)
                if result == True: # Assuming True means email in use
                    return render_template('signup.html', inUse = True)
                else:
                    userId = result
                    flask.session['role'] = userId
                    if userType == 2:
                        return redirect('/admin') 
                    elif userType == 1:
                        return redirect(f'/shop/{userId}')
    return render_template("signup.html")


@app.route('/shop/<userId>', methods = ['GET','POST'])
def userShop(userId):
    try:
        if flask.session['role'] != int(userId):
            return redirect('/index')
    except KeyError:
        return redirect('/index')

    product_list = db.returnProducts()
    decrypted_user_info  = db.decryptUser(userId) # Assuming db.decryptUser returns a tuple/list with name at index 0
    unencryptedName = decrypted_user_info[0] if decrypted_user_info else "User"


    if request.method == 'POST':
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            return render_template('userShop.html', products=product_list, userId=userId, unencryptedName=unencryptedName, csrf_error=True), 400
            
        productID = request.form.get('productId')
        quantity = int(request.form.get('quant'))
        # The logic for quantity > 2 seems unusual, usually max is handled by input or direct use.
        # Keeping it as is from your original code.
        if quantity > 2: 
            quantity = quantity+1
        db.addtoBasket(userId, productID, quantity)

    return render_template('userShop.html', products=product_list, userId=userId,unencryptedName=unencryptedName)

@app.route('/checkout/<userId>', methods=['POST']) # This route only accepts POST
def checkout(userId):
    try:
        if flask.session['role'] != int(userId):
            return redirect('/index')
    except KeyError:
        return redirect('/index')
    
    # Since this route is POST only, CSRF validation should happen right away.
    # If it's reached via a GET, it would be a 405 Method Not Allowed by default.
    # Assuming the form submission to this route is POST.
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        basketItems = db.getBasket(userId) # Need this for rendering template on error
        return render_template('checkout.html', basketItems=basketItems, userId=userId, paid=False, csrf_error=True), 400
    
    action = request.form.get('action') # This might always be 'submit' if only one button
    basketItems = db.getBasket(userId)
    if action == 'submit': # Or simply proceed if validation passed and it's a POST
        cardNumber = request.form.get('cardNum')
        expiryDate = request.form.get('expiryDate')
        CVV = request.form.get('CVV')  
        db.addOrder(basketItems) 
        return render_template('checkout.html', paid=True,userId=userId)
    
    # Fallback if action wasn't 'submit' but validation passed (should not happen with current HTML)
    return render_template('checkout.html', basketItems=basketItems,userId=userId,paid = False)


@app.route('/userDash/<userId>',methods = ['GET','POST'])
def userDash(userId):
    try:
        if flask.session['role'] != int(userId):
            return redirect('/index')
    except KeyError:
        return redirect('/index')

    if request.method == 'POST':
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            return render_template('userDash.html', userId=userId, csrf_error=True), 400

    action = request.form.get('action')
    if action == 'invoice':
        returnedOrder = db.getOrder(userId)
        return render_template('userdash.html', userId = userId, returnedOrder=returnedOrder, invoice = True)
    elif action == 'infoChange':
        return render_template('userDash.html', userId = userId, info = True)
    elif action == 'address':
        return render_template('userDash.html', userId = userId, addressChange = True)
    elif action == 'password':
        return render_template('userDash.html', userId = userId, passwordChange = True)
    elif action == 'email':
        return render_template('userDash.html', userId = userId, emailChange = True)
    elif action == 'submitAddress':
        houseNum = request.form.get('house')
        street = request.form.get('street')
        city = request.form.get('city')
        postcode = request.form.get('postcode')
        db.changeAddress(userId,houseNum,street,city,postcode)
    elif action == 'submitEmail':
        email = request.form.get('email')
        db.changeEmail(userId,email)
    elif action == 'submitPassword':
        returnedUser = db.getuserfromID(userId)
        oldPassword = request.form.get('oldPassword')
        newPassword = request.form.get('newPassword')
        if db.passwordHash(oldPassword,returnedUser.salt) != returnedUser.userPass:
            return render_template('userDash.html',failedLogin = True, userId=userId) # Added userId
        elif numberCheck(newPassword) == False or len(newPassword) < 8:
            return render_template('userDash.html',failedLogin = True, userId=userId) # Added userId
        else:
            db.changePassword(userId, newPassword)
            return render_template('userDash.html',successLogin = True, userId=userId) # Added userId
    return render_template('userDash.html', userId = userId)

@app.route('/logout')
def logout():
    flask.session.pop('role',None)
    return redirect('/index')

@app.route('/basket/<userId>', methods = ['GET','POST'])
def basket(userId):
    try:
        if flask.session['role'] != int(userId):
            return redirect('/index')
    except KeyError:
        return redirect('/index')
    
    if request.method == "POST":
        # Validate CSRF token
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            basketItems = db.getBasket(userId)
            totalPrice = sum((item.basketPrice * item.basketQuant) for item, _ in basketItems)
            return render_template('basket.html', basketItems=basketItems, userId=userId, totalPrice=totalPrice, csrf_error=True), 400

        basketID = request.form.get('basketID')
        db.removefromBasket(basketID)

    basketItems = db.getBasket(userId)
    totalPrice = sum((item.basketPrice * item.basketQuant) for item, _ in basketItems)

    return render_template('basket.html', basketItems=basketItems, userId=userId, totalPrice=totalPrice)

    
if __name__ == '__main__':
    app.run(ssl_context='adhoc')
