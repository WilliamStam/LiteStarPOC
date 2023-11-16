echo "Setup"

echo "Creating service alias"
sudo ln -sf /opt/api/deploy/alias.sh /etc/profile.d/api.sh
source /etc/profile.d/api.sh

api update