let mouseX = 0, mouseY = 0;

// Track mouse movement
document.addEventListener('mousemove', (event) => {
    mouseX = event.clientX;
    mouseY = event.clientY;
});

// Capture keypress and return mouse coordinates only for "Ctrl" key press
document.addEventListener('keydown', (event) => {
    const coordinates = {
        x: mouseX,
        y: mouseY
    };
    if (event.key === 'Control') {
        console.log(event);
        window.handle_click(coordinates);
    }
});