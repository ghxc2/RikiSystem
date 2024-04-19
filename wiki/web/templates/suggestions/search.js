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
      function populateAutocomplete(data) {
        var results = data[0].map(function(suggestion) {
          return suggestion;
        });
        var results_history = data[1].map(function(hist) {
          return hist;
        });

        var results_fixed = [];
        for (let i = 0; i < results.length; i++) {
            if (results_history.includes(results[i])) {
                results_fixed.push(results[i])
            }
        };

        for (let i = 0; i < results.length; i++) {
            if (!results_fixed.includes(results[i])) {
                results_fixed.push(results[i])
            }
        };
        $('#term').autocomplete({
          source: results_fixed
        }).autocomplete('instance')._renderItem = function(ul, item) {
            var string = '<a ' + checkHistory(item, results_history) + '>' + item.label + '</a>';
            return $('<li>')
                .append(string)
                .appendTo(ul);
        };
      }
      function checkHistory(item, history) {
        for (let i = 0; i < history.length; i++) {
            console.log('trying ' + history[i] + ' against ' + item.label)
            if (history[i] === item.label) {
                return 'style="color: purple;"';
            }
        }
            return '';
        }
      // Fetch data on input
      $('#term').on('input', fetchData);
    });

</script>