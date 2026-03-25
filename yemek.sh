#!/bin/bash

# Senin paylaştığın cookie'lerden kritik olanları buraya ekledim
# Not: _px3 değeri çok hızlı bayatlar, hata alırsan tarayıcıdan yenisini almalısın.
MY_COOKIES="dhhPerseusGuestId=1763832769892.092163970418918182.e0o0i917uc; ld_key=1763832769892.092163970418918182.e0o0i917uc; __ssid=3250ba319696692233da1fb0a4171e4; _pxvid=4461802e-c7c9-11f0-b851-9fc731067022; _px3=2a383a335acb703e1a82a8d34eecdf4dcfe4a35c07e6235035a47fef92794229:6DHUKkCM/Co+D8R2y5vIKbMDMDwYC0MJNZ0btHs053aalz6Pbhv3xfvyl9HgexM3g3mcCUbeDveYpEKKt7F/GQ==:1000:aTkeqL/phkNMUEjYEoVDqkG703Dq/mKyioBFdOasm7znM+lRZQJLGMep7jDwGI4AJO1AKfD2TAdsYM08+LTKr9brQyxBIB7bdBxL0HLRA0V+bcUJpZKgL8BdChRAcMDfwbRl+AyWbnRt+slaEbx3pYTDQq9YY1XRJ+LkhZkb89LA6a/j2yMd8meKmZ3X0vt1+WgBRrfvJzDgR8uG6k+2N7KSdXeJcBLoXpCR1Pd8XIEAeHYPX6hjJQZHkM6afjTPEWLktxPIvY/lUapuuh2D05+D2RctFv0GyxKZKrgANqDVkrpeVHw0HMxePIceyoelA+cDog3sFwUFiV1WDGHtXVT/f+Sp59j07LVyiNVT/xo="

echo "🚀 Yemeksepeti'ne istek atılıyor..."

curl -s -X GET "https://www.yemeksepeti.com/profile" \
     -H "authority: www.yemeksepeti.com" \
     -H "user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" \
     -H "cookie: $MY_COOKIES" \
     -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8" \
     --compressed > sonuc.html

echo "✅ İşlem tamamlandı. Çıktı 'sonuc.html' dosyasına kaydedildi."
