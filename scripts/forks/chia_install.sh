#!/bin/env bash
#
# Installs Chia as per https://github.com/Chia-Network/chia-blockchain/wiki/INSTALL#ubuntudebian
#

CHIA_BRANCH=$1

if [ -z ${CHIA_BRANCH} ]; then
	echo 'Skipping Chia install as not requested.'
else
	git clone --branch ${CHIA_BRANCH} --recurse-submodules https://github.com/Chia-Network/chia-blockchain.git /chia-blockchain \
		&& git submodule update --init mozilla-ca \
		&& chmod +x install.sh \
		&& /usr/bin/sh ./install.sh
fi
