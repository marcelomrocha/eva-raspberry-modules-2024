# EVA - Computer Vision (CV) - Module #

This module is responsible for the robot's processing, which involves computer vision elements using convolutional neural network models to perform tasks such as user face recognition, facial expression recognition (FER), and QR code reading.

## QR Code reading using only OpenCV library
Initially, QR code reading was performed using the OpenCV library. Therefore, reading was not as efficient in terms of speed or accuracy. It was necessary to position the card correctly for the reading to be performed correctly.

## QR Code reading using OpenCV and ZBar libraries
Now, the ZBar library is used. The ZBar library is consistently considered the fastest and most efficient for reading barcodes and QR codes on low-power platforms, such as the Raspberry Pi.

**Main Advantage**: It is written in C, which means it runs almost directly on the hardware (without the overhead of high-level languages ​​like pure Python). It focuses on optimized algorithms for finding barcode/QR code patterns.

### How to install ###

#### 1. Install the ZBar core library ####
`
sudo apt install zbar-tools
`
#### 2. Install the Python binding ####

To install the ZBar Python package, you need to enter the **EVA_ROBOT** folder on the Raspberry (EVA robot) and activate the Python virtual environment. To do this, use the following command:

`
source venv/bin/activate
`
#### 3. Now run the following command to install the Python library ####

`
pip install pyzbar
`



