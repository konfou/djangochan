function onbodyload() {
    try { // at board or thread
        buttonSubmit = document.querySelector('input[type=submit]').remove();
        document.getElementsByClassName('text-submit')[0].style.visibility = "visible";
    } catch (e) {} // at index
    var viewimage = document.querySelector('#viewimage');
    var images = document.querySelectorAll('.image');
    images.forEach((span) => {
        a = span.firstChild
        a.addEventListener('click', (e) => {
            viewimage.style.display = 'block';
            viewimage.style.backgroundImage = 'url(' + e.currentTarget.href + ')';
            e.preventDefault();
        }, false);
    });
}

onbodyload()
htmx.on('htmx:afterOnLoad', onbodyload)