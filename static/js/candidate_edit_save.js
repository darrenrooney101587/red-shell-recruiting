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

function PlacementEditSaveActions(mobile = false) {
    // INPUT PAGE TOGGLE
    $('#client-placement').change(function () {
        const isChecked = $(this).is(':checked');
        if (isChecked) {
            $('#placement-records-wrapper').slideDown(200);
        } else {
            $('#placement-records-wrapper').slideUp(200);
            $('#placement-records-wrapper').find('.placement-line-item').remove();
            placementIndex = 0;
        }
    });

    // EDIT PAGE TOGGLE
    $('#edit-client-placement-toggle').change(function () {
        const isChecked = $(this).is(':checked');
        const $wrapper = $('#placement-records-wrapper-edit');

        if (isChecked) {
            // Hide and mark for deletion
            $wrapper.slideUp(200);
            $wrapper.find('.placement-line-item').each(function () {
                $(this).find('.delete-marker').val('true');
            });
            $('#remove-all-placements-flag').val('true');
            $('#remove-placement-warning').fadeIn(200);
        } else {
            // Show existing records again (they were not removed yet)
            $wrapper.slideDown(200);
            $wrapper.find('.placement-line-item').show();
            $wrapper.find('.delete-marker').val('false');
            $('#remove-all-placements-flag').val('false');
            $('#remove-placement-warning').hide();
        }
    });

    // ADD PLACEMENT (EDIT MODE)
    let placementIndex = parseInt($('input[name="placement_total_count"]').val()) || 0;

    $('#add-placement-line-edit').click(function () {
        placementIndex++;
        console.log('Hello World')
        let newLine;

        if(mobile) {
            newLine = `
                    <div class="placement-line-item" data-index="${placementIndex}" style="margin-bottom: 1rem;">
                        <div class="flex-display vertical-align" style="margin-bottom: 1rem;">
                            <div class="custom-dropdown client-placement-dropdown-wrapper" style="border-bottom: 1px solid var(--ui-support-element-color);">
                                <div class="flex-display space-between">
                                    <div class="selected-option client-placement-dropdown">Select a Client</div>
                                    <span class="chevron-down">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" aria-hidden="true">
                                            <path fill="none" fill-rule="evenodd" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m16 10-4 4-4-4"/>
                                        </svg>
                                    </span>
                                    <span class="chevron-up" style="display: none;">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" aria-hidden="true" style="transform: rotate(180deg);">
                                            <path fill="none" fill-rule="evenodd" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m16 10-4 4-4-4"/>
                                        </svg>
                                    </span>
                                </div>
                                <ul class="dropdown-list client-placement-list"></ul>
                                <input class="client-placement-hidden" type="hidden" name="placement_id_${placementIndex}" value="">
                            </div>
                        </div>
                        <div class="flex-display space-between vertical-align" style="margin-bottom: 1rem;">
                            <input name="placement_month_${placementIndex}" placeholder="Month" class="text-input" style="margin-right: 1rem; width: 50%; border-bottom: 1px solid var(--ui-support-element-color);">
                            <input name="placement_year_${placementIndex}" placeholder="Year" class="text-input" style="width: 50%; border-bottom: 1px solid var(--ui-support-element-color);">
                        </div>
                        <div class="flex-display vertical-align space-between" style="width: 100%; margin-bottom: 1rem;">
                            <input name="placement_compensation_${placementIndex}" placeholder="Amount" class="text-input" type="number" style="width: 100%; border-bottom: 1px solid var(--ui-support-element-color);">
                            ${removePlacementButton}
                        </div>
                        <input type="hidden" name="delete_placement_${placementIndex}" value="false" class="delete-marker">
                    </div>
                `;
        } else {
            newLine = `
                <div class="placement-line-item" data-index="${placementIndex}" style="">
                    <div style="margin-bottom: 1rem;">
                        <div class="custom-dropdown" style="border-bottom: 1px solid var(--ui-support-element-color);">
                            <div class="flex-display space-between">
                                <div class="selected-option client-placement-dropdown">Select a Client</div>
                                <span class="chevron-down">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" aria-hidden="true">
                                        <path fill="none" fill-rule="evenodd" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m16 10-4 4-4-4"/>
                                    </svg>
                                </span>
                                <span class="chevron-up" style="display: none;">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" aria-hidden="true" style="transform: rotate(180deg);">
                                        <path fill="none" fill-rule="evenodd" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" d="m16 10-4 4-4-4"/>
                                    </svg>
                                </span>
                            </div>
                            <ul class="dropdown-list client-placement-list"></ul>
                            <input class="client-placement-hidden" type="hidden" name="placement_id_${placementIndex}" value="">
                        </div>
                    </div>
                    <div class="flex-display align-center">
                        <input name="placement_month_${placementIndex}" placeholder="Month" class="text-input" style="width: 80px; border-bottom: 1px solid var(--ui-support-element-color);">
                        <input name="placement_year_${placementIndex}" placeholder="Year" class="text-input" style="margin-left: 1rem; width: 100px; border-bottom: 1px solid var(--ui-support-element-color);">
                        <input name="placement_compensation_${placementIndex}" placeholder="Amount" class="text-input" type="number" style="border-bottom: 1px solid var(--ui-support-element-color); margin-left: 1rem; width: 200px;">
                        <input type="hidden" name="delete_placement_${placementIndex}" value="false" class="delete-marker">
                        <div style="position: relative; top: -6px;">
                            ${removePlacementButton}
                        </div>
                    </div>
                </div>
            `;
        }

        $('#placement-records-wrapper-edit').append(newLine);

        // Populate the dropdown list inside this new row
        const $newRow = $('#placement-records-wrapper-edit .placement-line-item').last();
        const $list = $newRow.find('.client-placement-list');

        $.get(clientPlacementListUrl, function (data) {
            $list.empty();
            data.forEach(function (item) {
                $list.append(`<li class="option" data-value="${item.id}">${item.name}</li>`);
            });
        });

        $('input[name="placement_total_count"]').val(placementIndex);

        // REMOVE PLACEMENT LINE (Shared)
        $(document).on('click', '.remove-placement', function () {
            const group = $(this).closest('.placement-line-item');
            group.find('.delete-marker').val('true');
            group.hide();
        });

        // DELETE PLACEMENT TOGGLE (Edit Mode)
        $(document).on('click', '.delete-single-placement', function () {
            $('#client-placement-toggle-wrapper').slideUp(200);
            $('#client-placement-delete').val('true');
            $('#client-placement').prop('checked', false).trigger('change');
        });

        $(document).on('click', function (e) {
            if (!$(e.target).closest('.custom-dropdown').length) {
                $('.dropdown-list').hide();
            }
        });

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
        forceSingleDateMultiMonth: true,
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
    $('#add-placement-record-btn').on('click', function () {
        var placementId = $('#placement-client').val();
        var month = $('#placement-month').val();
        var year = $('#placement-year').val();
        var compensation = $('#placement-compensation').val();
        if (!placementId || !month || !year || !compensation) {
            addClientMessage('Please fill all placement fields.');
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
                csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function () {
                $('#placement-client').val('');
                $('#placement-month').val('');
                $('#placement-year').val('');
                $('#placement-compensation').val('');
                LoadPlacementRecords();
            },
            error: function (xhr) {
                addClientMessage('Error: ' + xhr.responseText);
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
    PlacementEditSaveActions();
    HandleNewJournalEntry();
    LoadPlacementClients();
    LoadJournalEntries();
    HandleRemovePlacementRecord();
    HandleAddPlacementRecord();
    LoadPlacementRecords();
    HandleClientPlacementDropdown();
    HandleNewPlacementRecord();
});
