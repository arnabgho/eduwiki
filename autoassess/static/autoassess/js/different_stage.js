/**
 * Created by moonkey on 6/19/15.
 */

var start_time = new Date();
var topic_confidence_time = new Date();

$(document).ready(function () {
    start_time = Date.now();

    var topic_confidence_bar = $('#topic_confidence');
    var after_topic_confidence = $('#after_topic_confidence');
    var pre_topic_confidence = $('#pre_topic_confidence');

    topic_confidence_bar.change(function (e) {
        if (this.value <= 0) {
            return 1;
        }

        after_topic_confidence.show();
        pre_topic_confidence.hide();
//        this.attr("readonly", true);
        topic_confidence_time = Date.now();
    });
});