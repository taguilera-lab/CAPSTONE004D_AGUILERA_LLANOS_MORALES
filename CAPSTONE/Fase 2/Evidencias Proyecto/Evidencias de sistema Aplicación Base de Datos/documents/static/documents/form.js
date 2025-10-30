function mostrarFormulario() {
  console.log('mostrarFormulario called');
  console.log('window.isEdit:', window.isEdit);
  console.log('window.selectedForm:', window.selectedForm);

  const selector = document.getElementById("formSelector");
  console.log('selector:', selector);
  const selectedForm = (window.isEdit && window.selectedForm) ? window.selectedForm : (selector ? selector.value : null);
  console.log('selectedForm:', selectedForm);

  const forms = document.querySelectorAll(".form-container");
  console.log('forms found:', forms.length);
  forms.forEach(form => {
    form.style.display = "none";
  });
  const formElement = document.getElementById("form-" + selectedForm);
  console.log('formElement:', formElement);
  if (formElement) {
    formElement.style.display = "block";
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOMContentLoaded fired');
  console.log('window.isEdit:', window.isEdit);
  console.log('window.selectedForm:', window.selectedForm);

  if (!window.isEdit) {
    console.log('Initializing for create mode');
    mostrarFormulario();
    // Add event listener to selector
    const selector = document.getElementById("formSelector");
    if (selector) {
      console.log('Adding event listener to selector');
      selector.addEventListener('change', function() {
        console.log('Selector changed');
        mostrarFormulario();
      });
    } else {
      console.log('Selector not found');
    }
  } else {
    console.log('Initializing for edit mode');
    // For editing, show the selected form directly
    if (window.selectedForm) {
      const forms = document.querySelectorAll(".form-container");
      forms.forEach(form => {
        form.style.display = "none";
      });
      const formElement = document.getElementById("form-" + window.selectedForm);
      console.log('Showing form element:', formElement);
      if (formElement) {
        formElement.style.display = "block";
      }
    }
  }
});