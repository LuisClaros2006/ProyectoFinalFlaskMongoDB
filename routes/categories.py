from flask import Blueprint, request, jsonify, render_template
from models.category import Category
from database import dbConnection
import re
from bson import ObjectId
from bson.errors import InvalidId

categories_bp = Blueprint(
    'categories',
    __name__,
    url_prefix='/categories'
)

db = dbConnection()
categories = db['categories']


# Registrar una categoría
@categories_bp.route('', methods=['POST'])
def addCategory():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Se requiere un objeto JSON'
        }), 400

    name = data.get('name', '')
    description = data.get('description', '')

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            'message': 'El nombre de la categoría es obligatorio'
        }), 400

    if not isinstance(description, str):
        return jsonify({
            'message': 'La descripción debe ser texto'
        }), 400

    name = name.strip()
    description = description.strip()

    # Evitar nombres duplicados
    existing = categories.find_one({
        'name': {
            '$regex': '^' + re.escape(name) + '$',
            '$options': 'i'
        }
    })

    if existing:
        return jsonify({
            'message': 'La categoría ya existe'
        }), 409

    category = Category(name, description)
    result = categories.insert_one(
        category.toDBCollection()
    )

    return jsonify({
        'message': 'Categoría registrada correctamente',
        'id': str(result.inserted_id)
    }), 201

# Consultar las categorías
@categories_bp.route('', methods=['GET'])
def getCategories():
    result = []

    for category in categories.find():
        result.append({
            '_id': str(category['_id']),
            'name': category['name'],
            'description': category.get('description', ''),
            'status': category.get('status', True)
        })

    return jsonify(result), 200

# Actualizar una categoría
@categories_bp.route('/edit/<string:category_id>', methods=['PUT'])
def editCategory(category_id):
    try:
        object_id = ObjectId(category_id)
    except (InvalidId, TypeError):
        return jsonify({
            'message': 'ID de categoría inválido'
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Se requiere un objeto JSON'
        }), 400

    name = data.get('name', '')
    description = data.get('description', '')

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            'message': 'El nombre de la categoría es obligatorio'
        }), 400

    if not isinstance(description, str):
        return jsonify({
            'message': 'La descripción debe ser texto'
        }), 400

    name = name.strip()
    description = description.strip()

    # Verificar que exista la categoría
    category = categories.find_one({'_id': object_id})

    if not category:
        return jsonify({
            'message': 'Categoría no encontrada'
        }), 404

    # Verificar que el nombre no pertenezca a otra categoría
    import re

    existing = categories.find_one({
        'name': {
            '$regex': '^' + re.escape(name) + '$',
            '$options': 'i'
        },
        '_id': {'$ne': object_id}
    })

    if existing:
        return jsonify({
            'message': 'Ya existe otra categoría con ese nombre'
        }), 409

    # Actualizar los datos
    categories.update_one(
        {'_id': object_id},
        {'$set': {
            'name': name,
            'description': description
        }}
    )

    return jsonify({
        'message': 'Categoría actualizada correctamente'
    }), 200

# Desactivar una categoría
@categories_bp.route('/deactivate/<string:category_id>', methods=['PUT'])
def deactivateCategory(category_id):
    try:
        object_id = ObjectId(category_id)
    except (InvalidId, TypeError):
        return jsonify({
            'message': 'ID de categoría inválido'
        }), 400

    # Buscar la categoría
    category = categories.find_one({'_id': object_id})

    if not category:
        return jsonify({
            'message': 'Categoría no encontrada'
        }), 404

    # Verificar si ya está desactivada
    if category.get('status') is False:
        return jsonify({
            'message': 'La categoría ya está desactivada'
        }), 400

    # Cambiar únicamente su estado
    categories.update_one(
        {'_id': object_id},
        {'$set': {'status': False}}
    )

    return jsonify({
        'message': 'Categoría desactivada correctamente'
    }), 200

# Mostrar la interfaz de categorías
@categories_bp.route('/view', methods=['GET'])
def categoriesView():
    return render_template('categories.html')
