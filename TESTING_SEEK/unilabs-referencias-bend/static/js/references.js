(function($) {
'use strict';
$(document).ready(function() {
    let word = window.location.href.split("/");
    if(word[word.length - 2] === 'add' || word[word.length - 2] === 'change') {
        $('.column-user').html('USUARIOS');
        $(".results").text($(".results").text().replace("Results", "Resultados"));
    }

    const before_active = $('#id_active').is(":checked")
    const before_value = $('#id_motive').val()

    $('#id_active').change(function() {
        if($(this).is(":checked") === before_active) {
            $('#id_motive').val(before_value);
            $('#id_motive').css("border","solid 1px #cccccc");
        } else {
            $('#id_motive').css("border","solid 1px red");
            $('#id_motive').val('');
        }
    });

    $('#id_ruc').attr("maxlength", "11");
    $('#id_ruc').keypress(function (e) {
        if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
            return false;
        }
    });

    if ($('select[name=document_type_manager] option').filter(':selected').val() === 'Dni') {
        $('#id_document_number_manager').attr("maxlength", "8");
        $('#id_document_number_manager').keypress(function (e) {
            if ($('select[name=document_type_manager] option').filter(':selected').val() === 'Dni' && e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                return false;
            }
        });
    }
    
    $('select[name=document_type_manager]').on('change', function() {
        let current_type = $('select[name=document_type_manager] option').filter(':selected').val()
        $('#id_document_number_manager').val('')

        if (current_type == 'Dni') {
            $('#id_document_number_manager').attr("maxlength", "8");
            $('#id_document_number_manager').keypress(function (e) {
                if ($('select[name=document_type_manager] option').filter(':selected').val() === 'Dni' && e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                    return false;
                }
            });
        } else if (current_type == 'Carnet extranjeria') {
            $('#id_document_number_manager').attr("maxlength", "12");
        } else if (current_type == 'Pasaporte') {
            $('#id_document_number_manager').attr("maxlength", "12");
        }
    });

});
})(jQuery);