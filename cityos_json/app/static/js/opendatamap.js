const appname = 'opendatamap';

let map = null;
let layerMarker = null;

let dataset_list = null;
let selected_apiname = null;
let selected_distance = null;
let selected_count = null;
let selected_myconfig = null;
let selected_property = null;
let selected_datatype = null;
let myconfig_list = {}
let geometry_field = null;

const listMaxResult = [
    { value: 10,   text: '10件'},
    { value: 100,  text: '100件'},
    { value: 200,  text: '200件'},
    { value: 500,  text: '500件'}
];
const listDistance = [
    { value: 1000,   text: '1000m' },
    { value: 2000,   text: '2000m' },
    { value: 5000,   text: '5km' },
    { value: 10000,  text: '10km' },
    { value: 20000,  text: '20km' },
    { value: 50000,  text: '50km' },
    { value: 100000, text: '100km' },
    { value: 0, text: '制限なし' }
];

function show_page() {
    try {
        let location_button = document.getElementById('location');
        location_button.setAttribute('title', '位置を確認する');
        location_button.addEventListener('click', (evt) => {
            check_location();
        })

        let search_button = document.getElementById('search');
        search_button.setAttribute('title', 'データを検索する');
        search_button.addEventListener('click', (evt) => {
            search_data();
        })

        set_distance_select();
        set_count_select();
        get_dataset_list();
        
        set_datatype_select();

        initLeaflet();
    } catch(error) {
        alert('show_page:' + error);
    }
}

function get_dataset_list() {
    try {
        let headers = {
            'User-Agent': 'BODIK/2.0',
            'accept': 'application/json'
        }
        let options = {
            headers: headers
        }
        let url = `${fiware_server}/myapi/public?isLocation=true`;
        fetch(url, options)
        .then(response => response.json())
        .then(data => {
            set_dataset_select(data);
        });

    } catch(error) {
        alert('get_dataset_list:' + error);
    }
}

function set_dataset_select(apilist) {
    try {
        let combo = clear_child('select_dataset');
        if (combo) {
            dataset_list = {};            
            for (let info of apilist) {
                let apiname = info.entity_type;
                dataset_list[apiname] = info;
                
                let option = document.createElement('option');
                option.value = apiname;
                option.text = info.display_name;
                combo.appendChild(option);
            }
            combo.selectedIndex = 0;

            combo.addEventListener('change', (evt) => {
                select_dataset();
            });

            select_dataset();
        }
    } catch(error) {
        alert('set_dataset_select:' + error)
    }
}

function select_dataset() {
    try {
        let combo = document.getElementById('select_dataset');
        if (combo) {
            selected_apiname = combo.value;
            if (selected_apiname in myconfig_list) {
                selected_myconfig = myconfig_list[selected_apiname];
                set_property_select();
            } else {
                get_myconfig();
            }
        }
    } catch(error) {
        alert('select_dataset:' + error)
    }
}

function get_myconfig() {
    try {
        let info = dataset_list[selected_apiname];
        let apiname = info['apiname'];
        let headers = {
            'User-Agent': 'BODIK/2.0',
            'accept': 'application/json'
        }
        let options = {
            headers: headers
        }
        let url = `${fiware_server}/myapi/config?apiname=${apiname}`;
        fetch(url, options)
        .then(response => response.json())
        .then(data => {
            myconfig_list[selected_apiname] = data;
            selected_myconfig = data;
            geometry_field = selected_myconfig['geometry_field'];

            set_property_select();
        });
    } catch(error) {
        alert('select_dataset:' + error)
    }
}

function set_distance_select() {
    try {
        let combo = clear_child('select_distance');
        if (combo) {
            for (let info of listDistance) {
                let option = document.createElement('option');
                option.value = info.value;
                option.text = `半径: ${info.text}`;
                combo.appendChild(option);
            }
            combo.value = 2000;
            selected_distance = 2000;

            combo.addEventListener('change', (evt) => {
                select_distance();
            });
        }
    } catch(error) {
        alert('set_distance_select:' + error)
    }
}

function select_distance() {
    try {
        let combo = document.getElementById('select_distance');
        if (combo) {
            selected_distance = combo.value;
        }
    } catch(error) {
        alert('select_count:' + error)
    }
}

function set_count_select() {
    try {
        let combo = clear_child('select_count');
        if (combo) {
            for (let info of listMaxResult) {
                let option = document.createElement('option');
                option.value = info.value;
                option.text = `最大 ${info.text}`;
                combo.appendChild(option);
            }
            combo.value = 10;
            selected_count = 10;

            combo.addEventListener('change', (evt) => {
                select_count();
            });
        }
    } catch(error) {
        alert('set_count_select:' + error)
    }
}

function select_count() {
    try {
        let combo = document.getElementById('select_count');
        if (combo) {
            selected_count = combo.value;
        }
    } catch(error) {
        alert('select_count:' + error)
    }
}

const datatype_list = [ '文字列', '画像' ]
function set_datatype_select() {
    try {
        let combo = clear_child('select_datatype');
        if (combo) {
            for (let datatype of datatype_list) {
                let option = document.createElement('option');
                option.value = datatype;
                option.text = datatype;
                combo.appendChild(option);
            }
            combo.selectedIndex = 0;
        }
    } catch(error) {
        alert('set_count_select:' + error)
    }
}

const skip_fields = ['lat', 'lon'];
function set_property_select() {
    try {
        let settings = null;
        let key = appname + '.' + selected_apiname
        let text = localStorage.getItem(key);
        if (text) {
            settings = JSON.parse(text);
            console.log(settings);
        }

        if (selected_myconfig) {
            let datamodel = selected_myconfig['dataModel'];
            let combo = clear_child('select_property');
            if (combo) {

                for (let field in datamodel) {
                    if (!skip_fields.includes(field)) {
                        let option = document.createElement('option');
                        option.value = field;
                        option.text = field;
                        combo.appendChild(option);
                    }
                }
                combo.selectedIndex = 0;
            }

            //  前回の設定を復元する
            if (settings) {
                for (let item of combo.options) {
                    if (item.value == settings.selected_property) {
                        item.selected = true;
                        break;
                    }
                }

                let combo2 = document.getElementById('select_datatype');
                for (let item of combo2.options) {
                    if (item.value == settings.selected_datatype) {
                        item.selected = true;
                        break;
                    }
                }
            }
        }
    } catch(error) {
        alert('set_count_select:' + error)
    }
}

/*
    マップ
*/
function initLeaflet() {
    try {
        map = L.map('map', { zoomControl: true });
        //  指定された緯度経度を中心とした地図
        let center = [ 33.59253352302834, 130.35576696764173 ];
        let zoom = 14;
        map.setView(center, zoom);
        
        //地理院地図の標準地図タイル
        let gsi = L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png', 
            {attribution: "<a href='https://maps.gsi.go.jp/development/ichiran.html' target='_blank'>地理院タイル</a>"});
        //地理院地図の淡色地図タイル
        let gsipale = L.tileLayer('http://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png',
            {attribution: "<a href='https://maps.gsi.go.jp/development/ichiran.html' target='_blank'>地理院タイル</a>"});

        //地理院地図の航空写真タイル(写真地図最新版)
        let gsiphoto = L.tileLayer('http://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg',
            {attribution: "<a href='https://maps.gsi.go.jp/development/ichiran.html' target='_blank'>地理院タイル</a>"});
        
        //オープンストリートマップ
        let osm = L.tileLayer('http://tile.openstreetmap.jp/{z}/{x}/{y}.png',
            {  attribution: "<a href='http://osm.org/copyright' target='_blank'>OpenStreetMap</a> contributors" });

        let baseMaps = {
            "地理院地図" : gsi,
            "淡色地図" : gsipale,
            "地理院写真" : gsiphoto,
            "オープンストリートマップ"  : osm
        };

        L.control.layers(baseMaps).addTo(map);
        gsi.addTo(map);

        map.on('click', function(evt) {
            let latlng = evt.latlng;
            selected_pos = [ latlng.lat, latlng.lng ];
            setMarker(true);
        });
        
        check_location();

    } catch(error) {
        alert('initLeaflet ERROR:' + error.message);
    }
}

function search_data() {
    try {
        if (selected_apiname && selected_distance && selected_count) {
            selected_property = document.getElementById('select_property').value;
            selected_datatype = document.getElementById('select_datatype').value;
            
            //　設定を記録する
            let selected = {
                'selected_property': selected_property,
                'selected_datatype': selected_datatype
            }
            let key = appname + '.' + selected_apiname
            localStorage.setItem(key, JSON.stringify(selected));

            let info = dataset_list[selected_apiname];

            let headers = {
                'User-Agent': 'BODIK/2.0',
                'Accept': 'application/json',
                'Fiware-Service': info['Fiware-Service'],
                'Fiware-ServicePath': info['Fiware-ServicePath']
            }

            let options = {
                headers: headers
            }
            let q = {
                'type': info['entity_type'],
                'options': 'keyValues',
                'offset': 0,
                'limit': 100
            }
            const params = new URLSearchParams(q)
            let url = `${fiware_server}/v2/entities?` + params.toString();
            fetch(url, options)
            .then(response => response.json())
            .then(data => {
                show_data(data);
            });
        } else {
            alert(selected_apiname);
            alert(selected_distance);
            alert(selected_count);
        }
    } catch(error) {
        alert('search_data:' + error);
    }
}

function show_data(data) {
    try {
        if (layerMarker !== null) {
            map.removeLayer(layerMarker);
            layerMarker = null;
        }

        let bounds = null;
        let markers = [];
        for (let item of data) {
            console.log(item);
            //let coordinates = item['location']['coordinates'];
            let coordinates = item[geometry_field]['coordinates'];
            let pos = [ coordinates[1], coordinates[0] ];
            let marker = L.marker(pos);
            let info = item[selected_property];
            let content = info;
            if (selected_datatype == '画像') {
                let path = info.replace('uploads', 'download');
                console.log(path);
                content = `<img class="photo" src="${path}" />`
            }
            console.log(content);
            let popup = L.popup().setContent(content);
            marker.bindPopup(popup);

            markers.push(marker);
            if (bounds == null) {
                bounds = L.latLngBounds(pos, pos);
            } else {
                bounds.extend(pos);
            }
        }

        if (markers.length > 0) {
            layerMarker = L.layerGroup(markers);
            map.addLayer(layerMarker);
        }

        if (bounds != null) {
            map.fitBounds(bounds);
        }
    } catch(error) {
        alert('show_data:' + error)
    }
}
/*
    GPS
*/
function check_location() {
    try {
        //alert('check_location called');
        navigator.geolocation.getCurrentPosition(setPosition, locationError, { timeout: 10000});
    } catch(error) {
        alert('check_location:' + error);
    }
}

function locationError() {
    try {
        alert('位置情報を取得できませんでした');
    } catch(error) {
        alert('locationError:' + error);
    }
}

function setPosition(position) {
    try {
        let lat = position.coords.latitude;
        let lon = position.coords.longitude;
        let pos = [ lat, lon ];
        setView(pos)
    } catch(error) {
        alert('setPosition:' + error);
    }
}

function setView(pos) {
    try {
        if (map) {
            let zoom = 14;
            map.setView(pos, zoom);
        }
    } catch(error) {
        alert('setView:' + error);
    }
}