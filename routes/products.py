from flask import Blueprint, request, jsonify, render_template
from bson import ObjectId
from bson.errors import InvalidId
from decimal import Decimal, InvalidOperation
import re

from database import dbConnection
from models.product import Product

products_bp = Blueprint(
    'products',
    __name__,
    url_prefix='/products'
)

db = dbConnection()
products = db['products']
categories = db['categories']


# Registrar un producto
@products_bp.route('', methods=['POST'])
def addProduct():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Se requiere un objeto JSON'
        }), 400

    name = data.get('name', '')
    description = data.get('description', '')
    category_id = data.get('category_id')
    price = data.get('price')
    stock = data.get('stock')

    # Validar nombre
    if not isinstance(name, str) or not name.strip():
        return jsonify({
            'message': 'El nombre es obligatorio'
        }), 400

    name = name.strip()

    # Validar descripción
    if not isinstance(description, str):
        return jsonify({
            'message': 'La descripción debe ser texto'
        }), 400

    description = description.strip()

    # Validar categoría
    try:
        category_object_id = ObjectId(category_id)
    except (InvalidId, TypeError):
        return jsonify({
            'message': 'ID de categoría inválido'
        }), 400

    category = categories.find_one({
        '_id': category_object_id,
        'status': True
    })

    if not category:
        return jsonify({
            'message': 'La categoría no existe o está inactiva'
        }), 400

    # Validar precio
    try:
        price = Decimal(str(price))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({
            'message': 'El precio debe ser numérico'
        }), 400

    if not price.is_finite() or price < 0:
        return jsonify({
            'message': 'El precio debe ser válido y no negativo'
        }), 400

    if price.as_tuple().exponent < -2:
        return jsonify({
            'message': 'El precio admite máximo 2 decimales'
        }), 400

    # Validar stock
    if type(stock) is not int or stock < 0:
        return jsonify({
            'message': 'El stock debe ser un entero no negativo'
        }), 400

    # Evitar nombres duplicados
    existing = products.find_one({
        'name': {
            '$regex': '^' + re.escape(name) + '$',
            '$options': 'i'
        }
    })

    if existing:
        return jsonify({
            'message': 'El producto ya existe'
        }), 409

    # Crear y registrar producto
    try:
        product = Product(
            name,
            description,
            category_object_id,
            price,
            stock
        )

        result = products.insert_one(
            product.toDBCollection()
        )
    except (InvalidOperation, ValueError):
        return jsonify({
            'message': 'El precio no puede almacenarse'
        }), 400

    return jsonify({
        'message': 'Producto registrado correctamente',
        'id': str(result.inserted_id)
    }), 201

# Consultar los productos
@products_bp.route('', methods=['GET'])
def getProducts():
    result = []

    for product in products.find():
        category = categories.find_one({
            '_id': product['category_id']
        })

        result.append({
            '_id': str(product['_id']),
            'name': product['name'],
            'description': product.get('description', ''),
            'category_id': str(product['category_id']),
            'category_name': category['name'] if category else None,
            'price': str(product['price'].to_decimal()),
            'stock': product['stock'],
            'status': product.get('status', True)
        })

    return jsonify(result), 200

# Actualizar un producto
@products_bp.route('/edit/<string:product_id>', methods=['PUT'])
def editProduct(product_id):
    try:
        object_id = ObjectId(product_id)
    except (InvalidId, TypeError):
        return jsonify({
            'message': 'ID de producto inválido'
        }), 400

    # Verificar que el producto exista
    product = products.find_one({'_id': object_id})

    if not product:
        return jsonify({
            'message': 'Producto no encontrado'
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Se requiere un objeto JSON'
        }), 400

    name = data.get('name', '')
    description = data.get('description', '')
    category_id = data.get('category_id')
    price = data.get('price')
    stock = data.get('stock')

    # Validar nombre
    if not isinstance(name, str) or not name.strip():
        return jsonify({
            'message': 'El nombre es obligatorio'
        }), 400

    name = name.strip()

    # Validar descripción
    if not isinstance(description, str):
        return jsonify({
            'message': 'La descripción debe ser texto'
        }), 400

    description = description.strip()

    # Validar referencia de categoría
    try:
        category_object_id = ObjectId(category_id)
    except (InvalidId, TypeError):
        return jsonify({
            'message': 'ID de categoría inválido'
        }), 400

    category = categories.find_one({
        '_id': category_object_id,
        'status': True
    })

    if not category:
        return jsonify({
            'message': 'La categoría no existe o está inactiva'
        }), 400

    # Validar precio
    try:
        price = Decimal(str(price))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({
            'message': 'El precio debe ser numérico'
        }), 400

    if not price.is_finite() or price < 0:
        return jsonify({
            'message': 'El precio debe ser válido y no negativo'
        }), 400

    if price.as_tuple().exponent < -2:
        return jsonify({
            'message': 'El precio admite máximo 2 decimales'
        }), 400

    # Validar stock
    if type(stock) is not int or stock < 0:
        return jsonify({
            'message': 'El stock debe ser un entero no negativo'
        }), 400

    # Evitar nombres duplicados
    existing = products.find_one({
        'name': {
            '$regex': '^' + re.escape(name) + '$',
            '$options': 'i'
        },
        '_id': {'$ne': object_id}
    })

    if existing:
        return jsonify({
            'message': 'Ya existe otro producto con ese nombre'
        }), 409

    # Actualizar el producto
    try:
        updated_product = Product(
            name,
            description,
            category_object_id,
            price,
            stock,
            product.get('status', True)
        )

        products.update_one(
            {'_id': object_id},
            {'$set': updated_product.toDBCollection()}
        )
    except (InvalidOperation, ValueError):
        return jsonify({
            'message': 'El precio no puede almacenarse'
        }), 400

    return jsonify({
        'message': 'Producto actualizado correctamente'
    }), 200

# Desactivar un producto
@products_bp.route('/deactivate/<string:product_id>', methods=['PUT'])
def deactivateProduct(product_id):
    try:
        object_id = ObjectId(product_id)
    except (InvalidId, TypeError):
        return jsonify({
            'message': 'ID de producto inválido'
        }), 400

    # Buscar el producto
    product = products.find_one({'_id': object_id})

    if not product:
        return jsonify({
            'message': 'Producto no encontrado'
        }), 404

    # Verificar si ya está desactivado
    if product.get('status') is False:
        return jsonify({
            'message': 'El producto ya está desactivado'
        }), 400

    # Cambiar únicamente su estado
    products.update_one(
        {'_id': object_id},
        {'$set': {'status': False}}
    )

    return jsonify({
        'message': 'Producto desactivado correctamente'
    }), 200

# Mostrar la interfaz de productos
@products_bp.route('/view', methods=['GET'])
def productsView():
    return render_template('products.html')
