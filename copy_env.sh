#!/bin/bash

function copyenv() {
    # フォルダが存在するかチェック
    if [ ! -d "$1" ]; then
        echo "エラー: ディレクトリ '$1' が見つかりません。"
        exit 1
    fi

    # 指定されたフォルダに移動
    cd "$1" || { echo "cdコマンドに失敗しました。"; exit 1; }
    
    # appディレクトリに移動
    if [ -d "./app" ]; then
        cd "./app" || { echo "cd ./app に失敗しました。"; exit 1; }
    else
        echo "エラー: 'app' ディレクトリが見つかりません。"
        exit 1
    fi

    # env.py ファイルが存在するかチェック
    if [ -f "env.py" ]; then
        echo "ファイル 'env.py' は既に存在します。スキップします。"
    else
        # env_temp.py を env.py にコピー
        if [ -f "env_temp.py" ]; then
            cp "env_temp.py" "env.py"
            echo "'env_temp.py' から 'env.py' を作成しました。"
        else
            echo "エラー: 'env_temp.py' が見つかりません。コピーできませんでした。"
        fi
    fi
}

# ---
# メイン処理
# ---
# 許可されたパラメータの配列を定義
allowed_params=("cityos_json" "cityos_mqttsubsc" "cityos_subsc" "cityos_support")

# 入力パラメータを取得
folder="$1"

# パラメータが指定されているかチェック
if [ -z "$folder" ]; then
    echo "エラー: パラメータを指定してください。"
    echo "使用方法: $0 <${allowed_params[@]}>"
    exit 1
fi

# 入力されたパラメータが配列に含まれているかチェック
is_allowed=false
for param in "${allowed_params[@]}"; do
    if [ "$folder" == "$param" ]; then
        is_allowed=true
        break
    fi
done

# 許可されたパラメータの場合のみ処理を実行
if [ "$is_allowed" == true ]; then
    echo "パラメータ '$folder' は許可されています。処理を開始します。"
    # ここに実行したい処理を記述
    # 例: run_script "$input_param"
    copyenv "$folder"
else
    echo "エラー: パラメータ '$folder' は許可されていません。"
    echo "許可されたパラメータ: ${allowed_params[@]}"
    exit 1
fi

# 第1引数があるかチェック
if [ -z "$1" ]; then
    echo "使用方法: $0 <フォルダ名>"
    exit 1
fi

