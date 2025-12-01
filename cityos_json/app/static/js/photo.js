let streaming = false;
let localStream = null;

let credentials = null;
let access_token = null;
let refresh_token = null;

let width = 320;
let height = 0;

// HD画質程度
const maxWidth = 1280;
const maxHeight = 720;

let canvas = null;
let videoLayer = null;
let photoLayer = null;
let mapLayer = null;
let map = null;
let marker = null;
let current_position = null;
let prev_layer = null;
let current_layer = null;

let selected_photo_data_url = null;
let selected_name = 'unknown';
let constraints = null;
let cameraFacing = true;

//  fiware登録情報
const apiname = 'photo';
const entity_type = apiname;
const fiware_service = 'bodik';
const fiware_servicepath = `/public/${apiname}`;

function show_page() {
    try {
        canvas = document.getElementById('canvas');
        canvas.style.display = 'none';

        videoLayer = document.getElementById('video');
        //video.style.display = 'none';

        photoLayer = document.getElementById('photo');
        //photo.style.display = 'none';

        mapLayer = document.getElementById('map');
        //mapLayer.style.display = 'none';

        let map_button = document.getElementById('show_map');
        map_button.setAttribute('title', '位置を確認する');
        map_button.addEventListener('click', (evt) => {
            setMap();
        })
        constraints = {
            video: { facingMode: 'user'},
            audio: false
        }

        setMap();

    } catch(error) {
        alert('show_page:' + error);
    }
}

function setCamera() {
    try {
        if (videoLayer) {
            //  ビデオ表示部を有効化
            //photo.style.display = 'none';
            //video.style.display = 'block';
            showLayer('video');

            let row = clear_child('row');
            if (row) {
                let take_photo_button = makeButton(row, 'submit', take_photo, 'take_photo', '撮影');
                //take_photo_button.disabled = true;

                makeButton(row, 'submit', change_camera, 'change_camera', 'カメラ切替');
            }

            startVideo();
        }
    } catch(error) {
        alert('setCamera:' + error);
    }
}

function setPhoto(data) {
    try {
        if (photoLayer) {
            //  写真表示部を有効化
            //photo.style.display = 'block';
            //video.style.display = 'none';
            
            showLayer('photo');

            if (data) {
                photoLayer.setAttribute('src', data);
                selected_photo_data_url = data;
            }

            let row = clear_child('row');
            if (row) {
                makeButton(row, 'submit', data_upload, 'data_upload', '登録');
                makeButton(row, 'submit', setCamera, 'show_camera', 'カメラ');
            }

        }
    } catch(error) {
        alert('setPhoto:' + error);
    }
}

function setMap() {
    try {
        if (mapLayer) {
            //  写真表示部を有効化
            //photo.style.display = 'block';
            //video.style.display = 'none';
            prev_layer = current_layer;            
            showLayer('map');

            let row = clear_child('row');
            if (row) {
                makeButton(row, 'submit', check_location, 'checkGPS', 'GPS');
                makeButton(row, 'submit', set_location, 'set_location', '位置決定');
            }

            if (!map) {
                initLeaflet();
            }
        }
    } catch(error) {
        alert('setMap:' + error);
    }
}

function showLayer(id) {
    
    const layers = ['map', 'video', 'photo'];
    layers.forEach(layerId => {
        const el = document.getElementById(layerId);
        if (layerId === id) {
            el.classList.remove('inactive');
            el.classList.add('active');
        } else {
            el.classList.remove('active');
            el.classList.add('inactive');
        }
    });
    current_layer = id;
}

/*
    カメラ
*/
function startVideo() {
    try {
        if (localStream) {
            localStream.getVideoTracks().forEach((camera) => {
                camera.stop();
            });
            localStream = null;
            streaming = false;
        }

        navigator.mediaDevices
            .getUserMedia(constraints)
            .then((stream) => {
                localStream = stream;

                videoLayer.srcObject = stream;
                videoLayer.play();
            })
            .catch((err) => {
                alert('ビデオが見つかりません');
            });
        
            videoLayer.addEventListener("canplay", (ev) => {
            if (!streaming) {
                canvas.setAttribute('width', videoLayer.videoWidth);
                canvas.setAttribute('height', videoLayer.videoHeight);
                streaming = true;
                
                let take_photo_button = document.getElementById('take_photo');
                take_photo_button.disabled = false;
            }
        }, false);

    } catch(error) {
        alert('startVideo:' + error);
    }
}

function change_camera() {
    try {
        if (cameraFacing) {
            cameraFacing = false;
        } else {
            cameraFacing = true;
        }
        constraints.video.facingMode = cameraFacing ? 'user' : { exact: 'environment'};
        startVideo();
    } catch(error) {
        alert('change_camera:' + error);
    }
}

/*
    写真
*/
function init_canvas() {
    try {
        const context = canvas.getContext('2d');
        context.fillStyle = "#AAA";
        context.fillRect(0, 0, canvas.width, canvas.height);

    } catch(error) {
        alert('init_canvas:' + error);
    }
}

function clear_photo() {
    try {
        const context = canvas.getContext('2d');
        photoLayer.setAttribute('src', data);

    } catch(error) {
        alert('clear_photo:' + error);
    }
}

async function take_photo() {
    try {
        let data = null;
        const context = canvas.getContext('2d');
        //canvas.style.display = 'block';
        if (localStream) {
            context.drawImage(videoLayer, 0, 0, canvas.width, canvas.height);
            let org = canvas.toDataURL("image/png");
            data = await resizeImage(org)
        } else {
            context.fillStyle = "#AAA";
            context.fillRect(0, 0, canvas.width, canvas.height);
            data = canvas.toDataURL("image/png");
        }
        //canvas.style.display = 'none';
        setPhoto(data);

    } catch(error) {
        alert('take_photo:' + error);
    }
}

async function data_upload() {
    try {
        if (credentials !== null || await demo_login()) {
            let res_url = await upload_photo(selected_photo_data_url);
            if (res_url) {
                await upload_orion(res_url);
            }
        } else {
            alert('ログインできませんでした');
        }
    } catch(error) {
        alert('data_upload:' + error);
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

function getDeviceId() {
    let result = 'demo';
    try {
        let id = localStorage.getItem('device_id');
        if (!id) {
            id = window.crypto.randomUUID();
            localStorage.setItem('device_id', id);
        }
        result = id;

    } catch(error) {
        alert('getDeviceId:' + error);
    }
    return result;
}

function resizeImage(dataUrl) {
    try {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                let width = img.width;
                let height = img.height;
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width = Math.round(width * ratio);
                    height = Math.round(height * ratio);
                }

                const offCanvas = document.createElement('canvas');
                offCanvas.width = width;
                offCanvas.height = height;
                const ctx = offCanvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                resolve(canvas.toDataURL('image/jpeg', 0.8));       //  圧縮を優先するため、非可逆圧縮のJPEGになる
            };
            img.src = dataUrl;
        });
    } catch(error) {
        alert('resizeImage:' + error);
    }
    return null;
}

async function upload_photo(dataUrl) {
    let res_url = null;
    try {
        let deviceId = getDeviceId();
        const resized = await resizeImage(dataUrl);
        const blob = await (await fetch(resized)).blob();
        const formData = new FormData();
        formData.append('entity_type', entity_type);
        formData.append('device_id', deviceId);
        formData.append('upload_file', blob, 'photo.jpg');

        let headers = {
            'User-Agent': 'BODIK/2.0',
            'Accept': 'application/json',
            'Fiware-Service': fiware_service,
            'Fiware-ServicePath': fiware_servicepath
        }
        headers['Authorization'] = 'Bearer ' + access_token;

        let options = {
            method: 'POST',
            headers: headers,
            body: formData
        }

        const url = `${fiware_server}/uploads`;
        const uploadRes = await fetch(url, options);
        let status_code = uploadRes.status;
        let expired = false;
        if (status_code === 401) {
            //  認証期限切れ
            expired = true;
            try {
                //  リフレッシュを試す
                await refresh();
            } catch(err) {
                throw err;
            }
            headers['Authorization'] = 'Bearer ' + access_token;
            resp = await fetch(url, options);
            status_code = resp.status;
        }

        if (status_code == 200) {
            res_url = await uploadRes.json();
        } else {
            credentials = null;
            if (expired) {
                alert('認証時間切れです。もう一度、お試しください。' + status_code);
            } else {
                alert('エラーです:' + status_code);
            }
        }
    } catch(error) {
        alert('upload_photo:' + error);
    }
    return res_url;
}

async function upload_orion(res_url) {
    try {
        const deviceId = getDeviceId();

        const tm = new Date().toISOString();

        //  NGSI形式
        let doc = {
            'id': `${entity_type}.${deviceId}`,
            'type': entity_type,

            'device_id': {
                'type': 'String',
                'value': deviceId
            },
            'name': {
                'type': 'String',
                'value': selected_name
            },
            'photo_url': {
                'type': 'String',
                'value': res_url
            },
            'location': {
                'type': 'geo:json',
                'value': {
                    'type': 'Point',
                    'coordinates': [ current_position[1], current_position[0] ]     //  [ lon, lat ]
                }
            },
            'timestamp': {
                'type': 'DateTime',
                'value': tm
            }

        }

        let headers = {
            'User-Agent': 'BODIK/2.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Fiware-Service': fiware_service,
            'Fiware-ServicePath': fiware_servicepath
        }
        headers['Authorization'] = 'Bearer ' + access_token;

        options = {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(doc)
        }

        const url = `${fiware_server}/v2/entities?options=upsert`;
        let resp = await fetch(url, options);
        let status_code = resp.status;
        let expired = false;
        if (status_code === 401) {
            //  認証期限切れ
            expired = true;
            try {
                //  リフレッシュを試す
                await refresh();
            } catch(err) {
                throw err;
            }
            headers['Authorization'] = 'Bearer ' + access_token;
            resp = await fetch(url, options);
            status_code = resp.status;
        }

        if (status_code == 201 || status_code == 204) {
            //  201：作成OK、204：更新OK
            alert('登録しました');
        } else {
            credentials = null;
            if (expired) {
                alert('認証時間切れです。もう一度、お試しください。');
            } else {
                alert('登録できませんでした:' + status_code);
            }
        }

    } catch(error) {
        alert('upload_orion:' + error);
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
        console.log(pos);
        setMarker(pos)
    } catch(error) {
        alert('setPosition:' + error);
    }
}

function set_location() {
    try {
        if (prev_layer == 'photo') {
            setPhoto(null);
        } else {
            setCamera();
        }
    } catch(error) {
        alert('set_location:' + error);
    }
}

function setMarker(pos) {

    try {
        if (marker) {
            //  古いマーカーを削除
            map.removeLayer(marker);
            marker = null;
        }

        marker = L.marker(pos, { draggable: true }).addTo(map);
        let popup = L.popup().setContent("現在地");
        marker.bindPopup(popup);
        current_position = pos;
        marker.on('dragend', function(evt) {
            let latlng = this.getLatLng();
            current_position = [ latlng.lat, latlng.lng ];
        });

        let zoom = map.getZoom();
        map.setView(pos, zoom, { animate: true, duration: 1 });
    } catch(error) {
        alert('setMarker:' + error);
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
        
        map.on('dblclick', (evt) => {
            let latlng = evt.latlng;
            current_position = [ latlng.lat, latlng.lng ];
            setMarker(current_position);
            evt.preventDefault();
        });

        if (current_position) {
            setMarker(current_position);
        } else {
            check_location();
        }
    } catch(error) {
        alert('initLeaflet ERROR:' + error.message);
    }
}
