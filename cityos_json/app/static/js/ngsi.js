/*
    NGSIでfiwareのデータにアクセスする
*/
let credentials = null;
let access_token = null;
let refresh_token = null;
let selected_username = null;
let selected_password = null;

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

async function login() {
    let result = false;
    try {
        show_output(null);

        let username = document.getElementById('username').value;
        let password = document.getElementById('password').value;
        if (username != '' && password != '') {
            selected_username = username;
            selected_password = password;

            let data = {
                'username': username,
                'password': password
            }
            let options = {
                'method': 'POST',
                'headers': {
                    'User-Agent': 'BODIK/2.0',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                'body': JSON.stringify(data)
            }
            const url = `${fiware_server}/auth/login`;
            const response = await fetch(url, options);
            credentials = await response.json();
            if (credentials) {
                console.log(credentials);
                access_token = credentials['access_token']
                console.log('access_token : ' + access_token);
                refresh_token = credentials['refresh_token']
                result = true;
            } else {
                alert('ログインできませんでした');
            }
        } else {
            selected_username = '';
            selected_password = '';
            access_token = '';
            refresh_token = '';
            result = true;
        }
    } catch(error) {
        alert('login:' + error);
    }
    return result;
}

async function refresh() {
    let result = false;
    try {
        if (refresh_token != '') {
            let data = {
                'refresh_token': refresh_token
            };
            let options = {
                'method': 'POST',
                'headers': {
                    'User-Agent': 'BODIK/2.0',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                'body': JSON.stringify(data)
            }
            const url = `${fiware_server}/auth/refresh`;
            const response = await fetch(url, options);
            credentials = await response.json();
            console.log(credentials);
            access_token = credentials['access_token']
            console.log('access_token : ' + access_token);
            result = true;
        }
    } catch(error) {
        alert('refresh:' + error);
    }
    return result;
}

async function call_ngsi() {
    try {
        show_output(null);
        if (await login()) {
            let entity_type = document.getElementById('entity-type').value;
            let fiware_service = document.getElementById('fiware-service').value;
            let fiware_servicepath = document.getElementById('fiware-servicepath').value;

            let headers = {
                'User-Agent': 'BODIK/2.0',
                'Accept': 'application/json',
                'Fiware-Service': fiware_service,
                'Fiware-ServicePath': fiware_servicepath
            }
            if (access_token != '') {
                headers['Authorization'] = 'Bearer ' + access_token;
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

            let url = fiware_server + '/v2/entities' + '?' + params.toString();
            //alert(url);
            //alert(JSON.stringify(q));
            //alert(JSON.stringify(headers));

            let resp = await fetch(url, options);
            let status_code = resp.status;
            let expired = false;
            if (status_code == 401) {
                expired = true;

                try {
                    if (await refresh()) {
                        headers['Authorization'] = 'Bearer ' + access_token;
                        resp = await fetch(url, options)
                        status_code = resp.status;
                    }
                } catch(err) {
                    throw err;
                }
            }

            if (status_code == 200) {
                show_output(await resp.json());
            } else {
                credentials = null;
                if (expired) {
                    alert('認証時間切れです。もう一度、お試しください。' + status_code);
                } else {
                    alert('エラーです:' + status_code);
                }
            }

        }
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
