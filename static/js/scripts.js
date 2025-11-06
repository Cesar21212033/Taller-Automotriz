// Ejemplo de funcionalidad para el formulario de cotizaciones
document.addEventListener("DOMContentLoaded", function () {
    const formularioCotizacion = document.getElementById("formulario-cotizacion");

    if (formularioCotizacion) {
        formularioCotizacion.addEventListener("submit", function (event) {
            event.preventDefault();
            alert("Gracias por solicitar una cotización. Nos pondremos en contacto contigo pronto.");
        });
    }
});