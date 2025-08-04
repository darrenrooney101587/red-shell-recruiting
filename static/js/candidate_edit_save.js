function AddResumeAction() {

    // RESUME UPLOAD
    $('#trigger-resume-upload').on('click', function () {
        $('#candidate-resume').click();
    });

    $('#candidate-resume').on('change', function () {
        const file = this.files[0];
        if (file) {
            $('#file-name').text(file.name);
            $('#add-resume-button').show();
        } else {
            $('#file-name').text('');
            $('#add-resume-button').hide();
        }
    });

    $('#add-resume-button').on('click', function () {
        const fileInput = $('#candidate-resume')[0];
        if (fileInput.files.length === 0) {
            alert('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('candidate-resume', fileInput.files[0]);
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        $.ajax({
            url: uploadResumeUrl,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function () {
                location.reload();
            },
            error: function () {
                alert('Failed to upload resume.');
            }
        });
    });
}

function AddPortfolioAction() {

    // PORTFOLIO UPLOAD
    $('#trigger-portfolio-upload').on('click', function () {
        $('#candidate-culinary-portfolio').click();
    });

    $('#candidate-culinary-portfolio').on('change', function () {
        const file = this.files[0];
        if (file) {
            $('#portfolio-file-name').text(file.name);
            $('#add-portfolio-button').show();
        } else {
            $('#portfolio-file-name').text('');
            $('#add-portfolio-button').hide();
        }
    });

    $('#add-portfolio-button').on('click', function () {
        const fileInput = $('#candidate-culinary-portfolio')[0];
        if (fileInput.files.length === 0) {
            alert('Please select a portfolio file first.');
            return;
        }

        const formData = new FormData();
        formData.append('candidate-portfolio', fileInput.files[0]);
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        $.ajax({
            url: uploadCulinaryPortfolioUrl,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function () {
                location.reload();
            },
            error: function () {
                alert('Failed to upload culinary portfolio.');
            }
        });
    });
}

function AddDocumentAction() {

    // DOCUMENT UPLOAD
    $('#trigger-document-upload').on('click', function () {
        $('#candidate-document').click();
    });

    $('#candidate-document').on('change', function () {
        const file = this.files[0];
        if (file) {
            $('#document-file-name').text(file.name);
            $('#add-document-button').show();
        } else {
            $('#document-file-name').text('');
            $('#add-document-button').hide();
        }
    });

    $('#add-document-button').on('click', function () {
        const fileInput = $('#candidate-document')[0];
        if (fileInput.files.length === 0) {
            alert('Please select a document first.');
            return;
        }

        const formData = new FormData();
        formData.append('candidate-document', fileInput.files[0]);
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        $.ajax({
            url: uploadDocumentUrl,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function () {
                location.reload();
            },
            error: function () {
                alert('Failed to upload document.');
            }
        });
    });
}

function CandidateEditSaveActions() {
    // CANCEL BUTTON
    $('#cancel-button').on('click', function () {
        $('#candidate-edit-mode').hide();
        $('#candidate-view-mode').show();
    });
}

/**
 * Show a message in the .journal-messages container.
 * @param {string} msg
 */
function addJournalMessage(msg) {
    $('.journal-messages').html('<div class="alert alert-danger">' + msg + '</div>');
}

/**
 * Loads all journal entries for the candidate and updates the DOM.
 */
function LoadJournalEntries() {
    $.get(journalEntryUrl, function(data) {
        $('#journal-entries-list').html(data);
    });
}

/**
 * Handles adding a new journal entry via AJAX, with validation.
 */
function HandleNewJournalEntry() {
    // Date picker setup
    $('#journal-meeting-date').daterangepicker({
        autoApply: false,
        autoUpdateInput: false,
        // forceSingleDateMultiMonth: true,
        singleDatePicker: true,
        linkedCalendars: false,
        minDate: false,
        locale: {cancelLabel: 'Clear'},
        opens: 'center',
        theme: ''
    });
    $('#journal-meeting-date').on('apply.daterangepicker', function (ev, picker) {
        var date = picker.startDate.format('YYYY-MM-DD');
        $(this).text(date);
        $(this).data('selected-date', date);
    });
    $('#journal-meeting-date').on('cancel.daterangepicker', function (ev, picker) {
        $(this).text('Select date');
        $(this).data('selected-date', '');
    });

    $('#add-journal-entry-btn').on('click', function (e) {
        e.preventDefault();
        var notes = $('#journal-notes').val().trim();
        var date = $('#journal-meeting-date').data('selected-date');

        // Clear any previous error messages
        $('.journal-messages').empty();

        if (!notes || !date) {
            addJournalMessage('Please enter both date and notes.');
            return;
        }
        $.ajax({
            url: journalEntryUrl,
            method: 'POST',
            data: {
                notes: notes,
                meeting_date: date,
                csrfmiddlewaretoken: getCSRFToken()
            },
            success: function () {
                $('#journal-notes').val('');
                $('#journal-meeting-date').text('Select date').data('selected-date', '');
                $('.journal-messages').empty(); // Clear any messages on success
                LoadJournalEntries();
            },
            error: function (xhr) {
                addJournalMessage('Error: ' + xhr.responseText);
            }
        });
    });
}

/**
 * Handles removal of placement records via AJAX for both desktop and mobile views.
 */
function HandleRemovePlacementRecord() {
    $('#placement-records-list').on('click', '.remove-placement', function() {
        // Support both div and li containers
        var $item = $(this).closest('[data-placement-history-id]');
        var placementId = $item.data('placement-history-id');
        if (!placementId) return;
        $.ajax({
            url: placementRecordsUrl + '?placement_history_id=' + placementId,
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCSRFToken() },
            success: function() { LoadPlacementRecords(); },
            error: function(xhr) { alert('Error: ' + xhr.responseText); }
        });
    });
}

/**
 * Handles adding a new placement record via AJAX and reloads the list.
 */
function HandleAddPlacementRecord() {
    $('#add-placement-record-btn').on('click', function() {
        // Use direct selectors for hidden fields
        var placementId = $('input[name="placement-client"]').val();
        var month = $('input[name="placement-month"]').val();
        var year = $('input[name="placement-year"]').val();
        var compensation = $('#placement-compensation').val();

        if (!placementId || !month || !year || !compensation) {
            addClientMessage('Please fill in all placement fields.', 'error', this);
            return;
        }

        $.ajax({
            url: placementRecordsUrl,
            method: 'POST',
            data: {
                placement_id: placementId,
                month: month,
                year: year,
                compensation: compensation,
                csrfmiddlewaretoken: getCSRFToken()
            },
            success: function() {
                // Clear fields after successful add
                $('input[name="placement-client"]').val("");
                $('input[name="placement-month"]').val("");
                $('input[name="placement-year"]').val("");
                $('#placement-compensation').val("");
                // Reset custom dropdown UI for client
                var $dropdown = $('input[name="placement-client"]').closest('.custom-dropdown, .client-placement-dropdown-wrapper');
                $dropdown.find('.selected-option').text('Select a Client');
                $dropdown.find('.client-placement-hidden').val('');
                $dropdown.find('.dropdown-list').hide();
                LoadPlacementRecords();
            },
            error: function(xhr) {
                addClientMessage('Error: ' + xhr.responseText, 'error', '#add-placement-record-btn');
            }
        });
    });
}

/**
 * Loads all placement records for the candidate and updates the DOM.
 */
function LoadPlacementRecords() {
    $.get(placementRecordsUrl, function(data) {
        $('#placement-records-list').html(data);
    });
}

/**
 * Handles custom dropdown selection for client placement and updates the hidden input value.
 */
function HandleClientPlacementDropdown() {
    // For all dropdowns in the DOM (including dynamically added ones)
    $(document).on('click', '.client-placement-list .option', function() {
        var $option = $(this);
        var value = $option.data('value');
        var text = $option.text();
        var $dropdown = $option.closest('.custom-dropdown, .client-placement-dropdown-wrapper');
        $dropdown.find('.selected-option').text(text);
        $dropdown.find('.client-placement-hidden').val(value);
        $dropdown.find('.dropdown-list').hide();
    });
    // Show/hide dropdown list on click
    $(document).on('click', '.selected-option.client-placement-dropdown', function(e) {
        e.stopPropagation();
        var $dropdown = $(this).closest('.custom-dropdown, .client-placement-dropdown-wrapper');
        $dropdown.find('.dropdown-list').toggle();
    });
    // Hide dropdown if clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.custom-dropdown, .client-placement-dropdown-wrapper').length) {
            $('.dropdown-list').hide();
        }
    });
}

/**
 * Display a client message in the closest .messages container to the triggering element.
 * @param {string} messageText - The message to display.
 * @param {string} messageType - 'success' or 'error'.
 * @param {HTMLElement|JQuery} [contextElem] - Optional. The element relative to which the message should be shown.
 */
function addClientMessage(messageText, messageType = 'error', contextElem) {
    let $container;
    if (contextElem) {
        $container = $(contextElem).closest('.section, form, .placement-mobile-fields, .journal-mobile-fields').find('.messages').first();
    } else {
        $container = $('.messages').first();
    }
    $container.empty();
    const alertClass = messageType === 'success' ? 'alert-success' : 'alert-danger';
    const messageHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show flex-display space-between vertical-align" role="alert" style="width: 100%;">
            <span class="message-text">${messageText}</span>
            {% include 'red_shell_recruiting/components/candidate_close_button.html' %}
        </div>
    `;
    $container.append(messageHtml);
}

function LoadPlacementClients() {
    $.getJSON(clientPlacementListUrl, function (data) {
        var $select = $('#placement-client');
        $select.empty();
        $select.append($('<option>', {value: '', text: 'Select Client'}));
        $.each(data, function (i, item) {
            $select.append($('<option>', {value: item.id, text: item.name}));
        });
    });
}

function HandleNewPlacementRecord() {
    // Setup placement date picker
    $('#placement-date').daterangepicker({
        autoApply: false,
        autoUpdateInput: false,
        singleDatePicker: true,
        showDropdowns: true, // Enable year/month dropdowns
        linkedCalendars: false,
        minDate: false,
        locale: {cancelLabel: 'Clear'},
        opens: 'center',
        theme: ''
    });

    $('#placement-date').on('apply.daterangepicker', function (ev, picker) {
        var date = picker.startDate.format('YYYY-MM-DD');
        $(this).text(date);
        $(this).data('selected-date', date);
    });

    $('#placement-date').on('cancel.daterangepicker', function (ev, picker) {
        $(this).text('Select date');
        $(this).data('selected-date', '');
    });

    $('#add-placement-record-btn').on('click', function() {
        // Clear any previous error messages
        $('.placement-messages').empty();

        // Use direct selectors for hidden fields
        var placementId = $('input[name="placement-client"]').val();
        var placementDate = $('#placement-date').data('selected-date');
        var compensation = $('#placement-compensation').val();

        if (!placementId || !placementDate || !compensation) {
            addClientMessage('Please fill in all placement fields.', 'error', this);
            return;
        }

        // Extract month and year from the selected date
        var dateObj = moment(placementDate);
        var month = dateObj.month() + 1; // moment months are 0-indexed
        var year = dateObj.year();

        $.ajax({
            url: placementRecordsUrl,
            method: 'POST',
            data: {
                placement_id: placementId,
                month: month,
                year: year,
                compensation: compensation,
                csrfmiddlewaretoken: getCSRFToken()
            },
            success: function() {
                // Clear fields after successful add
                $('input[name="placement-client"]').val("");
                $('#placement-compensation').val("");
                $('#placement-date').text('Select date').data('selected-date', '');

                // Reset custom dropdown UI for client
                var $dropdown = $('input[name="placement-client"]').closest('.custom-dropdown, .client-placement-dropdown-wrapper');
                $dropdown.find('.selected-option').text('Select Client');
                $dropdown.find('.client-placement-hidden').val('');
                $dropdown.find('.dropdown-list').hide();

                $('.placement-messages').empty(); // Clear any messages on success
                LoadPlacementRecords();
            },
            error: function(xhr) {
                addClientMessage('Error: ' + xhr.responseText, 'error', '#add-placement-record-btn');
            }
        });
    });
}


$(document).ready(function() {
    // Initialize actions
    AddResumeAction();
    AddPortfolioAction();
    AddDocumentAction();
    SaveCandidate();
    CandidateEditSaveActions();
    // PlacementEditSaveActions();
    HandleNewJournalEntry();
    LoadPlacementClients();
    LoadJournalEntries();
    HandleRemovePlacementRecord();
    HandleAddPlacementRecord();
    LoadPlacementRecords();
    HandleClientPlacementDropdown();
    HandleNewPlacementRecord();
    HandleClientPlacementDatePicker();
});
