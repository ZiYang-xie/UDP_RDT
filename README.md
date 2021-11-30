# 计网传输层 - 可靠传输协议实验2

*谢子飏 19307130037*

*代码连接：[ZiYang-xie/UDP_RDT: Reliable Data Transmission implemented on UDP (github.com)](https://github.com/ZiYang-xie/UDP_RDT)*

## 1. 实验简介

​	本次实验和上次实验基本类似，不同之处是上次实验是模拟的传输环境，而这次需要在真实的UDP传输基础之上实现 RDT。和上次实验一样分别实现 RDT3.0 / GoBackN / Selective Repeat

​	上次实验使用c进行编写，这次我选择使用python再次重构实验，希望写的更oop一点。

## 2. 代码介绍

​	整个架构围绕 `sender` 和 `receiver` 展开，三个协议在 src 目录下

### 2.1 **继承架构图**

<img src="https://tva1.sinaimg.cn/large/008i3skNgy1gwxgfqn9bxj30ri0ngwg3.jpg" style="zoom:30%;" />

### 2.2 使用方式

- **基本使用**

分别开启接收端和发送端，第三个参数是协议类型，分别对应三种协议实现

```python
PORTOCOL
  'ab': altBit,
  'gbn': goBackN,
  'sr': selRepeat
```

```shell
python receiver.py [ab|gbn|sr]
```

```shell
python sender.py [ab|gbn|sr]
```

- **基础设置**

  - 基础设置可以在基类处 `src/rdt.py` 进行修改，将 Test_mode 改为False则没有测试信息输出，Verbose 代表是否打印中间收发包的详细信息（由于python print比较慢，建议在 Test_mode 的时候关闭 Verbose)

  ```python
  class RDT():
      def __init__(self, MSS=1024, TimeOut=0.1, Test_mode=True, Verbose=False) -> None:
  ```

- **文件生成**

​	可以使用 `file_creator.py` 在 `data/sender` 目录下生成传输文件，使用方法如下

```shell
Usage: python file_creator.py <file_name> <line_num>
```

- **弱网模拟**

​	本机是mac环境，可以通过 `simulator` 下的 `weak_network.py` 进行弱网模拟，通过 dnctl 创建弱网规则，再通过 dummynet 和 pfctl 将 udp 流量引导至对于规则。

```shell
sudo dnctl pipe 1 config bw {bw} delay {delay} plr {loss}
```

```
dummynet in proto udp from any to any pipe 1   
dummynet out proto udp from any to any pipe 1
```

*使用方法：*

```python
# simulator/weak_network
bw = 0 # 带宽设置，0代表无限制
delay = 0.1 # 延迟设置
loss = 0.01 # 丢包设置
# 设置弱网
python simulator/weak_network.py set
# 关闭弱网
python simulator/weak_network.py reset
```



### 2.3 正确性检验

​	`receiver` 最终接收到的内容被保存到了 `data/recv_file` 目录下，可以通过 `data/send_file` 和 `data/recv_file` 的一致性对比来验证协议栈的正确性。

```shell
➜  Code git:(main) ✗ diff ./data/recv_file/received ./data/send_file/large
➜  Code git:(main) ✗ 
# 可以看到没有差别
```

<img src="https://tva1.sinaimg.cn/large/008i3skNgy1gwxh1ycjkyj31cg0h4q70.jpg" style="zoom:50%;" />

## 3. 实验内容

​	本次实验内容和上次实验内容差不多，首先生成一个两万行的文件，可以看到大小为 2.1MB

```shell
➜  send_file git:(main) ✗ du -h large 
2.1M    large
```

### 3.1 理想情况

- **参数设置**

```yaml
Test_mode: True
Verbose: False # 即不输出内容，去除print速度影响
Timeout: 0.01
Window_size: 10
带宽: 无限制
延迟: 0ms
丢包: 0%
```

| Portocol         | Actual Loss Rate | Average RTT / ms | Time / s |
| :--------------- | :--------------: | :--------------: | :------: |
| AltBit           |      0.00%       |       0.08       |  0.313   |
| Go Back N        |      0.00%       |       0.11       |  0.273   |
| Selective Repeat |      0.00%       |       0.09       |  0.264   |

```shell
# Alt Bit
Send Times: 2040 | Success Times: 2040
Actual Loss Rate: 0.00 %
Avg RTT: 0.09ms
[Send Done] Time: 0.31284594535827637 s
# GBN
Send Times: 2040 | Success Times: 2040
Actual Loss Rate: 0.00 %
Avg RTT: 0.08ms
[Send Done] Time: 0.2726902961730957 s
# SR
Send Times: 2040 | Success Times: 2040
Actual Loss Rate: 0.00 %
Avg RTT: 0.09ms
[Send Done] Time: 0.2641279697418213 s
```

​	可以看出在理想情况下，三种协议的速度区别并不是很大，因为没有丢包和乱序，设计的差异就仅仅在滑动窗口式的发送上，当窗口不是很大的情况下 *(实验中为10)*  速度差异就仅仅是底层网络传输的速度波动。



### 3.2 低丢包情况

```yaml
Test_mode: True
Verbose: False # 即不输出内容，去除print速度影响
Timeout: 0.01s
Window_size: 10
带宽: 无限制
延迟: 0ms
丢包: 1%
```

| Portocol         | Actual Loss Rate | Average RTT / ms | Time / s |
| :--------------- | :--------------: | :--------------: | :------: |
| AltBit           |      3.82 %      |       0.64       |   1.61   |
| Go Back N        |     23.31 %      |       0.60       |   1.23   |
| Selective Repeat |      3.77 %      |       0.83       |   1.46   |

```shell
# Alt Bit
Send Times: 2121 | Success Times: 2040
Actual Loss Rate: 3.82 %
Avg RTT: 0.64ms
[Send Done] Time: 1.605008840560913 s
# GBN
Send Times: 2660 | Success Times: 2040
Actual Loss Rate: 23.31 %
Avg RTT: 0.60ms
[Send Done] Time: 1.2262442111968994 s
# SR
Send Times: 2120 | Success Times: 2040
Actual Loss Rate: 3.77 %
Avg RTT: 0.83ms
[Send Done] Time: 1.465817928314209 s
```

​	在丢包情况下，理论丢包率是 1%，实际丢包率较高一点，AltBit 和 SR 的丢包率在 3.8%左右 可以作为一个实际丢包率的参考。我们可以看到 GBN 的丢包率明显高于 AltBit 和 Selective Repeat 这是因为 GBN 的协议设置，在一次丢包后重发窗口中所有的包，因此可以看到 GBN 的 `send times` 明显高于停等和只发送没有接受到的左侧包的 Alt Bit 和 SR

​	速度上我们可以看到 GBN 虽然丢包率高，但得益于相对简单的buffer设计和累计确认模式，其比 Alt Bit 速度快的同时，打败了 Selective Repeat，这是由于 SR 协议需要在接收端维护缓冲区，牺牲了许多性能（尤其是使用python的情况下）这里可以从 `Avg RTT` 看出 SR 的 RTT 要比另两者更长，这里算入了处理时间。



### 3.2 高丢包情况

```yaml
Test_mode: True
Verbose: False # 即不输出内容，去除print速度影响
Timeout: 0.01s
Window_size: 10
带宽: 无限制
延迟: 0ms
丢包: 10%
```

| Portocol         | Actual Loss Rate | Average RTT / ms | Time / s |
| :--------------- | :--------------: | :--------------: | :------: |
| AltBit           |     18.47 %      |       2.50       |   6.71   |
| Go Back N        |     51.31 %      |       1.59       |   3.34   |
| Selective Repeat |     17.31 %      |       4.86       |   5.44   |

```shell
# Alt Bit
Send Times: 2502 | Success Times: 2040
Actual Loss Rate: 18.47 %
Avg RTT: 2.50ms
[Send Done] Time: 6.710391044616699 s
# GBN
Send Times: 4190 | Success Times: 2040
Actual Loss Rate: 51.31 %
Avg RTT: 1.59ms
[Send Done] Time: 3.3448100090026855 s
# SR
Send Times: 2467 | Success Times: 2040
Actual Loss Rate: 17.31 %
Avg RTT: 4.86ms
[Send Done] Time: 5.444291830062866 s
```

​	高丢包情况类似，可以看到 GBN 依然表现最好，原因仍然是 Selective Repeat 的缓冲区处理消耗太大，可以看到 Average RTT 为 4.86ms 是所有里面最长的。如果 Selective Repeat 的缓冲区可以通过编译型语言实现或者利用某些硬件优化实现，可以大幅提升性能。



## 4. 实验总结

​	本次实验从 UDP 基础上实现了可靠信息传输机制，更加了解掌握了 RDT3.0/GBN/Selective Repeat 协议的实现细节和使用场景。
