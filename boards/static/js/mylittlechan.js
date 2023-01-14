const tzname = Intl.DateTimeFormat().resolvedOptions().timeZone;
document.cookie = "tzname=" + tzname + ";Path=/" + ";SameSite=Strict";

function quote(pk) {
    var text = document.getElementById('id_text');
    text.value += `>>${pk}\n`;
    document.querySelector('.newpostform').scrollIntoView();
    var scrollback = document.getElementById('scrollback');
    scrollback.style.visibility = "visible";
    scrollback.style.margin = "8px";
    scrollback.firstChild.nextElementSibling.href = `#p${pk}`;
    scrollback.addEventListener('click', (e) => {
        scrollback.style.visibility = "hidden";
        scrollback.style.margin = "";
    }, false);
}

function onbodyload() {
    try { // at board or thread
        buttonSubmit = document.querySelector('input[type=submit]').remove();
        document.getElementById('text-submit').style.visibility = "visible";
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
