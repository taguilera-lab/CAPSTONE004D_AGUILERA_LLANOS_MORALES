document.addEventListener("DOMContentLoaded", function () {
  console.log('search_and_filter.js loaded');
  const searchBar = document.getElementById("searchBar");
  const tableSelector = document.getElementById("tablaSelector");

  // Function to filter rows based on the search term
  function filterRows() {
    const searchTerm = searchBar.value.toLowerCase();
    const tables = document.querySelectorAll(".tabla-contenedor");
    const selectedTableId = tableSelector.value;
    const selectedTable = document.getElementById(selectedTableId);

    if (!searchTerm) {
      tables.forEach((table) => {
        const rows = table.querySelectorAll("tbody tr");
        rows.forEach((row) => (row.style.display = ""));
      });
      const noResultsMessage = document.getElementById("noResultsMessage");
      noResultsMessage.style.display = "none";
      return;
    }

    tables.forEach((table) => {
      const rows = table.querySelectorAll("tbody tr");

      rows.forEach((row) => {
        const cells = Array.from(row.querySelectorAll("td"));
        let match = false;
        let patentIndex = -1;

        // Define the index of the 'Patente' column for each table
        if (table.id === "tabla-vehicles") {
          patentIndex = 0; // Patente column
        } else if (table.id === "tabla-ingresos") {
          patentIndex = 1; // Patente column
        } else if (table.id === "tabla-routes") {
          patentIndex = 4; // Patente Camión column
        } else if (table.id === "tabla-maintenanceschedules") {
          patentIndex = 1; // Patente column
        } else if (table.id === "tabla-flotausers") {
          patentIndex = 3; // Patente column
        }

        // Check only the 'Patente' column if defined
        if (patentIndex !== -1 && cells[patentIndex]) {
          if (cells[patentIndex].textContent.toLowerCase().includes(searchTerm)) {
            match = true;
          }
        }

        if (match) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });

    // Check if the selected table has any visible rows
    const visibleRows = selectedTable.querySelectorAll('tbody tr:not([style*="display: none"])');
    const noResultsMessage = document.getElementById("noResultsMessage");
    if (visibleRows.length === 0) {
      console.log('No results in selected table, showing message');
      console.log('noResultsMessage element:', noResultsMessage);
      noResultsMessage.textContent = `No se pudo encontrar la patente "${searchBar.value}".`;
      noResultsMessage.style.display = "block";
    } else {
      console.log('Results found in selected table, hiding message');
      noResultsMessage.style.display = "none";
    }
  }

  // Function to show the selected table
  function mostrarTabla() {
    const selectedTableId = tableSelector.value;
    const tables = document.querySelectorAll(".tabla-contenedor");

    tables.forEach((table) => {
      table.style.display = "none";
    });

    const selectedTable = document.getElementById(selectedTableId);
    selectedTable.style.display = "block";

    // Reapply the filter when switching tables
    filterRows();
  }

  // Event listeners
  searchBar.addEventListener("input", filterRows);
  tableSelector.addEventListener("change", mostrarTabla);

  // Initialize the view
  mostrarTabla();
});