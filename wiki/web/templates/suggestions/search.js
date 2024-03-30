<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/ui-lightness/jquery-ui.css"
        rel="stylesheet" type="text/css" />

<script>
    $(document).ready(function() {
      // Retrieve autofill results
      function fetchData() {
        $.ajax({
          url: '/search_autocomplete',
          method: 'GET',
          data: { query: $('#term').val() },
          success: function(data) {
            populateAutocomplete(data);
          },
          error: function(err) {
            console.error('Error fetching data:', err);
          }
        });
      }

      // Function to populate the autocomplete suggestions
      function populateAutocomplete(suggestions) {
        var results = suggestions.map(function(suggestion) {
          return suggestion;
        });
        $('#term').autocomplete({
          source: results
        });
      }

      // Fetch data on input
      $('#term').on('input', fetchData);
    });
</script>