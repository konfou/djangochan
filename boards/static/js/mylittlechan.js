const tzname = Intl.DateTimeFormat().resolvedOptions().timeZone;
document.cookie = "tzname=" + tzname + ";Path=/" + ";SameSite=Strict";

const kdEventExclude = ['input', 'textarea'];

var replies;
var viewimage;
var images;
var currentImageIndx;

var scrollPos;

/* generic utility functions */

function keepScrollPos() {
    scrollPos = document.scrollingElement.scrollTop;
}

/* site-specific functions */

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

function onBodyLoad() {
    try { // at board or thread
        buttonSubmit = document.querySelector('input[type=submit]').remove();
        document.getElementById('text-submit').style.visibility = "visible";
    } catch (e) {} // at index
    replies = document.querySelectorAll('.reply');
    viewimage = document.querySelector('#viewimage');
    images = document.querySelectorAll('.image');
    images.forEach((span, indx) => {
        a = span.firstChild;
        a.addEventListener('click', (e) => {
            viewimage.style.display = 'block';
            viewimage.style.backgroundImage = 'url(' + e.currentTarget.href + ')';
            currentImageIndx = indx;
            e.preventDefault();
        }, false);
    });
}

function changeImage(di) {
    var nextImageIndx = currentImageIndx + di;
    if (nextImageIndx < 0 || nextImageIndx >= images.length)
        return;
    currentImageIndx = nextImageIndx;
    var a = images[currentImageIndx].firstChild;
    viewimage.style.backgroundImage = 'url(' + a.href + ')';
}

document.addEventListener('keydown', (e) => {
    var srcElem = e.target;
    if (kdEventExclude.indexOf(srcElem.tagName) == -1) {
        switch (e.key) {
        case "b":
            keepScrollPos()
            document.querySelector('#bottom').scrollIntoView();
            break;
        case "t":
            keepScrollPos()
            document.querySelector('#top').scrollIntoView();
            break;
        case "s":
            document.scrollingElement.scrollTop = scrollPos;
            break;
        case "Escape":
            viewimage.style.display = 'none';
            break;
        case "ArrowLeft":
            if (viewimage.style.display == 'block') {
                changeImage(-1)
            } else {
                Array.from(replies).find((el) => el.getBoundingClientRect().top - document.scrollingElement.scrollTop < 0).scrollIntoView();
            }
            break;
        case "ArrowRight":
            if (viewimage.style.display == 'block') {
                changeImage(1)
            } else {
                Array.from(replies).find((el) => el.getBoundingClientRect().top - document.scrollingElement.scrollTop > 0).scrollIntoView();
            }
            break;
        }
    }
}, false);

onBodyLoad()
htmx.on('htmx:afterOnLoad', onBodyLoad)
