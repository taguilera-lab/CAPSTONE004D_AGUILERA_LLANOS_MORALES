function changeStatus(newStatus) {
  const statusTexts = {
    'PENDING': 'Pendiente',
    'APPROVED': 'Aprobada',
    'ORDERED': 'Ordenada',
    'RECEIVED': 'Recibida',
    'CANCELLED': 'Cancelada'
  };

  document.getElementById('newStatusInput').value = newStatus;
  document.getElementById('statusText').textContent = statusTexts[newStatus];
  new bootstrap.Modal(document.getElementById('statusModal')).show();
}