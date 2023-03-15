$(document).ready(function () {
    $('.invisible-row').css('opacity', 0.5);

    // Update link text for invisible rows
    $('.font-medium').each(function () {
        const $link = $(this);
        const subscriptionId = $link.data('subscription-id');
        const $row = $(`#row-${subscriptionId}`);
        if ($row.css('opacity') == 0.5) {
            $link.text('Unhide');
        }
    });
});


function hideChannel(event, element) {
    event.preventDefault(); // Prevent the link from redirecting
    const subscriptionId = $(element).data('subscription-id');
    const row = $(`#row-${subscriptionId}`);

    // Toggle opacity of the row
    const opacity = row.css('opacity') == 1 ? 0.5 : 1;
    row.css('opacity', opacity);

    // Send POST request to Flask route
    const visibility = opacity == 1 ? true : false;
    $.post('/update_subscription_visibility', { 'user_subscription_id': subscriptionId, 'visibility': visibility })
        .done(function (data) {
            // Change text of the link
            const linkId = `#hide-link-${subscriptionId}`;
            const text = opacity == 1 ? 'Hide' : 'Unhide';
            $(linkId).text(text);
        })
        .fail(function () {
            alert('Failed to update subscription visibility');
        });
}
