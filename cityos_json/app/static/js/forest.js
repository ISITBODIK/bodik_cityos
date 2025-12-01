let map = null;
let apiname = 'forest';
let fiware_service = 'bodik';
let fiware_servicepath = '/protected/forest';
let access_token = null;
let refresh_token = null;

const organ_list = {
    '420000': { 'name': '長崎県', 'tile': `${fiware_server}/tile/data/420000_forest/{z}/{x}/{y}.pbf`},
    '430005': { 'name': '熊本県', 'tile': `${fiware_server}/tile/data/430005_forest/{z}/{x}/{y}.pbf`}
};

function show_page() {
    try {
        let combo = clear_child('organ_select');
        if (combo) {
            combo.addEventListener('change', () => {
                select_organ();
            });

            for (let organ_code in organ_list) {
                let option = document.createElement('option');
                option.value = organ_code;
                option.text = organ_list[organ_code].name;
                combo.appendChild(option);
            }
        }

        initMap();

    } catch(error) {
        alert('show_page:' + error);
    }
}

async function demo_login() {
    let result = false;
    try {
        const url = `${fiware_server}/auth/demo/login/${apiname}`;
        const response = await fetch(url, { method: 'POST' });
        credentials = await response.json();
        if (credentials) {
            console.log(credentials);
            access_token = credentials['access_token']
            refresh_token = credentials['refresh_token']
            console.log('access_token : ' + access_token);
            console.log('refresh_token : ' + refresh_token);
            result = true;
        } else {
            alert('ログインできませんでした');
        }
    } catch(error) {
        alert('demo_login:' + error);
    }
    return result;
}

async function refresh() {
    let result = false;
    try {
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
    } catch(error) {
        alert('refresh:' + error);
    }
    return result;
}

async function select_organ() {
    try {
        let combo = document.getElementById('organ_select');
        let organ_code = combo.value;
        if (organ_code) {
            const info = organ_list[organ_code];

            //  古いレイヤーとソースを削除する
            if (map.getLayer('forest_outline')) {
                map.removeLayer('forest_outline');
            }
            if (map.getLayer('forest_layer')) {
                map.removeLayer('forest_layer');
            }
            if (map.getSource('forest')) {
                map.removeSource('forest');
            }

            let login_success = await demo_login();
            if (login_success) {
                //  新しいレイヤーとソースを追加する
                map.addSource('forest', {
                    type: 'vector',
                    tiles: [ info.tile ],
                    minzoom: 0,
                    maxzoom: 14
                });

                map.addLayer({
                    id: 'forest_layer',
                    type: 'fill',
                    source: 'forest',
                    'source-layer': 'forest',
                    paint: {
                        'fill-color': '#088',
                        'fill-opacity': 0.2
                    }
                });

                map.addLayer({
                    id: 'forest_outline',
                    type: 'line',
                    source: 'forest',
                    'source-layer': 'forest',
                    paint: {
                        'line-color': '#044',
                        'line-width': 1
                    }
                });
            }
        }
    } catch(error) {
        alert('select_organ:' + error);
    }
}

function initMap() {
    try {
        let center = [ 130.35576696764173, 33.59253352302834 ];

        map = new maplibregl.Map({
            container: 'map',
            style: {
                version: 8,
                sources: {
                    'osm': {
                        type: 'raster',
                        tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                        tileSize: 256,
                        attribution: '<a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>'
                    },
                    /*
                    'forest': {
                        type: 'vector',
                        //tiles: [`${tile_server}/data/430005_forest/{z}/{x}/{y}.pbf`],
                        tiles: [`http://localhost:8081/data/420000_forest/{z}/{x}/{y}.pbf`],
                        minzoom: 0,
                        maxzoom: 14
                    }
                        */
                },
                layers: [
                    { id: 'osm_base', type: 'raster', source: 'osm'},
                    /*
                    { id: 'forest_layer', type: 'fill', source: 'forest', 'source-layer': 'forest', paint: { 'fill-color': '#088', 'fill-opacity': 0.2}},
                    { id: 'forest_line', type: 'line', source: 'forest', 'source-layer': 'forest', paint: { 'line-color': '#044', 'line-width': 1}}
                     */
                ]                
            },
            center: center,
            zoom: 8,
            pitch: 0,
            transformRequest: (url, resourceType) => {
                if (resourceType === 'Tile') {
                    return {
                        url: url,
                        headers: {
                            'Fiware-Service': fiware_service,
                            'Fiware-ServicePath': fiware_servicepath,
                            'Authorization': 'Bearer ' + access_token
                        }
                    }
                }
            }
        });

        const popup = new maplibregl.Popup({
            anchor: 'bottom',
            closeButton: false,
            closeOnClick: false
        });

        map.on('mousemove', 'forest_layer', (e) => {
            if (e.features.length > 0) {
                const feature = e.features[0];
                popup.setLngLat(e.lngLat)
                    //.setHTML(JSON.stringify(feature.properties, null, 2).replace(/\n/g, '<br>'))
                    .setHTML(JSON.stringify(feature.properties))
                    .addTo(map);
            }
        });

        map.on('mouseleave', 'forest_layer', () => {
            popup.remove();
        })
    } catch(error) {
        alert('initMap ERROR:' + error.message);
    }
}
