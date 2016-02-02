function AssessElement(element) {
    var valid = true;
    if (!element.value.length) {
        element.scrollIntoView();
        element.style.boxShadow = "0 0 7px #FF0000";
        valid = false;
    }
    else {
        element.style.boxShadow = "";
    }
    return valid;    
}

function Validate() {
    var valid = true;
    if (!AssessElement(document.getElementById("name")) ||
        !AssessElement(document.getElementById("summary")) || 
        !AssessElement(document.getElementById("desc")) || 
        !AssessElement(document.getElementById("start-time")) || 
        !AssessElement(document.getElementById("start-date")) || 
        !AssessElement(document.getElementById("end-time")) || 
        !AssessElement(document.getElementById("end-date")) || 
        !AssessElement(document.getElementById("address"))  
        ) {
        
        valid = false;
    }
    else {
            var agree = document.getElementById("agree");
            if (!agree.checked) {
                valid = false;
                agree.scrollIntoView();
                agree.style.boxShadow = "0 0 7px #FF0000";
            }
    }

    return valid; 
}

function CaptureInfo(action) {
    if (!Validate()) return;

    var srcForm = document.getElementsByName("ap-data")[0];
    if (ID) srcForm.appendChild(GenFormField("id", ID));
    srcForm.appendChild(GenFormField("title", document.getElementById("name").value));
    srcForm.appendChild(GenFormField("summary", document.getElementById("summary").value));
    srcForm.appendChild(GenFormField("description", document.getElementById("desc").value));
    srcForm.appendChild(GenFormField("start-date", document.getElementById("start-date").value));
    srcForm.appendChild(GenFormField("start-time", document.getElementById("start-time").value));
    srcForm.appendChild(GenFormField("end-date", document.getElementById("end-date").value));
    srcForm.appendChild(GenFormField("end-time", document.getElementById("end-time").value));
    srcForm.appendChild(GenFormField("location", document.getElementById("address").value));
    srcForm.appendChild(GenFormField("map-center", ol.proj.transform(map.getView().getCenter(), 'EPSG:900913', 'EPSG:4326')));
    srcForm.appendChild(GenFormField("zoom-level", map.getView().getZoom()));
    
    var addedMedia = document.getElementsByClassName("ap-media-element")
    var elementCount = 0;

    var frontPage = -1;
    for (var i = 0; i < addedMedia.length; i++) {
        var element = addedMedia[i];
        if (element.style.display != "none") {
            var url = element.getElementsByClassName("ap-media-pic")[0].getAttribute("data-src");                  
            var title = element.getElementsByClassName("ap-media-description")[0].innerHTML;
            var isFront = element.getElementsByClassName("ap-media-check")[0].innerHTML == "F";
            if (isFront) {frontPage = elementCount;}
            srcForm.appendChild(GenFormField("media" + elementCount + "url", url));
            srcForm.appendChild(GenFormField("media" + elementCount + "title", title));
            elementCount += 1;
        }
    }
    srcForm.appendChild(GenFormField("front-page", frontPage));
    srcForm.appendChild(GenFormField("action", action));
    srcForm.submit();
}

function GenFormField(name, value) {
    var node = document.createElement("input");
    node.setAttribute("type", "hidden");
    node.setAttribute("name", name);
    node.setAttribute("value", value);
    return node
}

var inputs = $('input, textarea, select, button');
var modalVisible = false;
$(document).keydown(function(e) {
     if (modalVisible) {                    
        if (e.keyCode == 9 || e.which == 9) {
            console.log("Tab");
            var next = e.target;
            do {
                next = inputs.get(inputs.index(next) + 1)
                if (!next) {
                        next = inputs.get(0);
                }
                console.log("Searching");
                console.log(next);
            }while (!$(next).hasClass("modal") && next != e.target);
            next.focus();
            e.preventDefault();
            
        }
        if (e.keyCode == 27 || e.which == 25) {
            HideModal();
        }
     }
});

var edit = null;
function ShowModal(isEdit, element) {
    modal = document.getElementsByClassName("ap-modal")[0];
    modal.style.display = "";
    modalVisible = true;
    document.getElementById("ap-modal-data-url").focus();
    if (isEdit) {
        edit = element;

        var url = element.getElementsByClassName("ap-media-pic")[0].getAttribute("data-src");
        var title = element.getElementsByClassName("ap-media-description")[0].innerHTML;

        document.getElementById("ap-modal-data-url").value = url;
        document.getElementById("ap-modal-data-title").value = title;
    }
}

function HideModal() {
    modal = document.getElementsByClassName("ap-modal")[0];
    modal.style.display = "none";
    modalVisible = false;
    edit = null;
}

var pickMedia = document.getElementById("ap-pick-media");
pickMedia.addEventListener("click", function() {
    document.getElementById("ap-modal-data-url").value = "";
    document.getElementById("ap-modal-data-title").value = "";
    ShowModal();
});

function AddMedia(url, title) {
    var mediaUrl = url;
    if (mediaUrl.match(/(http:..)?(www\.)?youtube.com/i)) {
        var id = /watch\?v=(\w*)/i.exec(mediaUrl);
        mediaUrl = "http://img.youtube.com/vi/" + id[1] + "/0.jpg";
    }
    if (edit) {
        edit.getElementsByClassName("ap-media-pic")[0].style.backgroundImage = "url('" + mediaUrl + "')";
        edit.getElementsByClassName("ap-media-pic")[0].setAttribute("data-src", url);
        edit.getElementsByClassName("ap-media-description")[0].innerHTML=title;
    }
    else {
        var source= document.getElementsByClassName("ap-media-element")[0];
        var newNode = source.cloneNode(true);
        source.parentNode.appendChild(newNode);

        newNode.getElementsByClassName("ap-media-pic")[0].style.backgroundImage = "url('" + mediaUrl + "')";
        newNode.getElementsByClassName("ap-media-pic")[0].setAttribute("data-src", url);
        newNode.getElementsByClassName("ap-media-description")[0].innerHTML=title;
        newNode.style.display = "";                
    }
}

var frontElement;
function SetFrontElement(element) {
    //Unset current set
    if (frontElement && frontElement.parentNode != element) {
        frontElement.getElementsByClassName('ap-media-check')[0];
        frontElement.innerHTML="D";
    }

    frontElement = element.getElementsByClassName('ap-media-check')[0];                  
    if (frontElement.innerHTML=='D') 
        frontElement.innerHTML='F'; 
    else frontElement.innerHTML = 'D';
}

var nameText = document.getElementById("name")
nameText.addEventListener("keyup", UpdateName);
function UpdateName() {
    var name = document.getElementById("name-chars")
    name.innerHTML = parseInt(nameText.maxLength) - nameText.value.length;
}
UpdateName();

var summaryText = document.getElementById("summary")
summaryText.addEventListener("keyup", UpdateSummary);
function UpdateSummary() {
    var summary = document.getElementById("summary-chars")
    summary.innerHTML = parseInt(summaryText.maxLength) - summaryText.value.length;
}
UpdateSummary();

var descriptionText = document.getElementById("desc")
descriptionText.addEventListener("keyup", UpdateDescription);
function UpdateDescription() {
    var description = document.getElementById("description-chars")
    description.innerHTML = parseInt(descriptionText.maxLength) - descriptionText.value.length;
}
UpdateDescription();


$('#start-date').mask("99/99/9999");
$('#end-date').mask("99/99/9999");
$('#start-time').mask("99:99");
$('#end-time').mask("99:99");
InitMap(MapCenter);
AddListeners();
