/**
 * Created by moonkey on 11/23/15.
 */


$(document).ready(function () {
    var forms = $('.form-label-question');
    forms.submit(function (e) {
        e.preventDefault();

        var form_data = $(this).serializeArray();
        var form_dict = {};
        for (var i = 0; i < form_data.length; i++) {
            form_dict[form_data[i].name] = form_data[i].value;
        }

    var question_id = form_dict['question_id'];
    var info_region = $('#info_'+question_id);
    var next_pos = $(this).next().next().position().top;
    $.ajax({
        url: this.action,
        type: "POST",
        cache: false,
        async: true,
        traditional: true,
        data: form_dict,
        dataType: 'json',
        success: function (response) {
            // Nothing needs to be done for the intermediate results
            $(window).scrollTop(next_pos);
            info_region.html('<b>Label successfully submitted to server.</b>');
            info_region.addClass('alert-success');
            info_region.removeClass('alert-danger');
            info_region.show();
        },
        error: function (xhr) {
            info_region.html(
                    "<b>Error: The label was not successfully submitted."+
                    "Please report to the webmaster.</b>");
            info_region.addClass('alert-danger');
            info_region.removeClass('alert-success');
            info_region.show();
            $('#error_info').html(xhr.responseText);
        }
    });

    });

});