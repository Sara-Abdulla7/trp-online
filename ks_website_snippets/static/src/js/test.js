$(document).ready(function(){
    $(document).on('click', '.child-child', function () {
        var nextChildList = $(this).next('.child-list');
        if (nextChildList.is(':hidden')) {
            nextChildList.show();
        } else {
            nextChildList.hide();
        }
    });
});

