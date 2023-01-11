const images = document.querySelectorAll('.image');
const viewimage = document.querySelector('#viewimage');

images.forEach((span) => {
    a = span.firstChild
    a.addEventListener('click', (e) => {
        viewimage.style.display = 'block';
        viewimage.style.backgroundImage = 'url(' + a.href + ')';
        e.preventDefault();
    }, false);
});
