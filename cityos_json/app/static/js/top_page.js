const pages = [
    {
        'name': 'BODIK ODGW',
        'app': [
            {'caption': 'サブスクリプション管理', 'url': 'subscription', 'title': 'サブスクリプション管理' },
        ]
    }
];

function show_top_page() {
    try {
        let stage = document.getElementById('stage');
        if (stage) {
            for (let group of pages) {
                let box = makebox(stage, 'app_group', null, null);
                if (box) {
                    makebox(box, 'group_title', null, group.name);
                    let app_list = makebox(box, 'group_app', null, null);
                    if (app_list) {
                        for (let item of group.app) {
                            let button = makeButton(app_list, 'app_button', null, '', item.caption);
                            button.setAttribute('title', item.title);
                            button.addEventListener('click', function() {
                                let url = `${api_server}/${item.url}`;
                                window.open(url);
                            });
                        }
                    }
                }
            }
        }
        show_footer();
    } catch(error) {
        alert('show_top_page:' + error);
    }
}

