# Archive Internet to IPFS （将互联网保存到IPFS）

Usage 用法 :
    
    ipfs daemon
    mkidr data
    # choose a valuable page
    php fetch.php https://book.douban.com/review/9343427/
    # your will get 2 url, local and ipfs gateway
    # http://localhost:8080/ipfs/QmP3oHPzj7Jr6ch2rRGfHvJu7kHvu9S6enskCoRCvdg8t2/9343427.html
    # https://ipfs.io/ipfs/QmP3oHPzj7Jr6ch2rRGfHvJu7kHvu9S6enskCoRCvdg8t2/9343427.html

It will download the page, and show you the ipfs address.
这个小工具将会下载页面，并且给出IPFS的地址。

Prequisitions 依赖 :
- ipfs
- php

Now suport 现支持:

- 知乎（回答、用户回答列表）
- 豆瓣（影评、书评）

Issues are welcomed.
欢迎提 Issue。
