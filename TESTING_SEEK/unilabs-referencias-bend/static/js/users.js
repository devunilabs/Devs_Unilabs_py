(function($) {
'use strict';
$(document).ready(function() {
    $('.column-user').html('USUARIOS');
    
    let word = window.location.href.split("/");
    if(word[word.length - 2] === 'add') {
        // Selected all
        $('#id_access option').prop('selected', true);

        // Hide and show
        $('#id_type').on('change', function() {
           if (this.value === 'Unilabs') {
               $('#id_references').parent().parent().parent().parent().hide()
               $('#id_access').parent().parent().parent().parent().hide()
           } else {
               $('#id_references').parent().parent().parent().parent().show()
               $('#id_access').parent().parent().parent().parent().show()
           }
        });
    }

    if ($('select[name=type] option').filter(':selected').val()==='Unilabs') {
        $('#id_references_from').attr("disabled", true);
        $('#id_access').attr("disabled", true);
    } else {
        $('#id_is_admin_bk').attr("disabled", true);
        $('#id_is_superuser').attr("disabled", true);
    }

    $('#id_type').on('change', function() {
         if ($('select[name=type] option').filter(':selected').val()==='Unilabs') {
            $('#id_references_from').attr("disabled", true);
            $('#id_access').attr("disabled", true);

            $('#id_is_admin_bk').attr("disabled", false);
            $('#id_is_superuser').attr("disabled", false);

        } else {
             $('#id_references_from').attr("disabled", false);
             $('#id_access').attr("disabled", false);

             $('#id_is_admin_bk').attr("disabled", true);
             $('#id_is_superuser').attr("disabled", true);
         }
    });

    $("#user_form").submit(function(e){
        let references = $('select[name=references] option').filter(':selected').val()
        let access = $('select[name=access] option').filter(':selected').val()
        let type = $('select[name=type] option').filter(':selected').val()
        $( ".errorlist" ).remove();

        if(($("#id_references").length > 0) && references === undefined && type==='Referencia') {
            $('html, body').animate({
                scrollTop: $("#id_references").offset().top
            }, 500);
            $('#id_references').parent().parent().parent().append("<ul class=\"errorlist\"><li>Este campo es requerido.</li></ul>")
            e.preventDefault();
        }
        if(($("#id_access").length > 0) && access === undefined && type==='Referencia') {
            $('html, body').animate({
                scrollTop: $("#id_access").offset().top
            }, 500);
            $('#id_access').parent().parent().parent().append("<ul class=\"errorlist\"><li>Este campo es requerido.</li></ul>")
            e.preventDefault();
        }
    });

    if ($('select[name=document_type] option').filter(':selected').val() === 'Dni') {
        $('#id_document_number').attr("maxlength", "8");
        $('#id_document_number').keypress(function (e) {
            if ($('select[name=document_type] option').filter(':selected').val() === 'Dni' && e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                return false;
            }
        });
    }
    
    $('select[name=document_type]').on('change', function() {
        let current_type = $('select[name=document_type] option').filter(':selected').val()
        $('#id_document_number').val('')

        if (current_type == 'Dni') {
            $('#id_document_number').attr("maxlength", "8");
            $('#id_document_number').keypress(function (e) {
                if ($('select[name=document_type] option').filter(':selected').val() === 'Dni' && e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                    return false;
                }
            });
        } else if (current_type == 'Carnet extranjeria') {
            $('#id_document_number').attr("maxlength", "12");
        } else if (current_type == 'Pasaporte') {
            $('#id_document_number').attr("maxlength", "12");
        }
    });

    if(word[word.length - 2] === 'change') {
        if ($('select[name=type] option').filter(':selected').val()==='Unilabs') {
            setTimeout(function(){
                $('#id_references_add_all_link').hide();
                $('.selector-chooser').hide();
                $('#id_references_from').attr("disabled", true);
            }, 1500);
        }
    }
});
})(jQuery);