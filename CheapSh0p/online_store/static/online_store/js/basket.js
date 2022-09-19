
let form = document.forms[document.forms.length - 1];

for (let input of document.querySelectorAll("div.col_this_product > input")){
    img = input.parentNode.previousSibling.previousSibling.firstChild
    check_quantity_for_img(input, img)
    input.onchange = change_col_product;
}

function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function get_basket(){
    try{
        return JSON.parse(eval(getCookie('basket')))
    }
    catch{
        return JSON.parse(getCookie('basket'))
    }
}

function change_col_product(event){
    input = event.target
    value = Number(input.value)
        let info = input.parentNode.parentNode.parentNode.parentNode;
        let all_sum_of_this_product = info.children[6].children[1];
        let product_price = info.children[5].children[1];
        try{
            all_sum_of_this_product = info.children[6].children[1].children[0].children[0];
            str = String(all_sum_of_this_product.innerHTML).slice(0,-2)+'$'
            all_sum_of_this_product.innerHTML = str;
            product_price = info.children[5].children[1].children[0].children[0];
            if (String(product_price.innerHTML).indexOf(" ") === true){
                product_price.innerHTML = String(product_price.innerHTML).slice(0,-2)+'$'
            }
            span_sum = span_sum.children[0].children[0]
        }
        catch{}
        finally{
            recalculation_input_onchange(input, all_sum_of_this_product, span_sum, product_price)

        }
}


function check_quantity_for_img(input, img){
    if(Number(input.value) > 1){img.src = "static/online_store/images/pages/basket/minus.png";}else{img.src = "static/online_store/images/pages/basket/bucket.png";}
};

function recalculation_input_onchange(input, all_sum_of_this_product, span_sum, product_price){
    if (value <= 10){
            all_sum_of_this_product.innerHTML = get_string_manny(get_number_manny(product_price)*value)
            span_sum.innerHTML = get_string_manny(get_number_manny(span_sum) - get_number_manny(product_price)*input.getAttribute('value'))
            span_sum.innerHTML = recalculation_plus(span_sum, all_sum_of_this_product)
            input.setAttribute('value', value);
    }
    else{
        span_sum.innerHTML = get_string_manny(get_number_manny(span_sum) - get_number_manny(product_price)*input.getAttribute('value'))
        all_sum_of_this_product.innerHTML = 0
        input.value = 0;
        input.setAttribute('value', 0)
    };
    check_quantity_for_img(input, img)
};

function check_children_all_sum_of_this_product_and_product_price(input){
        let info = input.parentNode.parentNode.parentNode.parentNode;
    try {
        all_sum = info.children[6].children[1].children[0].children[0].innerHTML
        price = info.children[5].children[1].children[0].children[0].innerHTML
        all_sum_of_this_product = all_sum.slice(0, -2)+'$'
        product_price = get_number_manny(price.slice(0, -2)+"$")
        return [all_sum_of_this_product, product_price]
        }

    catch{
        return [info.children[6].children[1], info.children[5].children[1], get_number_manny(info.children[5].children[1])]
        }
}


function check_children_for_product_price(input){
    return get_number_manny(input.parentNode.parentNode.parentNode.parentNode.children[5].children[1])
}


function get_number_manny(event){
    e_i = event.innerHTML;
    if (e_i === undefined){
        e_i = event;
    }
    if (e_i == "0"){
        return 0
    }
    if (e_i.indexOf(".") != -1){
         return set_price('.', e_i)
    }
    else if (e_i.indexOf(" ") != -1 || e_i.indexOf(",") != -1){
        return set_price(',', e_i)
    }
}

function set_price(symbol, e_i){
    return Number(`${e_i.slice(0, e_i.indexOf(symbol))}${e_i.slice(e_i.indexOf(symbol)+1, -1)}`)
}

function get_string_manny(event){
    if (event == 0){
        return "0"
    }
    event  = String(event)
    return `${event.slice(0, event.indexOf(".")-1)}.${event.slice(event.indexOf(".")-1)}$`
}


function recalculation_plus(original_number, new_element_of_sum){
    return get_string_manny(get_number_manny(original_number) + get_number_manny(new_element_of_sum));
};

function recalculation_minus(original_number, new_element_of_sum){
    return get_string_manny(get_number_manny(original_number) - get_number_manny(new_element_of_sum));
};


let sum_basket = 0
for (let value of document.querySelectorAll("p.manny")){
    sum_basket += get_number_manny(value);
}


order_status_h2.onclick = () =>{
    order_status_h2.style["color"] = "#fff";
    order_status_h2.style["font-size"] = "250%";
    my_cart.style["color"] = '#7b7b7b';
    my_cart.style["font-size"] = '175%';
    try{all_orders.style["display"] = "block";}
    catch{not_orders.style["display"] = "block";}
    list_products = order_status_h2.parentNode;
    list_products.children[5].style['display'] = "none";
    list_products.nextElementSibling.style["display"] = "none";
}

my_cart.onclick = () =>{
    order_status_h2.style["color"] = '#7b7b7b';
    order_status_h2.style["font-size"] = "175%";
    my_cart.style["color"] = "#fff";
    my_cart.style["font-size"] = '300%';

    try{all_orders.style["display"] = "none";}
    catch{not_orders.style["display"] = "none";}
    list_products = order_status_h2.parentNode;
    list_products.children[5].style['display'] = "flex";
    if (list_products.nextElementSibling.classList[2] === "BUY"){
        list_products.nextElementSibling.style["display"] = "flex";
    }
}

let span_sum = document.querySelector("span.manny");
span_sum.innerHTML = get_string_manny(sum_basket);

function recalculation_of_money(event, plus_or_minus){
    let all_sum_of_this_product = event.parentNode.nextSibling.nextSibling.children[1];
    try{
        all_sum_of_this_product = all_sum_of_this_product.children[0].children[0];
        event = event.children[0].children[0];
        span_sum = span_sum.children[0].children[0];
    }
    catch{}
    if(plus_or_minus){
        all_sum_of_this_product.innerHTML = recalculation_plus(all_sum_of_this_product, event);
        return span_sum.innerHTML = recalculation_plus(span_sum, event);
    }
    all_sum_of_this_product.innerHTML = recalculation_minus (all_sum_of_this_product, event);
    span_sum.innerHTML = recalculation_minus(span_sum, event);
};


for (let input of document.querySelectorAll("div.plus > input")){
    input.onclick = plus;
};


for (let input of document.querySelectorAll("div.bucket_or_minus > input")){
    input.onclick = minus;
};


function get_col_product(event){
    return event.parentNode.parentNode.querySelector("div.col_this_product > input");
};


function minus_if_col_more_1(img, col_product){
    if(col_product.value < 2){
        img.src = "static/online_store/images/pages/basket/bucket.png";
    };
}


function minus(){
    let src = this.src
    let col_product = get_col_product(this);
    col_product.setAttribute('value', Number(col_product.getAttribute('value')) - 1);
    col_product.value = col_product.getAttribute('value');
    product_id = String(this.parentNode.parentNode.parentNode.parentNode.parentNode.children[2].name);
    size_or_color = col_product.parentNode.parentNode.parentNode.previousSibling.previousSibling.previousSibling.previousSibling
    size = size_or_color.children[0].children[1].children[0].innerHTML
    color = size_or_color.children[1].children[1].children[0].innerHTML

    work_with_cookie(product_id, size, color, "minus")
    if (src[src.length-10] == "/"){
        minus_if_col_more_1(this, col_product)
    }
    else{
        if (col_product.value == 0 || col_product.value == 1){
            let card = this.parentNode.parentNode.parentNode.parentNode.parentNode;
            let cards = card.parentNode;
            try{cards.removeChild(card.nextSibling.nextSibling);}
            catch{}
            card.children[2].children[5].children[1].setAttribute('value', 'on')
            card.children[2].children[5].children[1].setAttribute('checked', 'checked')
            card.style.display = 'none';
        }
        else{
            minus_if_col_more_1(this, col_product);
        }
    }
    value_this_product = this.parentNode.parentNode.parentNode.nextSibling.nextSibling.nextSibling.nextSibling.children[1];
    recalculation_of_money(value_this_product, 0);
};

function del_product_and_session_formation(event){
    order.innerHTML = event.querySelector('fieldset').innerHTML+"SQL";
    let editing = document.createElement('INPUT');
    editing.setAttribute('name', 'editing');
    order.append(editing)
    form.submit();
};

function plus(){
    let src = this.src
    let col_product = get_col_product(this);
    col_product.setAttribute('value', Number(col_product.getAttribute('value')) + 1);
    col_product.value = col_product.getAttribute('value');
    if(col_product.value > 1 && col_product.value < 20){
        col_product.parentNode.previousSibling.previousSibling.firstChild.src = "static/online_store/images/pages/basket/minus.png";
    };
    product_id = String(this.parentNode.parentNode.parentNode.parentNode.parentNode.children[2].name);
    size_or_color = col_product.parentNode.parentNode.parentNode.previousSibling.previousSibling.previousSibling.previousSibling
    size = size_or_color.children[0].children[1].children[0].innerHTML
    color = size_or_color.children[1].children[1].children[0].innerHTML
    work_with_cookie(product_id, size, color, "plus")
    value_this_product = this.parentNode.parentNode.parentNode.nextSibling.nextSibling.nextSibling.nextSibling.children[1];
    recalculation_of_money(value_this_product, true);
};


function work_with_cookie(product_id, size, color, plus_or_minus){
    basket = get_basket()
    products_with_join_id = basket[product_id]
    for(let product of products_with_join_id){
        if(product['size'] == size && product['color'] == color){
            if (plus_or_minus == 'minus'){
                if (product['quantity'] > 1){
                    product['quantity'] -= 1
                }
                else{
                    products_with_join_id.splice(products_with_join_id.indexOf(product), 1);
                    if (products_with_join_id == false){
                        delete basket[product_id]
                    }
                }
            }
            else if (plus_or_minus == 'plus'){
                product['quantity'] += 1
            }
            let updatedCookie = encodeURIComponent('basket') + "=" + String(JSON.stringify(basket));
            document.cookie = updatedCookie;
        }
    }
};


function get_id_product_in_cookie(product_id, cookie_value){
     return cookie_value.indexOf(product_id)
}


let check = 1
check_out.onclick = function (){
    order_address.style.cssText = 'display = 1'
    let centerX = document.documentElement.clientWidth/2;
    let centerY = document.documentElement.clientHeight/2;
    order_address.style.left = centerX - order_address.offsetWidth/2 + "px";
    order_address.style.top = centerY - order_address.offsetHeight/2 + "px";
    sum_plus_delivery.innerHTML = span_sum.innerHTML
    order_address.style.position = "fixed";
};

let X = document.getElementById("X").parentNode;
X.onclick = function(){
    order_address.style['display'] = "none";
}

pay.onclick = function(){
    order.style.display = 'none';
    product_cards = document.querySelector("div.carts");
    len_order = order.children.length;
    for (cart of product_cards.querySelectorAll('div.cart')){
        fieldset = cart.querySelector('fieldset');
        fieldset.children[4].children[1].setAttribute('value', cart.querySelector('div.col_this_product > input[name=col]').value);
        order.append(fieldset);
        len_order += 1;
        };

    let form_TOTAL_FORMS = document.createElement('INPUT');
    form_TOTAL_FORMS.setAttribute('name', 'orders-TOTAL_FORMS');
    form_TOTAL_FORMS.setAttribute('id', 'id_orders-TOTAL_FORMS');
    form_TOTAL_FORMS.setAttribute('type', 'hidden');
    form_TOTAL_FORMS.setAttribute('value', String(len_order));
    form.append(form_TOTAL_FORMS);
    let form_INITIAL_FORMS = document.createElement('INPUT');
    form_INITIAL_FORMS.setAttribute('name', 'orders-INITIAL_FORMS');
    form_INITIAL_FORMS.setAttribute('id', 'id_orders-INITIAL_FORMS');
    form_INITIAL_FORMS.setAttribute('type', 'hidden');
    form_INITIAL_FORMS.setAttribute('value', '0');
    form.append(form_INITIAL_FORMS);

    phone = document.getElementById('id_order_form-phone');
    region_phone = document.getElementById('region_phone');
    phone.value = region_phone.value + phone.value;
    order.prepend(order_1);
    order.prepend(order_2);
    BUY.setAttribute('form', "111");
};

let all_region_numbers = region_phone_list.cloneNode(true).children;


region_phone.addEventListener("click", function(event){
    if (region_phone.children.length){
        region_phone.innerHTML="";
    }
    if(region.style["display"] != "block"){
        region.style["display"] = "block";
        sum_plus_delivery.style["margin"] = order_address.style["margin"] = "1.5% 0";
    }
    else{
        region.style["display"] = "none";
    }
    for (elem of region_phone_list.children){
        elem.addEventListener("click", choose_a_regional_number);
    }
})



let after_search = false;



search.addEventListener("change", function(){
    s_v = search.value
    if (s_v != ""){
        found_regional_numbers = [];
        for (option_ of all_region_numbers){
            if (get_elem_from_fonts(option_.children[0]).innerHTML.indexOf(s_v)+1 || get_elem_from_fonts(option_.children[1]).innerHTML.indexOf(s_v)+1){
                found_regional_numbers.push(option_.cloneNode(true));
            };
        };
        region_phone_list.innerHTML = "";

        for (region_number of found_regional_numbers){
            region_phone_list.prepend(region_number);
            after_search = true;
            region_number.addEventListener("click", choose_a_regional_number);
        }
    }
})


function get_elem_from_fonts(elem_parentNode){
    try{
        if (elem_parentNode.children[0].children[0] === undefined){
        return elem_parentNode;
        }
        return elem_parentNode.children[0].children[0];
    }
    catch{
        return elem_parentNode;
    }
}



function choose_a_regional_number(event){
    elem = event.target;
    option = document.createElement("OPTION");
    option.innerHTML = get_elem_from_fonts(elem.children[0]).innerHTML;
    region_phone.prepend(option.cloneNode(true));
    region.style["display"] = "none";
    if (after_search){
        region_phone_list.innerHTML = "";
        for (elem of all_region_numbers){
            region_phone_list.append(elem.cloneNode(true));
        }
        after_search = false;
        search.value = "";
    }
}
