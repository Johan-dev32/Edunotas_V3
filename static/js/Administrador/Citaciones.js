const btn = document.getElementById('btnGuardar');

document.getElementById('form')
  .addEventListener('submit', function(event) {
    event.preventDefault();

    btn.innerText = 'Enviando...'; // 👈 en vez de .value usamos .innerText

    const serviceID = 'default_service';   // cámbialo por el tuyo si no es este
    const templateID = 'template_mnpwosp'; // cámbialo por el tuyo en EmailJS

    emailjs.sendForm(serviceID, templateID, this)
      .then(() => {
        btn.innerText = 'Enviar Citación';
        alert('✅ Citación enviada correctamente');
      }, (err) => {
        btn.innerText = 'Enviar Citación';
        alert('❌ Error: ' + JSON.stringify(err));
      });
  });
