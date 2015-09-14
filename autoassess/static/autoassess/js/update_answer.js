/**
 * Created by moonkey on 8/19/15.
 */

var last_submit_time = start_time;

function update_question(question_to_update) {
    var question_answer_form = $('#question_answer_form');
    var no_question_order = true;

    var form_data = question_answer_form.serializeArray();
    var form_dict = {};
    for (var i = 0; i < form_data.length; i++) {
        form_dict[form_data[i].name] = form_data[i].value;
    }

    // The first time of submitting, the question order should be recorded

    if (no_question_order) {
        form_dict['question_order'] = JSON.stringify(question_order);
    }

    // identifier for the question to update
    form_dict['question_to_update'] = question_to_update;

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
            no_question_order = false;
        },
        error: function (xhr) {
            alert(
                    "Error: The answer is not successfully posted. " +
                    "Please do not proceed if you see this message. " +
                    "If this is the first question, return this HIT (as it might be because " +
                    "of browser incompatibility)." +
                    "Otherwise try again in ten seconds," +
                    "and report to the webmaster if this still occurs.");
            $('#error_info').html(xhr.responseText);
        }
    });
}

$(document).ready(function () {
    var all_radio_inputs = $('input:radio');

    all_radio_inputs.change(function () {
        update_question(this.name);
    });
});