$(document).ready(function() {
    let currentPage = 1;
    let hasNext = true;
    let isLoading = false;
    function fetchCandidates(params, append=false) {
        isLoading = true;
        $('#loading-indicator').show();
        $.ajax({
            url: window.location.pathname + '?' + params,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(data) {
                if (append) {
                    $('#candidate-results-container').append(data);
                } else {
                    $('#candidate-results-container').html(data);
                }
                isLoading = false;
                $('#loading-indicator').hide();
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
    });
    // Free text search on enter
    $('#search-q').on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            let params = $('#candidate-search-form').serialize();
            fetchCandidates(params);
        }
    });
    // Lazy load on scroll
    $(window).on('scroll', function() {
        if (isLoading || !hasNext) return;
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 200) {
            currentPage++;
            let params = $('#candidate-search-form').serialize() + '&page=' + currentPage;
            fetchCandidates(params, true);
        }
    });
});
