Scripts and pipelines that are specific to the Mouse Imaging Centre lab. These programs are not very likely to be applicable to other centres.

Contains:
- script to crop brains for the large field of view in-vivo scans
- script to convert CT images to MINC (adding scan information to the header)
- MEMRI / saddle coil reconstruction script
- distortion correction script (ex-vivo, saddle coil, Bruker cryo coil)

Prerequisites
-------------
Python3 

Installation
------------
The perl and C++ code:
<pre><code>
./autogen.sh
[export PKG_CONFIG_PATH=/hpf/largeprojects/MICe/tools/opencv/3.1.0/lib/pkgconfig/]
./configure [--prefix=~] [--prefix=~/.local] 
make
make install
</pre></code>

PyTorch must be installed before fastai:
<pre><code>
# Python 3.6
pip3 install [--prefix=~] [--install-options="--home=~/virtual-environment/name"] https://download.pytorch.org/whl/cpu/torch-1.0.1.post2-cp36-cp36m-linux_x86_64.whl
pip3 install [--prefix=~] torchvision
# https://docs.fast.ai/install.html
# https://pytorch.org/get-started/locally/
</pre></code>

Python scripts:
<pre><code>
cd python
python3 setup.py install [--user] [--home=~/virtual-environment/name]
</pre></code>


