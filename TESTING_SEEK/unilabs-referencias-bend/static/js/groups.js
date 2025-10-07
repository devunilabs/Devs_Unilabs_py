(function($) {
'use strict';
$(document).ready(function() {
    $('.column-user').html('USUARIOS');
    
    let word = window.location.href.split("/");
    if(word[word.length - 2] === 'change') {
        if ($('#id_name').val() === 'Unilabs' || $('#id_name').val() === 'Referencia') {
            $('#id_name').attr('readonly', true);
        }
    }

});
})(jQuery);