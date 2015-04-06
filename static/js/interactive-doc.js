var blah;

$(document).ready(function () {
    $("#wsdemo_example").text($("#wsdemo_code").text().trim());

    $("tr").click(function () {
        if ($(this).attr("href") !== undefined)
            window.document.location = $(this).attr("href");
    });

    $('.api_submit').click(function () {
        var parent = $(this).parent().parent().parent();
        blah = parent;
        var data = {};
        parent.find('input').each(function () {
            var target = $(this);
            data[target.attr('name')] = target.val();
        });

        $.ajax({
            url: parent.attr('route'),
            type: parent.attr('method'),
            data: data,
            success: function (result) {
                var raw = JSON.stringify(result, null, 4);
                var ancestor = $(parent).parent().parent().parent();
                ancestor.find('code').text(raw);
            }
        });
    });

    hljs.initHighlighting();
});