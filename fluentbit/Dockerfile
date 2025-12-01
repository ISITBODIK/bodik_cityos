#FROM fluent/fluent-bit
FROM fluent/fluent-bit:4.0.7-debug

# ヘルスチェック用の netcat と、デバッグ用の bash をインストール
#RUN apk add --no-cache netcat-openbsd bash

ADD ./conf/fluent-bit.conf /fluent-bit/etc/
ADD ./conf/parsers.conf /fluent-bit/etc/
