document.addEventListener('DOMContentLoaded', function() {
  var patentSelect = document.getElementById('id_patent');
  var siteField = document.getElementById('id_site');
  var routeSelect = document.getElementById('id_route');

  if (patentSelect && siteField && routeSelect) {
    patentSelect.addEventListener('change', function() {
      var selectedPatent = patentSelect.value;
      var vehicle = vehiclesData.find(v => v.patent === selectedPatent);
      if (vehicle) {
        siteField.value = vehicle.site__name || '';
      } else {
        siteField.value = '';
      }

      // Filtrar routes por truck
      var filteredRoutes = routesData.filter(r => r.truck === selectedPatent);
      routeSelect.innerHTML = '<option value="">---------</option>';
      filteredRoutes.forEach(function(route) {
        var option = document.createElement('option');
        option.value = route.id_route;
        option.textContent = route.route_code;
        routeSelect.appendChild(option);
      });
    });
  }
});