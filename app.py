from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DIGITO_A_VALOR = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, 'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
}
VALOR_A_DIGITO = {v: k for k, v in DIGITO_A_VALOR.items()}

BASES_VALIDAS = {2: "Binario", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}
BITS_POR_DIGITO = {2: 1, 8: 3, 10: None, 16: 4}  # None = no aplica padding fijo


def validar_caracteres(valor, base):

    if valor == "":
        return False
    for caracter in valor:
        if caracter not in DIGITO_A_VALOR:
            return False
        if DIGITO_A_VALOR[caracter] >= base:
            return False
    return True


def calcular_maximo(bits):
  
    maximo = 1
    for _ in range(bits):
        maximo = maximo * 2
    return maximo - 1

def a_decimal(valor, base_origen):
   
    digitos_invertidos = valor[::-1]
    decimal = 0
    for posicion, caracter in enumerate(digitos_invertidos):
        valor_digito = DIGITO_A_VALOR[caracter]
        potencia = 1
        for _ in range(posicion):
            potencia = potencia * base_origen
        decimal = decimal + (valor_digito * potencia)
    return decimal


def desde_decimal(decimal, base_destino):

    if decimal == 0:
        return "0"

    residuos = []
    n = decimal
    while n > 0:
        residuo = n % base_destino
        residuos.append(VALOR_A_DIGITO[residuo])
        n = n // base_destino

    residuos.reverse()
    return "".join(residuos)


def aplicar_padding(cadena, bits, base):

    bits_por_digito = BITS_POR_DIGITO[base]
    if bits_por_digito is None: 
        return cadena

    digitos_necesarios = bits // bits_por_digito
    if bits % bits_por_digito != 0:
        digitos_necesarios += 1

    resultado = cadena
    while len(resultado) < digitos_necesarios:
        resultado = "0" + resultado
    return resultado



def tabla_and(bit1, bit2):
    return '1' if (bit1 == '1' and bit2 == '1') else '0'


def tabla_or(bit1, bit2):
    return '1' if (bit1 == '1' or bit2 == '1') else '0'


def tabla_xor(bit1, bit2):
    return '1' if (bit1 != bit2) else '0'


OPERACIONES_ALU = {"AND": tabla_and, "OR": tabla_or, "XOR": tabla_xor}


def operar_alu(bin1, bin2, operacion):

    largo = max(len(bin1), len(bin2))
    bin1 = bin1.rjust(largo, '0')
    bin2 = bin2.rjust(largo, '0')

    funcion = OPERACIONES_ALU[operacion]
    resultado = ""
    for i in range(largo):
        resultado = resultado + funcion(bin1[i], bin2[i])
    return resultado


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convertir", methods=["POST"])
def convertir():
    datos = request.get_json(force=True)
    valor = str(datos.get("valor", "")).strip().upper()
    base_origen = int(datos.get("base_origen", 10))
    bits = int(datos.get("bits", 8))

    if base_origen not in BASES_VALIDAS:
        return jsonify({"ok": False, "error": "Base de origen inválida."}), 400

    if not validar_caracteres(valor, base_origen):
        digitos_permitidos = ", ".join(
            VALOR_A_DIGITO[i] for i in range(base_origen)
        )
        return jsonify({
            "ok": False,
            "error": f"Valor inválido para {BASES_VALIDAS[base_origen]}. "
                     f"Dígitos permitidos: {digitos_permitidos}"
        }), 400

    decimal = a_decimal(valor, base_origen)
    maximo = calcular_maximo(bits)

    if decimal > maximo:
        return jsonify({
            "ok": False,
            "error": f"Overflow / Desbordamiento de Registro: el valor máximo "
                     f"permitido en {bits} bits es {maximo}."
        }), 400

    binario = aplicar_padding(desde_decimal(decimal, 2), bits, 2)
    octal = aplicar_padding(desde_decimal(decimal, 8), bits, 8)
    hexadecimal = aplicar_padding(desde_decimal(decimal, 16), bits, 16)

    return jsonify({
        "ok": True,
        "decimal": str(decimal),
        "binario": binario,
        "octal": octal,
        "hexadecimal": hexadecimal,
        "bits": bits,
        "maximo": maximo,
    })


@app.route("/alu", methods=["POST"])
def alu():
    datos = request.get_json(force=True)
    bin1 = str(datos.get("bin1", "")).strip()
    bin2 = str(datos.get("bin2", "")).strip()
    operacion = str(datos.get("operacion", "AND")).strip().upper()

    if not validar_caracteres(bin1, 2) or not validar_caracteres(bin2, 2):
        return jsonify({"ok": False, "error": "Ambos operandos deben ser cadenas binarias válidas."}), 400

    if operacion not in OPERACIONES_ALU:
        return jsonify({"ok": False, "error": "Operación no soportada."}), 400

    resultado = operar_alu(bin1, bin2, operacion)
    return jsonify({"ok": True, "resultado": resultado})


if __name__ == "__main__":
    app.run(debug=True)
