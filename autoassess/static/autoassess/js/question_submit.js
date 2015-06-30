/**
 * Created by moonkey on 6/18/15.
 */

$(document).ready(function () {
    var question_answer_form = $('#question_answer_form');

    var eduwiki_server_success = false;
    question_answer_form.submit(function (e) {
        if (eduwiki_server_success) {
            return 0;
            // default form submission behavior
        }
        e.preventDefault();


        var submit_time = Date.now();

        var form_data = $(this).serializeArray();
        var form_dict = {};
        for (var i = 0; i < form_data.length; i++) {
            form_dict[form_data[i].name] = form_data[i].value;
        }

        form_dict['submit_time_delta'] = (submit_time - start_time).toString();
        form_dict['topic_confidence_time_delta'] = (topic_confidence_time - start_time).toString();

        $.ajax({
            url: $(this).attr('eduwiki_action'),
            type: "POST",
            cache: false,
            async: true,
            traditional: true,
            data: form_dict,
            dataType: 'json',
            success: function (response) {
                // mturk will filter submitted data with field name 'hitId'
                delete form_dict['hitId'];
                delete form_dict['csrfmiddlewaretoken'];

                eduwiki_server_success = true;
                question_answer_form.submit();
            },
            error: function (xhr) {
                alert("SERVER Error: The answer is not successfully posted, please try again later. " +
                    "Report to the webmaster if this occurs all the time." + xhr.responseText);
            }
        });
    });
});