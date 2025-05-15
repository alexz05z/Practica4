from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import date, datetime
from bson.objectid import ObjectId

class Usuario:
    def __init__(self, nombre, email, contraseña, fecha_registro ,activo , numero_pedidos):
        self.nombre = nombre
        self.email = email
        self.contraseña = contraseña
        self.fecha_registro = fecha_registro
        self.activo = activo
        self.numero_pedidos = numero_pedidos

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "email": self.email,
            "contraseña": self.contraseña,
            "fecha_registro": self.fecha_registro,
            "activo" : self.activo ,
            "numero_pedidos" : self.numero_pedidos
        }



app = Flask(__name__)

online = MongoClient("mongodb+srv://arodsan013a:T1L7WBu0UDrxvMtH@alexz.lqhssf7.mongodb.net/")

app.db = online.tienda

nombre_admin = "Alejandro"
tienda = "TecnoMarket"
fecha = date.today()

@app.route("/dashboard")
def dashboard():    

    productos = [producto for producto in app.db.productos.find({})]
    clientes = [cliente for cliente in app.db.clientes.find({})]
    pedidos = [
        {"cliente": "Alejandro Rodriguez", "total": 3600.0, "fecha": "2025-05-01"},
        {"cliente": "Pepe Sanchez", "total": 15.5, "fecha": "2025-05-03"},
        {"cliente": "Manolo Gomez", "total": 5000.0, "fecha": "2025-05-04"}
    ]
    total_stock = 0
    for producto in productos:
        total_stock += producto["stock"]

    clientes_activos = 0
    for cliente in clientes:

        activo = cliente["activo"]
        activo = activo.lower()
        if activo == "activo" :
            clientes_activos += 1

    cliente_pedido = clientes[0]
    for cliente in clientes:
        if cliente["numero_pedidos"] > cliente_pedido["numero_pedidos"]:
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


        id_mas_alto = 0


        for producto in productos:
            if "id" in producto and producto["id"] > id_mas_alto:
                id_mas_alto = producto["id"]


        nuevo_id = id_mas_alto + 1


        nuevo_producto = {
            "id": nuevo_id,
            "nombre": request.form["nombre"],
            "precio": float(request.form["precio"]),
            "stock": int(request.form["stock"]),
            "categoria": request.form["categoria"]
        }

        app.db.productos.insert_one(nuevo_producto)
        mensaje = "Producto añadido correctamente."

    return render_template("añadir_producto.html", mensaje=mensaje, fecha=fecha)



@app.route("/productos")
def ver_productos():
    productos_cursor = app.db.productos.find()
    productos = []
    for producto in productos_cursor:
        producto["_id"] = str(producto["_id"])
        productos.append(producto)
    return render_template("lista_productos.html", productos=productos,fecha=fecha)


@app.route("/productos/<id_producto>")
def detalle_producto(id_producto):
    producto = app.db.productos.find_one({"_id": ObjectId(id_producto)})
    if producto:
        return render_template("detalle_producto.html", producto=producto,fecha=fecha)
    else:
        return render_template("404.html",fecha=fecha), 404


@app.route("/registro-usuarios", methods=["GET", "POST"])
def registro_usuario():
    mensaje = ""
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        contraseña = request.form["contraseña"]
        activo =request.form["activo"]
        numero_pedidos =int(request.form["pedidos"])
        nuevo_usuario = Usuario(nombre, email, contraseña, datetime.now() ,activo ,numero_pedidos)
        app.db.clientes.insert_one(nuevo_usuario.to_dict())
        mensaje = "Usuario registrado con éxito."
    return render_template("registro_usuarios.html", mensaje=mensaje, fecha=fecha)


@app.route("/usuarios")
def lista_usuarios():
    usuarios = [app.db.clientes.find()]
    return render_template("lista_usuarios.html", usuarios=usuarios, fecha=fecha)


@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run()