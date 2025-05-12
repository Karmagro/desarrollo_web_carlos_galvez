from enum import verify
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .extensions import db
from datetime import datetime
from werkzeug.utils import secure_filename
from app.models import Region, Comuna, Actividad, ActividadTema, Foto, TemaEnum, ContactosEnum, ContactarPor
import json
import re
import uuid
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():

    actividades = (Actividad.query.order_by(Actividad.id.desc()).limit(5).all())

    datos_actividades = []

    for actividad in actividades:

        datos_actividades.append({  
            "nombre": actividad.nombre,
            "sector": actividad.sector if actividad.sector else "-",
            "comuna": actividad.comuna.nombre,
            "temas": [t.glosa_otro if t.tema == TemaEnum.OTRO else t.tema.value for t in actividad.temas],
            "foto": actividad.fotos[0].ruta_archivo,
            "fecha_inicio": actividad.dia_hora_inicio.strftime("%Y-%m-%d %H:%M"),
            "fecha_termino": actividad.dia_hora_termino.strftime("%Y-%m-%d %H:%M") if actividad.dia_hora_termino else "-",
        })

    return render_template('index.html', actividades=datos_actividades)

@main.route("/agregar")
def agregar():

    regiones = Region.query.order_by(Region.nombre).all()

    comunas_por_region = {}

    for region in regiones:
        
        comunas = sorted(region.comunas, key=lambda c: c.nombre)
        
        comunas_por_region[region.id] = [{"id": comuna.id, "nombre": comuna.nombre} for comuna in comunas]

    comunas_json = json.dumps(comunas_por_region)

    return render_template("agregar.html", regiones=regiones, comunas_json=comunas_json)

@main.route('/listado')
def listado():
    # Obtener el número de página actual (por defecto 1)
    page = request.args.get('page', 1, type=int)
    per_page = 5

    # Consulta paginada
    pagination = Actividad.query.order_by(Actividad.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    actividades = pagination.items

    datos_actividades = []
    for actividad in actividades:
        datos_actividades.append({
            'id': actividad.id,
            'inicio': actividad.dia_hora_inicio.strftime("%Y-%m-%d %H:%M"),
            'termino': actividad.dia_hora_termino.strftime("%Y-%m-%d %H:%M") if actividad.dia_hora_termino else "-",
            'comuna': actividad.comuna.nombre,
            'sector': actividad.sector or "-",
            'temas': [t.glosa_otro if t.tema == TemaEnum.OTRO else t.tema.value for t in actividad.temas],
            'organizador': actividad.nombre,
            'total_fotos': len(actividad.fotos)
        })

    return render_template(
        "listado.html",
        actividades=datos_actividades,
        page=page,
        total_pages=pagination.pages
    )


@main.route('/actividad/<int:actividad_id>')
def actividad_detalle(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)

    actividad_datos = {
        'inicio': actividad.dia_hora_inicio.strftime("%Y-%m-%d %H:%M"),
        'termino': actividad.dia_hora_termino.strftime("%Y-%m-%d %H:%M") if actividad.dia_hora_termino else "-",
        'comuna': actividad.comuna.nombre,
        'sector': actividad.sector or "-",
        'temas': [t.glosa_otro if t.tema == TemaEnum.OTRO else t.tema.value for t in actividad.temas],
        'descripcion': actividad.descripcion or "-",
        'organizador': actividad.nombre,
        'email': actividad.email,
        'celular': actividad.celular or "-",
        'contactos': [{'tipo': contacto.nombre.value, 'valor': contacto.identificador} for contacto in actividad.contactos],
        'fotos':  [{'ruta': foto.ruta_archivo, 'nombre': foto.nombre_archivo} for foto in actividad.fotos]
    }

    return render_template("actividad.html", actividad=actividad_datos)



@main.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')



#Verify the region, if exist and is valid
def verify_region(region_id):
    if not region_id:
        return False
    try:
        region_id_int = int(region_id)
        region = Region.query.get(region_id_int)
        return region is not None
    except ValueError:
        return False

#Verify the comuna, if exist and is in the region
def verify_comuna(region_id, comuna_id):
    if not region_id or not comuna_id:
        return False
    try:
        region_id_int = int(region_id)
        comuna_id_int = int(comuna_id)
        comuna = Comuna.query.get(comuna_id_int)
        if comuna and comuna.region_id == region_id_int:
            return True
        return False
    except ValueError:
        return False

#Verify sector, if exist then it has to be less than 100 characters
def verify_sector(sector):
    if not sector:
        return True
    if len(sector) > 100:
        return False
    return True

#Verify name, it has to exist and be less than 200 characters
def verify_name(nombre):
    if not nombre:
        return False
    if len(nombre) > 200:
        return False
    return True

# Verify the email format
def verify_email(email):
    if not email:
        return False
    if len(email) > 100:
        return False
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

# Verify the phone format
def verify_phone(telefono):
    if not telefono:
        return True
    pattern = r"^\+[0-9]{3}\.[0-9]{8}$"
    return re.match(pattern, telefono) is not None  

def verify_social_media(selected_contact_values):

    social_media_data = {}

    for contact_enum_member in ContactosEnum:
        contact_type_value = contact_enum_member.value
        
        if contact_type_value in selected_contact_values:

            contact_input_value = request.form.get(contact_type_value, "").strip()

            if not contact_input_value:
                return False, f"El campo para {contact_enum_member.name} no puede estar vacío si está seleccionado.", None
            
            min_len = 3
            max_len = 50
            if not (min_len <= len(contact_input_value) <= max_len):
                return False, f"El identificador para {contact_enum_member.name} debe tener entre {min_len} y {max_len} caracteres.", None

            social_media_data[contact_enum_member] = contact_input_value

    return True, None, social_media_data

def verify_dates(start_time_str, finish_time_str):
    if not start_time_str:
        return False, "La fecha y hora de inicio son obligatorias.", None, None
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
    except (ValueError, TypeError):
        return False, "Fecha de inicio inválida.", None, None
    
    finish_time = None

    if finish_time_str:
        try:
            finish_time = datetime.strptime(finish_time_str, "%Y-%m-%dT%H:%M")
            if finish_time <= start_time:
                return False, "La fecha de término debe ser posterior a la de inicio.", None, None
        except (ValueError, TypeError):
            return False, "Fecha de término inválida.", None, None
    
    return True, None, start_time, finish_time


# Verify description, not required but length has to be less than 500 characters
def verify_description(descripcion):
    if not descripcion:
        return True
    if len(descripcion) > 500:
        return False
    return True

def verify_selected_themes(selected_theme_values, other_theme_text):
    if not selected_theme_values:
        return False, "Debe seleccionar al menos un tema para el evento.", None, None

    validated_theme_enums = []
    validated_other_text = None
    is_other_theme_selected = False

    for theme_value_str in selected_theme_values:
        try:
            theme_enum_member = TemaEnum(theme_value_str)
            validated_theme_enums.append(theme_enum_member)
            if theme_enum_member == TemaEnum.OTRO:
                is_other_theme_selected = True
        except ValueError:
            return False, f"El tema '{theme_value_str}' no es válido.", None, None

    if is_other_theme_selected:
        if not other_theme_text:
            return False, "Si selecciona 'Otro' tema, debe especificar el texto.", validated_theme_enums, None
        if not (3 <= len(other_theme_text) <= 15): 
            return False, "La descripción del tema 'Otro' debe tener entre 3 y 15 caracteres.", validated_theme_enums, None
        validated_other_text = other_theme_text
    elif other_theme_text and not is_other_theme_selected: 
        return False, "Se especificó un texto para 'Otro' tema, pero la opción 'Otro' no fue seleccionada.", validated_theme_enums, None
        
    return True, None, validated_theme_enums, validated_other_text

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_PHOTOS = 5

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_PHOTO_EXTENSIONS

def verify_photos(photos_data):
        if not photos_data:
            return False, "Debe subir al menos una foto para el evento.", None
        if len(photos_data) > MAX_PHOTOS:
            return False, f"No puede subir más de {MAX_PHOTOS} fotos.", None
        
        processed_photos = []
        for photo_file in photos_data:
            if not allowed_file(photo_file.filename):
                return False, f"Tipo de archivo no permitido para '{photo_file.filename}'. Solo se permiten PNG, JPG, JPEG.", None
            
            filename = secure_filename(photo_file.filename)
            processed_photos.append({'filename': filename, 'filestorage': photo_file})
        
        return True, None, processed_photos

@main.route("/agregar", methods=["POST"])
def procesar_agregar():
    region_id_str = request.form.get("region")
    comuna_id_str = request.form.get("comuna")
    sector = request.form.get("sector", "").strip()
    nombre = request.form.get("name", "").strip()
    email = request.form.get("e-mail", "").strip()
    telefono = request.form.get("phone", "").strip()
    start_time_str = request.form.get("start-time")
    finish_time_str = request.form.get("finish-time")
    descripcion = request.form.get("description", "").strip()
    selected_contact_values = request.form.getlist("contact")
    selected_themes = request.form.getlist("theme")
    other_theme_text = request.form.get("other-theme-text", "").strip()

    uploaded_files = request.files.getlist("photos")
    photos_data = [f for f in uploaded_files if f and f.filename]

    if not verify_region(region_id_str):
        flash("Región inválida o no seleccionada.", "error")
        return redirect(url_for("main.agregar"))
    region_id = int(region_id_str)

    if not verify_comuna(region_id, comuna_id_str):
        flash("Comuna inválida, no seleccionada o no pertenece a la región.", "error")
        return redirect(url_for("main.agregar"))
    comuna_id = int(comuna_id_str)
    
    if not verify_sector(sector):
        flash("El sector no debe exceder los 100 caracteres.", "error")
        return redirect(url_for("main.agregar"))

    if not verify_name(nombre):
        flash("El nombre del organizador es obligatorio y no debe exceder los 200 caracteres", "error")
        return redirect(url_for("main.agregar"))

    if not verify_email(email):
        flash("Email no ingresado, o formato inválido.", "error")
        return redirect(url_for("main.agregar"))
    
    if not verify_phone(telefono):
        flash("El formato del número de teléfono no es válido. Use +XXX.XXXXXXXX.", "error")
        return redirect(url_for("main.agregar"))
    
    is_socials_valid, error_message, social_media_contacts = verify_social_media(selected_contact_values)
    if not is_socials_valid:
        flash(error_message, "error")
        return redirect(url_for("main.agregar"))
    
    is_dates_valid, error_message, start_time, finish_time = verify_dates(start_time_str, finish_time_str)
    if not is_dates_valid:
        flash(error_message, "error")
        return redirect(url_for("main.agregar"))

    if not verify_description(descripcion):
        flash("La descripción no debe exceder los 500 caracteres.", "error")
        return redirect(url_for("main.agregar"))
    
    is_themes_valid, error_message, actual_selected_themes, other_theme_text = verify_selected_themes(selected_themes, other_theme_text)
    if not is_themes_valid:
        flash(error_message, "error")
        return redirect(url_for("main.agregar"))
    
    is_photos_valid, error_message, processed_photos = verify_photos(photos_data)
    if not is_photos_valid:
        flash(error_message, "error")
        return redirect(url_for("main.agregar"))

    print("Todas las validaciones pasaron (simulación).")
    print(f"Region ID: {region_id}, Comuna ID: {comuna_id}, Sector: {sector}")
    print(f"Nombre: {nombre}, Email: {email}, Teléfono: {telefono}")
    print(f"Social Media: {social_media_contacts}")
    print(f"Inicio: {start_time}, Término: {finish_time}")
    print(f"Descripción: {descripcion}")
    print(f"Temas seleccionados: {actual_selected_themes}")
    if "OTRO" in actual_selected_themes:
        print(f"Texto tema 'Otro': {other_theme_text}")
    print(f"Fotos procesadas: {[p['filename'] for p in processed_photos]}")

    nueva_actividad = Actividad(
        comuna_id=comuna_id,
        sector=sector if sector else None,
        nombre=nombre,
        email=email,
        celular=telefono if telefono else None,
        dia_hora_inicio=start_time,
        dia_hora_termino=finish_time,
        descripcion=descripcion if descripcion else None
    )

    db.session.add(nueva_actividad)
    db.session.flush()

    for tema_enum in actual_selected_themes:
        glosa_otro_val = other_theme_text if tema_enum == TemaEnum.OTRO else None
        tema = ActividadTema(
            tema=tema_enum,
            glosa_otro=glosa_otro_val,
            actividad_id=nueva_actividad.id
        )
        db.session.add(tema)

    for contacto_enum, valor in social_media_contacts.items():
        contacto = ContactarPor(
            nombre=contacto_enum,
            identificador=valor,
            actividad_id=nueva_actividad.id
        )
        db.session.add(contacto)

    UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    for foto in processed_photos:
        file_storage = foto["filestorage"]
        original_name = foto["filename"]
        unique_name = f"{uuid.uuid4().hex}_{secure_filename(original_name)}"
        full_path = os.path.join(UPLOAD_FOLDER, unique_name)

        # Guardar el archivo físico
        file_storage.save(full_path)

        foto_bd = Foto(
            ruta_archivo=f"/uploads/{unique_name}",
            nombre_archivo=original_name,
            actividad_id=nueva_actividad.id
        )
        db.session.add(foto_bd)

    db.session.commit()

    flash("Formulario procesado y validado exitosamente (simulación).", "success")
    return redirect(url_for("main.home"))