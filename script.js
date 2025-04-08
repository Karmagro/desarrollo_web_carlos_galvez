// Cargar regiones al iniciar la página
window.onload = function() {
    cargarRegiones();
};

// Cargar regiones en el select
function cargarRegiones() {
    const regionSelect = document.getElementById("region");
    region_comuna.regiones.forEach(region => {
        const option = document.createElement("option");
        option.value = region.numero;
        option.textContent = region.nombre;
        regionSelect.appendChild(option);
    });
    regionSelect.addEventListener("change", function() {
        cargarComunas(this.value);
    });
}

// Cargar comunas al seleccionar una región
function cargarComunas(regionNumero) {
    const comunaSelect = document.getElementById("comuna");
    comunaSelect.innerHTML = '<option value="">Seleccione...</option>';
    const region = region_comuna.regiones.find(r => r.numero == regionNumero);
    if (region) {
        region.comunas.forEach(comuna => {
            const option = document.createElement("option");
            option.value = comuna.nombre;
            option.textContent = comuna.nombre;
            comunaSelect.appendChild(option);
        });
    }
}

// Habilitar/deshabilitar campo asociado al checkbox
function revisaCheck(element) {
    const inputField = document.getElementById(element.id + "-id");
    if (element.checked) {
        inputField.disabled = false;
        inputField.focus();
    } else {
        inputField.value = "";
        inputField.disabled = true;
    }
}

// Validar el email
function validarEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Manejo de imágenes
let numFotos = 1;
function agregarFoto() {
    if (numFotos >= 5) {
        alert("No puede agregar más de 5 fotos.");
        return;
    }
    numFotos++;
    const fotoContainer = document.getElementById("foto-container");
    const nuevoInput = document.createElement("input");
    nuevoInput.type = "file";
    nuevoInput.accept = "image/*";
    nuevoInput.id = "foto" + numFotos;
    fotoContainer.appendChild(nuevoInput);
}

// Manejo del campo "Otro" en tema
const temaSelect = document.getElementById("tema");
temaSelect.addEventListener("change", function() {
    const otroInput = document.getElementById("tema-otro");
    if (this.value === "otro") {
        otroInput.style.display = "block";
    } else {
        otroInput.style.display = "none";
        otroInput.value = "";
    }
});

// Validación del formulario completo
function validarFormulario() {
    const email = document.getElementById("email").value;
    if (!validarEmail(email)) {
        alert("Formato de email no válido.");
        return false;
    }
    const fotos = document.querySelectorAll("input[type='file']");
    if (fotos.length < 1) {
        alert("Debe subir al menos una foto.");
        return false;
    }
    const tema = temaSelect.value;
    const otro = document.getElementById("tema-otro").value;
    if (tema === "otro" && (otro.length < 3 || otro.length > 15)) {
        alert("El tema especificado debe tener entre 3 y 15 caracteres.");
        return false;
    }
    alert("Formulario enviado correctamente.");
    return true;
}

// Evento de envío del formulario
document.getElementById("form-actividad").addEventListener("submit", function(event) {
    event.preventDefault();
    if (validarFormulario()) {
        if (confirm("¿Está seguro que desea agregar esta actividad?")) {
            alert("Hemos recibido su información, muchas gracias y suerte en su actividad.");
            location.href = 'index.html';
        }
    }
});


