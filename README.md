# pyownet, a pythonic interface to ownet

pyownet is a pure python package that allows to access an 
[owserver](http://owfs.org/index.php?page=owserver_protocol) via the 
[owserver network protocol](http://owfs.org/index.php?page=owserver-protocol),
in short _ownet_.

owserver is part of the [OWFS 1-Wire File System](http://owfs.org):
> OWFS is an easy way to use the powerful 1-wire system of Dallas/Maxim.
>
> OWFS is a simple and flexible program to monitor and control the physical
> environment. You can write scripts to read temperature, flash lights, write
> to an LCD, log and graph, ...

The `pyownet.protocol` module is a low-level implementation of the ownet
protocol. Interaction with an owserver takes place via a proxy object whose
methods correspond to ownet messages:

```
>>> owproxy = OwnetProxy(host="owserver.example.com", port=4304)
>>> owproxy.ping()
>>> owproxy.dir()
['/10.67C6697351FF/', '/05.4AEC29CDBAAB/']
>>> owproxy.present('/10.67C6697351FF/temperature')
True
>>> owproxy.read('/10.67C6697351FF/temperature')
'     91.6195'
```

Higher level modules will follow, providing OO access to sensors on the 1-wire
network.
