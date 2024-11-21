import tkinter
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import logging
import re
import uuid
import datetime
from datetime import datetime
import datetime
from tkcalendar import Calendar
# Define the connection variable in the global scope
connection = None
order_cart_window = None
cart_items = []
total_price = 0
# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# Function to handle sign-in button
def enter_app():
    global connection
    user_id = userid_entry.get()
    password = password_entry.get()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User_Account WHERE User_ID = %s AND Password = %s", (user_id, password))
        user_account = cursor.fetchone()
        if user_account:
            # Authentication successful, open order cart screen
            print("Authentication successful. Entering app.")
            clear_signin_entries()
            current_user = user_account[0]  # Assuming User_Account table's first column is User_ID
            order_cart_screen(current_user)  # Pass current_user to the function
        else:
            print("Invalid credentials. Please try again.")
            logging.warning("Invalid sign-in attempt with user ID: %s", user_id)
            messagebox.showerror("Error", "Invalid credentials. Please try again.")
    except mysql.connector.Error as error:
        print("Error occurred during sign-in:", error)
        logging.error("Error occurred during sign-in: %s", error)
        messagebox.showerror("Error", "Error occurred during sign-in. Please try again.")
# Function to clear sign-in entries
def clear_signin_entries():
    userid_entry.delete(0, tkinter.END)
    password_entry.delete(0, tkinter.END)
def userdetails():
    # Create a new window for sign-up
    signup_window = tkinter.Toplevel(window)
    signup_window.title("Sign Up")
    # Create a frame to organize widgets
    frame = tkinter.Frame(signup_window)
    frame.pack()
    # User info frame
    user_info_frame = tkinter.LabelFrame(frame, text="User Details")
    user_info_frame.grid(row=0, column=0, sticky="news", padx=20, pady=10)
    first_name_label = tkinter.Label(user_info_frame, text="First Name:")
    first_name_label.grid(row=0, column=0)
    first_name_entry = tkinter.Entry(user_info_frame)
    first_name_entry.grid(row=0, column=1)
    last_name_label = tkinter.Label(user_info_frame, text="Last Name:")
    last_name_label.grid(row=1, column=0)
    last_name_entry = tkinter.Entry(user_info_frame)
    last_name_entry.grid(row=1, column=1)
    email_label = tkinter.Label(user_info_frame, text="Email:")
    email_label.grid(row=2, column=0)
    email_entry = tkinter.Entry(user_info_frame)
    email_entry.grid(row=2, column=1)
    phone_label = tkinter.Label(user_info_frame, text="Phone:")
    phone_label.grid(row=3, column=0)
    phone_entry = tkinter.Entry(user_info_frame)
    phone_entry.grid(row=3, column=1)
    dob_label = tkinter.Label(user_info_frame, text="Date of Birth:")
    dob_label.grid(row=4, column=0)
    dob_entry = tkinter.Entry(user_info_frame)
    dob_entry.grid(row=4, column=1)
    # Add a Combobox for selecting states
    state_label = tkinter.Label(user_info_frame, text="State:")
    state_label.grid(row=5, column=0)
    # List of US states
    us_states = [
      "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
      "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
      "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
      "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
      "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
      "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
      "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
    state_combobox = ttk.Combobox(user_info_frame, values=us_states, state="readonly")
    state_combobox.grid(row=5, column=1)
    # Function to set the selected date in the Date of Birth entry
    def set_date():
        dob_entry.delete(0, tkinter.END)
        dob_entry.insert(0, cal.get_date())
    # Calendar button for selecting DOB
    def show_calendar():
        def on_date_select():
            dob_entry.delete(0, tkinter.END)
            dob_entry.insert(0, cal.get_date())
            cal_window.destroy()
        cal_window = tkinter.Toplevel(signup_window)
        cal_window.title("Select Date of Birth")
        cal = Calendar(cal_window, selectmode="day", date_pattern="MM/DD/YYYY")
        cal.pack()
        select_button = tkinter.Button(cal_window, text="Select", command=on_date_select)
        select_button.pack()
    cal_button = tkinter.Button(user_info_frame, text="Calendar", command=show_calendar)
    cal_button.grid(row=4, column=2)
    user_id_label = tkinter.Label(user_info_frame, text="User ID:")
    user_id_label.grid(row=6, column=0)
    user_id_entry = tkinter.Entry(user_info_frame)
    user_id_entry.grid(row=6, column=1)
    password_label = tkinter.Label(user_info_frame, text="Password:")
    password_label.grid(row=7, column=0)
    password_entry = tkinter.Entry(user_info_frame, show="*")  # Passwords are shown as asterisks
    password_entry.grid(row=7, column=1)
    retype_password_label = tkinter.Label(user_info_frame, text="Retype Password:")
    retype_password_label.grid(row=8, column=0)
    retype_password_entry = tkinter.Entry(user_info_frame, show="*")
    retype_password_entry.grid(row=8, column=1)
    def validate_email(email):
        # Regular expression for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|org|net|gov|edu|mil|int|co.in|biz)$'
        return re.match(pattern, email)
    # Function to add a new user to the database
    def add_user():
        first_name = first_name_entry.get()
        last_name = last_name_entry.get()
        email = email_entry.get()
        phone = phone_entry.get()
        dob_str = dob_entry.get()
        state = state_combobox.get()  # Get selected state
        user_id = user_id_entry.get()
        password = password_entry.get()
        retype_password = retype_password_entry.get()

        # Validate email format
        if not validate_email(email):
            messagebox.showerror("Error", "Invalid email format. Please enter a valid email.")
            return

        # Validate phone number length
        if len(phone) != 10:
            messagebox.showerror("Error", "Phone number should be 10 digits.")
            return

        # Validate date format
        dob_parts = dob_str.split("/")
        if len(dob_parts) != 3:
            messagebox.showerror("Error", "Invalid date format. Please use MM/DD/YYYY.")
            return

        try:
            month = int(dob_parts[0])
            day = int(dob_parts[1])
            year = int(dob_parts[2])
            dob_datetime = datetime.datetime(year, month, day)
            dob_formatted = dob_datetime.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use MM/DD/YYYY.")
            return

        # Validate age
        today = datetime.datetime.today()
        age = today.year - dob_datetime.year - ((today.month, today.day) < (dob_datetime.month, dob_datetime.day))
        if age < 18:
            messagebox.showerror("Error", "You must be at least 18 years old to sign up.")
            return

        # Validate password match
        if password != retype_password:
            messagebox.showerror("Error", "Passwords do not match. Please retype password correctly.")
            return

        # Check if User ID is unique
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT User_ID FROM User_Account WHERE User_ID = %s", (user_id,))
            existing_user = cursor.fetchone()
            if existing_user:
                messagebox.showerror("Error", "User ID already exists. Please choose a different one.")
                return
        except mysql.connector.Error as error:
            print("Error occurred while checking user ID:", error)
            logging.error("Error occurred while checking user ID: %s", error)
            messagebox.showerror("Error", "Error occurred while checking user ID. Please try again.")
            return

        try:
            cursor.execute(
                "INSERT INTO Customer (First_Name, Last_Name, Email_ID, Phone_No, Date_of_Birth, State, User_Acc_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (first_name, last_name, email, phone, dob_formatted, state, None))
            connection.commit()
            cursor.execute("INSERT INTO User_Account (User_ID, Password) VALUES (%s, %s)", (user_id, password))
            connection.commit()
            print("User added successfully.")
            logging.info("New user added to the database.")
            messagebox.showinfo("Success", "User added successfully.")
            signup_window.destroy()  # Close the sign-up window after successful registration
        except mysql.connector.Error as error:
            print("Error occurred while adding user:", error)
            logging.error("Error occurred while adding user: %s", error)
            messagebox.showerror("Error", "Error occurred while adding user. Please try again.")


    
    # Sign-up button
    btnSignUp = tkinter.Button(frame, width=10, text="Sign Up", command=add_user)
    btnSignUp.grid(row=1, column=0, padx=20, pady=10)
    # Cancel button
    btnCancel = tkinter.Button(frame, width=10, text="Cancel", command=signup_window.destroy)
    btnCancel.grid(row=1, column=1, padx=20, pady=10)
def login():
    # Authenticate user (e.g., by checking credentials against database)
    # If authentication is successful, set the current_user variable
    global current_user
    current_user = get_current_user_id()  # Assuming get_current_user_id() retrieves the user's ID after successful login
    order_cart_screen()  # Open the order cart screen after successful login
# Function to create the order cart screen
def order_cart_screen(current_user):
    global order_cart_window
    
    # Function to select only Wednesdays and Saturdays from the next 14 days
    def select_delivery_dates():
        today = datetime.datetime.today().date()
        delivery_dates = []
        delivery_days = []
        for i in range(14):
            current_date = today + datetime.timedelta(days=i)
            if current_date.weekday() in [2, 5]:  # Wednesday: 2, Saturday: 5
                delivery_dates.append(current_date)
                if current_date.weekday() == 2:
                    delivery_days.append("Wednesday")
                else:
                    delivery_days.append("Saturday")
        return delivery_dates, delivery_days
    
    # Function to handle radio button selection
    def select_delivery():
        print(delivery_var.get())  # Print selected delivery date
    
    # Fetch the first name of the user from the database
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT First_Name FROM Customer WHERE User_Acc_ID = %s", (current_user,))
        user_data = cursor.fetchone()
        connection.commit()
        if user_data:
            user_first_name = user_data[0]
        else:
            user_first_name = ""
    except mysql.connector.Error as error:
        print("Error occurred while fetching user data:", error)
        logging.error("Error occurred while fetching user data: %s", error)
        messagebox.showerror("Error", "Error occurred while fetching user data. Please try again.")
        return
    # Create the order cart window
    order_cart_window = tkinter.Toplevel(window)
    order_cart_window.title("Order Cart")
    # Set background color to light green
    order_cart_window.configure(bg="#e6ffe6")
    # Make the window fullscreen
    width = order_cart_window.winfo_screenwidth()
    height = order_cart_window.winfo_screenheight()
    order_cart_window.geometry(f"{width}x{height}+0+0")
    # Create a frame to organize widgets
    frame = tkinter.Frame(order_cart_window, bg="#e6ffe6")  # Set frame background color
    frame.pack(fill=tkinter.BOTH, expand=True)
    # Filter section
    filter_frame = tkinter.Frame(frame, bg="#e6ffe6")  # Set frame background color
    filter_frame.pack(side=tkinter.LEFT, padx=20, pady=10, fill=tkinter.BOTH)
    filter_label = tkinter.Label(filter_frame, text="Filter", font=("Helvetica", 16, "bold"), bg="#e6ffe6")  # Set label background color
    filter_label.pack()
    # Product Search
    search_label = tkinter.Label(filter_frame, text="Search Product:", bg="#e6ffe6", font=("Helvetica", 12))  # Set label background color and font
    search_label.pack()
    search_entry = tkinter.Entry(filter_frame, width=20, font=("Helvetica", 10))  # Set entry width and font
    search_entry.pack()
    search_button = tkinter.Button(filter_frame, text="Search", bg="#99ff99", font=("Helvetica", 10, "bold"),  # Set button background color and font
                                   command=lambda: search_product(search_entry.get()))
    search_button.pack()
    # Product Filter
    price_range_label = tkinter.Label(filter_frame, text="Price Range:", bg="#e6ffe6", font=("Helvetica", 12))  # Set label background color and font
    price_range_label.pack()
    # Frame to organize minimum and maximum price fields
    price_entry_frame = tkinter.Frame(filter_frame, bg="#e6ffe6")
    price_entry_frame.pack()
    # Minimum price entry
    min_price_label = tkinter.Label(price_entry_frame, text="Min:", bg="#e6ffe6", font=("Helvetica", 10))  # Set label background color and font
    min_price_label.pack(side=tkinter.LEFT)
    price_from_entry = tkinter.Entry(price_entry_frame, width=10, font=("Helvetica", 10))  # Set entry width and font
    price_from_entry.pack(side=tkinter.LEFT, padx=(0, 5))
    # Maximum price entry
    max_price_label = tkinter.Label(price_entry_frame, text="Max:", bg="#e6ffe6", font=("Helvetica", 10))  # Set label background color and font
    max_price_label.pack(side=tkinter.LEFT)
    price_to_entry = tkinter.Entry(price_entry_frame, width=10, font=("Helvetica", 10))  # Set entry width and font
    price_to_entry.pack(side=tkinter.LEFT)
    filter_button = tkinter.Button(filter_frame, text="Apply Filter", bg="#99ff99", font=("Helvetica", 10, "bold"),
                                                                      command=lambda: filter_products(price_from_entry.get(), price_to_entry.get()))
    filter_button.pack()
    # Products section
    products_frame = tkinter.Frame(frame, bg="#e6ffe6")  # Set frame background color
    products_frame.pack(side=tkinter.LEFT, padx=20, pady=10, fill=tkinter.BOTH, expand=True)
    products_label = tkinter.Label(products_frame, text="Products", font=("Helvetica", 16, "bold"), bg="#e6ffe6")  # Set label background color
    products_label.pack()
    # Create a Canvas for the products
    products_canvas = tkinter.Canvas(products_frame, bg="#e6ffe6")
    products_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    # Add a scrollbar for the products
    scrollbar = tkinter.Scrollbar(products_frame, orient="vertical", command=products_canvas.yview)
    scrollbar.pack(side=tkinter.RIGHT, fill="y")
    # Configure the canvas
    products_canvas.configure(yscrollcommand=scrollbar.set)
    products_canvas.bind('<Configure>', lambda e: products_canvas.configure(scrollregion=products_canvas.bbox("all")))
    # Create a frame inside the canvas to place products
    products_frame_inside_canvas = tkinter.Frame(products_canvas, bg="#e6ffe6")
    products_canvas.create_window((0, 0), window=products_frame_inside_canvas, anchor='nw')
    # Fetch products from the database
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Product_ID, Description, Price FROM Product")
        products = cursor.fetchall()
        connection.commit()
        # Display products in a list format
        for product in products:
            product_label = tkinter.Label(products_frame_inside_canvas, text=f"{product[1]} - ${product[2]}", bg="#e6ffe6", font=("Helvetica", 12))  # Set label background color and font
            product_label.pack()
            quantity_combobox = ttk.Combobox(products_frame_inside_canvas, values=[i for i in range(1, 6)], state="readonly", width=5, font=("Helvetica", 10))  # Set combobox width and font
            quantity_combobox.pack()
            add_to_cart_button = tkinter.Button(products_frame_inside_canvas, text="Add to Cart", bg="#99ff99", font=("Helvetica", 10, "bold"),  # Set button background color and font
                                                 command=lambda p_id=product[0], desc=product[1],
                                                                price=product[2], qty=quantity_combobox: add_to_cart(
                                                     p_id, desc, price, qty))
            add_to_cart_button.pack(pady=5)
    except mysql.connector.Error as error:
        print("Error occurred while fetching products:", error)
        logging.error("Error occurred while fetching products: %s", error)
        messagebox.showerror("Error", "Error occurred while fetching products. Please try again.")
    # Delivery Date Selection
    delivery_frame = tkinter.Frame(frame, bg="#e6ffe6")  # Set frame background color
    delivery_frame.pack(side=tkinter.RIGHT, padx=20, pady=10, fill=tkinter.BOTH)
    delivery_label = tkinter.Label(delivery_frame, text="Select Delivery Date:", font=("Helvetica", 16, "bold"), bg="#e6ffe6")
    delivery_label.pack()
    delivery_dates, delivery_days = select_delivery_dates()[:2]  # Get the next 2 delivery dates and corresponding days
    delivery_var = tkinter.StringVar()  # Variable to hold selected delivery date
    for date, day in zip(delivery_dates, delivery_days):
        for time_slot in ["6-7pm", "7-8pm", "8-9pm"]:
            delivery_radio = tkinter.Radiobutton(delivery_frame, text=f"{day} {date.strftime('%Y-%m-%d')} {time_slot}", variable=delivery_var,
                                                 value=f"{date.strftime('%Y-%m-%d')} {time_slot}",
                                                 font=("Helvetica", 12), bg="#e6ffe6", command=select_delivery)
            delivery_radio.pack(anchor=tkinter.W)
    
    
   # Add a button to view the cart in the order cart screen
    view_cart_button = tkinter.Button(frame, text="View Cart", command=lambda: view_cart(delivery_var.get()))
    view_cart_button.pack()  # Adjust the positioning as needed
    # Adjust padding and spacing for a better appearance
    frame.grid_rowconfigure((0, 1, 2), weight=1)
    frame.grid_columnconfigure((0, 1), weight=1)
# Function to search for a product
def search_product(keyword):
    global order_cart_window
    if not keyword:
        messagebox.showerror("Error", "Please enter a search keyword.")
        return
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Product_ID, Description, Price FROM Product WHERE Description LIKE %s",
                       ('%' + keyword + '%',))
        products = cursor.fetchall()
        connection.commit()
        if not products:
            messagebox.showinfo("Info", "No products found matching the search criteria.")
        else:
            search_result_window = tkinter.Toplevel(order_cart_window)
            search_result_window.title("Search Results")
            frame = tkinter.Frame(search_result_window)
            frame.pack()
            title_label = tkinter.Label(frame, text="Search Results", font=("Helvetica", 16))
            title_label.pack(pady=10)
            for product in products:
                product_label = tkinter.Label(frame, text=f"{product[1]} - ${product[2]}")
                product_label.pack()
    except mysql.connector.Error as error:
        print("Error occurred while searching for products:", error)
        logging.error("Error occurred while searching for products: %s", error)
        messagebox.showerror("Error", "Error occurred while searching for products. Please try again.")
# Function to filter products by price range
def filter_products(min_price, max_price):
    global order_cart_window
    if not min_price or not max_price:
        messagebox.showerror("Error", "Please enter both minimum and maximum price.")
        return
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT Product_ID, Description, Price FROM Product WHERE Price BETWEEN %s AND %s",
                       (min_price, max_price))
        products = cursor.fetchall()
        connection.commit()
        if not products:
            messagebox.showinfo("Info", "No products found within the specified price range.")
        else:
            filter_result_window = tkinter.Toplevel(order_cart_window)
            filter_result_window.title("Filtered Results")
            frame = tkinter.Frame(filter_result_window)
            frame.pack()
            title_label = tkinter.Label(frame, text="Filtered Results", font=("Helvetica", 16))
            title_label.pack(pady=10)
            for product in products:
                product_label = tkinter.Label(frame, text=f"{product[1]} - ${product[2]}")
                product_label.pack()
    except mysql.connector.Error as error:
        print("Error occurred while filtering products:", error)
        logging.error("Error occurred while filtering products: %s", error)
        messagebox.showerror("Error", "Error occurred while filtering         products: %s", error)
# Function to add a product to the cart
# Function to add a product to the cart
def add_to_cart(product_id, description, price, quantity_combobox):
    global cart_items, total_price
    # Extract the selected quantity from the Combobox
    selected_quantity = int(quantity_combobox.get())
    # Check if the product is already in the cart
    for i, item in enumerate(cart_items):
        if item[0] == product_id:
            current_quantity = item[3]  # Get the current quantity
            new_quantity = current_quantity + selected_quantity  # Add the selected quantity
            if new_quantity > 5:
                messagebox.showinfo("Info", "Maximum quantity limit reached.")
                return  # Exit the function if the maximum limit is reached
            # Update the cart item with the new quantity and price
            cart_items[i] = (item[0], item[1], item[2], new_quantity)
            total_price += price * selected_quantity  # Update the total price
            break
    else:
        # If the product is not already in the cart, add it as a new item
        cart_items.append((product_id, description, price, selected_quantity))
        total_price += price * selected_quantity  # Update the total price
    # Create a custom messagebox
    success_window = ttk.Toplevel()
    success_window.title("Success")
    
    # Create a label to display the success message with fixed width
    success_label = ttk.Label(success_window, text="Product added to cart.", width=20, justify="center")
    success_label.pack(padx=10, pady=10)
    # Set the size of the window and center it on the screen
    success_window.geometry("200x100")
    success_window.eval('tk::PlaceWindow . center')
    # Destroy the window after a few seconds
    success_window.after(2000, success_window.destroy)
# Example usage:
# add_to_cart(product_id, description, price, quantity_combobox)
# Example usage:
# add_to_cart(product_id, description, price, quantity_combobox)
def edit_profile(current_user):
    
    # Function to update the profile information
    def update_profile():
        new_first_name = first_name_entry.get()
        new_last_name = last_name_entry.get()
        new_email = email_entry.get()
        new_password = password_entry.get()
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE Customer SET First_Name = %s, Last_Name = %s, Email = %s, Password = %s WHERE User_Acc_ID = %s",
                           (new_first_name, new_last_name, new_email, new_password, current_user))
            connection.commit()
            # Display success message
            messagebox.showinfo("Success", "Profile updated successfully!")
        except mysql.connector.Error as error:
            print("Error occurred while updating profile:", error)
            messagebox.showerror("Error", "Error occurred while updating profile. Please try again.")
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT First_Name, Last_Name, Email FROM Customer WHERE User_Acc_ID = %s", (current_user,))
        user_data = cursor.fetchone()
        
       
        first_name_label = tkinter.Label(frame, text="First Name:")
        first_name_label.grid(row=0, column=0, padx=10, pady=5)
        first_name_entry = tkinter.Entry(frame)
        first_name_entry.grid(row=0, column=1, padx=10, pady=5)
        first_name_entry.insert(0, user_data[0])
        last_name_label = tkinter.Label(frame, text="Last Name:")
        last_name_label.grid(row=1, column=0, padx=10, pady=5)
        last_name_entry = tkinter.Entry(frame)
        last_name_entry.grid(row=1, column=1, padx=10, pady=5)
        last_name_entry.insert(0, user_data[1])
        email_label = tkinter.Label(frame, text="Email:")
        email_label.grid(row=2, column=0, padx=10, pady=5)
        email_entry = tkinter.Entry(frame)
        email_entry.grid(row=2, column=1, padx=10, pady=5)
        email_entry.insert(0, user_data[2])
        password_label = tkinter.Label(frame, text="Password:")
        password_label.grid(row=3, column=0, padx=10, pady=5)
        password_entry = tkinter.Entry(frame, show="*")
        password_entry.grid(row=3, column=1, padx=10, pady=5)
        # Button to update profile
        update_button = tkinter.Button(frame, text="Update Profile", command=update_profile)
        update_button.grid(row=4, columnspan=2, padx=10, pady=10)
    except mysql.connector.Error as error:
        print("Error occurred while fetching user data for profile edit:", error)
        messagebox.showerror("Error", "Error occurred while fetching user data for profile edit. Please try again.")
# Function to view the cart
def view_cart(selected_delivery_date):
    global cart_items
    def reduce_quantity(product_id, quantity_label):
        global cart_items
        for i, item in enumerate(cart_items):
            if item[0] == product_id:
                current_quantity = int(quantity_label.cget("text"))
                if current_quantity > 1:
                    new_quantity = current_quantity - 1
                    quantity_label.config(text=str(new_quantity))
                    cart_items[i] = (item[0], item[1], item[2], new_quantity)
                    break
                else:
                    cart_items.pop(i)  # Remove the item if quantity becomes zero
                    update_cart_display()  # Update the cart display
                    break
        else:
            messagebox.showerror("Error", "Product not found in cart.")
    def increase_quantity(product_id, quantity_label):
        global cart_items
        for i, item in enumerate(cart_items):
            if item[0] == product_id:
                current_quantity = int(quantity_label.cget("text"))
                if current_quantity < 5:  # Maximum quantity limit
                    new_quantity = current_quantity + 1
                    quantity_label.config(text=str(new_quantity))
                    cart_items[i] = (item[0], item[1], item[2], new_quantity)
                    break
                else:
                    messagebox.showinfo("Info", "Maximum quantity limit reached.")
                    break
        else:
            messagebox.showerror("Error", "Product not found in cart.")
    def cancel_order():
        global cart_items
        cart_items = []  # Clear the cart items
        cart_window.destroy()  # Close the cart window
        order_cart_screen()  # Return to the order cart page
    def checkout():
        global cart_items

        # Calculate total order amount
        total_amount = sum(item[2] * item[3] for item in cart_items)

        # Check if the total amount is greater than $50
        if total_amount >= 50:
            delivery_fee = 0
        else:
            delivery_fee = 10

        # Close the current cart window
        cart_window.destroy()

        # Create a new window for the checkout process
        checkout_window = tkinter.Toplevel(window)
        checkout_window.title("Checkout")
        # Create a frame to organize widgets
        frame = ttk.Frame(checkout_window)
        frame.pack()
        # Function to validate US zip code
        def validate_zip(zip_code):
            # Allowed zip codes for MOUNT Pleasant
            allowed_zip_codes = ["48858", "48859"]
            return zip_code in allowed_zip_codes
        # Name field
        name_label = ttk.Label(frame, text="Name:")
        name_label.grid(row=0, column=0, padx=10, pady=5)
        name_entry = ttk.Entry(frame)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        # Delivery address fields
        street_label = ttk.Label(frame, text="Street:")
        street_label.grid(row=1, column=0, padx=10, pady=5)
        street_entry = ttk.Entry(frame)
        street_entry.grid(row=1, column=1, padx=10, pady=5)
        # Zip Code field with limited options
        zip_label = ttk.Label(frame, text="Zip Code:")
        zip_label.grid(row=2, column=0, padx=10, pady=5)
        zip_entry = ttk.Combobox(frame, values=["48858", "48859"])
        zip_entry.grid(row=2, column=1, padx=10, pady=5)
        # City field with limited options
        city_label = ttk.Label(frame, text="City:")
        city_label.grid(row=3, column=0, padx=10, pady=5)
        city_entry = ttk.Combobox(frame, values=["MOUNT PLEASANT"])
        city_entry.grid(row=3, column=1, padx=10, pady=5)
        # State field with limited options
        state_label = ttk.Label(frame, text="State:")
        state_label.grid(row=4, column=0, padx=10, pady=5)
        state_entry = ttk.Combobox(frame, values=["Michigan"])
        state_entry.grid(row=4, column=1, padx=10, pady=5)
        # Phone number field
        phone_label = ttk.Label(frame, text="Phone Number:")
        phone_label.grid(row=5, column=0, padx=10, pady=5)
        phone_entry = ttk.Entry(frame)
        phone_entry.grid(row=5, column=1, padx=10, pady=5)
        # Payment processing (simulate with a button)
        def process_payment():
            # Retrieve values from entry fields
            street = street_entry.get()
            zip_code = zip_entry.get()
            city = city_entry.get()
            state = state_entry.get()
            name = name_entry.get()
            phone_number = phone_entry.get()
            # Validate mandatory fields
            if not (street and zip_code and city and state and name and phone_number):
                messagebox.showerror("Error", "All fields are mandatory. Please fill in all required information.")
                return
            # Validate phone number format
            if len(phone_number) != 10 or not phone_number.isdigit():
                messagebox.showerror("Error", "Please enter a valid 10-digit phone number.")
                return
            # Validate US zip code format
            if not validate_zip(zip_code):
                messagebox.showerror("Error", "Please enter a valid zip code for MOUNT Pleasant.")
                return

            # Calculate total order amount including delivery fee
            total_amount_with_delivery_fee = total_amount + delivery_fee

            # Generate a unique order number (simulation)
            uuid_str = str(uuid.uuid4())
            order_id = int(uuid_str.replace("-", "")[:4])

            # Display the order number to the user
            messagebox.showinfo("Order Placed", f"Your order has been placed successfully!\nOrder Number: {order_id}")
            # Display the order details to the user
            messagebox.showinfo("Order Placed", f"Your order has been placed successfully!\n"
                                                 f"Order Number: {order_id}\n"
                                                 f"Total Amount: ${total_amount}\n"
                                                 f"Delivery Fee: ${delivery_fee}\n"
                                                 f"Total Amount with Delivery Fee: ${total_amount_with_delivery_fee}")

            # Close the payment and checkout window
            checkout_window.destroy()
            # Return to the order cart page
            order_cart_screen(current_user)
        # Payment button
        payment_button = ttk.Button(frame, text="Process Payment", command=process_payment)
        payment_button.grid(row=6, columnspan=2, padx=10, pady=10)
    def update_cart_display():
        # Clear the current content of the frame
        for widget in frame.winfo_children():
            widget.destroy()
        # Add widgets to display updated cart items
        title_label = ttk.Label(frame, text="Cart Items", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        for index, item in enumerate(cart_items):
            product_id, description, price, quantity = item
            # Product label
            product_label = ttk.Label(frame, text=f"{description} - ${price} x {quantity}")
            product_label.grid(row=index+1, column=0)
            # Quantity label
            quantity_label = ttk.Label(frame, text=str(quantity))
            quantity_label.grid(row=index+1, column=1)
            # Reduce quantity button
            reduce_button = ttk.Button(frame, text="Reduce", command=lambda p_id=product_id, ql=quantity_label: reduce_quantity(p_id, ql))
            reduce_button.grid(row=index+1, column=2, padx=5)
            # Increase quantity button
            increase_button = ttk.Button(frame, text="Increase", command=lambda p_id=product_id, ql=quantity_label: increase_quantity(p_id, ql))
            increase_button.grid(row=index+1, column=3, padx=5)

        # Display selected delivery date
        delivery_label = ttk.Label(frame, text=f"Selected Delivery Date: {selected_delivery_date}", font=("Helvetica", 12))
        delivery_label.grid(row=len(cart_items)+1, column=0, columnspan=4, pady=10)
        # Selected delivery date label
        delivery_label = ttk.Label(frame, text=f"Selected Delivery Date: {selected_delivery_date}")
        delivery_label.grid(row=len(cart_items)+1, columnspan=4, pady=10)

        # Calculate total order amount
        total_amount = sum(item[2] * item[3] for item in cart_items)

        # Check if the total amount is greater than $50
        if total_amount >= 50:
            total_label_text = f"Total Amount: ${total_amount}"
        else:
            total_label_text = f"Total Amount: ${total_amount} (Includes $10 delivery fee)"

        # Total amount label
        total_label = ttk.Label(frame, text=total_label_text)
        total_label.grid(row=len(cart_items)+2, columnspan=4, pady=10)

        # Cancel order button
        cancel_button = ttk.Button(frame, text="Cancel Order", command=cancel_order)
        cancel_button.grid(row=len(cart_items)+2, column=0, columnspan=2, pady=10)
        cancel_button.grid(row=len(cart_items)+3, column=0, columnspan=2, pady=10)

        # Checkout button
        checkout_button = ttk.Button(frame, text="Checkout", command=checkout)
        checkout_button.grid(row=len(cart_items)+2, column=2, columnspan=2, pady=10)
        checkout_button.grid(row=len(cart_items)+3, column=2, columnspan=2, pady=10)

    cart_window = tkinter.Toplevel(order_cart_window)
    cart_window.title("View Cart")
    # Create a frame to organize widgets
    frame = ttk.Frame(cart_window)
    frame.pack()

    update_cart_display()


# function to place order
def place_order():
    global cart_items, total_price, current_user
    try:
        cursor = connection.cursor()
        # Get the current date and time
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Retrieve the current user's ID
        current_user_id = current_user  # Assuming current_user holds the user's ID
        # Insert the order details into the Orders table
        cursor.execute("INSERT INTO Orders (Date, Total_Price, Customer_ID, Shipment_ID) VALUES (%s, %s, %s, %s)",
                       (current_date, total_price, current_user_id, None))
        # Commit the transaction
        connection.commit()
        # Retrieve the auto-generated order ID
        cursor.execute("SELECT LAST_INSERT_ID()")
        order_id = cursor.fetchone()[0]
        # Show success message with the order ID
        messagebox.showinfo("Success", f"Order placed successfully! Order ID: {order_id}")
        # Clear cart items after placing the order
        cart_items.clear()
        # Close the order cart window after placing the order
        order_cart_window.destroy()
    except mysql.connector.Error as error:
        # Print the error
        print("Error occurred while placing order:", error)
        # Log the error
        logging.error("Error occurred while placing order: %s", error)
        # Display error message to the user
        messagebox.showerror("Error", "Error occurred while placing order. Please try again.")
try:
    # Replace '141.209.241.81', 'bis698_S24_w200', 'grp2w200', and 'passinit' with your actual database details
    connection = mysql.connector.connect(
        host='141.209.241.81',  # Or your database server IP
        database='bis698_S24_w200',
        user='grp2w200',
        password='passinit'
    )
    if connection.is_connected():
        db_info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_info)
        cursor = connection.cursor()
        cursor.execute("SELECT database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
except mysql.connector.Error as error:
    print("Failed to connect to MySQL:", error)
    logging.error("Failed to connect to MySQL: %s", error)
    messagebox.showerror("Error", "Failed to connect to MySQL. Please try again.")
# Create the main window
window = tkinter.Tk()
window.title("Indian Grocery Hub Login Page")
# Create a frame to organize widgets
frame = tkinter.Frame(window)
frame.pack()
# User info frame
user_info_frame = tkinter.LabelFrame(frame, text="User Credentials")
user_info_frame.grid(row=0, column=0, sticky="news", padx=20, pady=10)
userid_label = tkinter.Label(user_info_frame, text="User ID:")
userid_label.grid(row=0, column=0)
userid_entry = tkinter.Entry(user_info_frame)
userid_entry.grid(row=0, column=1)
password_label = tkinter.Label(user_info_frame, text="Password:")
password_label.grid(row=1, column=0)
password_entry = tkinter.Entry(user_info_frame, show="*")  # Passwords are shown as asterisks
password_entry.grid(row=1, column=1)
for widget in user_info_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)
# Buttons frame
buttons_frame = tkinter.LabelFrame(frame, text="Buttons")
buttons_frame.grid(row=3, column=0, sticky="news", padx=20, pady=10)
btnSignIn = tkinter.Button(buttons_frame, width=10, text="Sign-In", command=enter_app)
btnSignIn.grid(row=3, column=0)
btnSignUp = tkinter.Button(buttons_frame, width=10, text="Sign-Up", command=userdetails)
btnSignUp.grid(row=3, column=1)
btnExit = tkinter.Button(buttons_frame, width=10, text="Exit", command=window.destroy)
btnExit.grid(row=3, column=2)
for widget in buttons_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)
# Start the main event loop
window.mainloop()
