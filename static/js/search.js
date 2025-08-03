$(document).ready(function() {
    let currentPage = 1;
    let hasNext = true;
    let isLoading = false;
    let lastSearchParams = ''; // Store the last search parameters

    function fetchCandidates(params, append=false) {
        isLoading = true;
        $('#loading-indicator').show();

        // Show spinner on Load More button if appending
        if (append) {
            $('#load-more-candidates .loading-spinner').show();
            $('#load-more-candidates').prop('disabled', true);
        }

        // Store search params for pagination (exclude page parameter)
        if (!append) {
            lastSearchParams = params.replace(/&?page=\d+/, '').replace(/^page=\d+&?/, '');
        }

        $.ajax({
            url: window.location.pathname + '?' + params,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(data) {
                if (append) {
                    // Remove the existing Load More button before appending new content
                    $('#load-more-candidates').closest('div').remove();
                    $('#candidate-results-container').append(data);
                } else {
                    $('#candidate-results-container').html(data);
                    // Reset pagination state for new searches
                    currentPage = 1;
                }

                // Update hasNext based on whether there's a Load More button in the response
                hasNext = $(data).find('#load-more-candidates').length > 0;

                // Debug logging
                console.log('Current page:', currentPage);
                console.log('Has next:', hasNext);
                console.log('Last search params:', lastSearchParams);

                isLoading = false;
                $('#loading-indicator').hide();
            },
            error: function() {
                isLoading = false;
                $('#loading-indicator').hide();
                if (append) {
                    $('#load-more-candidates .loading-spinner').hide();
                    $('#load-more-candidates').prop('disabled', false);
                }
            }
        });
    }

    // Search button
    $('#search-btn').on('click', function(e) {
        e.preventDefault();
        let params = $('#candidate-search-form').serialize();
        fetchCandidates(params);
    });

    // All button
    $('#all-btn').on('click', function(e) {
        e.preventDefault();
        fetchCandidates('q=all');
    });

    // Clear button
    $('#clear-btn').on('click', function(e) {
        e.preventDefault();
        $('#candidate-search-form')[0].reset();
        $('#candidate-search-form input[type=checkbox]').prop('checked', false);
        $('#candidate-search-form select').each(function() {
            this.selectedIndex = 0;
        });
        $('#search-q').val('');
        $('.custom-dropdown .selected-option').each(function() {
            $(this).text($(this).data('placeholder'));
        });
        $('.custom-dropdown input[type=hidden]').val('');
        $('.custom-dropdown .chevron-up').hide();
        $('.custom-dropdown .chevron-down').show();
        $('#candidate-results-container').empty();
        // Reset pagination state when clearing
        currentPage = 1;
        hasNext = true;
    });

    // Free text search on enter
    $('#search-q').on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            let params = $('#candidate-search-form').serialize();
            fetchCandidates(params);
        }
    });

    // Load More button click handler
    $(document).on('click', '#load-more-candidates', function(e) {
        e.preventDefault();
        if (isLoading || !hasNext) return;

        currentPage++;
        let params = lastSearchParams + (lastSearchParams ? '&' : '') + 'page=' + currentPage;
        fetchCandidates(params, true);
    });
});
