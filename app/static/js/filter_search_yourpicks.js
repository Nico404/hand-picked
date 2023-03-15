$(document).ready(function () {
    $("#search_bar").on("keyup", function () {
        var value = $(this).val().toLowerCase();
        $("#list_item tr").filter(function () {
            $(this).toggle($(this).text()
                .toLowerCase().indexOf(value) > -1)
        });
    });
});
