const btn = document.getElementById('btnGuardar');
const form = document.getElementById('form'); // 👈 guardamos referencia al form

form.addEventListener('submit', function(event) {
  event.preventDefault();

  btn.innerText = 'Enviando...'; // 👈 en vez de .value usamos .innerText

  const serviceID = 'default_service';   // cámbialo por el tuyo si no es este
  const templateID = 'template_mnpwosp'; // cámbialo por el tuyo en EmailJS

  emailjs.sendForm(serviceID, templateID, this)
    .then(() => {
      btn.innerText = 'Enviar Citación';
      alert('✅ Citación enviada correctamente');
      form.reset(); // 👈 reinicia el formulario
    }, (err) => {
      btn.innerText = 'Enviar Citación';
      alert('❌ Error: ' + JSON.stringify(err));
    });
});
