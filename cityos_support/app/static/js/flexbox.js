function makebox(parent, classname, id, text) {

    let item = document.createElement('div');
    item.className = classname;
    item.id = id;
    item.innerHTML = text;
    parent.appendChild(item);

    return item;
}

function makeimg(parent, classname, src) {

    let img = document.createElement('img');
    img.className = classname;
    img.setAttribute('src', src);
    img.setAttribute('alt', 'photo');
    parent.appendChild(img);

    return img;
}

function makeanchor(parent, href) {
    let anchor = document.createElement('a');
    anchor.href = href;
    parent.appendChild(anchor);
}

function makeouterlink(parent, href) {
    let anchor = document.createElement('a');
    anchor.href = href;
    anchor.target = '_blank';
    anchor.rel = 'noopener noreferrer';

    parent.appendChild(anchor);
}

function makeButton(parent, classname, handler, id, text) {
    let button = document.createElement('button');
    parent.appendChild(button);

    button.className = classname;
    button.id = id;
    //button.setAttribute('type', 'button');
    button.addEventListener('click', handler);
    button.innerHTML = text;

    return button;
}

function makeRadioButton(parent, classname, group, value, id, text) {
    let div = makebox(parent, classname, '', '');

    let radio = document.createElement('input');
    div.appendChild(radio);
    radio.setAttribute('type', 'radio');
    radio.setAttribute('name', group);
    radio.setAttribute('value', value);
    radio.setAttribute('id', id);

    let label = document.createElement('label');
    div.appendChild(label);
    label.setAttribute('for', id);
    label.innerHTML = text;

    return radio;
}

function makeEdittext(parent, classname, id) {
    let etext = document.createElement('input');
    parent.appendChild(etext);
    etext.className = classname;
    etext.setAttribute('type', 'text');
    etext.setAttribute('id', id);

    return etext;
}

function makeTextarea(parent, classname, id, rows, cols) {
    let atext = document.createElement('textarea');
    parent.appendChild(atext);
    atext.className = classname;
    atext.setAttribute('id', id);
    atext.setAttribute('rows', rows);
    atext.setAttribute('cols', cols);

    return atext;
}

function makedropdown(parent, classname, handler, id) {
    
    let item = document.createElement('select');
    parent.appendChild(item);
    item.className = classname;

    if (id != null) {
        item.id = id;
    }
    if (handler) {
        item.addEventListener('click', handler);
    }

    return item;
}

function makeListbox(parent, classname, handler, id, rows) {
    
    let item = document.createElement('select');
    parent.appendChild(item);
    item.className = classname;
    if (rows > 0) {
        item.setAttribute('size', rows);
    }

    if (id != null) {
        item.id = id;
    }
    if (handler) {
        item.addEventListener('click', handler);
    }

    return item;
}

function makeFileButton(parent, classname, handler, id, text) {
    let label = document.createElement('label');
    label.setAttribute('for', id);
    label.className = classname;
    label.innerText = text;

    parent.appendChild(label);

    let button = document.createElement('input');
    button.type = 'file';
    button.id = id;
    button.style.display = 'none';
    button.addEventListener('change', handler);

    label.appendChild(button);

    return button;
}

function makeDate(parent, classname, id) {
    let item = document.createElement('input');
    item.type = 'date';
    item.className = classname;
    item.id = id;

    parent.appendChild(item);

    return item;
}

function makeTime(parent, classname, id) {
    let item = document.createElement('input');
    item.type = 'time';
    item.className = classname;
    item.id = id;

    parent.appendChild(item);

    return item;
}

function makeSlider(parent, classname, handler, id) {
    let item = null;
    try {
        item = document.createElement('input');
        item.type = 'range';
        item.className = classname;
        item.id = id;
        item.min = '0';
        item.max = '365';
        item.step = '1';
        item.addEventListener('input', handler);        //  change: スライダが止まったとき, input: スライダが動いたとき

        parent.appendChild(item);
    } catch(error) {
        alert('makeSlider:' + error);
    }
    return item;
}

function clear_child(parent) {

    let content = document.getElementById(parent)
    if (content) {
        while (content.lastChild) {
            content.removeChild(content.lastChild)
        }
    }

    return content;
}

function show_aggrid_copyright(parent) {

    try {
        let message = 'AG-Gridを使用しています　'
        makebox(parent, '', '', message);

        let mit = 'https://www.ag-grid.com/eula/AG-Grid-Community-License.html';
        let id = 'ag-grid-link';

        let copyright = 'Copyright (c) 2015-2020 AG GRID LTD'
        let anchor = document.createElement('a');
        anchor.href = mit;
        anchor.target = '_blank';
        anchor.rel = 'noopener noreferrer';
        anchor.innerHTML = copyright;
        
        parent.appendChild(anchor);
    } catch(error) {
        alert('show_aggrid_copyright:' + error);
    }
}

function show_footer() {
    try {
        let footer = clear_child('footer');
        if (footer) {
            let footer_contents = 'BODIK Utilityは、公益財団法人 九州先端科学技術研究所が提供しています。<br>';
            footer_contents += 'BODIK Utilityの最新情報や使い方については、<a href="https://www.bodik.jp/blog/" target="_blank">BODIKウェブサイトのブログ記事</a>をご確認ください。';
            footer_contents += 'お問い合わせは、<a href="https://www.bodik.jp/" target="_blank">BODIKウェブサイト</a>からお願いいたします。';
            makebox(footer, 'div', '', footer_contents);
        }
    } catch(error) {
        alert('show_footer:' + error);
    }
}

function show_footer_old() {
    try {
        let footer = document.getElementById('footer');
        let ul = document.createElement('ul');
        ul.className = 'nav-list';
        footer.appendChild(ul);

        let li1 = document.createElement('ul');
        li1.className = 'nav-list-item';
        let link1 = "<a href='https://www.isit.or.jp/' target='_blank' rel='noopener noreferrer'>公益財団法人 九州先端科学技術研究所</a>";
        li1.innerHTML = link1;
        ul.appendChild(li1);

        let li2 = document.createElement('ul');
        li2.className = 'nav-list-item';
        let link2 = "<a href='https://www.bodik.jp/' target='_blank' rel='noopener noreferrer'>BODIK</a>";
        li2.innerHTML = link2;
        ul.appendChild(li2);

    } catch(error) {
        alert('show_footer:' + error);
    }
}

function set_gtag_event(action, category, label, value) {
    try {
        let param = {
            'event_category': category,
            'event_label': label
        };
        if (value) {
            param['value'] = value
        }

        gtag('event', action, param);
    } catch(error) {
        alert('set_gtag:' + error);
    }
}

var unEscapeHTML = function (str) {
    return str
            .replace(/(&lt;)/g, '<')
            .replace(/(&gt;)/g, '>')
            .replace(/(&quot;)/g, '"')
            .replace(/(&#39;)/g, "'")
            .replace(/(&amp;)/g, '&');
};
