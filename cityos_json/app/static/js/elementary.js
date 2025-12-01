let map = null;
let apiname = 'elementary';
let fiware_service = 'bodik';
let fiware_servicepath = '/protected/elementary';
let access_token = null;
let refresh_token = null;

let hoveredId = null;

const organ_list = {
    '400009': { 'name': '福岡市', 'tile': `${fiware_server}/tile/data/401307_elementary/{z}/{x}/{y}.pbf`},
};

async function show_page() {
    try {
        let combo = clear_child('organ_select');
        if (combo) {
            combo.addEventListener('click', () => {
                select_organ();
            });

            for (let organ_code in organ_list) {
                let option = document.createElement('option');
                option.value = organ_code;
                option.text = organ_list[organ_code].name;
                combo.appendChild(option);
            }
            combo.selectedIndex = 0;
        }

        await initMap();

        //select_organ();

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
            let login_success = await demo_login();
            if (login_success) {
                if (map) {
                    const info = organ_list[organ_code];
                    console.log('organ_code', organ_code, info)

                    //  古いレイヤーとソースを削除する
                    if (map.getLayer('elementary_outline')) {
                        map.removeLayer('elementary_outline');
                    }
                    if (map.getLayer('elementary_layer')) {
                        map.removeLayer('elementary_layer');
                    }
                    if (map.getSource('elementary')) {
                        map.removeSource('elementary');
                    }

                    //  新しいレイヤーとソースを追加する
                    map.addSource('elementary', {
                        type: 'vector',
                        tiles: [ info.tile ],
                        minzoom: 0,
                        maxzoom: 14
                    });

                    map.addLayer({
                        id: 'elementary_layer',
                        type: 'fill',
                        source: 'elementary',
                        'source-layer': 'elementary',
                        paint: {
                            'fill-color': [
                                'case',
                                ['boolean', ['feature-state', 'hover'], false],
                                '#ffff00',          // hover=trueならば、黄色
                                'rgba(0,0,0,0)',    // hover=falseならば、透明     
                            ],
                            'fill-opacity': 0.5
                        }
                    });

                    map.addLayer({
                        id: 'elementary_outline',
                        type: 'line',
                        source: 'elementary',
                        'source-layer': 'elementary',
                        paint: {
                            'line-color': '#044',
                            'line-width': 1
                        }
                    });
                }
            }
        }
    } catch(error) {
        alert('select_organ:' + error);
    }
}

async function initMap() {
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
                },
                layers: [
                    { id: 'osm_base', type: 'raster', source: 'osm'},
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

        map.on('mousemove', 'elementary_layer', (e) => {
            if (e.features.length > 0) {
                const feature = e.features[0];
                //  古いhover状態をリセット
                if (hoveredId !== null) {
                    map.setFeatureState(
                        { source: 'elementary', sourceLayer: 'elementary', id: hoveredId },
                        { hover: false }
                    )
                }

                //  新しいhover状態
                hoveredId = feature.id;
                console.log('hoveredId', hoveredId);
                map.setFeatureState(
                    { source: 'elementary', sourceLayer: 'elementary', id: hoveredId },
                    { hover: true }
                )

                popup.setLngLat(e.lngLat)
                    .setHTML(feature.properties['校区名'])
                    .addTo(map);
            }
        });

        map.on('mouseleave', 'elementary_layer', () => {
            if (hoveredId !== null) {
                map.setFeatureState(
                    { source: 'elementary', sourceLayer: 'elementary', id: hoveredId },
                    { hover: false }
                )
            }
            hoveredId = null;
            popup.remove();
        })

        map.on('load', () => {
            select_organ();
        });

    } catch(error) {
        alert('initMap ERROR:' + error.message);
    }
}
