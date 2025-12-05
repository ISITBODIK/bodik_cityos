let dataset_list = null;
let myconfig_list = {};
let selected_myconfig = null;

function show_page() {
    let result = false;
    try {
        let search_button = document.getElementById('search');
        search_button.addEventListener('click', () => {
            execute_search();
        });

        let grid_area = document.getElementById('grid_area');
        let grid = makebox(grid_area, 'ag-theme-alpine', 'grid-csv', '');
        grid.style.width = 'auto';
        grid.style.height = '100%'; //'600px';
        grid.style.margin = '10px';

        get_dataset_list();

        show_data([]);

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
        let url = `${fiware_server}/myapi/public`;
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
                show_params();
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
            show_params();
        });
    } catch(error) {
        alert('select_dataset:' + error)
    }
}

function show_params() {
    try {
        let area = clear_child('param_area');
        if (area) {
            if (selected_myconfig) {
                let datamodel = selected_myconfig['dataModel'];
                for (let field in datamodel) {
                    let info = datamodel[field];
                    let row = makebox(area, 'row', '', '');
                    makebox(row, 'caption', '', field);
                    makeEdittext(row, 'text_field', field);
                }
                //makebox(area, 'row_last', 'dummy', '');
            }
        }
    } catch(error) {
        alert('show_params:' + error);
    }
}

function execute_search() {
    try {
        let query = build_query();
        search_history(query);
    } catch(error) {
        alert('execute_search:' + error);
    }
}

function build_query() {
    let result = null;
    try {
        if (selected_myconfig) {
            let condition = {};
            let datamodel = selected_myconfig['dataModel'];
            for (let field in datamodel) {
                let info = datamodel[field];
                let item = document.getElementById(field);
                if (item) {
                    let field_name = info['field_name'];
                    let text = item.value;
                    if (text.length > 0) {
                        condition[field_name] = text
                    }
                }
            }
            result = condition;
        }
    } catch(error) {
        alert('build_query:' + error);
    }
    return result;
}

async function search_history(query) {
    try {
        show_data(null);
        let apiname = selected_myconfig.apiname;
        let fiware_service = selected_myconfig['Fiware-Service'];
        let fiware_servicepath = selected_myconfig['Fiware-ServicePath'];

        let headers = {
            'User-Agent': 'BODIK/2.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Fiware-Service': fiware_service,
            'Fiware-ServicePath': fiware_servicepath
        }

        let p = {
            'apiname': apiname,
            'maxResults': 1000
        };
        let params = Object.assign(p, query);

        options = {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(params)
        }

        let url = fiware_server + '/history';
        let resp = await fetch(url, options);
        let status_code = resp.status;
        if (status_code == 200) {
            let data = await resp.json(); 
            if (data && 'resultsets' in data) {
                if ('features' in data.resultsets) {
                    show_data(data.resultsets.features);
                }
            }
        } else {
            alert('エラーです:' + status_code);
        }
    } catch(error) {
        alert('call_ngsi:' + error);
    }
}

function show_data(features) {
    try {
        console.log(features);
        let headerdata = [];
        let rowdata = [];
        if (features && features.length > 0) {
            let item0 = features[0].properties
            let csv_header = Object.keys(item0);
            let header = null;
            header = csv_header;
    
            let updated_at_exists = false;
            for (let fld of header) {
                if (fld == '_updated_at') {
                    updated_at_exists = true;
                }
                let col = {
                    'headerName': fld,
                    'field': fld
                };
                headerdata.push(col);
            }

            if (!updated_at_exists) {
                let col = {
                    headerName: '_updated_at',
                    field: '_updated_at'
                }
                headerdata.push(col);
            }

            rowdata = [];
            for (let feature of features) {
                rowdata.push(feature.properties)
            }
        }

        grid_options = {
            'columnDefs': headerdata,
            'defaultColDef': {
                editable: true,
                filter: true,
                sortable: true,
                resizable: true
            },
            'rowSelection': 'single',
            'rowData': rowdata
        };

        let grid = clear_child('grid-csv');
        new agGrid.Grid(grid, grid_options);
        //grid_options.api.sizeColumnsToFit();

    } catch(error) {
        alert('show_data:' + error);
    }
}
