new Swiper("#swiper-1", {
    loop: true,
    autoplay: {
        delay: 5000,
        disableOnInteraction: false,
    },
    pagination: {
        el: ".swiper-pagination",
        clickable: false,
    },
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
});
function updatePaymentForm() {
    //sets const variables for the delivery method and address input field.
    const deliveryMethod = document.getElementById('delivery_method').value;
    const addressInput = document.querySelector('input[name="address"]');
    // fetches the address form and determines if delivery methods is delivery or pickup. 
    if (deliveryMethod === "delivery") {
        addressInput.required = true;
        addressInput.placeholder = "Enter your address (required)";
    } else {
        addressInput.required = false;
        addressInput.placeholder = "Enter your address (optional)";
    }
}
