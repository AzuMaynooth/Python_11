import os
import time
import csv

class File:
    def __init__(self, name, date, n_package, weight):
        self.name = name
        self.date = date
        self.n_package = n_package
        self.weight = weight

    def __str__(self):
        return f"{self.name},{self.date}, {self.n_package}, {self.weight}"

class Balance(File):
    def __init__(self, name, date, n_package, n_units, total_price):
        super().__init__(name, date, n_package, total_price)
        self.n_units = n_units  # Número de unidades vendidas o compradas (positivo siempre)
        self.total_price = total_price  # Precio total (positivo o negativo)

    def __str__(self):
        return f"{self.name},{self.date},{self.n_package},{self.n_units},{self.total_price}"


class Inventory(File):
    def __init__(self, name, date, n_package, weight, price_per_unit):
        super().__init__(name, date, n_package, weight)
        self.price_per_unit = price_per_unit  # Guardamos el precio por unidad

    def __str__(self):
        return f"{super().__str__()}, {self.price_per_unit}"

class Shipment:
    def __init__(self, shipment_id, item_name, shipment_date, destination, shipping_cost):
        self.shipment_id = shipment_id
        self.item_name = item_name
        self.shipment_date = shipment_date
        self.destination = destination
        self.shipping_cost = shipping_cost

    def __str__(self):
        return f"{self.shipment_id}, {self.item_name}, {self.shipment_date}, {self.destination}, {self.shipping_cost}"





# Directories and files
directory = os.getcwd()
balance_file = directory + '\\Balance.txt'
inventory_file = directory + '\\Inventory.txt'
history_file = directory + '\\History.txt'
shipment_file = directory + '\\shipment_file.txt'


# Load data from file
def load_data_from_file(file_name):
    data = []
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', newline='') as f:
                reader = csv.reader(f)
                next(reader)  # skip header
                for row in reader:
                    data.append(row)
        except Exception as e:
            print(f"Error loading file {file_name}: {e}")
    return data

# Save data to file
def save_data_to_file(file_name, data, header):
    try:
        with open(file_name, 'w', newline='') as f:  # Cambiado 'a' por 'w' para sobrescribir el archivo
            writer = csv.writer(f)
            writer.writerow(header)
            for row in data:
                writer.writerow(row)
    except Exception as e:
        print(f"Error saving data in file {file_name}: {e}")


# Load existing data from files
balance_data = load_data_from_file(balance_file)
inventory_data = load_data_from_file(inventory_file)
history_data = load_data_from_file(history_file)

# Initialize lists from loaded data
balance_lst = [Balance(data[0], data[1], int(data[2]), float(data[3]), float(data[4])) for data in balance_data]
inventory_lst = [Inventory(data[0], data[1], int(data[2]), float(data[3]), float(data[4])) for data in inventory_data]
shipments = []

# Records on historical
def add_to_history(operation, details):
    curr_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
    history_data.append([curr_time, operation, details])
    save_data_to_file(history_file, history_data, ["Date", "Operation", "Details"])


# Manager class with decorators and assign method
import time
import functools

class Manager:
    def __init__(self):
        self.operations = {
            "purchase": self.purchase_item,
            "sale": self.sale_item,
            "balance": self.show_balance,
            "inventory": self.show_inventory,
            "send": self.send_item
        }

    def clean_inventory(self):
        global inventory_lst

        # Filtrar el inventario para eliminar cualquier artículo con peso 0 o atributos vacíos
        inventory_lst = [item for item in inventory_lst if item.name and item.weight > 0]

        print("Inventory cleaned. Removed invalid or empty items.")
    def clean_balance(self):
        global balance_lst

        # Filtrar transacciones para eliminar aquellas con total_price vacío o n_units vacío
        balance_lst = [entry for entry in balance_lst if
                       entry.name and entry.total_price is not None and entry.n_units > 0]

        print("Balance cleaned. Removed invalid or empty transactions.")

    def calculate_shipping_cost(self, quantity):
        # Determinar el costo de envío basado en la cantidad
        if quantity > 50:
            shipping_cost = 5  # Si la cantidad es mayor a 50, añadir 5€ de costo de envío
        else:
            shipping_cost = 2  # Si la cantidad es 50 o menos, añadir 2€ de costo de envío

        return shipping_cost
    # Decorator to log operation
    def log_operation(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            curr_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
            #print(f"Operation '{func.__name__}' started at {curr_time}")
            #print(f"Inputs: {args} {kwargs}")
            result = func(self, *args, **kwargs)
            #print(f"Operation '{func.__name__}' completed at {curr_time}")
            #print(f"Result: {result}")
            return result

        return wrapper

    # Decorator to validate input for purchase and sale
    def validate_input(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
                return None

        return wrapper

    # Purchase operation with decorators
    # Compra: Actualizar o agregar inventario
    @log_operation
    @validate_input
    def purchase_item(self):
        print("\n--- Purchasing item ---")
        try:
            item_name = str(input("Add item name: ")).strip()
            quantity = abs(int(input("How many units/kg?: ")))
            price_per_unit = abs(float(input("Add price per unit/kg (€): ")))
            total_cost = price_per_unit * quantity
            curr_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())

            # Actualizar inventario
            existing_item = next((item for item in inventory_lst if item.name == item_name), None)
            if existing_item:
                # Recalcular precio promedio por unidad
                total_weight = existing_item.weight + quantity
                existing_item.price_per_unit = (
                                                       (
                                                                   existing_item.weight * existing_item.price_per_unit) + total_cost
                                               ) / total_weight
                existing_item.weight = total_weight
            else:
                inventory_lst.append(Inventory(item_name, curr_time, len(inventory_lst) + 1, quantity, price_per_unit))

            # Actualizar balance
            balance_lst.append(Balance(item_name, curr_time, len(balance_lst) + 1, quantity, -total_cost))

            # Guardar en historial
            add_to_history("Purchase", f"Item: {item_name}, Quantity: {quantity}, Total Cost: {total_cost}€")
            print(f"Purchase completed: {item_name}, Quantity: {quantity}, Total Cost: {total_cost}€")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # Sale operation with decorators
    # Venta: Actualizar inventario

    @log_operation
    @validate_input
    def sale_item(self):
        print("\n--- Making sale ---")
        try:
            item_name = str(input("Enter the item name: ")).strip()
            existing_item = next((item for item in inventory_lst if item.name == item_name), None)

            if not existing_item:
                print(f"Error: The item '{item_name}' is not in the inventory.")
                return

            while True:
                quantity_input = input("Enter quantity to sell: ").strip()
                if not quantity_input.isdigit():
                    print("Error: Please enter a valid number for the quantity.")
                    continue
                quantity_to_sell = abs(int(quantity_input))
                break  # Valid input, exit loop

            if quantity_to_sell > existing_item.weight:
                print(f"Error: Not enough {item_name} in inventory. Available: {existing_item.weight}.")
                return

            # Detalles de la venta
            price_per_unit = existing_item.price_per_unit
            total_sale = price_per_unit * quantity_to_sell
            curr_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())

            # Actualizar inventario
            existing_item.weight -= quantity_to_sell
            if existing_item.weight == 0:
                inventory_lst.remove(existing_item)

            # Actualizar balance
            balance_lst.append(Balance(item_name, curr_time, len(balance_lst) + 1, quantity_to_sell, total_sale))

            # Guardar en historial
            add_to_history("Sale", f"Item: {item_name}, Quantity: {quantity_to_sell}, Total Sale: {total_sale}€")
            print(f"Sale completed: {item_name}, Quantity: {quantity_to_sell}, Total Sale: {total_sale}€")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def show_balance(self):
        print("\n--- Showing Detailed Balance ---")
        if not balance_lst:
            print("No transactions have been recorded yet.")
            return

        # Mostrar detalles de las transacciones
        print(f"{'Item Name':<20}{'Date':<20}{'Quantity':<15}{'Total Price (€)':<20}{'Transaction Type':<20}")
        print("-" * 95)

        # Detalles de cada transacción
        for entry in balance_lst:
            # Identificar si es un costo de envío
            if entry.total_price < 0 and entry.n_units == 0:
                transaction_type = "Shipping Cost"
            elif entry.total_price > 0:
                transaction_type = "Sale"
            elif entry.total_price < 0:
                transaction_type = "Purchase"
            else:
                transaction_type = "Unknown"

            print(
                f"{entry.name:<20}{entry.date:<20}{entry.n_units:<15}{entry.total_price:<20.2f}{transaction_type:<20}")

        # Cálculo de métricas
        total_income = sum(entry.total_price for entry in balance_lst if entry.total_price > 0)
        total_expenses = sum(entry.total_price for entry in balance_lst if entry.total_price < 0)
        total_balance = total_income + total_expenses

        # Mostrar métricas finales
        print("-" * 95)
        print(f"{'Total Income':<20}{total_income:<15.2f}")
        print(f"{'Total Expenses':<20}{total_expenses:<15.2f}")
        print(f"{'Net Balance':<20}{total_balance:<15.2f}")
        print("-" * 95)

    @log_operation
    def show_inventory(self):
        print("\n--- Current Inventory ---")
        if not inventory_lst:
            print("The inventory is empty.")
            return

        print(f"{'Item Name':<20}{'Date Added':<20}{'Quantity (kg)':<15}{'Price/Unit (€)':<15}")
        print("-" * 70)
        for item in inventory_lst:
            print(f"{item.name:<20}{item.date:<20}{item.weight:<15.2f}{item.price_per_unit:<15.2f}")
        print("-" * 70)

        # Enviar artículo (registro de envío)

    @log_operation
    def send_item(self):
        print("\n--- Sending item ---")
        while True:
            item_name = str(input("Enter the item name (or type 'end' to stop): ")).strip()

            # Si el usuario escribe "end", se detiene el proceso
            if item_name.lower() == "end":
                print("Ending the shipment process.")
                return  # Volver al menú principal

            # Verificar que el artículo exista en el inventario
            existing_item = next((item for item in inventory_lst if item.name == item_name), None)
            if not existing_item:
                print(f"Error: The item '{item_name}' is not in the inventory. Try again or type 'end'.")
                continue  # Volver a pedir el nombre del artículo

            print(f"Item found! Quantity available: {existing_item.weight} kg.")  # Mostrar cantidad disponible

            while True:
                try:
                    # Validación de la cantidad a enviar
                    quantity_to_send = abs(int(input(f"Enter quantity to send (max {existing_item.weight} kg): ")))

                    # Verificar que la cantidad a enviar no sea mayor que la cantidad disponible
                    if quantity_to_send > existing_item.weight:
                        print(f"Error: You cannot send more than {existing_item.weight} kg. Try again.")
                    elif quantity_to_send <= 0:
                        print("Error: Quantity must be greater than zero. Try again.")
                    else:
                        # Calcular el costo de envío
                        shipping_cost = self.calculate_shipping_cost(quantity_to_send)

                        # Pedir el destino y validarlo
                        destination = input("Enter destination: ").strip()
                        if not destination:
                            print("Error: Destination cannot be empty. Try again.")
                            continue  # Pedir destino nuevamente

                        # Crear el registro de envío
                        shipment_id = len(shipments) + 1
                        shipment_date = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())

                        # Crear y agregar el envío a la lista
                        shipment = Shipment(shipment_id, item_name, shipment_date, destination, shipping_cost)
                        shipments.append(shipment)

                        # Actualizar inventario (restando el peso enviado)
                        existing_item.weight -= quantity_to_send
                        if existing_item.weight == 0:
                            inventory_lst.remove(existing_item)

                        # **Contabilizar la venta como una transacción en el balance**
                        total_sale_value = existing_item.price_per_unit * quantity_to_send

                        # Registrar el envío como una venta en el balance (sin costo de envío)
                        balance_lst.append(
                            Balance(item_name, shipment_date, len(balance_lst) + 1, quantity_to_send, total_sale_value))

                        # Registrar el costo de envío como un gasto en el balance
                        balance_lst.append(
                            Balance(item_name, shipment_date, len(balance_lst) + 1, 0,
                                    -shipping_cost))  # Gasto de envío

                        # **Registrar el costo de envío en el historial de transacciones**
                        add_to_history("Shipping Cost",
                                       f"Item: {item_name}, Quantity: {quantity_to_send}, Shipping Cost: {shipping_cost}€")
                        print(
                            f"Shipment completed: {item_name}, Quantity: {quantity_to_send}, Shipping Cost: {shipping_cost}€")

                        # Limpiar inventario y balance
                        self.clean_inventory()
                        self.clean_balance()

                        # Guardar los cambios en los archivos de inventario y balance
                        save_data_to_file(
                            inventory_file,
                            [(entry.name, entry.date, entry.n_package, entry.weight, entry.price_per_unit) for entry in
                             inventory_lst],
                            ["Name", "Date", "Package Number", "Weight", "Price per Unit"]
                        )

                        save_data_to_file(
                            balance_file,
                            [(entry.name, entry.date, entry.n_package, entry.n_units, entry.total_price) for entry in
                             balance_lst],
                            ["Name", "Date", "Package Number", "N units", "Total Price"]
                        )

                        save_data_to_file(
                            shipment_file,
                            [(shipment.shipment_id, shipment.item_name, shipment.shipment_date,
                              shipment.destination, shipment.shipping_cost) for shipment in shipments],
                            ["Shipment ID", "Item Name", "Shipment Date", "Destination", "Shipping Cost"]
                        )

                        break  # Envío exitoso, salimos del bucle

                except ValueError:
                    print("Error: Please enter a valid number for quantity.")

    # Method to assign tasks
    def assign(self, task):
        if task in self.operations:
            self.operations[task]()  # Call the method dynamically
        else:
            print("Invalid task.")


# Main Menu

def main_menu():
    manager = Manager()
    while True:
        print("\n--- Operations Menu ---\n" +
              "1. Make purchase\n" +
              "2. Make sale\n" +
              "3. See balance\n" +
              "4. View inventory\n" +
              "5. Send item\n" +
              "6. Exit\n")
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
                manager.assign("send")
            elif option == 6:
                print("Thank you for using the system.")
                save_data_to_file(
                    balance_file,
                    [(entry.name, entry.date, entry.n_package, entry.n_units, entry.total_price) for entry in
                     balance_lst],
                    ["Name", "Date", "Package Number", "N units", "Total Price"]
                )

                # Guardar en archivo Inventory.txt
                save_data_to_file(inventory_file,
                    [(entry.name, entry.date, entry.n_package, entry.weight, entry.price_per_unit) for entry in
                     inventory_lst],
                    ["Name", "Date", "Package Number", "Weight", "Price per Unit"])
                save_data_to_file(history_file, history_data, ["Date", "Operation"])
                save_data_to_file(shipment_file, [(shipment.shipment_id, shipment.item_name, shipment.shipment_date,
                                                   shipment.destination, shipment.shipping_cost) for shipment in
                                                  shipments],
                                  ["Shipment ID", "Item Name", "Shipment Date", "Destination", "Shipping Cost"])
                exit()
            else:
                print("Invalid option. Try again.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation interrupted. Exiting gracefully.")
            break  # Exit the loop on keyboard interrupt


# Run the program
if __name__ == "__main__":
    print("------------ Welcome to warehouse accounting system -------------------------")
    main_menu()
