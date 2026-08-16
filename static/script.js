function updatePaymentForm() {
    const deliveryMethod = document.getElementById('delivery_method').value;
    const addressInput = document.querySelector('input[name="address"]');

    if (deliveryMethod === "delivery") {
        addressInput.required = true;
        addressInput.placeholder = "Enter your address (required)";
    } else {
        addressInput.required = false;
        addressInput.placeholder = "Enter your address (optional)";
    }
}