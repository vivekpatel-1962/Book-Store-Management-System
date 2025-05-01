import mysql.connector as a
import re
import matplotlib.pyplot as plt

# Database connection setup
passwd = str(input("Enter database password: "))
con = a.connect(host="localhost", user="root", passwd=passwd)

# Select database if it exists
c = con.cursor()
c.execute("show databases")
dl = c.fetchall()
dl2 = []

for i in dl:
    dl2.append(i[0])

if "bbshop" in dl2:
    sql = "use bbshop"
    c.execute(sql)
else:
    sql1 = "create database bbshop"
    c.execute(sql1)
    sql2 = "use bbshop"
    c.execute(sql2)
    # Create necessary tables
    sql3 = """create table Book(
                Name varchar(50),
                Author varchar(50),
                CostPrice integer,
                SellPrice integer,
                Quantity integer)"""
    c.execute(sql3)
    
    sql4 = """create table Bills(
                Name varchar(50),
                Book varchar(50),
                Phone varchar(50),
                Cost integer)"""
    c.execute(sql4)
    
    sql5 = """create table Customers(
                Name varchar(50),
                Email varchar(50),
                Phone varchar(50))"""
    c.execute(sql5)
    
    con.commit()

# Admin or Customer login function
def login():
    print("\n------------>>>>>>> Welcome to Online Book Store <<<<<<<<---------------\n")
    while True:
        role = input("Login as Admin or Customer? (Enter 'Admin', 'Customer', or 'Exit' to quit): ").strip().lower()
        
        if role == 'admin':
            admin_signin()
        elif role == 'customer':
            customer_options()
        elif role == 'exit':
            print("Exiting the program. Goodbye!")
            break  # Exit the program
        else:
            print("Invalid choice. Please try again.")

# Admin sign-in function
def admin_signin():
    print("\nAdmin Login\n")
    p = input("Enter Admin password: ")
    if p == "admin123":  # The admin password
        admin_options()
    else:
        print("Incorrect password. Please try again.")
        admin_signin()

# Admin options menu
def admin_options():
    f = True
    while f:
        print("""  
                            BOOK STORE ADMIN PANEL
                       -------------------------------------------
                       1. Add Book             4. See Sales Report
                       2. Update Book          5. Check Low Stock Alerts
                       3. Delete Book          6. Exit to Main Menu
                       -------------------------------------------
        """)
        choice = input("Select Option: ")
        
        if choice == '1':
            add_book()
        elif choice == '2':
            update_book()
        elif choice == '3':
            delete_book()
        elif choice == '4':
            sales_report()
        elif choice == '5':
            check_stock()
        elif choice == '6':
            print("Exiting Admin Panel.")
            f = False  # Exit the admin panel and return to login
        else:
            print("Invalid option. Please select again.")

# Customer options menu
def customer_options():
    f1 = True
    while f1:
        print("""  
                            BOOK STORE CUSTOMER PANEL
                       -------------------------------------------
                       1. Add Book to Cart     4. View Cart
                       2. Display Available Books
                       3. Search Book          5. Exit to Main Menu
                       -------------------------------------------
        """)
        choice = input("Select Option: ")
        
        if choice == '1':
            add_to_cart()
        elif choice == '2':
            display_available_books()
        elif choice == '3':
            search_book()
        elif choice == '4':
            view_cart()
        elif choice == '5':
            print("Exiting Customer Panel.")
            f1 = False  # Exit the customer panel and return to login
        else:
            print("Invalid option. Please select again.")

# Cart system
cart = []

# Adding book to the cart
def add_to_cart():
    book_name = input("Enter the name of the book you want to add to your cart: ")
    quantity = int(input("Enter the quantity: "))
    
    # Check the book's current stock in the inventory
    sql = "SELECT Name, SellPrice, Quantity FROM Book WHERE Name = %s"
    c = con.cursor()
    c.execute(sql, (book_name,))
    book = c.fetchone()
    
    if book:
        # Check if the book has sufficient quantity in stock
        if book[2] >= quantity:
            # Check if the book is already in the cart
            found_in_cart = False
            for item in cart:
                if item['name'] == book_name:
                    # Update the quantity in the cart if it's already added
                    item['quantity'] += quantity
                    found_in_cart = True
                    print(f"Updated the quantity of {book_name} to {item['quantity']} in your cart.")
                    break
            
            # If not in cart, add new entry
            if not found_in_cart:
                cart.append({
                    'name': book_name,
                    'quantity': quantity,
                    'price': book[1]  # Store the price as well
                })
                print(f"Added {quantity} of {book_name} to your cart.")
        else:
            print("Sorry, not enough stock available.")
    else:
        print(f"Book {book_name} not found.")

# View cart details and proceed with checkout
def view_cart():
    if not cart:
        print("Your cart is empty.")
        return

    print("Your Cart:")
    total_cost = 0
    for book in cart:
        print(f"Name: {book['name']}, Quantity: {book['quantity']}")
        total_cost += book['price'] * book['quantity']  # Assuming you track price in cart items

    print(f"Total cost: {total_cost}")
    proceed = input("Proceed to checkout? (Y/N): ")
    if proceed.lower() == 'y':
        checkout(total_cost)
    else:
        print("Returning to customer options.")

# Checkout process
# Checkout process
def checkout(total_cost):
    if not cart:
        print("Your cart is empty.")
        return

    name = input("Enter your Name: ")
    mobile = input("Enter your Mobile Number: ")
    
    email=input("Enter your email: ")
    
    if is_valid_email(email):
        print("Valid email address!")
    else:
        print("Invalid email address. Please enter a valid email.")
    

    # Validate the mobile number
    if not validate_phone(mobile):
        print("Invalid mobile number! Please enter a 10-digit number.")
        return

    # Initialize a new total cost that will be recalculated after quantity adjustments
    new_total_cost = 0

    # Check stock for each book in the cart before proceeding
    for item in cart:
        sql = "SELECT Quantity, SellPrice FROM Book WHERE Name = %s"
        c = con.cursor()
        c.execute(sql, (item['name'],))
        book = c.fetchone()

        if book:
            available_stock = book[0]
            if available_stock < item['quantity']:
                # If stock is less than the requested quantity, ask the customer to modify the quantity
                print(f"Sorry, not enough stock available for '{item['name']}'. Available stock: {available_stock}.")
                new_quantity = int(input(f"Please enter a new quantity for '{item['name']}' (max {available_stock}): "))
                
                # Update the cart with the new quantity
                if new_quantity <= available_stock:
                    item['quantity'] = new_quantity
                    print(f"Quantity for '{item['name']}' updated to {new_quantity}.")
                else:
                    print("The entered quantity exceeds available stock. Cannot proceed with checkout.")
                    return  # Exit the checkout process since the customer cannot proceed

            # Update the total cost with the new quantity for this book
            new_total_cost += item['price'] * item['quantity']
        else:
            print(f"Book '{item['name']}' not found in inventory.")
            return

    print(f"Total cost after quantity update: {new_total_cost}")

    # Insert into the Bills table and update stock after confirming the quantity
    for item in cart:
        sql_bill = 'INSERT INTO Bills(Name, Book, Phone,Cost) VALUES (%s, %s, %s, %s)'
        c.execute(sql_bill, (name, item['name'], mobile, item['price'] * item['quantity']))
        con.commit()

        # Update book quantity in the Book table
        sql = "SELECT Quantity FROM Book WHERE Name = %s"
        c.execute(sql, (item['name'],))
        book = c.fetchone()
        
        if book:
            new_quantity = book[0] - item['quantity']
            sql_update = 'UPDATE Book SET Quantity = %s WHERE Name = %s'
            c.execute(sql_update, (new_quantity, item['name']))
            con.commit()

            # If the quantity becomes 0, delete the book from the Book table
            if new_quantity == 0:
                sql_delete = 'DELETE FROM Book WHERE Name = %s'
                c.execute(sql_delete, (item['name'],))
                con.commit()

    # Insert into the Customers table the name, mobile number, and quantity of each book
    for item in cart:
        sql_customer = 'INSERT INTO Customers(Name, Email, Phone) VALUES (%s, %s, %s)'
        c.execute(sql_customer, (name,email, mobile))  # Assuming email is optional
        con.commit()

    print(f"Thank you for your purchase!")
    print(f"Final Total Cost: {new_total_cost}")
    
    cart.clear()  # Empty the cart after purchase



# Validate phone number (10 digits)
def validate_phone(phone):
    return bool(re.match(r'^\d{10}$', phone)) 

# Validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

# Admin function to add new book to inventory
def add_book():
    name = input("Enter book name: ")
    author = input("Enter author name: ")
    cost_price = int(input("Enter cost price: "))
    sell_price = int(input("Enter sell price: "))
    quantity = int(input("Enter quantity: "))
    
    sql = "INSERT INTO Book (Name, Author, CostPrice, SellPrice, Quantity) VALUES (%s, %s, %s, %s, %s)"
    c = con.cursor()
    c.execute(sql, (name, author, cost_price, sell_price, quantity))
    con.commit()
    print(f"Book '{name}' added successfully.")

# Admin function to update book details
def update_book():
    book_name = input("Enter the name of the book to update: ")
    sql = "SELECT * FROM Book WHERE Name = %s"
    c = con.cursor()
    c.execute(sql, (book_name,))
    book = c.fetchone()
    
    if not book:
        print("Book not found!")
        return
    
    print(f"Current details: Name: {book[0]}, Author: {book[1]}, Cost Price: {book[2]}, Sell Price: {book[3]}, Quantity: {book[4]}")
    
    new_price = input("Enter new Sell Price (leave empty to keep current): ")
    if new_price:
        sql_update = "UPDATE Book SET SellPrice = %s WHERE Name = %s"
        c.execute(sql_update, (new_price, book_name))
        con.commit()
        print("Book details updated successfully!")
    else:
        print("No changes made.")

# Admin function to delete book from inventory
def delete_book():
    book_name = input("Enter the name of the book to delete: ")
    sql = "SELECT * FROM Book WHERE Name = %s"
    c = con.cursor()
    c.execute(sql, (book_name,))
    book = c.fetchone()
    
    if not book:
        print("Book not found!")
        return
    
    sql_delete = "DELETE FROM Book WHERE Name = %s"
    c.execute(sql_delete, (book_name,))
    con.commit()
    print(f"Book '{book_name}' has been deleted.")

# Admin function to generate sales report
def sales_report():
    sql = "SELECT Book, COUNT(*) FROM Bills GROUP BY Book"
    c = con.cursor()
    c.execute(sql)
    sales_data = c.fetchall()
    
    if sales_data:
        books = [data[0] for data in sales_data]
        sales_count = [data[1] for data in sales_data]
        
        # Plotting bar graph using Matplotlib
        plt.bar(books, sales_count)
        plt.xlabel("Book Name")
        plt.ylabel("Books Sold")
        plt.title("Sales Record")
        plt.xticks(rotation=45)
        plt.show()
    else:
        print("No sales data available.")

# Admin function to check low stock books
def check_stock():
    sql = "SELECT * FROM Book WHERE Quantity < 5"
    c = con.cursor()
    c.execute(sql)
    low_stock_books = c.fetchall()
    if low_stock_books:
        for book in low_stock_books:
            print(f"Low stock: {book[0]} (Only {book[4]} left)")
    else:
        print("All books are well-stocked.")

# Function to display available books (Customer)
def display_available_books():
    sql = "SELECT * FROM Book"
    c = con.cursor()
    c.execute(sql)
    books = c.fetchall()
    print("\nDisplaying available books:")
    for book in books:
        print(f"Name: {book[0]}, Author: {book[1]}, Sell Price: {book[3]}, Quantity: {book[4]}")
    customer_options()

# Function to search a book by name (Customer)
def search_book():
    book_name = input("Enter Book Name to Search: ")
    sql = "SELECT * FROM Book WHERE Name LIKE %s"
    c = con.cursor()
    c.execute(sql, ('%' + book_name + '%',))
    books = c.fetchall()
    print("\nSearching for books:")
    if books:
        for book in books:
            print(f"Name: {book[0]}, Author: {book[1]}, Sell Price: {book[3]}, Quantity: {book[4]}")
    else:
        print("No books found with that name.")
    customer_options()

# Start the program by calling the login function
login()
