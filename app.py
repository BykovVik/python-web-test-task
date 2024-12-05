from flask import Flask, request, jsonify
from pymongo import MongoClient
import re

app = Flask(__name__)

# Подключение к MongoDB
client = MongoClient('mongodb://mongo:27017/')
db = client['form_db']
templates_collection = db['form_templates']

# Валидация полей
def validate_field(field_name, value):
    if field_name.startswith('date'):
        if re.match(r'^\d{2}\.\d{2}\.\d{4}$', value) or re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            return 'date'
    elif field_name.startswith('phone'):
        if re.match(r'^\+7 \d{3} \d{3} \d{2} \d{2}$', value):
            return 'phone'
    elif field_name.startswith('email'):
        if re.match(r'^[\w\.-]+@[\w\.-]+$', value):
            return 'email'
    return 'text'

@app.route('/get_form', methods=['POST'])
def get_form():
    data = request.form.to_dict()
    matching_template = None

    # Поиск подходящего шаблона
    for template in templates_collection.find():
        template_fields = {k: v for k, v in template.items() if k != 'name'}
        if all(k in data and validate_field(k, data[k]) == template_fields[k] for k in template_fields):
            matching_template = template['name']
            break

    if matching_template:
        return jsonify(matching_template)

    # Если подходящий шаблон не найден, возвращаем типы полей
    field_types = {k: validate_field(k, v) for k, v in data.items()}
    return jsonify(field_types)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)