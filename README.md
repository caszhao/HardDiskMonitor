# HardDiskMonitor V1.0

A light browser tool to monitor your Hard Disk status in Linux through websocket protocal.
一个轻量级的硬盘监控工具，基于Websocket协议传输，用于监控硬盘的状态。

>Server: Python3+Websocket

>Client: 任何浏览器

Server端运行推荐Ubuntu系统，基于局域网通信，其他Linux理论可行，但没验证过。Windows暂时不考虑。
整个思路是Websocket收发Json，Python3做Server端，Client端就是网页，一个网页监控一台机的数据，要看多个网页，多开几个窗口。

前端请霍大侠写了一个基础版本，后续修改样式，增减功能均由ChatGPT修正和提供。过程有点意思。

* "我发你一段css代码，帮我根据最新流行元素改进一下css样式表，直接给出答案即可"
  
* "我发你html代码，帮我每隔xx秒刷新一下页面=="

>Python3写的Websocket Server端，只是为了采集数据然后送给前端显示。70-80%代码为ChatGPT帮我生成。

* "帮我写一个基于Python3的Websocket的Server端"
  
* "帮我遍历所有硬盘，获取挂载节点，容量，已使用容量，生成json数据"

感谢最早的两位热心捐赠者Loyi和浮生若梦。为表感谢，捐赠者头像会默认嵌入页面中，请捐赠者转xch后与我联系。

如果捐赠者列表对你造成不便，请自行修改移除。

捐赠者名单列表：
Loyi、浮生若梦

XCH地址：
xch1wrdcyq9euygcek9cudlvtuw0v52t93slkfz4vd7fjyjtknzflxms7r7nuu

#使用方法：
## 一、安装所需包
sudo apt install -y smartmontools net-tools lm-sensors python3-full python3-websockets python3-psutil

wget http://archive.ubuntu.com/ubuntu/pool/universe/h/hddtemp/hddtemp_0.3-beta15-53_amd64.deb  

sudo apt install ./hddtemp_0.3-beta15-53_amd64.deb

## 二、Ubuntu上运行服务
sudo python3 server_websocket.py

当然，你也可以后台运行。  nohup sudo python3 ./server_websocket.py >log.txt 2>err.txt &

如果你的Linux主机有多个局域网IP，你可能需要手动修改server_websocket.py把IP固定下来，搜索local_ip，并改成你要的ip即可。默认端口为8765，如果没有冲突，可以不改。

## 三、本地打开go.html后，使用参数传入局域网ip，参数：
必填参数:

ip: 运行server_websocket.py的server端。

time: 为数据刷新时间time，不加time默认是30秒，监控也意味着读取，建议设置长一点。

title：为左上角标题，可以设置成譬如“XX主机“。

以下例子为连接局域网IP为192.168.1.102的机器，数据刷新时间间隔120秒，该机器名称为“我的奇幻世界”，你可以保存为浏览器标签，方便跳转。

go.html?ip=192.168.1.102&time=120&title=我的奇幻世界
