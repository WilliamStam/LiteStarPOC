api() {
  case $1 in
    start)
      echo "Starting"
      sudo supervisorctl start api || true
      ;;
    stop)
      echo "Stopping"
      sudo supervisorctl stop api || true
      ;;
    restart)
      echo "Stopping"
      sudo supervisorctl stop api || true
      sleep 2
      echo "Starting"
      sudo supervisorctl start api || true
      ;;
    status)
      echo "Status"
      sudo supervisorctl status api || true
      ;;
    watch)
      sudo supervisorctl tail -f api
      ;;

    update)
      echo " > Stopping"
      sudo supervisorctl stop api || true

      echo " > Updating files"
      cd /opt/api
      git reset --hard origin/master
      git pull origin master

      sleep 2

      echo " > Linking supervisord service file"
      sudo ln -sf /opt/api/deploy/service.conf /etc/supervisor/conf.d/api.conf
      echo " > Linking service alias"
      sudo ln -sf /opt/api/deploy/alias.sh /etc/profile.d/api.sh
      source /etc/profile.d/api.sh

      sleep 2

      echo " > Updating supervisord services"
      sudo supervisorctl reread
      sudo supervisorctl update

      sleep 2

      source venv/bin/activate
      echo " > Updating dependencies"
      pip install -U -r requirements.txt

      echo "------------------------"
      echo "Done"

      read -p "Start the service? (y/n) " -n 1 -r
      echo    # (optional) move to a new line
      if [[ $REPLY =~ ^[Yy]$ ]]
      then
          echo "Starting"
          sudo supervisorctl start api || true
      fi
      ;;

    help)
      echo "Available options:"
      echo "  api start"
      echo "  api stop"
      echo "  api restart"
      echo "  api status"
      echo "  api watch"
      echo "  api update"
      ;;

    *)
      cd /opt/api
    ;;
  esac
}