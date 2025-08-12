from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['data']

@main_bp.route('/')
def home():
    try:
        client.server_info()
        # Obtener todas las sesiones sin pago
        sessions = list(db.Sessions.aggregate([{'$match': {'Payment': {'$exists': False} }},
                {'$group': {'_id': '$id', 'amnt': {'$sum': '$NumberSessions'}}},
                {'$sort': {'_id': 1}}]))
        amount_due = 0
        for session in sessions:
            provider = db.Providers.find_one({"id": session["_id"]})
            #if 'amnt' in session:
            #    print(session, provider['SessionPrice'])
            if provider and "SessionPrice" in provider and "amnt" in session:
                amount_due += session["amnt"] * provider["SessionPrice"]
        
        
        today = datetime.now().strftime("%d/%m/%Y")
        return render_template("home.html", today=today, amountDue=amount_due)
    
    except Exception as e:
        return jsonify({"error": "Error de conexión a MongoDB", "details": str(e)}), 500

@main_bp.route('/register-session', methods=['GET', 'POST'])
def register_session():
    if request.method == 'POST':
        data = request.get_json()
        provider_id = data.get('provider_id')
        fecha = data.get('fecha')
        cantidad = int(data.get('cantidad', 1))
        # Aquí iría la lógica para registrar una nueva sesión
        db.Sessions.insert_one({'id': provider_id, 'Date': fecha, 'NumberSessions': cantidad})
        # ...
        return jsonify({"mensaje": "Registro confirmado"})

    proveedores = db.Providers.find({}, {"id": 1, "Name": 1, "_id": 0})
    lista_proveedores = [{"id": p["id"], "nombre": p["Name"]} for p in proveedores]    

    return render_template("register_session.html",
    proveedores=lista_proveedores)

@main_bp.route('/make-payment', methods=['GET', 'POST'])
def make_payment():
    providers = list(db.Providers.find({}))
    selected_provider = request.args.get('provider_id')
    amount_due = None
    sessions = []
    provider_name = ""
    if selected_provider:
        provider = db.Providers.find_one({"id": selected_provider})
        if provider:
            provider_name = provider.get("Name", "")
            sessions = list(db.Sessions.find({"id": selected_provider, "Payment": {"$exists": False}}).sort("Date", 1))
            total_sessions = sum(s.get("NumberSessions", 0) for s in sessions)
            session_price = provider.get("SessionPrice", 0)
            amount_due = total_sessions * session_price

    if request.method == 'POST':
        provider_id = request.form.get('provider_id')
        provider = db.Providers.find_one({"id": provider_id})
        sessions = list(db.Sessions.find({"id": provider_id, "Payment": {"$exists": False}}).sort("Date", 1))
        total_sessions = sum(s.get("NumberSessions", 0) for s in sessions)
        session_price = provider.get("SessionPrice", 0)
        amount_due = total_sessions * session_price
        provider_name = provider.get("Name", "")
        reference_id = f"{total_sessions}{provider_id}{datetime.now().strftime('%b%d')}"
        bank_account = provider.get('AccountNumber')

        # Aquí podrías actualizar la base de datos para marcar las sesiones como pagadas
        us = {'$set': {'Payment': datetime.now().strftime('%Y-%m-%d'), 'PaymentId': reference_id}}
        db.Sessions.update_many({'id': provider_id, 'Payment': {'$exists': False}}, us)

        # Renderiza el comprobante de pago
        return render_template(
            "payment_receipt.html",
            provider_name=provider_name,
            amount_due=amount_due,
            total_sessions=total_sessions,
            session_price=session_price,
            sessions=sessions,
            fecha_pago=datetime.now().strftime("%d/%m/%Y"),
            reference_id=reference_id,
            bank_account=bank_account
            )

    return render_template(
        "make_payment.html",
        providers=providers,
        selected_provider=selected_provider,
        amount_due=amount_due,
        sessions=sessions,
        provider_name=provider_name
        )

@main_bp.route('/provider/<provider_id>')
def provider_details(provider_id):
    try:
        # Buscar el provider por ID
        provider = db.Providers.find_one({"id": provider_id})
        
        if provider:
            provider["_id"] = str(provider["id"])
            
            # Buscar las clases asociadas al provider
            classes = list(db.Sessions.find(
                {"id": provider_id},
                {
                    "id": 1,
                    "Name": 1,
                    "Date": 1,
                    "Status": 1
                }
            ))
            
            for class_item in classes:
                class_item["id"] = str(class_item["id"])
            
            return jsonify({
                "provider": provider,
                "classes": classes
            })
            
        return jsonify({"error": "Provider no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "ID de provider inválido"}), 400

@main_bp.route('/get-provider/<provider_id>')
def get_provider(provider_id):
    try:
        provider = db.Providers.find_one({"id": provider_id})
        if provider:
            # Asegurarse que los campos coincidan con los nombres esperados
            return jsonify({
                "id": provider["id"],
                "nombre": provider["Name"],
                "cuenta": provider["AccountNumber"],
                "banco": provider["Bank"],
                "costoxh": provider["SessionPrice"]
            })
        return jsonify({"error": "Provider no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/update-provider/<provider_id>', methods=['PUT'])
def update_provider(provider_id):
    try:
        data = request.get_json()
        db.Providers.update_one(
            {"id": provider_id},
            {"$set": {
                "Name": data.get('nombre'),
                "AccountNumber": data.get('cuenta'),
                "Bank": data.get('banco'),
                "SessionPrice": float(data.get('costoxh', 0))
            }}
        )
        return jsonify({"mensaje": "Provider actualizado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/admin-providers', methods=['GET', 'POST'])
def admin_providers():
    providers = list(db.Providers.find())

    if request.method == 'POST':
        data = request.get_json()
        # Generar un nuevo ID
        currency = data.get('currency', 'mx').lower()
        full_name = data.get('nombre', '')
        n, ln = full_name.split(' ')
        
        new_id = f"{currency[:2]}{n}{ln[0]}"
        
        nombre = data.get('nombre')
        cuenta = data.get('cuenta')
        banco = data.get('banco')
        pais = data.get('pais')
        clase = data.get('clase')
        costoxh = float(data.get('costoxh', 0))
        
        db.Providers.insert_one({
            "id": new_id,
            "Name": nombre,
            "AccountNumber": cuenta,
            "Bank": banco,
            "Country": pais,
            "ServiceName": clase,
            "SessionPrice": costoxh
        })
        return jsonify({"mensaje": "Proveedor agregado correctamente"})
    
    return render_template("admin_providers.html", providers=providers)

