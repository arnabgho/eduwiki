/**
 * Created by moonkey on 8/19/15.
 */

$(document).ready(function () {
    var question_answer_form = $('#question_answer_form');

    var all_radio_inputs = $('input:radio');

    var last_submit_time = start_time;

    all_radio_inputs.change(function () {
        var form_data = question_answer_form.serializeArray();
        var form_dict = {};
        for (var i = 0; i < form_data.length; i++) {
            form_dict[form_data[i].name] = form_data[i].value;
        }

        // identifier for the question to update
        form_dict['question_to_update'] = this.name;

        var submit_time = Date.now();
        form_dict['submit_time_delta'] = (submit_time - last_submit_time).toString();

        last_submit_time = submit_time;

        $.ajax({
            url: question_answer_form.attr('eduwiki_update_action'),
            type: "POST",
            cache: false,
            async: true,
            traditional: true,
            data: form_dict,
            dataType: 'json',
            success: function (response) {
                // Nothing needs to be done for the intermediate results
            },
            error: function (xhr) {
                alert(
                        "SERVER Error: The answer is not successfully posted, please try again later. " +
                        "Report to the webmaster if this occurs all the time.");
                $('#error_info').html(xhr.responseText);
            }
        });


    });


});