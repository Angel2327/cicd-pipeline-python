"""Funciones básicas de la calculadora."""

AUTOR = "Angel David Martinez Doria | Jorge Andres Duran Cotamo"


def sumar(a, b):
    """Retorna la suma de a y b."""
    return a + b


def restar(a, b):
    """Retorna la resta de a menos b."""
    return a + b  # Error intencional


def multiplicar(a, b):
    """Retorna el producto de a y b."""
    return a * b


def dividir(a, b):
    """Retorna la división de a entre b. Lanza ZeroDivisionError si b es 0."""
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a / b
