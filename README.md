# MOL LibraExplorer  [![Build Status](https://travis-ci.org/MoveOnLibra/LibraExplorer.svg?branch=master)](https://travis-ci.org/MoveOnLibra/LibraExplorer) [![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

An Explorer for the Libra Blockchain Netwrok powered by `MoveOnLibra` OpenAPI. The `MoveOnLibra` is an OpenAPI platform which make write Libra wallet and smart contract program easier.

## A Realtime Libra Blockchain Explorer
There are several Libra explorers there already. Why write another Libra Explorer? Because all other explorers there are not realtime. They pull data from Libra blockchian and save it to their own private database. When you access their explorer website, they search data from private database and return data to you.

On the other hand, `MOL LibraExplorer` fetch data from original Libra blockchain in realtime and return data to you. So, the data is more accurate and fresher. You can access the Libra blockchain data by visiting following website:

[explorer.moveonlibra.com](https://explorer.moveonlibra.com/) which is power by this opensource project.

It's fast and accurate.

## Installation

Require python 3.6 or above installed. Firstly, download the source code:

```sh
$ git clone https://github.com/MoveOnLibra/LibraExplorer.git
```

Then, install required pip libraries:

```sh
$ cd LibraExplorer
$ python3 -m pip install -r requirements.txt
```

Finally, start the `MOL explorer` at **http://localhost:5000** by run:

```sh
$ ./start_debug.sh
```

## How to support a new language

All language translation file is located at the `translations` directory. For example, if you want add japanese language support for this project. You need translate the file:

```text
translations/ja/LC_MESSAGES/messages.po
```

You should create a new branch to make the change:
```text
$ git branch ja_support
$ git checkout ja_support
```

when you finish the translation, run following command to compile the translation file:

```sh
$ pybabel compile -d translations -l ja
```

Now, use your favorite browser open the url  [http://localhost:5000](http://localhost:5000) to see your excellent work.

If you have completed the translation work, you can submit a pull request to merge your work to the original code base.



## What's new

### Add Chinese language support(2019-12-01)

We now support both simplified chinese and tranditional chinese language.


### Libra Network Select(2019-11-28)

"MOL LibraExplorer" support three  types of libra blockchain network:

* **Testnet**, official libra blockchain network for test, operated by Libra Association.

* **Devnet**, a specail version of testnet maintained by MoveOnLibra instead of Libra Association, support publish and execute custom move modules and scripts.

* **Anonymous**, any third-party Libra network as long as the host and port of those network is publicly accessible.

![Select Network](docs/select_network.png "Select Libra Network")

The `Select Network` feature let's you select one of supported networks to explore.

### Show Error Message For Failed Transactions(2019-11-28)

Show Error Message In the Transaction List Page:
![Select Network](docs/error_title.png "Error Message")

Show Error Code and Error Message In the Single Transaction Show Page:
![Select Network](docs/error_code.png "Error Code and Message")




## Feedback is welcome.

TODO: multi-language support
