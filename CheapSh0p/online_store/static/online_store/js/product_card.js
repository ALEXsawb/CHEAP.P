let form = document.forms[0];


first_color_label = document.querySelector('label.color');
first_color_label.className = 'action';
form.add_color.value = first_color_label.children[0].id;

first_size_label = document.querySelector('label.size');
first_size_label.className = 'action';
form.add_size.value = first_size_label.children[0].id;


img.height = img.height;
img.width = img.width;


color_list_style = color_list.currentStyle || window.getComputedStyle(color_list);
color_list_style_margin_top = Math.floor(color_list_style.marginTop.slice(0, -2));


try{
    for (label of colors.querySelectorAll("label")){
        color = label.children[0].id;
        label.style.background = color;
    };
}
catch{};


for (let p of global_description.querySelectorAll("div.col-3 > p")){
    p.onclick = function(event){
        event = event.currentTarget;
        if (event.className != "stirring"){
            for (elem of global_description.querySelectorAll("p.stirring")){
                elem.className = "no_stirring";
            };
            for (elem of global_description.querySelectorAll("h7.stirring")){
                first_className = elem.className.split(" ")[0];
                elem.className = first_className + " not_stirring";
            };
            event.className = "stirring";
            event_id = "h7." + event.id;
            h7 = global_description.querySelector(event_id);
            first_className = global_description.querySelector(event_id).className.split(" ")[0];
            h7.className = first_className + " stirring";

            if (color_list_style_margin_top - h7.offsetHeight <= 0){
                color_list.style.marginTop = '0px';
                choose.style.marginTop = '0px';
            }
            else{
                color_list.style.marginTop = String(color_list_style_margin_top)+'px';
                choose.style.marginTop = color_list.style.marginTop;
            }
            console.log(choose.style.marginTop, color_list.style.marginTop, color_list_style_margin_top);
        }
    }
}


function get_inputs(){
    return document.querySelectorAll("label > input");
}


for (label of document.querySelectorAll("label")){
    label.onclick = function(event){
        for (let input of get_inputs()){
            if (input.checked == true){
                input.parentNode.className = "action";
                if (input.name == 'size'){
                    form.add_size.value = input.id
                }
                else{
                    form.add_color.value = input.id
                }
            }
            else{
                if (input.parentNode.style['background']){
                    input.parentNode.className = 'fake color'
                }
                else{
                    input.parentNode.className = 'fake size'
                }
            }
        }
    }
}

//if (input.parentNode.previousSibling.previousSibling.id == 'color'){
//    input.parentNode.className = 'fake color'
//}
//else{
//    input.parentNode.className = 'fake size'
//}