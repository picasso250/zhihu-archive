# Archive Internet to IPFS

Usage:
    
    ipfs daemon
    mkidr data
    # choose a valuable page
    php fetch.php https://book.douban.com/review/9343427/
    # your will get 2 url, local and ipfs gateway
    # http://localhost:8080/ipfs/QmP3oHPzj7Jr6ch2rRGfHvJu7kHvu9S6enskCoRCvdg8t2/9343427.html
    # https://ipfs.io/ipfs/QmP3oHPzj7Jr6ch2rRGfHvJu7kHvu9S6enskCoRCvdg8t2/9343427.html

It will download the page, and show you the ipfs address.

Prequisitions:
- ipfs
- php