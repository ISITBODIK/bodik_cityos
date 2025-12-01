import os
from pathlib import Path
import subprocess

import json
import zipfile
import time

OUTPUT_DIR = Path('./tiledata')

class Map:

    def __init__(self, name, organ_code):
        try:
            print('map.init called')
            self.name = name
            self.organ_code = organ_code
            self.output_dir = os.path.join(OUTPUT_DIR, name)
            os.makedirs(self.output_dir, exist_ok=True)

        except Exception as e:
            print('map.init', e)

    def parse_shapefile(self, tmp_dir, zip_path):
        result = False
        try:
            print('parse_shapefile called')
            #org_path = Path(zip_path)
            mbtile_name = f'{self.organ_code}_{self.name}'

            now = str(int(time.time()))
            mytemp = os.path.join(tmp_dir, now)
            os.makedirs(mytemp, exist_ok=True)  # ← ここがポイント
            print('extract zip')
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(mytemp)
            
            print('zip extraced')
            shp_files = []
            for root, dirs, files in os.walk(mytemp):
                for f in files:
                    print('解凍されたもの', os.path.join(root, f))

                    if f.endswith(".shp") or f.endswith(".SHP"):
                        print('shp file', f)
                        #shp_files.append(f)
                        shp_files.append(os.path.join(root, f))

            if len(shp_files) > 0:
                print('shp_files', shp_files)

                mbtile_list = []
                no = 0
                for shp_file in shp_files:
                    sf = Path(shp_file)
                    # shpをgeojsonに変換する
                    geojson_filename = sf.stem + ".geojson"
                    geojson_path = os.path.join(mytemp, geojson_filename)
                    cmd = [
                            "ogr2ogr",
                            "-f", "GeoJSON",
                            #"-s_srs", "EPSG:4326",  # 抜けているケースあり。いいのか？
                            "-t_srs", "EPSG:4326",
                            geojson_path,
                            shp_file
                    ]
                    print('make geojson cmd', cmd)
                    subprocess.run(cmd, check=True)

                    mbtile_filename = f'{mbtile_name}_{no:03}.mbtiles'
                    mbtile_path = os.path.join(mytemp, mbtile_filename)
                    # geojsonごとにタイルを作成する
                    cmd = [
                        "tippecanoe",
                        "-o", mbtile_path,
                        "-l", self.name,
                        "--force",
                        "--generate-ids",           # feature に id をセットする。feature特定する時に使用する
                        "--simplification=10",
                        "--drop-densest-as-needed",
                        "--coalesce-densest-as-needed",
                        "--reorder",
                        "--extend-zooms-if-still-dropping",
                        "-Z0",      # 最低ズーム
                        "-z14",     # 最高ズーム
                        geojson_path
                    ]
                    print('make tile cmd', cmd)
                    resp = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print('stdout', resp.stdout)
                    print('stderr', resp.stderr)
                    no += 1
                    mbtile_list.append(mbtile_path)

                if len(mbtile_list) > 0:
                    merged_mbtile_filename = f'{mbtile_name}.mbtiles'
                    merged_mbtile_path = os.path.join(self.output_dir, merged_mbtile_filename)
                    cmd = [
                        "tile-join",
                        "-o", merged_mbtile_path,
                        "--force",
                        "--no-tile-size-limit"
                    ] + mbtile_list
                    print('merge tile cmd', cmd)
                    resp = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print('stdout', resp.stdout)
                    print('stderr', resp.stderr)
                    
                result = True

        except Exception as e:
            print('parse_shapefile', e)
        return result

    def convert_geojson(self, geojson_path):
        result = False
        try:
            mbtile_name = f'{self.organ_code}_{self.name}'
            mbtile_filename = f'{mbtile_name}.mbtiles'
            mbtile_path = os.path.join(self.output_dir, mbtile_filename)
            # geojsonをタイルに変換する
            cmd = [
                "tippecanoe",
                "-o", mbtile_path,
                "-l", self.name,
                "--force",
                "--generate-ids",               # feature に id をセットする。feature特定する時に使用する
                "--simplification=10",
                "--drop-densest-as-needed",
                "--coalesce-densest-as-needed",
                "--reorder",
                "--extend-zooms-if-still-dropping",
                "-Z0",      # 最低ズーム
                "-z14",     # 最高ズーム
                geojson_path
            ]
            print('make tile cmd', cmd)
            resp = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print('stdout', resp.stdout)
            print('stderr', resp.stderr)

            result = True

        except Exception as e:
            print('convert_geojson', e)
        return result
