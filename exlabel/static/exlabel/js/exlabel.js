/**
 * Created by moonkey on 2/29/16.
 */

$(document).ready(function () {
    var pixel_size = 20;
    var x1, y1, timeout;//, totimes = 100, distance = 30;
    var trajectory = [];
    var steps = 0;

    var canvas = document.getElementById("cas"), ctx = canvas.getContext("2d");
    var canvasBox = document.getElementById("bb");
    canvas.width = canvasBox.clientWidth;
    canvas.height = canvasBox.clientHeight;
    mask_img.onload = function () {
        var w = canvas.height * mask_img.width / mask_img.height;
        ctx.drawImage(mask_img, (canvas.width - w) / 2, 0, w, canvas.height);
        tapClip();
    };

    var label_form = $('#label_form');
    label_form.submit(function (e) {
        e.preventDefault();
        var form_data = $(this).serializeArray();
        var form_dict = {};
        for (var i = 0; i < form_data.length; i++) {
            form_dict[form_data[i].name] = form_data[i].value;
        }
        form_dict['trajectory'] = JSON.stringify(trajectory);

        info_region = $('#submit_info');
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
                        "<b>Error: The label was not successfully submitted." +
                        "Please report to the webmaster.</b>");
                info_region.addClass('alert-danger');
                info_region.removeClass('alert-success');
                info_region.show();
                $('#error_info').html(xhr.responseText);
            }
        });
    });

    function getClipArea(e, hastouch) {
        var x = hastouch ? e.targetTouches[0].pageX : e.clientX;
        var y = hastouch ? e.targetTouches[0].pageY : e.clientY;
        var ndom = canvas;
        while (ndom.tagName !== "BODY") {
            x -= ndom.offsetLeft;
            y -= ndom.offsetTop;
            ndom = ndom.parentNode;
        }
        return {
            x: x,
            y: y
        }
    }

// Getting the erasing effect by changing "globalCompositeOperation"
    function tapClip() {
        var hastouch = false, tapstart = "mousedown", keydown = "keydown";
        var area;
//        var x2, y2;
        ctx.globalCompositeOperation = "destination-out";

        function tapstartHandler(e) {
            clearTimeout(timeout);
            e.preventDefault();
            area = getClipArea(e, hastouch);
            x1 = Math.round(area.x / pixel_size) * pixel_size;
            y1 = Math.round(area.y / pixel_size) * pixel_size;
            x1 = Math.max(x1, 10);
            y1 = Math.max(y1, 10);
            x1 = Math.min(x1, canvas.width - 10);
            y1 = Math.min(y1, canvas.height - 10);
            goDot(x1, y1);
            this.removeEventListener(tapstart, tapstartHandler);
            this.addEventListener(keydown, keydownHandler);
        }

        window.addEventListener(tapstart, tapstartHandler);
    }

    function keydownHandler(e) {
        e = e || event;
        //window.alert(e.keyCode);
        if (e.keyCode == "81") {
            // Q
            x1 = x1 - pixel_size;
            y1 = y1 - pixel_size;
            goDot(x1, y1);
        }
        if (e.keyCode == "69") {
            // E
            x1 = x1 + pixel_size;
            y1 = y1 - pixel_size;
            goDot(x1, y1);
        }
        if (e.keyCode == "90") {
            // E
            x1 = x1 - pixel_size;
            y1 = y1 + pixel_size;
            goDot(x1, y1);
        }
        if (e.keyCode == "67") {
            // C
            x1 = x1 + pixel_size;
            y1 = y1 + pixel_size;
            goDot(x1, y1);
        }
        if (e.keyCode == "37" || e.keyCode == "65") {
            // left
            x1 = x1 - pixel_size;
            goDot(x1, y1);
        }
        if (e.keyCode == "38" || e.keyCode == "87") {
            // up or W
            y1 = y1 - pixel_size;
            goDot(x1, y1);
        }
        if (e.keyCode == "39" || e.keyCode == "68") {
            // right or D
            x1 = x1 + pixel_size;
            goDot(x1, y1);
        }
        if (e.keyCode == "40" || e.keyCode == "88") {
            // down or W
            y1 = y1 + pixel_size;
            goDot(x1, y1);
        }
    }

    function goDot(x1, y1) {
        x1 = Math.min(Math.max(x1, 0), canvas.width - pixel_size);
        y1 = Math.min(Math.max(y1, 0), canvas.height - pixel_size);
        drawDot(x1, y1);

        trajectory.push([x1/pixel_size, y1/pixel_size]);
        steps = trajectory.length;

        document.getElementById("steps").innerHTML = steps.toString();
    }

    function drawDot(x1, y1) {
        ctx.save();
        ctx.beginPath();
        ctx.rect(x1, y1, pixel_size, pixel_size);
        ctx.fill();
        ctx.restore();
    }
});