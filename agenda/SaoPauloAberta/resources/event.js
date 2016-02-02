function ScrollDownCb() {
        var media = document.getElementsByClassName("media-elements")[0];    
        media.scrollTop += 30;
}

var downInterval;
function ScrollMediaDownPress() {
        ScrollDownCb();
        downInterval = setInterval(ScrollDownCb, 100);
}

function ScrollMediaDownRelease() {
        clearInterval(downInterval);
}
var mediaDown = document.getElementById("media-down");
mediaDown.addEventListener("mousedown", ScrollMediaDownPress);
mediaDown.addEventListener("mouseup", ScrollMediaDownRelease);

var upInterval;
function ScrollMediaUpPress() {
        ScrollUpCb();
        upInterval = setInterval(ScrollUpCb, 100);
}

function ScrollMediaUpRelease() {
        clearInterval(upInterval);
}

function ScrollUpCb() {
        var media = document.getElementsByClassName("media-elements")[0];    
        media.scrollTop -= 30;
}
var mediaUp = document.getElementById("media-up");
mediaUp.addEventListener("mousedown", ScrollMediaUpPress);
mediaUp.addEventListener("mouseup", ScrollMediaUpRelease);

var mediaTitle = document.getElementById("media-title");
var mediaEmbed= document.getElementById("media-embed");
function SelectMedia(element) {
	var name = element.getAttribute("data-name");
	var address = element.getAttribute("data-address");
	mediaTitle.innerHTML = name;
	mediaEmbed.innerHTML = '<iframe src="' + address + '" frameborder="0" allowfullscreen></iframe>';
}

