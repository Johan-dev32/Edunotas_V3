document.getElementById("loginBtn").addEventListener("click", function() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (email === "" || password === "") {
    alert("Por favor, completa todos los campos.");
    return;
  }
  const emailRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  if (!emailRegex.test(email)) {
    alert("Por favor, ingresa un correo válido.");
    return;
  }
      
  window.location.href = "http://127.0.0.1:5500/template/Paginainicio.html";
});

// --- Mostrar/Ocultar contraseña ---
function togglePassword() {
  const input = document.getElementById("password");
  const icon = document.querySelector("#togglePassword i");

  if (input.type === "password") {
    input.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    input.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}