#!/bin/env bash
#
# Initialize cactus service, depending on mode of system requested
#

cd /cactus-blockchain

. ./activate

# Only the /root/.chia folder is volume-mounted so store cactus within
mkdir -p /root/.chia/cactus
rm -f /root/.cactus
ln -s /root/.chia/cactus /root/.cactus

mkdir -p /root/.cactus/mainnet/log
cactus init >> /root/.cactus/mainnet/log/init.log 2>&1

echo 'Configuring cactus...'
while [ ! -f /root/.cactus/mainnet/config/config.yaml ]; do
  echo "Waiting for creation of /root/.cactus/mainnet/config/config.yaml..."
  sleep 1
done
sed -i 's/log_stdout: true/log_stdout: false/g' /root/.cactus/mainnet/config/config.yaml
sed -i 's/log_level: WARNING/log_level: INFO/g' /root/.cactus/mainnet/config/config.yaml

# Loop over provided list of key paths
for k in ${keys//:/ }; do
  if [ -f ${k} ]; then
    echo "Adding key at path: ${k}"
    cactus keys add -f ${k} > /dev/null
  else
    echo "Skipping 'cactus keys add' as no file found at: ${k}"
  fi
done

# Loop over provided list of completed plot directories
if [ -z "${cactus_plots_dir}" ]; then
  for p in ${plots_dir//:/ }; do
    cactus plots add -d ${p}
  done
else
  for p in ${cactus_plots_dir//:/ }; do
    cactus plots add -d ${p}
  done
fi

sed -i 's/localhost/127.0.0.1/g' ~/.cactus/mainnet/config/config.yaml

chmod 755 -R /root/.cactus/mainnet/config/ssl/ &> /dev/null
cactus init --fix-ssl-permissions > /dev/null

# Start services based on mode selected. Default is 'fullnode'
if [[ ${mode} == 'fullnode' ]]; then
  if [ ! -f ~/.cactus/mainnet/config/ssl/wallet/public_wallet.key ]; then
    echo "No wallet key found, so not starting farming services.  Please add your mnemonic.txt to /root/.chia and restart."
  else
    cactus start farmer
  fi
elif [[ ${mode} =~ ^farmer.* ]]; then
  if [ ! -f ~/.cactus/mainnet/config/ssl/wallet/public_wallet.key ]; then
    echo "No wallet key found, so not starting farming services.  Please add your mnemonic.txt to /root/.chia and restart."
  else
    cactus start farmer-only
  fi
elif [[ ${mode} =~ ^harvester.* ]]; then
  if [[ -z ${farmer_address} || -z ${farmer_port} ]]; then
    echo "A farmer peer address and port are required."
    exit
  else
    if [ ! -f /root/.cactus/farmer_ca/cactus_ca.crt ]; then
      mkdir -p /root/.cactus/farmer_ca
      response=$(curl --write-out '%{http_code}' --silent http://${controller_host}:8932/certificates/?type=cactus --output /tmp/certs.zip)
      if [ $response == '200' ]; then
        unzip /tmp/certs.zip -d /root/.cactus/farmer_ca
      else
        echo "Certificates response of ${response} from http://${controller_host}:8932/certificates/?type=cactus.  Try clicking 'New Worker' button on 'Workers' page first."
      fi
      rm -f /tmp/certs.zip
    fi
    if [ -f /root/.cactus/farmer_ca/cactus_ca.crt ]; then
      cactus init -c /root/.cactus/farmer_ca 2>&1 > /root/.cactus/mainnet/log/init.log
      chmod 755 -R /root/.cactus/mainnet/config/ssl/ &> /dev/null
      cactus init --fix-ssl-permissions > /dev/null
    else
      echo "Did not find your farmer's certificates within /root/.cactus/farmer_ca."
      echo "See: https://github.com/guydavis/machinaris/wiki/Workers#harvester"
    fi
    cactus configure --set-farmer-peer ${farmer_address}:${farmer_port}
    cactus configure --enable-upnp false
    cactus start harvester -r
  fi
elif [[ ${mode} == 'plotter' ]]; then
    echo "Starting in Plotter-only mode.  Run Plotman from either CLI or WebUI."
fi
