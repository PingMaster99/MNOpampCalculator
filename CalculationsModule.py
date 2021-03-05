# encoding: utf-8
"""
    CalculationModule.py
    Author: Dario Marroquin 18269   (dariomarroquin)
    Author: Pablo Ruiz 18259        (PingMaster99)
    Version 1.0
    Updated March 4, 2021

    Required functions for the op amp calculator
"""
from sympy import *
import DatabaseConnection as Db

x = symbols('x')
y = symbols('y')
database = Db.Data()


def quadratic_least_square(points):
    """
    Calculates the quadratic least square regression of a set of points
    :param points: points
    :return: a0 and a1 values of the regression
    """
    n = len(points)

    x_summation = ls_summation(points, "x")
    y_summation = ls_summation(points, "y")
    xy_summation = ls_summation(points, "x * y")
    x_squared_summation = ls_summation(points, "x ** 2")

    a0 = (x_squared_summation * y_summation - x_summation * xy_summation) / (n * x_squared_summation - x_summation ** 2)
    a1 = (n * xy_summation - x_summation * y_summation) / (n * x_squared_summation - x_summation ** 2)

    return a0, a1


def ls_summation(points, function):
    """
    Calculates the least square regression needed summations
    :param points: point list
    :param function: function for the summation
    :return: summation result
    """
    ls_result = 0
    function = parse_expr(function)

    for i in range(0, len(points)):
        ls_result += function.evalf(subs={x: points[i][0], y: points[i][1]})
    return ls_result


def populate_calculations(filename=None):
    """
    Loads the database for it to be operated
    :param filename: name of the file
    :return: True if the operation was successful
    """
    if filename is not None:
        try:
            database.set_data(filename)
        except FileNotFoundError:
            return None
    return True


def calculate_opamp_function(point=None, inverter=False):
    """
    Calculates the op amp function using quadratic least square regression
    and evaluates it at a point
    :param point: point to be evaluated
    :param inverter: if the circuit is an inverter or not
    :return: function, evaluation, and theoretical value
    """
    data = database.get_data()
    function_values = quadratic_least_square(data[0])

    if point is not None:
        evaluation = parse_expr(f"{function_values[1]} * x + {function_values[0]}").evalf(subs={x: point})
    else:
        evaluation = "N.A."

    resistors = data[1]
    if inverter:
        real_value = - resistors[1] / resistors[0]
    else:
        real_value = resistors[1] / resistors[0] + 1

    return function_values, evaluation, real_value


def calculate_opamp_spline(point=None):
    """
    Calculates the spline result of the op amp points
    :param point: point to be evaluated
    :return: point, spline result
    """
    if point is None:
        data = database.get_data()[0]
        result = spline(data, quadratic=False)
        print_spline = print_spline_result(result, False)
        return "N.A.", print_spline

    data = database.get_data()[0]
    result = spline(data, quadratic=False)
    print_spline = print_spline_result(result, False)
    return evaluate_spline(point, result, False), print_spline


def print_spline_result(equations, quadratic=True):
    """
    Prints the equations that represent a spline
    :param equations: equations
    :param quadratic: if the spline is quadratic or cubic
    """
    cutoff = 3 if quadratic else 4
    points = equations[1]
    equations = equations[0]
    print_result = ""
    point_index = 0
    element_number = 0

    for element in equations:
        element = round(element, 4)
        if element == 0:
            point_index = (point_index + 1) % cutoff
            if point_index > 2:
                point_index = 0
            continue

        elif element > 0:
            e_sign = "+" if point_index != 0 else ""

        else:
            element = str(element)[1:]
            e_sign = "-"

        print_result += f"{e_sign} {element}"
        if quadratic:
            if point_index == 0:
                print_result += "x^2 "
            elif point_index == 1:
                print_result += "x "
            else:
                print_result += f"    [{points[element_number][0]}, {points[element_number + 1][0]}]\n"
                element_number += 1
        else:
            if point_index == 0:
                print_result += "x^3 "
            elif point_index == 1:
                print_result += f"x^2 "
            elif point_index == 2:
                print_result += "x "
            else:
                print_result += f"    [{points[element_number][0]}, {points[element_number + 1][0]}]\n"
                element_number += 1
        point_index = (point_index + 1) % cutoff
    return print_result[0:len(print_result) - 1]


def calculate_error(point, result, inverter=False):
    """
    Calculates the error of a point
    :param point: point
    :param result: result
    :param inverter: if the circuit is an inverter
    :return: percentage error
    """
    if point is None or result is None:
        return "N.A."
    data = database.get_data()
    resistors = data[1]
    if inverter:
        theoretical_value = - resistors[1] / resistors[0]
    else:
        theoretical_value = resistors[1] / resistors[0] + 1

    real_value = theoretical_value * point

    error = abs((real_value - result) / result) * 100
    return error


def spline(points, quadratic=True):
    """
    Calculates a quadratic or cubic spline of a set of points
    :param points: point list
    :param quadratic: if the spline is quadratic. For cubic, set this to False
    :return: spline equations and intervals
    """
    s_degree = 2 if quadratic else 3
    equations = Matrix([])
    constant_vector = Matrix([])
    zeros_to_add = 0

    # Continuity and extremes
    for i in range(len(points)):

        if len(points) > i > 1:
            zeros_to_add = (i - 1) * (s_degree + 1)

        point_list = []

        if i != 0 and i < len(points) - 1:
            double_insert = True
        else:
            double_insert = False

        # Initial zeros
        for k in range(zeros_to_add):
            point_list.append(0)

        # Coefficients
        for j in range(s_degree, -1, -1):
            point_list.append(points[i][0] ** j)

        # Final zeros
        for k in range((len(points) - 1) * (s_degree + 1) - (s_degree + 1) - zeros_to_add):
            point_list.append(0)

        equations = equations.row_insert(len(equations), Matrix([point_list]))
        constant_vector = constant_vector.row_insert(len(constant_vector), Matrix([points[i][1]]))

        if double_insert:
            for j in range(s_degree + 1):
                point_list.insert(0, 0)
                point_list.pop()
            equations = equations.row_insert(len(equations), Matrix([point_list]))
            constant_vector = constant_vector.row_insert(len(constant_vector), Matrix([points[i][1]]))

    # First derivative
    for i in range(1, len(points) - 1):
        point_list = []
        coefficient = s_degree

        # Initial zeros
        for k in range((i - 1) * (s_degree + 1)):
            point_list.append(0)

        # Coefficients
        for j in range(s_degree - 1, -1, -1):
            point_list.append(coefficient * points[i][0] ** j)
            coefficient -= 1

        point_list.append(0)
        coefficient = s_degree

        for j in range(s_degree - 1, -1, -1):
            point_list.append(-1 * coefficient * points[i][0] ** j)
            coefficient -= 1

        point_list.append(0)

        # Final zeros
        for k in range((len(points) - 1) * (s_degree + 1) - (s_degree + 1) * 2 - (i - 1) * (s_degree + 1)):
            point_list.append(0)

        equations = equations.row_insert(len(equations), Matrix([point_list]))
        constant_vector = constant_vector.row_insert(len(constant_vector), Matrix([[0]]))

    if quadratic:

        point_list = [1]

        for i in range((len(points) - 1) * (s_degree + 1) - 1):
            point_list.append(0)

        equations = equations.row_insert(len(equations), Matrix([point_list]))
        constant_vector = constant_vector.row_insert(len(constant_vector), Matrix([[0]]))

        if equations.det() == 0:
            return None
        return (equations ** -1) * constant_vector, points

    else:
        coefficient = s_degree * 2

        # Second derivative

        # Initial point
        point_list = [6 * points[0][0], 2, 0, 0]
        for i in range((len(points) - 1) * (s_degree + 1) - 4):
            point_list.append(0)

        equations = equations.row_insert(len(equations), Matrix([point_list]))
        constant_vector = constant_vector.row_insert(len(constant_vector), Matrix([[0]]))

        for i in range(1, len(points) - 1):
            point_list = []

            # Initial zeros
            for k in range((i - 1) * (s_degree + 1)):
                point_list.append(0)

            # Coefficients
            for j in range(s_degree - 2, -1, -1):
                point_list.append(coefficient * points[i][0] ** j)
                coefficient -= 4

            point_list.append(0)
            point_list.append(0)
            coefficient = s_degree * 2

            for j in range(s_degree - 2, -1, -1):
                point_list.append(-1 * coefficient * points[i][0] ** j)
                coefficient -= 4

            point_list.append(0)
            point_list.append(0)

            # Final zeros
            for k in range((len(points) - 1) * (s_degree + 1) - (s_degree + 1) * 2 - (i - 1) * (s_degree + 1)):
                point_list.append(0)

            equations = equations.row_insert(len(equations), Matrix([point_list]))
            constant_vector = constant_vector.row_insert(len(constant_vector), Matrix([[0]]))

        # Final point
        point_list = []

        for i in range((len(points) - 1) * (s_degree + 1) - 4):
            point_list.append(0)

        point_list.append(6 * points[len(points) - 1][0])
        point_list.append(2)

        for i in range(2):
            point_list.append(0)

        equations = equations.row_insert(len(equations), Matrix([point_list]))
        constant_vector = constant_vector.row_insert(len(constant_vector), Matrix([[0]]))

        if equations.det() != 0:
            return (equations ** -1) * constant_vector, points
        else:
            return None


def evaluate_spline(point, e_spline, quadratic=True):
    """
    Evaluates a selected point in a spline
    :param point: point to evaluate
    :param e_spline: spline equations and intervals
    :param quadratic: if the spline is quadratic or cubic. Set to False for
    a cubic spline
    :return: The result of the evaluation
    """
    points = e_spline[1]
    equations = e_spline[0]
    equation_index = 0
    equation_offset = 3 if quadratic else 0
    for i in range(len(points) - 1):
        if points[i + 1][0] >= point >= points[i][0]:
            equation_index = i * equation_offset
            break
        if i == (len(points) - 2):
            return None

    if quadratic:
        return parse_expr(f"{equations[equation_index]} * x ** 2 + {equations[equation_index + 1]} * x + "
                          f"{equations[equation_index + 2]}").evalf(subs={x: point})
    else:
        return parse_expr(f"{equations[equation_index]} * x ** 3 + {equations[equation_index + 1]} * x ** 2 + "
                          f"{equations[equation_index + 2]} * x + "
                          f"{equations[equation_index + 3]}").evalf(subs={x: point})


