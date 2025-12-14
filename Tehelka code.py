import numpy as np
import matplotlib.pyplot as plt
import csv

# ============================================================
# PYTHON GRAPH PLOTTER WITH CSV CRUD SUPPORT (CLI)
# ============================================================

CSV_FILE = 'graph.csv'

# ------------------------------------------------------------
# Allowed mathematical functions and constants
# ------------------------------------------------------------
ALLOWED = {
    'sin': np.sin,
    'cos': np.cos,
    'tan': np.tan,
    'asin': np.arcsin,
    'acos': np.arccos,
    'atan': np.arctan,
    'sqrt': np.sqrt,
    'log': np.log,
    'pi': np.pi,
    'e': np.e
}


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def print_line():
    print('-' * 60)


def print_header(title):
    print_line()
    print(title.center(60))
    print_line()


def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print('Invalid number. Try again.')


def get_positive_int(prompt):
    while True:
        try:
            v = int(input(prompt))
            if v <= 0:
                raise ValueError
            return v
        except ValueError:
            print('Enter a positive integer.')


# ------------------------------------------------------------
# X-axis handling
# ------------------------------------------------------------

def get_x_range():
    print_header('X-AXIS CONFIGURATION')
    while True:
        start = get_float('Enter starting value of x-axis: ')
        end = get_float('Enter ending value of x-axis: ')
        if start >= end:
            print('Start must be less than end.')
            continue
        points = int((end - start) * 200)
        if points < 100:
            points = 100
        x = np.linspace(start, end, points)
        return start, end, x


# ------------------------------------------------------------
# Equation handling
# ------------------------------------------------------------

def validate_equation(expr, x):
    try:
        eval(expr, {'__builtins__': {}}, {**ALLOWED, 'x': x})
        return True
    except Exception:
        return False


def get_equations(x):
    print_header('EQUATION INPUT')
    equations = []
    count = get_positive_int('How many equations do you want to plot? ')
    for i in range(count):
        expr = input(f'Enter equation {i + 1} (use x): ')
        if validate_equation(expr, x):
            equations.append(expr)
            print('Equation accepted.')
        else:
            print('Invalid equation. Skipped.')
    return equations


# ------------------------------------------------------------
# Y-axis handling
# ------------------------------------------------------------

def get_y_limits():
    print_header('Y-AXIS CONFIGURATION')
    choice = input('Restrict y-axis? (y/n): ').lower()
    if choice == 'y':
        low = get_float('Enter lower y-limit: ')
        high = get_float('Enter upper y-limit: ')
        if low >= high:
            print('Invalid limits. Ignoring.')
            return None
        return low, high
    return None


# ------------------------------------------------------------
# Plotting
# ------------------------------------------------------------

def plot_graph(x, equations, y_limits):
    print_header('PLOTTING GRAPH')
    fig, ax = plt.subplots()
    for expr in equations:
        try:
            y = eval(expr, {'__builtins__': {}}, {**ALLOWED, 'x': x})
            ax.plot(x, y, label=expr)
        except Exception as e:
            print('Failed to plot:', expr, e)
    ax.set_title(f'Graphs of {equations}')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.grid(True)
    if y_limits:
        ax.set_ylim(y_limits[0], y_limits[1])
    ax.legend()
    plt.show()


# ------------------------------------------------------------
# CSV CRUD OPERATIONS
# ------------------------------------------------------------

def create_record(start, end, equations, y_limits):
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            ';'.join(equations),
            start,
            end,
            y_limits[0] if y_limits else '',
            y_limits[1] if y_limits else ''
        ])


def read_records():
    print_header('SAVED GRAPHS')
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader, start=1):
                print(f'{i}. Eq: {row[0]} | X: {row[1]} to {row[2]} | Y: {row[3]}, {row[4]}')
    except FileNotFoundError:
        print('No saved graphs found.')


def plot_record_from_csv(index):
    try:
        with open(CSV_FILE, 'r') as f:
            records = list(csv.reader(f))
    except FileNotFoundError:
        print('No saved graphs found.')
        return

    if index < 1 or index > len(records):
        print('Invalid record number.')
        return

    row = records[index - 1]
    equations = row[0].split(';')
    start = float(row[1])
    end = float(row[2])
    y_limits = None
    if row[3] != '' and row[4] != '':
        y_limits = (float(row[3]), float(row[4]))

    points = int((end - start) * 200)
    if points < 100:
        points = 100
    x = np.linspace(start, end, points)

    plot_graph(x, equations, y_limits)


def update_record(index):
    try:
        with open(CSV_FILE, 'r') as f:
            records = list(csv.reader(f))
    except FileNotFoundError:
        print('No records to update.')
        return

    if index < 1 or index > len(records):
        print('Invalid record number.')
        return

    start, end, x = get_x_range()
    equations = get_equations(x)
    y_limits = get_y_limits()

    records[index - 1] = [
        ';'.join(equations),
        start,
        end,
        y_limits[0] if y_limits else '',
        y_limits[1] if y_limits else ''
    ]

    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(records)

    print('Record updated successfully.')


def delete_record(index):
    try:
        with open(CSV_FILE, 'r') as f:
            records = list(csv.reader(f))
    except FileNotFoundError:
        print('No records to delete.')
        return

    if index < 1 or index > len(records):
        print('Invalid record number.')
        return

    records.pop(index - 1)

    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(records)

    print('Record deleted successfully.')


# ------------------------------------------------------------
# Main controller
# ------------------------------------------------------------

def main():
    print_header('PYTHON GRAPH PLOTTER')

    start, end, x = get_x_range()
    equations = get_equations(x)

    if not equations:
        print('No valid equations. Exiting.')
        return

    y_limits = get_y_limits()
    plot_graph(x, equations, y_limits)

    save = input('Save this graph to CSV? (y/n): ').lower()
    if save == 'y':
        create_record(start, end, equations, y_limits)
        print('Graph saved.')

    while True:
        print_header('CSV CRUD MENU')
        print('1. Read saved graphs')
        print('2. Plot a saved graph')
        print('3. Update a saved graph')
        print('4. Delete a saved graph')
        print('5. Exit')

        choice = input('Enter choice: ')

        if choice == '1':
            read_records()
        elif choice == '2':
            idx = get_positive_int('Enter record number: ')
            plot_record_from_csv(idx)
        elif choice == '3':
            idx = get_positive_int('Enter record number: ')
            update_record(idx)
        elif choice == '4':
            idx = get_positive_int('Enter record number: ')
            delete_record(idx)
        elif choice == '5':
            break
        else:
            print('Invalid choice.')

    print_line()
    print('Program ended.')
    print_line()


#calling the funtion
main()