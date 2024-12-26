import os
import time
import csv

# Existing File, Balance, and Inventory classes (unchanged)
class File:
    def __init__(self, date, n_package, weight):
        self.date = date
        self.n_package = n_package
        self.weight = weight

    def __str__(self):
        return f"{self.date}, {self.n_package}, {self.weight}"

class Balance(File):
    def __init__(self, date, n_package, weight, amount):
        super().__init__(date, n_package, weight)
        self.amount = amount

    def __str__(self):
        return f"{super().__str__()}, {self.amount}"

class Inventory(File):
    def __init__(self, date, n_package, weight, amount):
        super().__init__(date, n_package, weight)
        self.amount = amount

    def __str__(self):
        return f"{super().__str__()}, {self.amount}"

# File paths (unchanged)
directory = os.getcwd()
balance_file = directory + '\Balance.txt'
inventory_file = directory + '\Inventory.txt'
history_file = directory + '\History.txt'


# Load and save functions (unchanged)
def load_data_from_file(file_name):
    data = []
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', newline='') as f:
                reader = csv.reader(f)
                next(reader)  # jump header
                for row in reader:
                    data.append(row)
        except Exception as e:
            print(f"Error loading file {file_name}: {e}")
    return data

def save_data_to_file(file_name, data, header):
    try:
        with open(file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
                writer.writerow(header)
            for row in data:
                writer.writerow(row)
    except Exception as e:
        print(f"Error saving data in file {file_name}: {e}")


# Load data from the files
balance_data = load_data_from_file(balance_file)
inventory_data = load_data_from_file(inventory_file)
history_data = load_data_from_file(history_file)

# Initialize lists from loaded data
balance_lst = [Balance(*data) for data in balance_data]
inventory_lst = [Inventory(*data) for data in inventory_data]

# Add history operation
def add_to_history(operation, date):
    history_data.append([date, operation])
    save_data_to_file(history_file, history_data, ["Date", "Operation"])


# Manager class with decorators and assign method
class Manager:
    def __init__(self):
        self.operations = {
            "purchase": self.purchase_item,
            "sale": self.sale_item,
            "balance": self.show_balance,
            "inventory": self.show_inventory
        }

    # Decorator to log operation
    def log_operation(func):
        def wrapper(self, *args, **kwargs):
            curr_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
            print(f"Operation started at {curr_time}")
            result = func(self, *args, **kwargs)
            print(f"Operation completed at {curr_time}")
            return result
        return wrapper

    # Decorator to validate input for purchase and sale
    def validate_input(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
        return wrapper

    # Purchase operation with decorators
    @log_operation
    @validate_input
    def purchase_item(self):
        print("\n--- Purchasing item ---")
        item_weight = abs(round(float(input("Add weight (kg): ")), 2))
        item_amount = abs(round(float(input("Add amount (€): ")), 2))
        curr_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())

        item = Balance(curr_time, len(balance_lst) + 1, item_weight, item_amount)
        balance_lst.append(item)
        inventory_lst.append(item)

        save_data_to_file(balance_file, [(item.date, item.n_package, item.weight, item.amount)], ["Date", "Package Number", "Weight", "Amount"])
        save_data_to_file(inventory_file, [(item.date, item.n_package, item.weight, item.amount)], ["Date", "Package Number", "Weight", "Amount"])

        add_to_history("Purchase made", curr_time)
        print(f"Purchase made: {item.amount}€ by {item.weight}kg")

    # Sale operation with decorators
    @log_operation
    @validate_input
    def sale_item(self):
        print("\n--- Making sale ---")
        item_weight = abs(round(float(input("Add weight (kg): ")), 2))
        item_amount = abs(round(float(input("Add amount (€): ")), 2))
        curr_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())

        item = Balance(curr_time, len(balance_lst) + 1, item_weight, -item_amount)
        balance_lst.append(item)
        inventory_lst.append(item)

        save_data_to_file(balance_file, [(item.date, item.n_package, item.weight, item.amount)], ["Date", "Package Number", "Weight", "Amount"])
        save_data_to_file(inventory_file, [(item.date, item.n_package, item.weight, item.amount)], ["Date", "Package Number", "Weight", "Amount"])

        add_to_history("Sale made", curr_time)
        print(f"Sale made: {item.amount}€ by {item.weight}kg")

    # Balance operation with decorators
    @log_operation
    def show_balance(self):
        try:
            total_balance = sum([float(item.amount) for item in balance_lst])
            print(f"Total balance: {total_balance}€")
        except ValueError:
            print("Error calculating balance.")

    # Inventory operation with decorators
    @log_operation
    def show_inventory(self):
        print("\n--- Current inventory ---")
        for item in inventory_lst:
            print(item)

    # Assign method to map operations
    def assign(self, task):
        if task in self.operations:
            self.operations[task]()
        else:
            print("Invalid task.")


# Main Menu
def main_menu():
    manager = Manager()

    while True:
        print("\n--- Menú de operaciones ---\n" +
              "1. Make purchase\n" +
              "2. Make sale\n" +
              "3. See balance\n" +
              "4. View inventory\n" +
              "5. Exit\n")
        try:
            option = int(input("\nChoose one option: "))

            if option == 1:
                manager.assign("purchase")
            elif option == 2:
                manager.assign("sale")
            elif option == 3:
                manager.assign("balance")
            elif option == 4:
                manager.assign("inventory")
            elif option == 5:
                print("Thank you for using the system.")
                # Save all data before exit
                save_data_to_file(balance_file,
                                  [(item.date, item.n_package, item.weight, item.amount) for item in balance_lst],
                                  ["Date", "Package Number", "Weight", "Amount"])
                save_data_to_file(inventory_file,
                                  [(item.date, item.n_package, item.weight, item.amount) for item in inventory_lst],
                                  ["Date", "Package Number", "Weight", "Amount"])
                save_data_to_file(history_file, history_data, ["Date", "Operation"])
                exit()
            else:
                print("Invalid option. Try again.")
        except ValueError:
            print("Please enter a valid number.")


# Run the program
if __name__ == "__main__":
    print("------------ Welcome to warehouse accounting system -------------------------")
    main_menu()
