document.addEventListener("DOMContentLoaded", () => {
    const firstError = document.querySelector(".field-error input, .field-error select, .field-error textarea")
    if (firstError) {
        firstError.focus()
    }
})
