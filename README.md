# TestCensor
Attempts to establish connections with various websites in different categories to know the extent of online censorship

## Getting Started
Install Python

Install package manager pip, requests, beautifulsoup4, and lxml by typing in the following command lines in cmd
```bash
python -m pip install --upgrade pip
pip install requests
pip install beautifulsoup4
pip install lxml
pip install django-clear-cache
pip install matplotlib
```
## Usage

### newRequest.py

The current file is adapted to detecting online censorship mechanism in South Korea.

The program could fail due to an update on URL or change in HTML script.

The Alexa and KCSC URL on the file is from June 14th, 2020.

## Technologies

The project is created using *Python 3.7* and it involves the process of...
* Understanding the HTTP protocol and how it is dealt in Internet
* Comprehending different outcomes under the presence of online censorship
* Sending HTTP requests via python script
* Extracting information from online HTML pages
* Handling different types of exceptions

## Authors

* **EuiSuh (John) Jeong** - *Initial work* - [website](https://web2.qatar.cmu.edu/~ejeong/)

## References
* https://requests.readthedocs.io/en/master/
* https://www.youtube.com/watch?v=ng2o98k983k
