/**
 * Created by moonkey on 9/10/15.
 */
//TODO:: always add update_answer.js before this, for function update_question()

$(document).ready(function () {
//    var question_answer_form = $('#question_answer_form');

    var quiz_submit_button = $('#submit_answer');

    var first_question = question_order[0];

    for (var idx = 0; idx < question_order.length; idx++) {
        var qid = question_order[idx];
        var q_panel_name = 'question_panel_' + qid;
        var q_panel = $("#" + q_panel_name);
        if (qid != first_question) {
            q_panel.hide();
        } else {
            q_panel.show();
        }
    }

    var next_question_buttons = $('.btn-next-question');

    next_question_buttons.click(function () {
        var current_question = this.name.substring('submit_question_'.length);
        var current_question_page_idx = question_order.indexOf(current_question);

        var question_radio = 'question_answer_' + current_question;
        var question_comment = 'comment_' + current_question;
        var comment_validated = false;
        if ($('#'+question_comment)[0] == undefined){
            comment_validated = true;
        }else{
            if($('#'+question_comment)[0].checkValidity()){
                comment_validated = true;
            }
        }
        if (!$('#'+question_radio)[0].checkValidity() ||
            !(comment_validated)
            ){
            quiz_submit_button.click();
            return false;
        }

        update_question(question_radio);

        if (current_question_page_idx < question_order.length - 1) {
            // not the last question
            var next_question = question_order[current_question_page_idx + 1];

            for (var idx = 0; idx < question_order.length; idx++) {

                var qid = question_order[idx];
                var q_panel_name = 'question_panel_' + qid;
                var q_panel = $("#" + q_panel_name);
                if (qid != next_question) {
                    q_panel.hide();
                } else {
                    q_panel.show();
                }
            }
        } else {
            var quiz_area = $('#quiz_area');
            quiz_area.hide();
            var submission_area = $('#final_submission_area');
            submission_area.show();
        }
    });

});