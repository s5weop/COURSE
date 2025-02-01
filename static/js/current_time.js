document.addEventListener("DOMContentLoaded", function () {
    const timeBlock = document.querySelector(".time__update");
    if (timeBlock) {
        const now = new Date();
        const formattedTime = now.toLocaleString(); // Локальный формат даты и времени
        timeBlock.textContent = `Обновлено: ${formattedTime}`;
    }
});