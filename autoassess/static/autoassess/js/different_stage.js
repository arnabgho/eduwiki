/**
 * Created by moonkey on 6/19/15.
 */

var start_time = new Date();
var topic_confidence_time = new Date();

$(document).ready(function () {
    start_time = Date.now();

    var topic_confidence_bar = $('#topic_confidence');
    var topic_cofidence_region = $('#topic_confidence_region');
    var after_topic_confidence = $('#after_topic_confidence');
    var pre_topic_confidence = $('#pre_topic_confidence');

    topic_confidence_bar.change(function (e) {
        if (this.value <= 0) {
            return 1;
        }

        topic_cofidence_region.hide();

        pre_topic_confidence.hide();
        after_topic_confidence.show();
        topic_confidence_time = Date.now();
    });

//    $(document).on('mouseleave', function () {
//        console.log('mouse exited');
//        alert("You cannot leave this page before you submit.");
//    });


//    $(window).blur(function () {
//        if (!confirm("You cannot leave the page during the process of the HIT. " +
//            "If you leave this page now, you will not be able to submit!")) {
//            if (!document.hasFocus()) {
//                console.log("user left the page");
//                $("#submit_answer").disable();
//            }
//        }
//    });

});