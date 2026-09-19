from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
from db import get_connection

app = Flask(__name__)

# listar
@app.route("/")
def index():
    busqueda = request.args.get("busqueda", "")

    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        if busqueda:
            cur.execute("""
                SELECT * FROM inventario
                WHERE codigo ILIKE %s OR nombre ILIKE %s
                ORDER BY id ASC
            """, (f"%{busqueda}%", f"%{busqueda}%"))
        else:
            cur.execute("SELECT * FROM inventario ORDER BY id ASC")

        productos = cur.fetchall()

    conn.close()

    return render_template("index.html", productos=productos, busqueda=busqueda)

# crear
@app.route("/inventario/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        codigo = request.form["codigo"]
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        precio = request.form["precio"]
        existencia = request.form["existencia"]
        activo = request.form.get("activo") == "on"

        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO inventario
                (codigo, nombre, categoria, precio, existencia, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (codigo, nombre, categoria, precio, existencia, activo))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("form.html")

# editar
@app.route("/inventario/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_connection()

    if request.method == "POST":
        codigo = request.form["codigo"]
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        precio = request.form["precio"]
        existencia = request.form["existencia"]
        activo = request.form.get("activo") == "on"

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE inventario
                SET codigo = %s,
                    nombre = %s,
                    categoria = %s,
                    precio = %s,
                    existencia = %s,
                    activo = %s
                WHERE id = %s
            """, (codigo, nombre, categoria, precio, existencia, activo, id))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM inventario WHERE id = %s", (id,))
        producto = cur.fetchone()

    conn.close()

    return render_template("form.html", producto=producto)

# elimiar
@app.route("/inventario/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("DELETE FROM inventario WHERE id = %s", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)