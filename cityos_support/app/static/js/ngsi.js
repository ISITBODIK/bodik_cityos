/*
    NGSIでfiwareのデータにアクセスする
*/
function show_page() {
    let result = false;
    try {
        let execute_button = document.getElementById('execute');
        if (execute_button) {
            execute_button.addEventListener('click', () => {
                call_ngsi();
            })
        }
    } catch(error) {
        alert('show_page:' + error);
    }
}

function call_ngsi() {
    try {
        show_output(null);
        let entity_type = document.getElementById('entity-type').value;
        let fiware_service = document.getElementById('fiware-service').value;
        let fiware_servicepath = document.getElementById('fiware-servicepath').value;
        let apikey = document.getElementById('apikey').value;
        let protected = document.getElementById('protected').checked;

        let headers = {
            'User-Agent': 'BODIK/2.0',
            'Accept': 'application/json',
            'Fiware-Service': fiware_service,
            'Fiware-ServicePath': fiware_servicepath
        }
        if (apikey != '') {
            headers['Authorization'] = 'Bearer ' + apikey;
            //alert(apikey);
        }
        options = {
            headers: headers
        }

        let q = {
            'type': entity_type,
            'options': 'keyValues',
            'offset': 0,
            'limit': 100
        }
        const params = new URLSearchParams(q);

        let url = '';
        if (protected) {
            url = ngsi_server + '/protected/v2/entities' + '?' + params.toString();
        } else {
            url = ngsi_server + '/v2/entities' + '?' + params.toString();
        }
        
        //alert(url);
        //alert(JSON.stringify(q));
        //alert(JSON.stringify(headers));

        fetch(url, options)
        .then(response => response.json())
        .then(data => {
            show_output(data)
        })
        .catch(error => {
            //alert('通信エラー：' + error);
            console.log('通信エラー：' + error);
            show_output({'message': String(error)})
        });

    } catch(error) {
        alert('call_ngsi:' + error);
    }
}

function show_output(data) {
    try {
        let output = clear_child('output');
        if (output && data) {
            output.innerText = JSON.stringify(data, null, 2);
        }
    } catch(error) {
        alert('show_output:' + error);
    }
}