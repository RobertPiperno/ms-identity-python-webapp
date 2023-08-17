$(document).ready(function () {
  // Function to convert the CSV data to DataTables format
  function formatDataForDataTables(data) {
    const columns = Object.keys(data[0]);
    const formattedData = data.map((row) => Object.values(row));
    return { columns, data: formattedData };
  }

  // Function to fetch the CSV file
  function fetchCSVData() {
    return fetch('DailyInventory.csv') // Update the file path here
      .then((response) => response.text())
      .then((csvData) => {
        // Parse CSV data
        const parsedData = Papa.parse(csvData, { header: true }).data;
        // Convert the data to DataTables format
        const tableData = formatDataForDataTables(parsedData);
        // Initialize DataTable
        $('#dynamic-table').DataTable({
          data: tableData.data,
          columns: tableData.columns.map((col) => ({ title: col })),
          dom: 'Bfrtip', // Show buttons (optional)
          buttons: ['copy', 'csv', 'excel', 'pdf', 'print'], // Add export buttons (optional)
        });
      });
  }

  // Call the fetchCSVData function to populate the DataTable
  fetchCSVData();
});
