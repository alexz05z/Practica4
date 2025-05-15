from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import datetime
from datetime import date

class Usuario:
    def __init__(self, nombre, email, contraseña, fecha_registro):
        self.nombre = nombre
        self.email = email
        self.contraseña = contraseña
        self.fecha_registro = fecha_registro

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "email": self.email,
            "contraseña": self.contraseña,
            "fecha_registro": self.fecha_registro
        }



app = Flask(__name__)

online = MongoClient("mongodb+srv://jjen527:35OpRHzih8l1N14m@jjannik.aliwych.mongodb.net/")

app.db = online.tienda

nombre_admin = "Jannik"
tienda = "TecnoMarket"
fecha = date.today()


@app.route("/dashboard")
def inicio():    

    productos = [producto for producto in app.db.productos.find({})]
    clientes = [cliente for cliente in app.db.clientes.find({})]
    pedidos = [pedido for pedido in app.db.pedidos.find({})]

    total_stock = 0
    for producto in productos:
        total_stock += producto["stock"]

    clientes_activos = 0
    for cliente in clientes:
        if cliente["activo"]:
            clientes_activos += 1

    cliente_pedido = clientes[0]
    for cliente in clientes:
        if cliente["pedidos"] > cliente_pedido["pedidos"]:
            cliente_pedido = cliente


    total = 0
    for pedido in pedidos:
        total += pedido["total"]

    return render_template("dashboard.html",nombre_admin=nombre_admin,tienda=tienda,fecha=fecha,productos=productos,clientes=clientes,pedidos=pedidos,total=total,cliente_pedido=cliente_pedido,clientes_activos=clientes_activos,total_stock=total_stock)





@app.route("/añadir-producto", methods=["GET", "POST"])
def añadir_producto():
    mensaje = None
    if request.method == "POST":
        productos = [app.db.productos.find()]

        # Paso 1: Creamos una variable para guardar el id más alto
        id_mas_alto = 0

        # Paso 2: Recorremos cada producto y revisamos su id
        for producto in productos:
            if "id" in producto and producto["id"] > id_mas_alto:
                id_mas_alto = producto["id"]

        # Paso 3: El nuevo id será uno más
        nuevo_id = id_mas_alto + 1

        # Crear y guardar el producto
        nuevo_producto = {
            "id": nuevo_id,
            "nombre": request.form["nombre"],
            "precio": float(request.form["precio"]),
            "stock": int(request.form["stock"]),
            "categoria": request.form["categoria"]
        }

        app.db.productos.insert_one(nuevo_producto)
        mensaje = "Producto añadido correctamente."

    return render_template("añadir_producto.html", mensaje=mensaje)


# Ruta: Ver productos
@app.route("/productos")
def ver_productos():
    productos = [app.db.productos.find()]
    return render_template("lista_productos.html", productos=productos)

# Ruta: Detalle producto
@app.route("/productos/<int:id_producto>")
def detalle_producto(id_producto):
    producto = app.db.productos.find_one({"id": id_producto})
    if producto:
        return render_template("detalle_producto.html", producto=producto)
    else:
        return render_template("404.html"), 404

# Ruta: Registro de usuario
@app.route("/registro-usuario", methods=["GET", "POST"])
def registro_usuario():
    mensaje = ""
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        contraseña = request.form["contraseña"]
        nuevo_usuario = Usuario(nombre, email, contraseña, datetime.now())
        app.db.clientes.insert_one(nuevo_usuario.to_dict())
        mensaje = "Usuario registrado con éxito."
    return render_template("registro_usuario.html", mensaje=mensaje)

# Ruta: Lista de usuarios
@app.route("/usuarios")
def lista_usuarios():
    usuarios = [app.db.clientes.find()]
    return render_template("lista_usuarios.html", usuarios=usuarios)

# Ruta: Error 404
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run()