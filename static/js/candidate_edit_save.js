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
        formData.append('resume', fileInput.files[0]);
        formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');

        $.ajax({
            url: '{% url "upload-resume" candidate.id %}',
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
        formData.append('candidate_document', fileInput.files[0]);
        formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');

        $.ajax({
            url: '{% url "upload-document" candidate.id %}',
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
            $wrapper.slideDown(200);
            $wrapper.find('.placement-line-item').show();
            $('#remove-all-placements-flag').val('false');
            $('#remove-placement-warning').hide();
        } else {
            $wrapper.slideUp(200);
            $wrapper.find('.placement-line-item').hide();
            $('#remove-all-placements-flag').val('true');
            $('#remove-placement-warning').fadeIn(200);
        }
    });

    // ADD PLACEMENT (EDIT MODE)
    let placementIndex = parseInt($('input[name="placement_total_count"]').val()) || 0;

    $('#add-placement-line-edit').click(function () {
        placementIndex++;

        $('#edit-client-placement-toggle').prop('checked', true).trigger('change');

        let newLine;

        if(mobile) {
            newLine = `
                    <div class="placement-line-item" data-index="${placementIndex}" style="margin-bottom: 1rem;">
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
                        <div class="flex-display space-between vertical-align">
                            <input name="placement_month_${placementIndex}" placeholder="Month" class="text-input" style="width: 80px; border-bottom: 1px solid var(--ui-support-element-color);">
                            <input name="placement_year_${placementIndex}" placeholder="Year" class="text-input" style="width: 100px; border-bottom: 1px solid var(--ui-support-element-color);">
                            <input type="hidden" name="delete_placement_${placementIndex}" value="false" class="delete-marker">
                            ${removePlacementButton}
                        </div>
                    </div>
                `;
        } else {
            newLine = `
                    <div class="placement-line-item flex-display align-center" data-index="${placementIndex}" style="margin-bottom: 1rem;">
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
                        <input name="placement_month_${placementIndex}" placeholder="Month" class="text-input" style="margin-left: 1rem; width: 80px; border-bottom: 1px solid var(--ui-support-element-color);">
                        <input name="placement_year_${placementIndex}" placeholder="Year" class="text-input" style="margin-left: 1rem; width: 100px; border-bottom: 1px solid var(--ui-support-element-color);">
                        <input type="hidden" name="delete_placement_${placementIndex}" value="false" class="delete-marker">
                        ${removePlacementButton}
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
