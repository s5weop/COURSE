document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("img").forEach(img => {
        // Добавление иконки лупы
        const magnifier = document.createElement("div");
        magnifier.style.position = "absolute";
        magnifier.style.width = "20px";
        magnifier.style.height = "20px";
        magnifier.style.background = "url(static/icons/searching.png)";
        magnifier.style.backgroundSize = "contain";
        magnifier.style.pointerEvents = "none";
        magnifier.style.right = "10px";
        magnifier.style.bottom = "10px";
        magnifier.style.position = "absolute";

        const wrapper = document.createElement("div");
        wrapper.style.position = "relative";
        wrapper.style.display = "inline-block";

        img.parentNode.insertBefore(wrapper, img);
        wrapper.appendChild(img);
        wrapper.appendChild(magnifier);

        img.addEventListener("click", function () {
            const overlay = document.createElement("div");
            overlay.style.position = "fixed";
            overlay.style.top = 0;
            overlay.style.left = 0;
            overlay.style.width = "100vw";
            overlay.style.height = "100vh";
            overlay.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
            overlay.style.display = "flex";
            overlay.style.justifyContent = "center";
            overlay.style.alignItems = "center";
            overlay.style.zIndex = 1000;

            const enlargedImg = document.createElement("img");
            enlargedImg.src = this.src;
            enlargedImg.style.maxWidth = "90vw";
            enlargedImg.style.maxHeight = "90vh";

            enlargedImg.style.objectFit = "contain";

            overlay.appendChild(enlargedImg);
            document.body.appendChild(overlay);

            overlay.addEventListener("click", function () {
                overlay.remove();
            });
        });
    });
});
