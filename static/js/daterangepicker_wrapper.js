/**
 * Returns an array of class names for a jQuery element.
 * @param el - jQuery element
 * @returns {Array}
 */
function getClasses(el) {
    var classAttr = el.attr('class');
    return classAttr ? classAttr.split(/\s+/) : [];
}

/**
 * Custom date picker initialization for journal entry date field.
 * @param parentEl - selector for the parent element
 */
function datePicker(parentEl) {
    setTimeout(function() {
        picker();
    }, 500);

    function picker() {
        var el = $(parentEl).parent();
        var classes = getClasses(el);
        var hasTheme = function() {
            for(var i = 0; i < classes.length; i++) {
                if(classes[i].includes('section-theme')) {
                    return classes[i];
                }
            }
            return '';
        };

        var dateParams = {
            date_bx_ext: parentEl,
            date_bx_date_std_input: parentEl + ' #journal-meeting-date',
            date_bx_input_class: 'date-bx-input',
            single_date_picker: true
        };

        $(dateParams.date_bx_date_std_input).daterangepicker({
            opens: 'center',
            minDate: new Date(),
            singleDatePicker: dateParams.single_date_picker,
            locale: { cancelLabel: 'Clear' },
            autoUpdateInput: false,
            theme: hasTheme()
        }, function(start) {
            $(dateParams.date_bx_ext + ' #journal-meeting-date').val(start.format('YYYY-MM-DD'));
        });

        $(dateParams.date_bx_date_std_input).on('cancel.daterangepicker', function() {
            $(dateParams.date_bx_date_std_input).val('').blur();
            picker();
        });

    }
}
