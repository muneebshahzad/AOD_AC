import asyncio
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, abort
import datetime, requests
from datetime import datetime
import pymssql, shopify
import aiohttp
import lazop
import aiohttp

app = Flask(__name__)
app.debug = True
app.secret_key = os.getenv('APP_SECRET_KEY', 'default_secret_key')  # Use environment variable

order_details = []
def get_db_connection():
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    try:
        connection = pymssql.connect(server=server, user=username, password=password, database=database)
        return connection
    except pymssql.Error as e:
        print(f"Error connecting to the database: {str(e)}")
        return None

@app.route("/submit_tasks", methods=["POST"])
def submit_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.date.today()
    cursor.execute("SELECT * FROM tasks WHERE Date = %s", (today,))
    existing_tasks = cursor.fetchone()

    if existing_tasks:
        flash("Tasks have already been submitted for today.", "error")
        return redirect(url_for("index"))

    selected_tasks = {}
    task_names = ["Confirm_Pending_Orders", "Track_Dispatched_Orders", "Contact_Abandoned_Orders", "Email_Courier",
                  "Track_Daraz_Orders", "Solve_Customer_Complaints", "Call_Delivered_Orders", "Add_Reviews_to_Shopify",
                  "Add_Reviews_to_Google_Maps", "Answer_Whatsapp_Messages_Calls", "Answer_Instagram_Facebook_Messages_Comments",
                  "Answer_Daraz_Messages", "Answer_Phone_Calls"]

    for task_name in task_names:
        selected_tasks[task_name] = 1 if task_name in request.form else 0

    cursor.execute("""
        INSERT INTO tasks (Date, Confirm_Pending_Orders, Track_Dispatched_Orders, Contact_Abandoned_Orders, Email_Courier,
        Track_Daraz_Orders, Solve_Customer_Complaints, Call_Delivered_Orders, Add_Reviews_to_Shopify,
        Add_Reviews_to_Google_Maps, Answer_Whatsapp_Messages_Calls, Answer_Instagram_Facebook_Messages_Comments,
        Answer_Daraz_Messages, Answer_Phone_Calls)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (today, *selected_tasks.values()))

    conn.commit()
    conn.close()

    flash("Tasks submitted successfully!", "success")
    return redirect(url_for("index"))

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    to_emails = data.get('to', [])
    cc_emails = data.get('cc', [])
    subject = data.get('subject', '')
    body = data.get('body', '')

    try:
        # SMTP server configuration
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_user = os.getenv('SMTP_USER')  # Use environment variable
        smtp_password = os.getenv('SMTP_PASSWORD')  # Use environment variable

        # Create the message
        msg = MIMEText(body)
        msg['From'] = smtp_user
        msg['To'] = ', '.join(to_emails)
        msg['Cc'] = ', '.join(cc_emails)
        msg['Subject'] = subject

        # Connect to the SMTP server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_emails + cc_emails, msg.as_string())
        server.quit()

        return jsonify({'message': 'Email sent successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def fetch_tracking_data(session, tracking_number):
        return await response.json()

async def process_line_item(session, line_item, fulfillments):
        {"tracking_number": "N/A", "status": "Un-Booked", "quantity": line_item.quantity}]

async def process_order(session, order):
    return order_info



@app.route('/apply_tag', methods=['POST'])
def apply_tag():
        return jsonify({"success": False, "error": str(e)})

async def getShopifyOrders():

    global order_details
    orders = shopify.Order.find(limit=250, order='created_at DESC')
    order_details = []
    total_start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [process_order(session, order) for order in orders]
        order_details = await asyncio.gather(*tasks)

    total_end_time = time.time()
    print(f"Total time taken to process all orders: {total_end_time - total_start_time:.2f} seconds")

    return order_details

@app.route("/track")
def tracking():
    global order_details
    return render_template("track.html", order_details=order_details)


def get_daraz_orders(statuses):
    try:
        access_token = '50000601237osiZ0F1HkTZVojWcjq6szVDmDPjxiuvoEbCSvB15ff2bc8xtn4m'
        client = lazop.LazopClient('https://api.daraz.pk/rest', '501554', 'nrP3XFN7ChZL53cXyVED1yj4iGZZtlcD')

        all_orders = []

        for status in statuses:
            request = lazop.LazopRequest('/orders/get', 'GET')
            request.add_api_param('sort_direction', 'DESC')
            request.add_api_param('update_before', '2025-02-10T16:00:00+08:00')
            request.add_api_param('offset', '0')
            request.add_api_param('created_before', '2025-02-10T16:00:00+08:00')
            request.add_api_param('created_after', '2017-02-10T09:00:00+08:00')
            request.add_api_param('limit', '50')
            request.add_api_param('update_after', '2017-02-10T09:00:00+08:00')
            request.add_api_param('sort_by', 'updated_at')
            request.add_api_param('status', status)
            request.add_api_param('access_token', access_token)

            response = client.execute(request)
            darazOrders = response.body.get('data', {}).get('orders', [])

            for order in darazOrders:
                print(order)
                order_id = order.get('order_id', 'Unknown')

                item_request = lazop.LazopRequest('/order/items/get', 'GET')
                item_request.add_api_param('order_id', order_id)
                item_request.add_api_param('access_token', access_token)

                item_response = client.execute(item_request)
                try:
                    items = item_response.body.get('data', [])
                    if not items:
                        raise ValueError("No items found in the response.")
                except (AttributeError, ValueError) as e:
                    print(f"Error retrieving items: {e}")
                    items = []

                item_details = []
                for item in items:
                    tracking_num = item.get('tracking_code', 'Unknown')

                    tracking_req = lazop.LazopRequest('/logistic/order/trace', 'GET')
                    tracking_req.add_api_param('order_id', order_id)
                    tracking_req.add_api_param('access_token', access_token)
                    tracking_response = client.execute(tracking_req)

                    tracking_data = tracking_response.body.get('result', {})
                    packages = tracking_data.get('data', [{}])[0].get('package_detail_info_list', [])

                    track_status = "N/A"
                    for package in packages:
                        if package.get("tracking_number") == tracking_num:
                            try:
                                track_status = package.get('logistic_detail_info_list', [{}])[-1].get('title', "N/A")
                            except (IndexError, KeyError) as e:
                                print(f"Error processing tracking data: {e}")
                                track_status = "N/A"
                            print("MATCHED")
                            break

                    item_detail = {
                        'item_image': item.get('product_main_image', 'N/A'),
                        'item_title': item.get('name', 'Unknown'),
                        'quantity': item.get('variation', 'N/A'),
                        'tracking_number': item.get('tracking_code', 'N/A'),
                        'status': track_status
                    }
                    item_details.append(item_detail)

                filtered_order = {
                    'order_id': order.get('order_id', 'Unknown'),
                    'customer': {
                        'name': f"{order.get('customer_first_name', 'Unknown')} {order.get('customer_last_name', 'Unknown')}",
                        'address': order.get('address_shipping', {}).get('address', 'N/A'),
                        'phone': order.get('address_shipping', {}).get('phone', 'N/A')
                    },
                    'status': status.replace('_', ' ').title(),
                    'date': format_date(order.get('created_at', 'N/A')),
                    'total_price': order.get('price', '0.00'),
                    'items_list': item_details,
                }
                all_orders.append(filtered_order)

        return all_orders
    except Exception as e:
        print(f"Error fetching darazOrders: {e}")
        return []


@app.route('/daraz')
def daraz():
    statuses = ['shipped','pending','ready_to_ship']
    darazOrders = get_daraz_orders(statuses)
    return render_template('daraz.html', darazOrders=darazOrders)

def format_date(date_str):
    # Parse the date string
    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
    # Format the date object to only show the date
    return date_obj.strftime("%Y-%m-%d")

@app.route('/refresh', methods=['POST'])
def refresh_data():
    global order_details
    try:
        order_details = asyncio.run(getShopifyOrders())
        return jsonify({'message': 'Data refreshed successfully'})
    except Exception as e:
        print(f"Error refreshing data: {e}")
        return jsonify({'message': 'Failed to refresh data'}), 500

def check_database_connection():
    server = 'tickbags.database.windows.net'
    database = 'TickBags'
    username = 'tickbags_ltd'
    password = 'TB@2024!'

    try:
        print('Connecting to the database...')
        connection = pymssql.connect(server=server, user=username, password=password, database=database)
        print('Connected to the database')
        return connection
    except pymssql.Error as e:
        print(f"Error connecting to the database: {str(e)}")
        return None

def fetch_transaction_data():
    connection = check_database_connection()
    if connection is None:
        return []
    print("CONNECTED TO DATABASE")

    try:
        with connection.cursor(as_dict=True) as cursor:
            query = 'SELECT * FROM transactiondetails3 ORDER BY Payment_Date desc'
            cursor.execute(query)
            transactions = cursor.fetchall()
            return transactions
    except pymssql.Error as e:
        print(f"Error fetching data from the database: {str(e)}")
        return []
    finally:
        connection.close()

@app.route('/finance_report')
def finance_report():
    transactions = fetch_transaction_data()

    return render_template('finance_report.html', transactions=transactions)

@app.route('/addTransaction')
def addTransaction():

    return render_template('addTransaction.html')

def run_async(func, *args, **kwargs):
    return asyncio.run(func(*args, **kwargs))
@app.route('/track/<tracking_num>')
def displayTracking(tracking_num):
    print(f"Tracking Number: {tracking_num}")  # Debug line

    async def async_func():
        async with aiohttp.ClientSession() as session:
            return await fetch_tracking_data(session, tracking_num)

    data = run_async(async_func)

    return render_template('trackingdata.html', data=data)


## ACCOUNTS ###


def check_database_connection():
    server = 'tickbags.database.windows.net'
    database = 'TickBags'
    username = 'tickbags_ltd'
    password = 'TB@2024!'

    try:
        print('Connecting to the database...')
        connection = pymssql.connect(server=server, user=username, password=password, database=database)

        print('Connected to the database')
        return connection
    except pymssql.Error as e:
        print(f"Error connecting to the database: {str(e)}")
        time.sleep(5)
        check_database_connection()
        return None

def fetch_transaction_data():
    connection = check_database_connection()
    if connection is None:
        return []
    print("CONNECTED TO DATABASE")

    try:
        with connection.cursor(as_dict=True) as cursor:
            query = '''SELECT * FROM AODIncomeExpenseTable ORDER BY "Payment_Date" desc'''
            cursor.execute(query)
            transactions = cursor.fetchall()
            return transactions
    except pymssql.Error as e:
        print(f"Error fetching data from the database: {str(e)}")
        return []
    finally:
        connection.close()


def fetch_monthly_financial_data(connection):
    cursor = connection.cursor()

    try:
        # Updated SQL query to fetch NetProfit instead of NetAmount
        cursor.execute('SELECT Month, NetProfit FROM AODMonthlySummary ORDER BY Month ASC')
        financial_data = cursor.fetchall()

        formatted_data = {
            'months': [row[0] for row in financial_data],
            'net_profits': [row[1] for row in financial_data]
        }

        return formatted_data

    except Exception as e:
        print(f"Error fetching monthly financial data: {str(e)}")
        return {'months': [], 'net_profits': []}

    finally:
        cursor.close()


def fetch_account_summary(connection):
    cursor = connection.cursor()

    try:
        # Fetch Cash on Hand (assuming it's stored in the 'AODaccounts' table)
        cursor.execute(
            "SELECT FORMAT(accounts_balance, 'N0') as FormattedAmount FROM AODaccounts WHERE accounts_name='Bank'")
        cash_on_hand = cursor.fetchone()[0]

        # Fetch Earnings (Monthly)
        cursor.execute("""
            SELECT FORMAT(Income, 'N0') as FormattedAmount
            FROM AODMonthlySummary
            WHERE [Month] = FORMAT(GETDATE(), 'yyyy-MM')
        """)
        earnings_monthly = cursor.fetchone()[0] or 0

        # Fetch Expenses (Monthly)
        cursor.execute("""
            SELECT FORMAT(Expense, 'N0') as FormattedAmount
            FROM AODMonthlySummary
            WHERE [Month] = FORMAT(GETDATE(), 'yyyy-MM')
        """)
        expenses_monthly = cursor.fetchone()[0] or 0

        # Calculate Net Profit (Including Withdrawal)
        cursor.execute("""
            SELECT FORMAT(NetProfit, 'N0') AS FormattedAmount
            FROM AODMonthlySummary
            WHERE [Month] = FORMAT(GETDATE(), 'yyyy-MM')
        """)
        net_profit = cursor.fetchone()[0] or 0

        return {
            'cash_on_hand': cash_on_hand,
            'earnings_monthly': earnings_monthly,
            'expenses_monthly': expenses_monthly,
            'net_profit': net_profit
        }

    except Exception as e:
        print(f"Error fetching account summary: {str(e)}")
        return {}

    finally:
        cursor.close()


def fetch_accounts_data(connection):
    cursor = connection.cursor()

    try:
        cursor.execute(
            'SELECT accounts_name, accounts_balance FROM AODaccounts ORDER BY accounts_balance DESC')  # Adjust the query accordingly
        accounts_data = cursor.fetchall()

        formatted_accounts = []

        for row in accounts_data:
            formatted_account = {
                'person_name': row[0],
                'balance': int(row[1]),
            }

            formatted_accounts.append(formatted_account)

        return formatted_accounts

    except Exception as e:
        print(f"Error fetching accounts data: {str(e)}")
        return []

    finally:
        cursor.close()


def fetch_income_list(connection):
    cursor = connection.cursor()

    try:
        # Execute the SQL query
        query = '''
            SELECT TOP 5
                Income_Expense_Name,
                SUM(CAST(Amount AS FLOAT)) AS Amount
            FROM AODIncomeExpenseTable
            WHERE Type = 'Income'
                AND FORMAT(CONVERT(datetime, Payment_Date, 120), 'yyyy-MM') = FORMAT(GETDATE(), 'yyyy-MM')
            GROUP BY Income_Expense_Name
            ORDER BY Amount DESC
        '''
        cursor.execute(query)
        summary_data = cursor.fetchall()

        formatted_data = {
            'income': [row[0] for row in summary_data],
            'net_amounts': [row[1] for row in summary_data]
        }

        return formatted_data

    except Exception as e:
        print(f"Error fetching income and expense summary: {str(e)}")
        return [], []

    finally:
        cursor.close()


def fetch_expenses(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT TOP 5
                Income_Expense_Name,
                SUM(CAST(Amount AS FLOAT)) AS Amount
            FROM AODIncomeExpenseTable
            WHERE Type = 'Expense'
                AND FORMAT(CONVERT(datetime, Payment_Date, 120), 'yyyy-MM') = FORMAT(GETDATE(), 'yyyy-MM')
            GROUP BY Income_Expense_Name
            ORDER BY Amount DESC;
        """)

        summary_data = cursor.fetchall()
        formatted_data = {
            'expense': [row[0] for row in summary_data],
            'net_amounts': [row[1] for row in summary_data]
        }

        return formatted_data

    except Exception as e:
        print(f"Error fetching incomes data: {str(e)}")
        return []

    finally:
        cursor.close()


@app.route('/')
def accounts():
    connection = check_database_connection()

    try:
        if not connection:
            connection = check_database_connection()

        if connection:
            # Fetch account data from your database
            financial_data = fetch_monthly_financial_data(connection)
            accounts = fetch_accounts_data(connection)
            account_summary = fetch_account_summary(connection)
            income_data = fetch_income_list(connection)
            expense_data = fetch_expenses(connection)
            colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796']
            labeled_colors = list(zip(income_data['income'], colors[:len(income_data['income'])]))
            labeled_expenses_colors = list(zip(expense_data['expense'], colors[:len(expense_data['expense'])]))

            return render_template('accounts.html',
                                   labeled_colors=labeled_colors,
                                   colors=colors,
                                   accounts=accounts,
                                   account_summary=account_summary,
                                   financial_data=financial_data,
                                   income_data=income_data,
                                   expense_data=expense_data,
                                   labeled_expenses_colors=labeled_expenses_colors)
        else:
            return render_template('error.html', message="Could not connect to the database. Please try again later.")

    except Exception as e:
        print(f"Error in account_balances route: {str(e)}")
        return render_template('error.html', message="An unexpected error occurred. Please try again later.")

    finally:
        if connection:
            connection.close()


@app.route('/accounts/<account_name>')
def accountData(account_name):
    print(f"Account Name: {account_name}")  # Debug line

    connection = check_database_connection()
    if connection is None:
        return "Database connection error", 500  # Return an error message or page if connection fails

    print("CONNECTED TO DATABASE")

    try:
        with connection.cursor(as_dict=True) as cursor:
            query = "SELECT * FROM AODIncomeExpenseTable WHERE Income_Expense_Name LIKE %s ORDER BY Payment_Date DESC"
            cursor.execute(query, ('%' + account_name + '%',))
            transactions = cursor.fetchall()
    except pymssql.Error as e:
        print(f"Error fetching data from the database: {str(e)}")
        transactions = []  # Ensure transactions is defined
    finally:
        connection.close()

    # Simple template rendering to verify if template works without data
    return render_template('finance_report.html', transactions=transactions)

@app.route('/expense_data')
def expense_data():
    connection = check_database_connection()

    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT e.expense_id, e.expense_title, s.subtype_title
                FROM AODExpenseTypes e
                LEFT JOIN AODExpenseSubtypes s ON e.expense_id = s.expense_id
            """)
            rows = cursor.fetchall()

            expense_data = {}
            for expense_id, expense_title, subtype_title in rows:
                if expense_id not in expense_data:
                    expense_data[expense_id] = {
                        "expense_title": expense_title,
                        "subtypes": []
                    }
                if subtype_title:
                    expense_data[expense_id]["subtypes"].append(subtype_title)

            # Convert the dictionary to the format needed
            response_data = {
                'types': [{'expense_id': k, 'expense_title': v['expense_title']} for k, v in expense_data.items()],
                'subtypes': {str(k): v['subtypes'] for k, v in expense_data.items()}
            }

            return jsonify(response_data)
        else:
            return "Error: No database connection"

    except Exception as e:
        print(f"Error in expense_data route: {str(e)}")
        return "Error in expense_data route"

    finally:
        if connection:
            connection.close()


@app.route('/income_data')
def income_data():
    connection = check_database_connection()

    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT e.income_id, e.income_title, s.subtype_title
                FROM AODincomeTypes e
                LEFT JOIN aodincomesubstypes s ON e.income_id = s.income_id
            """)
            rows = cursor.fetchall()

            income_types = {}
            income_subtypes = []

            for income_id, income_title, subtype_title in rows:
                if income_title not in income_types:
                    income_types[income_title] = income_id
                if subtype_title:
                    income_subtypes.append({
                        'subtype_title': subtype_title,
                        'income_id': income_id
                    })

            # Convert the dictionary to the format needed
            response_data = {
                'types': [{'income_id': v, 'income_title': k} for k, v in income_types.items()],
                'subtypes': income_subtypes
            }

            return jsonify(response_data)
        else:
            return "Error: No database connection"

    except Exception as e:
        print(f"Error in income_data route: {str(e)}")
        return "Error in income_data route"

    finally:
        if connection:
            connection.close()

@app.route('/add_income', methods=['POST'])
def add_income():
    connection = check_database_connection()

    if connection:
        try:
            cursor = connection.cursor()

            amount = request.form['amount']
            income_title = request.form['income_type']
            payment_to = request.form['income_subtype']
            description = request.form.get('description', '')
            submission_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            income_expense_name = f"{income_title} - {payment_to}"

            cursor.execute("""
                INSERT INTO AODIncomeExpenseTable (Income_Expense_Name, Description, Amount, Type, [Payment_Date])
                VALUES (%s, %s, %s, %s, %s)
            """, (income_expense_name, description, amount, 'Income', submission_datetime))

            if income_title == 'Investments':
                cursor.execute("""
                    UPDATE AODaccounts
                    SET accounts_balance = accounts_balance + %s
                    WHERE accounts_name = %s
                """, (amount, payment_to))

            # Always update the 'Bank' account
            cursor.execute("""
                UPDATE AODaccounts
                SET accounts_balance = accounts_balance + %s
                WHERE accounts_name = 'Bank'
            """, (amount,))

            # Commit the transaction
            connection.commit()

            return jsonify({'status': 'success', 'message': 'Income successfully added!'})

        except Exception as e:
            connection.rollback()
            print(f"Error in add_income route: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Error in adding income'})

        finally:
            connection.close()
    else:
        return jsonify({'status': 'error', 'message': 'Error: No database connection'})

from flask import request, jsonify
from datetime import datetime


@app.route('/add_expense', methods=['POST'])
def add_expense():
    connection = check_database_connection()

    if connection:
        try:
            cursor = connection.cursor()

            amount = float(request.form['amount'])  # Convert to float for numeric operations
            expense_title = request.form['expense_type']
            payment_to = request.form['expense_subtype']
            description = request.form.get('description', '')
            submission_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            income_expense_name = f"{expense_title} - {payment_to}"

            # Insert into AODIncomeExpenseTable
            cursor.execute("""
                INSERT INTO AODIncomeExpenseTable (Income_Expense_Name, Description, Amount, Type, [Payment_Date])
                VALUES (%s, %s, %s, %s, %s)
            """, (income_expense_name, description, amount, 'Expense', submission_datetime))

            # Update accounts if expense_title is 'Profit Withdrawal'
            if expense_title == 'Profit Withdrawal' or expense_title == 'Employee Salary' or expense_title == 'Employee Loan':
                cursor.execute("""
                    UPDATE AODaccounts
                    SET accounts_balance = accounts_balance + %s
                    WHERE accounts_name = %s
                """, (amount, payment_to))

            # Always update the 'Bank' account
            cursor.execute("""
                UPDATE AODaccounts
                SET accounts_balance = accounts_balance - %s
                WHERE accounts_name = 'Bank'
            """, (amount,))

            # Commit the transaction
            connection.commit()

            return jsonify({'status': 'success', 'message': 'Expense successfully added!'})

        except Exception as e:
            connection.rollback()
            print(f"Error in add_expense route: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Error in adding expense'})

        finally:
            connection.close()
    else:
        return jsonify({'status': 'error', 'message': 'Error: No database connection'})




shop_url = os.getenv('SHOP_URL')
api_key = os.getenv('API_KEY')
password = os.getenv('PASSWORD')
shopify.ShopifyResource.set_site(shop_url)
shopify.ShopifyResource.set_user(api_key)
shopify.ShopifyResource.set_password(password)
order_details = asyncio.run(getShopifyOrders())

if __name__ == "__main__":
    shop_url = os.getenv('SHOP_URL')
    api_key = os.getenv('API_KEY')
    password = os.getenv('PASSWORD')
    shopify.ShopifyResource.set_site(shop_url)
    shopify.ShopifyResource.set_user(api_key)
    shopify.ShopifyResource.set_password(password)

    app.run(port=5002)

