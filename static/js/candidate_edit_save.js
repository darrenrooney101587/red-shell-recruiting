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
                        <input name="placement_compensation_${placementIndex}" placeholder="Amount" class="text-input" type="number" style="margin-left: 1rem; width: 150px; border-bottom: 1px solid var(--ui-support-element-color);">
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
